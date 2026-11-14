#include "hammond/RotaryMotion.h"

#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Test-only batch adapter. One whitespace-delimited request produces one JSON
// line. The adapter contains no motion approximation or acceptance tolerance.
// tests/test_rotary_motion_acceptance.py owns fixtures and independent grading.
namespace {
using namespace hammond::rotary;

template <typename T>
T integer(std::istream& input) {
    T result{};
    if (!(input >> result)) throw std::runtime_error("missing integer");
    return result;
}

double scalar(std::istream& input) {
    std::string token;
    if (!(input >> token)) throw std::runtime_error("missing scalar");
    char* end = nullptr;
    const double value = std::strtod(token.c_str(), &end);
    // strtod also admits representable subnormals; ERANGE alone is not a
    // parsing failure. Physical admission remains the native module's work.
    if (end != token.c_str() + token.size()) throw std::runtime_error("invalid scalar");
    return value;
}

MotionState read_state(std::istream& input) {
    const double phase = scalar(input);
    const auto turns = integer<std::int64_t>(input);
    const double speed = scalar(input);
    return {phase, turns, speed};
}

std::int8_t direction(std::istream& input) {
    const int value = integer<int>(input);
    if (value < -128 || value > 127) throw std::runtime_error("direction out of byte range");
    return static_cast<std::int8_t>(value);
}

SpeedCommand command(std::istream& input) {
    const unsigned value = integer<unsigned>(input);
    if (value > 255) throw std::runtime_error("command out of byte range");
    return static_cast<SpeedCommand>(value);
}

MotionSegment segment(std::istream& input) {
    const MotionState initial = read_state(input);
    const double target = scalar(input);
    const double tau = scalar(input);
    const auto sign = direction(input);
    return {0, initial, target, tau, sign};
}

void end_request(std::istream& input) {
    std::string extra;
    if (input >> extra) throw std::runtime_error("trailing request fields");
}

void print_state(const MotionState& value) {
    std::cout << '[' << value.phase_rad << ',' << value.turns << ',' << value.speed_rad_s << ']';
}

void start_result(std::uint64_t id, Status status) {
    std::cout << "{\"id\":" << id << ",\"status\":\"" << status_name(status) << '"';
}

void print_evaluation(std::uint64_t id, Status status, const MotionEvaluation& value) {
    start_result(id, status);
    if (status == Status::Ok) {
        std::cout << ",\"state\":";
        print_state(value.state);
        std::cout << ",\"increment\":" << value.angle_increment_rad;
    }
    std::cout << "}\n";
}

void run_request(std::istringstream& input, const std::string& operation, std::uint64_t id) {
    if (operation == "segment") {
        const auto motion = segment(input);
        const double elapsed = scalar(input);
        end_request(input);
        MotionEvaluation result;
        const auto status = evaluate_motion_segment(motion, elapsed, result);
        print_evaluation(id, status, result);
    } else if (operation == "sample") {
        auto motion = segment(input);
        motion.anchor_frame = integer<std::uint64_t>(input);
        const auto frame = integer<std::int64_t>(input);
        const double fraction = scalar(input);
        const double rate = scalar(input);
        end_request(input);
        MotionState result;
        const auto status = evaluate_motion_segment_at(motion, {frame, fraction}, rate, result);
        start_result(id, status);
        if (status == Status::Ok) {
            std::cout << ",\"state\":";
            print_state(result);
        }
        std::cout << "}\n";
    } else if (operation == "prehistory" || operation == "presample") {
        const MotionState initial = read_state(input);
        const auto sign = direction(input);
        if (operation == "prehistory") {
            const double elapsed = scalar(input);
            end_request(input);
            MotionEvaluation result;
            const auto status = evaluate_motion_prehistory(initial, sign, elapsed, result);
            print_evaluation(id, status, result);
        } else {
            const auto frame = integer<std::int64_t>(input);
            const double fraction = scalar(input);
            const double rate = scalar(input);
            end_request(input);
            MotionState result;
            const auto status = evaluate_motion_prehistory_at(initial, sign, {frame, fraction}, rate, result);
            start_result(id, status);
            if (status == Status::Ok) {
                std::cout << ",\"state\":";
                print_state(result);
            }
            std::cout << "}\n";
        }
    } else if (operation == "split") {
        auto motion = segment(input);
        const double first = scalar(input);
        const double second = scalar(input);
        end_request(input);
        MotionEvaluation whole, left, right;
        auto status = evaluate_motion_segment(motion, first + second, whole);
        if (status == Status::Ok) status = evaluate_motion_segment(motion, first, left);
        if (status == Status::Ok) {
            motion.initial = left.state;
            status = evaluate_motion_segment(motion, second, right);
        }
        start_result(id, status);
        if (status == Status::Ok) {
            std::cout << ",\"state\":";
            print_state(whole.state);
            std::cout << ",\"split_state\":";
            print_state(right.state);
            std::cout << ",\"increment\":" << whole.angle_increment_rad
                      << ",\"left_increment\":" << left.angle_increment_rad
                      << ",\"right_increment\":" << right.angle_increment_rad;
        }
        std::cout << "}\n";
    } else if (operation == "timeline") {
        const double rate = scalar(input);
        MotionProfile profile;
        profile.slow_rad_s = scalar(input);
        profile.fast_rad_s = scalar(input);
        profile.tau_up_s = scalar(input);
        profile.tau_down_s = scalar(input);
        profile.direction = direction(input);
        const double initial_phase = scalar(input);
        const double initial_speed = scalar(input);
        const auto initial_command = command(input);
        const auto event_count = integer<std::size_t>(input);
        const auto query_count = integer<std::size_t>(input);
        if (event_count > 4096 || query_count > 4096) throw std::runtime_error("oversized timeline fixture");
        std::vector<std::pair<std::uint64_t, SpeedCommand>> events;
        std::vector<SamplePosition> queries;
        for (std::size_t i = 0; i < event_count; ++i) {
            const auto frame = integer<std::uint64_t>(input);
            events.emplace_back(frame, command(input));
        }
        for (std::size_t i = 0; i < query_count; ++i) {
            const auto frame = integer<std::int64_t>(input);
            queries.push_back({frame, scalar(input)});
        }
        end_request(input);
        RotaryMotion owner;
        auto status = owner.prepare(profile, initial_phase, initial_speed, initial_command, rate);
        std::size_t event = 0;
        std::vector<MotionState> states;
        for (const auto query : queries) {
            if (status != Status::Ok) break;
            while (query.frame >= 0 && event < events.size()
                   && events[event].first <= static_cast<std::uint64_t>(query.frame)) {
                status = owner.apply_command(events[event].first, events[event].second);
                ++event;
                if (status != Status::Ok) break;
            }
            MotionState state;
            if (status == Status::Ok) status = owner.state_at(query, state);
            if (status == Status::Ok) states.push_back(state);
        }
        start_result(id, status);
        std::cout << ",\"states\":[";
        for (std::size_t i = 0; i < states.size(); ++i) {
            if (i != 0) std::cout << ',';
            print_state(states[i]);
        }
        std::cout << "]}\n";
    } else {
        throw std::runtime_error("unknown operation");
    }
}
} // namespace

int main() {
    std::cout << std::setprecision(std::numeric_limits<double>::max_digits10);
    std::string line;
    std::size_t count = 0;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        if (++count > 100000 || line.size() > 1024 * 1024) {
            std::cerr << "oversized probe batch\n";
            return 2;
        }
        try {
            std::istringstream input(line);
            std::string operation;
            input >> operation;
            const auto id = integer<std::uint64_t>(input);
            run_request(input, operation, id);
        } catch (const std::exception& error) {
            std::cerr << "probe request " << count << ": " << error.what() << '\n';
            return 2;
        }
    }
    return std::cin.bad() ? 2 : 0;
}
