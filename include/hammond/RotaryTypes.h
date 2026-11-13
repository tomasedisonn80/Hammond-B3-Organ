#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

// Independent nominal M7 research types. These are not Engine parameters,
// musical control-state fields, measured cabinet values or a native host API.
// Contract and provenance: docs/ROTARY_NUMERICAL_CONTRACT.md (v1).
namespace hammond::rotary {

inline constexpr std::string_view kModelId = "nominal-effective-mouth-rotary-v1";
inline constexpr std::string_view kNumericalContractId = "rotary-numerics-v1";
inline constexpr std::size_t kRotorCount = 2;
inline constexpr std::size_t kMicrophoneCount = 2;
inline constexpr std::size_t kPathCount = kRotorCount * kMicrophoneCount;

// Engineering admission limits, deliberately distinct from specimen data.
inline constexpr double kTwoPi = 6.283185307179586476925286766559;
inline constexpr double kMinSoundSpeedMetresPerSecond = 300.0;
inline constexpr double kMaxSoundSpeedMetresPerSecond = 380.0;
inline constexpr double kMaxCoordinateMetres = 10.0;
inline constexpr double kMaxRadiusMetres = 1.0;
inline constexpr double kMinPathMetres = 0.02;
inline constexpr double kMaxPathMetres = 20.0;
inline constexpr double kMinReferenceDistanceMetres = 0.02;
inline constexpr double kMaxReferenceDistanceMetres = 10.0;
inline constexpr double kMaxSpeedRadiansPerSecond = 200.0;
inline constexpr double kMinTimeConstantSeconds = 0.001;
inline constexpr double kMaxTimeConstantSeconds = 60.0;
inline constexpr double kMaxTangentialMach = 0.25;
inline constexpr double kMaxInputMagnitude = 1.0;
inline constexpr std::uint64_t kMaxEpochSeconds = 86400;
inline constexpr std::uint32_t kMaxBlockFrames = 4096;
inline constexpr std::size_t kMaxEventsPerBlock = 1024;
inline constexpr std::size_t kMaxHistoryFrames = 16384;
inline constexpr std::uint32_t kAlgorithmicLatencyFrames = 2;
inline constexpr std::uint32_t kMaxSolverIterations = 48;
inline constexpr double kMaxSolverResidualSeconds = 1.0e-11;

enum class RotorId : std::uint8_t { Horn = 0, Drum = 1 };
enum class SpeedCommand : std::uint8_t { Chorale = 0, Tremolo = 1 };

// Separate error vocabulary: the nominal module does not extend hammond::Status.
enum class Status : std::uint8_t {
    Ok = 0,
    NotPrepared,
    InvalidSpec,
    InvalidProfile,
    InvalidEvent,
    InvalidBuffer,
    TooManyEvents,
    BlockTooLarge,
    TimelineOverflow,
    InsufficientHistory,
    NumericalFailure,
    AllocationFailure,
};

[[nodiscard]] constexpr bool is_supported_sample_rate(double rate) noexcept {
    return rate == 44100.0 || rate == 48000.0 || rate == 96000.0 || rate == 192000.0;
}

[[nodiscard]] constexpr bool is_valid_rotor(RotorId rotor) noexcept {
    return rotor == RotorId::Horn || rotor == RotorId::Drum;
}

[[nodiscard]] constexpr bool is_valid_command(SpeedCommand command) noexcept {
    return command == SpeedCommand::Chorale || command == SpeedCommand::Tremolo;
}

[[nodiscard]] constexpr std::string_view command_name(SpeedCommand command) noexcept {
    switch (command) {
    case SpeedCommand::Chorale: return "chorale";
    case SpeedCommand::Tremolo: return "tremolo";
    }
    return {};
}

[[nodiscard]] constexpr std::string_view status_name(Status status) noexcept {
    switch (status) {
    case Status::Ok: return "ok";
    case Status::NotPrepared: return "not_prepared";
    case Status::InvalidSpec: return "invalid_spec";
    case Status::InvalidProfile: return "invalid_profile";
    case Status::InvalidEvent: return "invalid_event";
    case Status::InvalidBuffer: return "invalid_buffer";
    case Status::TooManyEvents: return "too_many_events";
    case Status::BlockTooLarge: return "block_too_large";
    case Status::TimelineOverflow: return "timeline_overflow";
    case Status::InsufficientHistory: return "insufficient_history";
    case Status::NumericalFailure: return "numerical_failure";
    case Status::AllocationFailure: return "allocation_failure";
    }
    return {};
}

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};
    [[nodiscard]] bool operator==(const Vec3&) const noexcept = default;
};

struct MotionProfile {
    double slow_rad_s{0.0};
    double fast_rad_s{0.0};
    double tau_up_s{0.0};
    double tau_down_s{0.0};
    std::int8_t direction{1};
    [[nodiscard]] bool operator==(const MotionProfile&) const noexcept = default;
};

struct RotorProfile {
    Vec3 origin_m{};
    double radius_m{0.0};
    MotionProfile motion{};
    double initial_phase_rad{0.0};
    double initial_speed_rad_s{0.0};
    SpeedCommand initial_command{SpeedCommand::Chorale};
    [[nodiscard]] bool operator==(const RotorProfile&) const noexcept = default;
};

struct MicrophoneProfile {
    Vec3 position_m{};
    [[nodiscard]] bool operator==(const MicrophoneProfile&) const noexcept = default;
};

// Array order is Horn, Drum and Left, Right respectively. Authoring provenance
// remains in the strict external profile. This immutable runtime projection has
// only admitted SI values. A default-constructed Profile is invalid.
struct Profile {
    std::array<RotorProfile, kRotorCount> rotors{};
    std::array<MicrophoneProfile, kMicrophoneCount> microphones{};
    double sound_speed_m_s{0.0};
    double reference_distance_m{0.0};
    [[nodiscard]] bool operator==(const Profile&) const noexcept = default;
};

// Continuous angle is phase_rad + 2*pi*turns. phase_rad is always in [0,2*pi);
// speed magnitude is nonnegative. Direction belongs to the immutable profile.
struct MotionState {
    double phase_rad{0.0};
    std::int64_t turns{0};
    double speed_rad_s{0.0};
    [[nodiscard]] bool operator==(const MotionState&) const noexcept = default;
};

// One exact constant-command segment, anchored at a sample boundary of its
// clock epoch. Evaluate elapsed physical seconds from this anchor, not from the
// start of the current host block. Repeated unchanged commands do not reanchor.
struct MotionSegment {
    std::uint64_t anchor_frame{0};
    MotionState initial{};
    double target_rad_s{0.0};
    double tau_s{0.0};
    std::int8_t direction{1};
    [[nodiscard]] bool operator==(const MotionSegment&) const noexcept = default;
};

struct ProcessSpec {
    double sample_rate{48000.0};
    std::uint32_t max_block_frames{1024};
    [[nodiscard]] bool operator==(const ProcessSpec&) const noexcept = default;
};

// Stable nondecreasing offsets in [0,frames], including the end boundary.
// Equal-offset events keep input order. A common cabinet switch is two events.
// Zero-frame calls may apply offset-zero commands but advance no physical time.
struct CommandEvent {
    std::uint32_t offset{0};
    RotorId rotor{RotorId::Horn};
    SpeedCommand command{SpeedCommand::Chorale};
    [[nodiscard]] bool operator==(const CommandEvent&) const noexcept = default;
};

struct PathBounds {
    double min_distance_m{0.0};
    double max_distance_m{0.0};
    double max_tangential_mach{0.0};
    [[nodiscard]] bool operator==(const PathBounds&) const noexcept = default;
};

// This is a direct, omnidirectional point-path result. No microphone pattern,
// cabinet/driver/room filtering or electrical conversion is included.
struct PathResult {
    double delay_s{0.0};
    double distance_m{0.0};
    double emission_phase_rad{0.0};
    double radial_speed_m_s{0.0}; // Positive toward the microphone.
    double frequency_ratio{1.0};
    double distance_gain{0.0}; // reference_distance_m / distance_m.
    double residual_s{0.0};
    std::uint32_t iterations{0};
    [[nodiscard]] bool operator==(const PathResult&) const noexcept = default;
};

// Signed integer plus fraction prevents loss of fractional resolution when an
// epoch is long. For negative time, floor semantics still apply; 0 <= fraction < 1.
struct SamplePosition {
    std::int64_t frame{0};
    double fraction{0.0};
    [[nodiscard]] bool operator==(const SamplePosition&) const noexcept = default;
};

// Failure observations are returned to the caller. A rejected processing call
// does not increment persistent counters or partially publish caller audio.
struct ProcessResult {
    Status status{Status::Ok};
    std::uint32_t events_consumed{0};
    double max_solver_residual_s{0.0};
    std::uint32_t max_solver_iterations{0};
    [[nodiscard]] constexpr bool ok() const noexcept { return status == Status::Ok; }
    [[nodiscard]] constexpr explicit operator bool() const noexcept { return ok(); }
};

} // namespace hammond::rotary
