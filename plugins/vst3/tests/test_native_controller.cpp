#include "Controller.h"
#include "PluginIds.h"
#include "StateStream.h"

#include "hammond/ControlStateIO.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cfenv>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <limits>
#include <new>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {

using namespace Steinberg;
using namespace Steinberg::Vst;
using hammond::ControlSnapshot;
using hammond::vst3::Controller;
using hammond::vst3::read_control_state;
using hammond::vst3::write_control_state;

std::size_t checks = 0;
std::size_t threshold_cases = 0;
std::size_t string_cases = 0;
std::size_t rejected_streams = 0;

#define CHECK(condition) do { ++checks; if (!(condition)) { \
    throw std::runtime_error(std::string("line ") + std::to_string(__LINE__) + ": " #condition); \
} } while (false)

struct Expected {
    std::uint32_t id;
    const char* path;
    const char* unit;
    double maximum;
    double default_value;
    int steps;
};

// Independent literal reading of all records in data/parameter-registry.json.
// Expected identities/text/limits do not come from the production C++ table.
constexpr std::array<Expected, 45> expected{{
    {4096U, "manual.upper.bank.A.drawbar.16ft", "drawbar-position", 8.0, 0.0, 8},
    {4097U, "manual.upper.bank.A.drawbar.5_1/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4098U, "manual.upper.bank.A.drawbar.8ft", "drawbar-position", 8.0, 0.0, 8},
    {4099U, "manual.upper.bank.A.drawbar.4ft", "drawbar-position", 8.0, 0.0, 8},
    {4100U, "manual.upper.bank.A.drawbar.2_2/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4101U, "manual.upper.bank.A.drawbar.2ft", "drawbar-position", 8.0, 0.0, 8},
    {4102U, "manual.upper.bank.A.drawbar.1_3/5ft", "drawbar-position", 8.0, 0.0, 8},
    {4103U, "manual.upper.bank.A.drawbar.1_1/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4104U, "manual.upper.bank.A.drawbar.1ft", "drawbar-position", 8.0, 0.0, 8},
    {4112U, "manual.upper.bank.B.drawbar.16ft", "drawbar-position", 8.0, 0.0, 8},
    {4113U, "manual.upper.bank.B.drawbar.5_1/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4114U, "manual.upper.bank.B.drawbar.8ft", "drawbar-position", 8.0, 0.0, 8},
    {4115U, "manual.upper.bank.B.drawbar.4ft", "drawbar-position", 8.0, 0.0, 8},
    {4116U, "manual.upper.bank.B.drawbar.2_2/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4117U, "manual.upper.bank.B.drawbar.2ft", "drawbar-position", 8.0, 0.0, 8},
    {4118U, "manual.upper.bank.B.drawbar.1_3/5ft", "drawbar-position", 8.0, 0.0, 8},
    {4119U, "manual.upper.bank.B.drawbar.1_1/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4120U, "manual.upper.bank.B.drawbar.1ft", "drawbar-position", 8.0, 0.0, 8},
    {4128U, "manual.lower.bank.A.drawbar.16ft", "drawbar-position", 8.0, 0.0, 8},
    {4129U, "manual.lower.bank.A.drawbar.5_1/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4130U, "manual.lower.bank.A.drawbar.8ft", "drawbar-position", 8.0, 0.0, 8},
    {4131U, "manual.lower.bank.A.drawbar.4ft", "drawbar-position", 8.0, 0.0, 8},
    {4132U, "manual.lower.bank.A.drawbar.2_2/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4133U, "manual.lower.bank.A.drawbar.2ft", "drawbar-position", 8.0, 0.0, 8},
    {4134U, "manual.lower.bank.A.drawbar.1_3/5ft", "drawbar-position", 8.0, 0.0, 8},
    {4135U, "manual.lower.bank.A.drawbar.1_1/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4136U, "manual.lower.bank.A.drawbar.1ft", "drawbar-position", 8.0, 0.0, 8},
    {4144U, "manual.lower.bank.B.drawbar.16ft", "drawbar-position", 8.0, 0.0, 8},
    {4145U, "manual.lower.bank.B.drawbar.5_1/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4146U, "manual.lower.bank.B.drawbar.8ft", "drawbar-position", 8.0, 0.0, 8},
    {4147U, "manual.lower.bank.B.drawbar.4ft", "drawbar-position", 8.0, 0.0, 8},
    {4148U, "manual.lower.bank.B.drawbar.2_2/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4149U, "manual.lower.bank.B.drawbar.2ft", "drawbar-position", 8.0, 0.0, 8},
    {4150U, "manual.lower.bank.B.drawbar.1_3/5ft", "drawbar-position", 8.0, 0.0, 8},
    {4151U, "manual.lower.bank.B.drawbar.1_1/3ft", "drawbar-position", 8.0, 0.0, 8},
    {4152U, "manual.lower.bank.B.drawbar.1ft", "drawbar-position", 8.0, 0.0, 8},
    {8192U, "global.expression", "normalized-linear-gain-surrogate", 1.0, 1.0, 0},
    {8208U, "manual.upper.selected_bank", "bank-index-0=A-1=B", 1.0, 1.0, 1},
    {8209U, "manual.lower.selected_bank", "bank-index-0=A-1=B", 1.0, 1.0, 1},
    {12288U, "percussion.enabled", "enabled-index-0=off-1=on", 1.0, 0.0, 1},
    {12289U, "percussion.harmonic", "harmonic-index-0=second-1=third", 1.0, 0.0, 1},
    {12290U, "percussion.volume", "volume-index-0=normal-1=soft", 1.0, 0.0, 1},
    {12291U, "percussion.decay", "decay-index-0=slow-1=fast", 1.0, 0.0, 1},
    {16384U, "pedal.drawbar.mixture1", "drawbar-position", 8.0, 0.0, 8},
    {16385U, "pedal.drawbar.mixture2", "drawbar-position", 8.0, 0.0, 8},
}};

std::string ascii(const TChar* text) {
    std::string result;
    for (std::size_t index = 0; index < 128; ++index) {
        const auto code = static_cast<std::uint32_t>(text[index]);
        if (code == 0) return result;
        CHECK(code < 128);
        result.push_back(static_cast<char>(code));
    }
    throw std::runtime_error("nonterminated native metadata");
}

bool bits_equal(double first, double second) {
    return std::bit_cast<std::uint64_t>(first) == std::bit_cast<std::uint64_t>(second);
}

std::string serialize(const ControlSnapshot& controls) {
    std::string bytes;
    std::string error;
    CHECK(hammond::serialize_controls(controls, bytes, error));
    return bytes;
}

class TestStream final : public IBStream {
public:
    enum class Fault {
        None, EofFalse, EofError, ResultError, ResultFalseWithBytes,
        NegativeCount, ExcessCount, ZeroWrite, BadAlloc, Exception
    };
    std::size_t chunk{32768};
    Fault read_fault{Fault::None};
    Fault write_fault{Fault::None};
    std::size_t read_calls{0};
    std::size_t write_calls{0};
    std::size_t seek_calls{0};
    std::size_t total_read{0};

    TestStream() = default;
    explicit TestStream(std::string_view bytes) : data_(bytes) {}

    tresult PLUGIN_API queryInterface(const TUID requested_iid, void** object) override {
        if (object == nullptr) return kInvalidArgument;
        *object = nullptr;
        if (FUnknownPrivate::iidEqual(requested_iid, IBStream::iid) ||
            FUnknownPrivate::iidEqual(requested_iid, FUnknown::iid)) {
            *object = static_cast<IBStream*>(this);
            addRef();
            return kResultOk;
        }
        return kNoInterface;
    }
    uint32 PLUGIN_API addRef() override { return ++references_; }
    uint32 PLUGIN_API release() override { return --references_; }

    tresult PLUGIN_API read(void* buffer, int32 requested, int32* received) override {
        ++read_calls;
        CHECK(requested > 0 && requested <= static_cast<int32>(hammond::kMaxControlStateBytes + 1));
        CHECK(received != nullptr);
        if (read_fault == Fault::BadAlloc) throw std::bad_alloc{};
        if (read_fault == Fault::Exception) throw std::runtime_error("fixture read error");
        if (read_fault == Fault::ResultError) { *received = 0; return kInternalError; }
        if (read_fault == Fault::NegativeCount) { *received = -1; return kResultOk; }
        if (read_fault == Fault::ExcessCount) { *received = requested + 1; return kResultOk; }
        const auto limited = std::min({static_cast<std::size_t>(requested), chunk, data_.size() - position_});
        if (limited != 0) std::memcpy(buffer, data_.data() + position_, limited);
        position_ += limited;
        *received = static_cast<int32>(limited);
        total_read += limited;
        if (read_fault == Fault::ResultFalseWithBytes && *received > 0) return kResultFalse;
        if (*received == 0 && read_fault == Fault::EofFalse) return kResultFalse;
        if (*received == 0 && read_fault == Fault::EofError) return kInternalError;
        return kResultOk;
    }

    tresult PLUGIN_API write(void* buffer, int32 requested, int32* written) override {
        ++write_calls;
        CHECK(requested > 0 && requested <= static_cast<int32>(hammond::kMaxControlStateBytes));
        CHECK(written != nullptr);
        if (write_fault == Fault::BadAlloc) throw std::bad_alloc{};
        if (write_fault == Fault::Exception) throw std::runtime_error("fixture write error");
        if (write_fault == Fault::ResultError) { *written = 0; return kInternalError; }
        if (write_fault == Fault::NegativeCount) { *written = -1; return kResultOk; }
        if (write_fault == Fault::ExcessCount) { *written = requested + 1; return kResultOk; }
        if (write_fault == Fault::ZeroWrite) { *written = 0; return kResultOk; }
        const auto limited = std::min(static_cast<std::size_t>(requested), chunk);
        data_.resize(position_ + limited);
        std::memcpy(data_.data() + position_, buffer, limited);
        position_ += limited;
        *written = static_cast<int32>(limited);
        if (write_fault == Fault::ResultFalseWithBytes) return kResultFalse;
        return kResultOk;
    }

    tresult PLUGIN_API seek(int64 position, int32 mode, int64* result) override {
        ++seek_calls;
        int64 origin = 0;
        if (mode == kIBSeekCur) origin = static_cast<int64>(position_);
        else if (mode == kIBSeekEnd) origin = static_cast<int64>(data_.size());
        else if (mode != kIBSeekSet) return kInvalidArgument;
        if (position < -origin || position > std::numeric_limits<int64>::max() - origin) {
            return kInvalidArgument;
        }
        const auto destination = origin + position;
        if (static_cast<std::size_t>(destination) > data_.size()) return kInvalidArgument;
        position_ = static_cast<std::size_t>(destination);
        if (result != nullptr) *result = destination;
        return kResultOk;
    }

    tresult PLUGIN_API tell(int64* position) override {
        if (position == nullptr) return kInvalidArgument;
        *position = static_cast<int64>(position_);
        return kResultOk;
    }

    std::string bytes() const { return data_; }

private:
    std::string data_;
    std::size_t position_{0};
    uint32 references_{1}; // Stack-owned fixture; the helpers never retain it.
};

class QuietHandler final : public IComponentHandler {
public:
    std::size_t calls{0};
    uint32 references{1};
    tresult PLUGIN_API queryInterface(const TUID requested_iid, void** object) override {
        if (object == nullptr) return kInvalidArgument;
        *object = nullptr;
        if (FUnknownPrivate::iidEqual(requested_iid, IComponentHandler::iid) ||
            FUnknownPrivate::iidEqual(requested_iid, FUnknown::iid)) {
            *object = static_cast<IComponentHandler*>(this);
            addRef();
            return kResultOk;
        }
        return kNoInterface;
    }
    uint32 PLUGIN_API addRef() override { return ++references; }
    uint32 PLUGIN_API release() override { return --references; }
    tresult PLUGIN_API beginEdit(ParamID) override { ++calls; return kResultOk; }
    tresult PLUGIN_API performEdit(ParamID, ParamValue) override { ++calls; return kResultOk; }
    tresult PLUGIN_API endEdit(ParamID) override { ++calls; return kResultOk; }
    tresult PLUGIN_API restartComponent(int32) override { ++calls; return kResultOk; }
};

std::array<double, 45> values(IEditController& controller) {
    std::array<double, 45> result{};
    for (std::size_t index = 0; index < expected.size(); ++index) {
        result[index] = controller.getParamNormalized(expected[index].id);
    }
    return result;
}

void check_equal(const std::array<double, 45>& first, const std::array<double, 45>& second) {
    for (std::size_t index = 0; index < first.size(); ++index) {
        CHECK(bits_equal(first[index], second[index]));
    }
}

void descriptors_and_conversions(IEditController& controller) {
    CHECK(controller.getParameterCount() == 45);
    for (std::size_t index = 0; index < expected.size(); ++index) {
        const auto& record = expected[index];
        ParameterInfo info{};
        CHECK(controller.getParameterInfo(static_cast<int32>(index), info) == kResultOk);
        CHECK(info.id == record.id);
        CHECK(ascii(info.title) == record.path);
        CHECK(ascii(info.shortTitle) == record.path);
        CHECK(ascii(info.units) == record.unit);
        CHECK(info.stepCount == record.steps);
        CHECK(info.flags == ParameterInfo::kCanAutomate);
        CHECK(info.unitId == kRootUnitId);
        CHECK(info.defaultNormalizedValue == record.default_value / record.maximum);
        CHECK(controller.getParamNormalized(record.id) == info.defaultNormalizedValue);
        const int last = record.steps == 0 ? 8 : record.steps;
        for (int plain_index = 0; plain_index <= last; ++plain_index) {
            const auto plain = record.steps == 0 ? static_cast<double>(plain_index) / 8.0
                                                : static_cast<double>(plain_index);
            const auto normalized = plain / record.maximum;
            CHECK(controller.plainParamToNormalized(record.id, plain) == normalized);
            CHECK(controller.normalizedParamToPlain(record.id, normalized) == plain);
            String128 text{};
            CHECK(controller.getParamStringByValue(record.id, normalized, text) == kResultOk);
            double roundtrip = -1.0;
            CHECK(controller.getParamValueByString(record.id, text, roundtrip) == kResultOk);
            CHECK(bits_equal(roundtrip, normalized));
            ++string_cases;
        }
    }
    ParameterInfo marker{};
    marker.id = 17;
    CHECK(controller.getParameterInfo(-1, marker) != kResultOk && marker.id == 17);
    CHECK(controller.getParameterInfo(45, marker) != kResultOk && marker.id == 17);

    const int original_rounding = std::fegetround();
    CHECK(original_rounding != -1);
    for (const int mode : {FE_TONEAREST, FE_DOWNWARD, FE_UPWARD, FE_TOWARDZERO}) {
        CHECK(std::fesetround(mode) == 0);
        for (const auto& record : expected) {
            if (record.steps == 0) continue;
            for (int index = 0; index < record.steps; ++index) {
                const auto threshold = (static_cast<double>(index) + 0.5) / record.maximum;
                const std::array<double, 3> points{
                    std::nextafter(threshold, 0.0), threshold, std::nextafter(threshold, 1.0)};
                for (std::size_t at = 0; at < points.size(); ++at) {
                    const auto wanted = static_cast<double>(index + (at == 0 ? 0 : 1));
                    CHECK(controller.normalizedParamToPlain(record.id, points[at]) == wanted);
                    CHECK(std::fegetround() == mode);
                    ++threshold_cases;
                }
            }
        }
        for (const double expression : {-0.0, std::numeric_limits<double>::denorm_min(),
                                       std::nextafter(0.5, 0.0), 0.12345678901234567,
                                       std::nextafter(1.0, 0.0), 1.0}) {
            String128 text{};
            CHECK(controller.getParamStringByValue(8192U, expression, text) == kResultOk);
            CHECK(std::fegetround() == mode);
            double roundtrip = 0.0;
            CHECK(controller.getParamValueByString(8192U, text, roundtrip) == kResultOk);
            CHECK(bits_equal(expression, roundtrip));
            CHECK(std::fegetround() == mode);
            ++string_cases;
        }
    }
    CHECK(std::fesetround(original_rounding) == 0);
}

void invalid_values(IEditController& controller) {
    for (const auto& record : expected) {
        CHECK(controller.setParamNormalized(record.id, 0.25) == kResultOk);
        for (const double value : {-0.1, 1.1, std::numeric_limits<double>::infinity(),
                                  -std::numeric_limits<double>::infinity(),
                                  std::numeric_limits<double>::quiet_NaN()}) {
            CHECK(controller.setParamNormalized(record.id, value) != kResultOk);
            CHECK(controller.getParamNormalized(record.id) == 0.25);
            String128 text{};
            text[0] = u'Q';
            CHECK(controller.getParamStringByValue(record.id, value, text) != kResultOk);
            CHECK(text[0] == u'Q');
        }
    }
    const auto before = values(controller);
    CHECK(controller.setParamNormalized(0x1009U, 0.5) != kResultOk);
    CHECK(controller.setParamNormalized(0xFFFFFFFFU, 0.5) != kResultOk);
    check_equal(before, values(controller));
    CHECK(controller.normalizedParamToPlain(0x1009U, 0.5) == 0.0);
    CHECK(controller.plainParamToNormalized(0x1009U, 0.5) == 0.0);
    CHECK(controller.plainParamToNormalized(4096U, 0.5) == 0.0);
    CHECK(controller.getParamStringByValue(4096U, 0.5, nullptr) != kResultOk);
    double destination = 0.123;
    CHECK(controller.getParamValueByString(4096U, nullptr, destination) != kResultOk);
    CHECK(destination == 0.123);
    const std::array<std::u16string, 13> invalid{
        u"", u"nan", u"inf", u"0x1p0", u"8junk", u" 1", u"1 ", u"0.5", u"9",
        u"\uFF18", u"\U0001F600", u"1e9999", u"1e-9999"};
    for (auto text : invalid) {
        destination = 0.123;
        CHECK(controller.getParamValueByString(4096U, text.data(), destination) != kResultOk);
        CHECK(destination == 0.123);
    }
    auto too_long = std::u16string(128, u'0');
    CHECK(controller.getParamValueByString(4096U, too_long.data(), destination) != kResultOk);
    CHECK(destination == 0.123);
    CHECK(controller.setParamNormalized(8192U, -0.0) == kResultOk);
    CHECK(std::signbit(controller.getParamNormalized(8192U)));
}

ControlSnapshot rich_snapshot() {
    ControlSnapshot result{};
    for (std::size_t manual = 0; manual < 2; ++manual) {
        for (std::size_t bank = 0; bank < 2; ++bank) {
            for (std::size_t drawbar = 0; drawbar < 9; ++drawbar) {
                result.drawbars[manual][bank][drawbar] =
                    static_cast<std::uint8_t>((manual * 4 + bank * 2 + drawbar) % 9);
            }
        }
    }
    result.selected_banks = {hammond::DrawbarBank::A, hammond::DrawbarBank::B};
    result.route_enabled = {false, false};
    result.expression = -0.0;
    result.percussion = {true, hammond::PercussionHarmonic::Third,
        hammond::PercussionVolume::Soft, hammond::PercussionDecay::Fast};
    result.pedal_drawbars = {7, 3};
    return result;
}

void check_snapshot(IEditController& controller, const ControlSnapshot& snapshot) {
    for (std::size_t index = 0; index < 36; ++index) {
        const auto manual = index / 18;
        const auto bank = (index % 18) / 9;
        const auto drawbar = index % 9;
        CHECK(controller.getParamNormalized(expected[index].id) ==
              static_cast<double>(snapshot.drawbars[manual][bank][drawbar]) / 8.0);
    }
    CHECK(bits_equal(controller.getParamNormalized(8192U), snapshot.expression));
    CHECK(controller.getParamNormalized(8208U) == static_cast<double>(snapshot.selected_banks[0]));
    CHECK(controller.getParamNormalized(8209U) == static_cast<double>(snapshot.selected_banks[1]));
    CHECK(controller.getParamNormalized(12288U) == (snapshot.percussion.enabled ? 1.0 : 0.0));
    CHECK(controller.getParamNormalized(12289U) == static_cast<double>(snapshot.percussion.harmonic));
    CHECK(controller.getParamNormalized(12290U) == static_cast<double>(snapshot.percussion.volume));
    CHECK(controller.getParamNormalized(12291U) == static_cast<double>(snapshot.percussion.decay));
    CHECK(controller.getParamNormalized(16384U) == static_cast<double>(snapshot.pedal_drawbars[0]) / 8.0);
    CHECK(controller.getParamNormalized(16385U) == static_cast<double>(snapshot.pedal_drawbars[1]) / 8.0);
}

std::string old_state(std::string current, int version) {
    CHECK(version == 1 || version == 2);
    current[10] = static_cast<char>('0' + version);
    const auto pedal = current.find("pedal drawbars");
    CHECK(pedal != std::string::npos);
    current.erase(pedal, current.find('\n', pedal) + 1 - pedal);
    if (version == 1) {
        const auto percussion = current.find("percussion enabled");
        CHECK(percussion != std::string::npos);
        current.erase(percussion, current.find('\n', percussion) + 1 - percussion);
    }
    return current;
}

void stream_and_restore_tests(IEditController& controller, QuietHandler& handler) {
    const auto snapshot = rich_snapshot();
    const auto canonical = serialize(snapshot);
    for (const std::size_t chunk : {1U, 7U, 512U, 32768U}) {
        for (const auto eof : {TestStream::Fault::None, TestStream::Fault::EofFalse}) {
            TestStream input(canonical);
            input.chunk = chunk;
            input.read_fault = eof;
            ControlSnapshot read{};
            CHECK(read_control_state(&input, read) == kResultOk);
            CHECK(read == snapshot && std::signbit(read.expression));
            CHECK(input.total_read == canonical.size());
            CHECK(input.seek_calls == 0);
            CHECK(input.read_calls <= canonical.size() + 1);
            TestStream output;
            output.chunk = chunk;
            CHECK(write_control_state(&output, read) == kResultOk);
            CHECK(output.bytes() == canonical);
            CHECK(output.seek_calls == 0);
        }
    }
    ControlSnapshot destination{};
    const auto marker = destination;
    CHECK(read_control_state(nullptr, destination) == kInvalidArgument && destination == marker);
    CHECK(write_control_state(nullptr, snapshot) == kInvalidArgument);
    auto invalid_snapshot = snapshot;
    invalid_snapshot.pedal_drawbars[0] = 9;
    TestStream untouched;
    CHECK(write_control_state(&untouched, invalid_snapshot) != kResultOk);
    CHECK(untouched.write_calls == 0 && untouched.bytes().empty());

    const std::array<TestStream::Fault, 7> read_errors{
        TestStream::Fault::EofError, TestStream::Fault::ResultError,
        TestStream::Fault::ResultFalseWithBytes, TestStream::Fault::NegativeCount,
        TestStream::Fault::ExcessCount, TestStream::Fault::BadAlloc, TestStream::Fault::Exception};
    for (const auto fault : read_errors) {
        TestStream input(canonical);
        input.read_fault = fault;
        destination = marker;
        const auto result = read_control_state(&input, destination);
        CHECK(result != kResultOk && destination == marker);
        CHECK(input.seek_calls == 0);
        if (fault == TestStream::Fault::BadAlloc) CHECK(result == kOutOfMemory);
        if (fault == TestStream::Fault::Exception) CHECK(result == kInternalError);
        ++rejected_streams;
    }
    const std::array<TestStream::Fault, 7> write_errors{
        TestStream::Fault::ResultError, TestStream::Fault::ResultFalseWithBytes,
        TestStream::Fault::NegativeCount, TestStream::Fault::ExcessCount,
        TestStream::Fault::ZeroWrite, TestStream::Fault::BadAlloc, TestStream::Fault::Exception};
    for (const auto fault : write_errors) {
        TestStream output;
        output.write_fault = fault;
        const auto result = write_control_state(&output, snapshot);
        CHECK(result != kResultOk);
        CHECK(output.seek_calls == 0 && output.write_calls == 1);
        if (fault == TestStream::Fault::BadAlloc) CHECK(result == kOutOfMemory);
        if (fault == TestStream::Fault::Exception) CHECK(result == kInternalError);
        ++rejected_streams;
    }
    for (const auto size : {hammond::kMaxControlStateBytes, hammond::kMaxControlStateBytes + 1}) {
        auto padded = canonical;
        padded.resize(size, ' ');
        TestStream input(padded);
        input.chunk = 7;
        destination = marker;
        const auto result = read_control_state(&input, destination);
        if (size == hammond::kMaxControlStateBytes) CHECK(result == kResultOk && destination == snapshot);
        else { CHECK(result != kResultOk && destination == marker); ++rejected_streams; }
        CHECK(input.total_read <= hammond::kMaxControlStateBytes + 1);
    }
    // The helper starts at the host's current position and does not seek.
    TestStream offset_input("prefix:" + canonical);
    CHECK(offset_input.seek(7, IBStream::kIBSeekSet, nullptr) == kResultOk);
    offset_input.seek_calls = 0;
    CHECK(read_control_state(&offset_input, destination) == kResultOk && destination == snapshot);
    CHECK(offset_input.seek_calls == 0);

    for (const int version : {1, 2, 3}) {
        const auto text = version == 3 ? canonical : old_state(canonical, version);
        auto wanted = snapshot;
        if (version < 3) wanted.pedal_drawbars = {0, 0};
        if (version == 1) wanted.percussion = {};
        TestStream input(text);
        input.chunk = 3;
        CHECK(controller.setComponentState(&input) == kResultOk);
        check_snapshot(controller, wanted);
        CHECK(handler.calls == 0);
    }
    const auto before = values(controller);
    // Every truncation before complete 'end' is rejected without partial values.
    const auto complete_end = canonical.rfind("end") + 3;
    CHECK(complete_end != std::string::npos && complete_end <= canonical.size());
    for (std::size_t size = 0; size < complete_end; ++size) {
        TestStream input(std::string_view(canonical).substr(0, size));
        CHECK(controller.setComponentState(&input) != kResultOk);
        check_equal(before, values(controller));
        ++rejected_streams;
    }
    auto malformed = canonical;
    malformed.replace(malformed.find("pedal drawbars 7"), 15, "pedal drawbars 9");
    for (const auto& bad : std::vector<std::string>{malformed, canonical + "trailing", "B3CONTROLS4\n", "\xEF\xBB\xBF" + canonical}) {
        TestStream input(bad);
        CHECK(controller.setComponentState(&input) != kResultOk);
        check_equal(before, values(controller));
        ++rejected_streams;
    }
    CHECK(handler.calls == 0);
}

} // namespace

int main() {
    try {
        QuietHandler handler;
        Controller controller;
        IEditController& native = controller;
        CHECK(native.getParameterCount() == 0);
        CHECK(controller.initialize(nullptr) == kResultOk);
        CHECK(controller.initialize(nullptr) != kResultOk);
        CHECK(native.setComponentHandler(&handler) == kResultOk);
        descriptors_and_conversions(native);
        invalid_values(native);
        stream_and_restore_tests(native, handler);
        CHECK(native.createView(ViewType::kEditor) == nullptr);
        CHECK(handler.calls == 0);
        CHECK(controller.terminate() == kResultOk);
        CHECK(native.getParameterCount() == 0);
        CHECK(handler.references == 1);
        CHECK(controller.terminate() != kResultOk);
        CHECK(controller.initialize(nullptr) == kResultOk);
        CHECK(native.getParameterCount() == 45);
        CHECK(native.getParamNormalized(8192U) == 1.0);
        CHECK(native.getParamNormalized(16384U) == 0.0);
        CHECK(controller.terminate() == kResultOk);
        auto* created = Controller::createInstance(nullptr);
        CHECK(created != nullptr);
        IEditController* native_interface = nullptr;
        CHECK(created->queryInterface(IEditController::iid, reinterpret_cast<void**>(&native_interface)) == kResultOk);
        CHECK(native_interface != nullptr);
        CHECK(native_interface->initialize(nullptr) == kResultOk);
        CHECK(native_interface->getParameterCount() == 45);
        CHECK(native_interface->terminate() == kResultOk);
        native_interface->release();
        created->release();
        std::cout << "native-controller: checks=" << checks
                  << " threshold_cases=" << threshold_cases
                  << " string_roundtrips=" << string_cases
                  << " rejected_streams=" << rejected_streams << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "native-controller failure: " << error.what() << '\n';
        return 1;
    }
}
