#include "hammond/RotaryPropagation.h"

#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

// Test-only persistent batch adapter. It owns immutable native histories and
// exposes native results, without an oracle, numerical budget or root algorithm.
// Each input line produces one flushed JSON record. The Python acceptance suite
// can query all active bisection candidates in a batch in this single process.
namespace {
using namespace hammond::rotary;

template <typename T>
T integer(std::istream& input) {
    T value{};
    if (!(input >> value)) throw std::runtime_error("missing integer");
    return value;
}

double scalar(std::istream& input) {
    std::string token;
    if (!(input >> token)) throw std::runtime_error("missing scalar");
    char* end = nullptr;
    const double value = std::strtod(token.c_str(), &end);
    if (end != token.c_str() + token.size()) throw std::runtime_error("invalid scalar");
    return value;
}

std::int8_t direction(std::istream& input) {
    const auto value = integer<int>(input);
    if (value < -128 || value > 127) throw std::runtime_error("direction out of byte range");
    return static_cast<std::int8_t>(value);
}

SpeedCommand command(std::istream& input) {
    const auto value = integer<unsigned>(input);
    if (value > 255) throw std::runtime_error("command out of byte range");
    return static_cast<SpeedCommand>(value);
}

Vec3 vector(std::istream& input) {
    const double x = scalar(input);
    const double y = scalar(input);
    const double z = scalar(input);
    return {x, y, z};
}

SamplePosition position(std::istream& input) {
    const auto frame = integer<std::int64_t>(input);
    return {frame, scalar(input)};
}

void end_request(std::istream& input) {
    std::string extra;
    if (input >> extra) throw std::runtime_error("trailing request fields");
}

void print_vector(const Vec3& value) {
    std::cout << '[' << value.x << ',' << value.y << ',' << value.z << ']';
}

void print_state(const MotionState& value) {
    std::cout << '[' << value.phase_rad << ',' << value.turns << ',' << value.speed_rad_s << ']';
}

void start_result(std::uint64_t id, Status status) {
    std::cout << "{\"id\":" << id << ",\"status\":\"" << status_name(status) << '"';
}

struct Scene {
    std::vector<MotionSegment> segments;
    MotionHistoryView history;
    PreparedRetardedPath path;
    Vec3 origin{};
    double radius{0.0};
    MicrophoneProfile microphone{};
};

std::unordered_map<std::uint64_t, std::unique_ptr<Scene>> scenes;

void print_geometry(const Scene& scene, const MotionState& state) {
    Vec3 source;
    Vec3 velocity;
    const auto status = evaluate_circular_source(scene.origin, scene.radius, state,
                                                 scene.history.profile().direction, source, velocity);
    if (status != Status::Ok) throw std::runtime_error("admitted scene geometry failed");
    std::cout << ",\"state\":";
    print_state(state);
    std::cout << ",\"position\":";
    print_vector(source);
    std::cout << ",\"velocity\":";
    print_vector(velocity);
    std::cout << ",\"cartesian_distance\":"
              << std::hypot(scene.microphone.position_m.x - source.x,
                            scene.microphone.position_m.y - source.y,
                            scene.microphone.position_m.z - source.z);
}

void run(std::istringstream& input, const std::string& operation, std::uint64_t id) {
    if (operation == "scene") {
        const auto scene_id = integer<std::uint64_t>(input);
        if (scenes.contains(scene_id) || scenes.size() >= 16000) {
            throw std::runtime_error("duplicate or excessive scenes");
        }
        const double rate = scalar(input);
        MotionProfile profile;
        profile.slow_rad_s = scalar(input);
        profile.fast_rad_s = scalar(input);
        profile.tau_up_s = scalar(input);
        profile.tau_down_s = scalar(input);
        profile.direction = direction(input);
        const double phase = scalar(input);
        const double speed = scalar(input);
        const auto initial_command = command(input);
        const auto through = integer<std::uint64_t>(input);
        const auto event_count = integer<std::size_t>(input);
        if (event_count > 4096) throw std::runtime_error("excessive events");
        std::vector<std::pair<std::uint64_t, SpeedCommand>> events;
        for (std::size_t index = 0; index < event_count; ++index) {
            const auto frame = integer<std::uint64_t>(input);
            events.emplace_back(frame, command(input));
        }
        auto scene = std::make_unique<Scene>();
        scene->origin = vector(input);
        scene->radius = scalar(input);
        scene->microphone.position_m = vector(input);
        const double sound_speed = scalar(input);
        const double reference_distance = scalar(input);
        end_request(input);

        RotaryMotion owner;
        auto status = owner.prepare(profile, phase, speed, initial_command, rate);
        if (status == Status::Ok) scene->segments.push_back(owner.segment());
        for (const auto& event : events) {
            if (status != Status::Ok) break;
            status = owner.apply_command(event.first, event.second);
            if (status != Status::Ok) break;
            const auto snapshot = owner.segment();
            if (scene->segments.back() == snapshot) continue;
            if (scene->segments.back().anchor_frame == snapshot.anchor_frame) scene->segments.back() = snapshot;
            else scene->segments.push_back(snapshot);
        }
        if (status == Status::Ok) {
            status = scene->history.prepare(profile, owner.epoch_initial_state(), rate,
                                             scene->segments, through);
        }
        if (status == Status::Ok) {
            status = scene->path.prepare(scene->history, scene->origin, scene->radius,
                                          scene->microphone, sound_speed, reference_distance);
        }
        start_result(id, status);
        if (status == Status::Ok) {
            const auto bounds = scene->path.bounds();
            std::cout << ",\"bounds\":[" << bounds.min_distance_m << ',' << bounds.max_distance_m
                      << ',' << bounds.max_tangential_mach << "],\"segments\":" << scene->segments.size();
            scenes.emplace(scene_id, std::move(scene));
        }
    } else if (operation == "receiver") {
        const auto scene_id = integer<std::uint64_t>(input);
        const auto source_id = integer<std::uint64_t>(input);
        if (scenes.contains(scene_id) || !scenes.contains(source_id) || scenes.size() >= 16000) {
            throw std::runtime_error("invalid receiver scene");
        }
        auto scene = std::make_unique<Scene>();
        const auto& source = *scenes.at(source_id);
        scene->history = source.history;
        scene->origin = source.origin;
        scene->radius = source.radius;
        scene->microphone.position_m = vector(input);
        const double sound_speed = scalar(input);
        const double reference_distance = scalar(input);
        end_request(input);
        const auto status = scene->path.prepare(scene->history, scene->origin, scene->radius,
                                                 scene->microphone, sound_speed, reference_distance);
        start_result(id, status);
        if (status == Status::Ok) {
            const auto bounds = scene->path.bounds();
            std::cout << ",\"bounds\":[" << bounds.min_distance_m << ',' << bounds.max_distance_m
                      << ',' << bounds.max_tangential_mach << "],\"borrowed_from\":" << source_id;
            scenes.emplace(scene_id, std::move(scene));
        }
    } else if (operation == "geometry") {
        const auto origin = vector(input);
        const double radius = scalar(input);
        const double phase = scalar(input);
        const double speed = scalar(input);
        const auto sign = direction(input);
        const auto microphone = vector(input);
        end_request(input);
        Vec3 source;
        Vec3 velocity;
        const auto status = evaluate_circular_source(origin, radius, {phase, 0, speed}, sign, source, velocity);
        start_result(id, status);
        if (status == Status::Ok) {
            std::cout << ",\"position\":";
            print_vector(source);
            std::cout << ",\"velocity\":";
            print_vector(velocity);
            std::cout << ",\"distance\":"
                      << std::hypot(microphone.x - source.x, microphone.y - source.y, microphone.z - source.z);
        }
    } else if (operation == "state" || operation == "solve") {
        const auto scene_id = integer<std::uint64_t>(input);
        const auto query = position(input);
        end_request(input);
        if (!scenes.contains(scene_id)) throw std::runtime_error("missing scene");
        const auto& scene = *scenes.at(scene_id);
        if (operation == "state") {
            MotionState state;
            const auto status = scene.history.state_at(query, state);
            start_result(id, status);
            if (status == Status::Ok) print_geometry(scene, state);
        } else {
            PathResult path;
            SamplePosition emission;
            const auto status = scene.path.solve(query, path, emission);
            start_result(id, status);
            if (status == Status::Ok) {
                std::cout << ",\"delay\":" << path.delay_s << ",\"distance\":" << path.distance_m
                          << ",\"phase\":" << path.emission_phase_rad
                          << ",\"radial_speed\":" << path.radial_speed_m_s
                          << ",\"ratio\":" << path.frequency_ratio
                          << ",\"gain\":" << path.distance_gain
                          << ",\"residual\":" << path.residual_s
                          << ",\"evaluations\":" << path.iterations
                          << ",\"emission\":[" << emission.frame << ',' << emission.fraction << ']';
                MotionState state;
                if (scene.history.state_at(emission, state) != Status::Ok) {
                    throw std::runtime_error("solver returned unavailable emission");
                }
                // This diagnostic query is outside solve() and is not a solver
                // iteration. It independently exposes the selected trajectory.
                print_geometry(scene, state);
            }
        }
    } else {
        throw std::runtime_error("unknown operation");
    }
    std::cout << "}\n" << std::flush;
}
} // namespace

int main() {
    std::cout << std::setprecision(std::numeric_limits<double>::max_digits10);
    std::string line;
    std::size_t count = 0;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        if (++count > 1000000 || line.size() > 1024 * 1024) {
            std::cerr << "excessive probe input\n";
            return 2;
        }
        try {
            std::istringstream input(line);
            std::string operation;
            input >> operation;
            const auto id = integer<std::uint64_t>(input);
            run(input, operation, id);
        } catch (const std::exception& error) {
            std::cerr << "probe request " << count << ": " << error.what() << '\n';
            return 2;
        }
    }
    return std::cin.bad() ? 2 : 0;
}
