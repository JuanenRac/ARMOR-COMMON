// Generated from the A.R.M.O.R. JSON Schemas by tools/generate_types.py. Do not edit.
#pragma once
#include <array>
#include <cstddef>
#include <string_view>

namespace armor::contract {

inline constexpr std::string_view kNodeIdPattern = R"(^[a-z0-9][a-z0-9_-]{0,63}$)";
inline constexpr std::size_t kMaxTargets = 15;
inline constexpr double kMaxLux = 200000.0;
inline constexpr int kSensitivityMin = 1;
inline constexpr int kSensitivityMax = 10;
inline constexpr std::array<std::string_view, 3> kCommands = {"calibrate", "set_thresholds", "restart"};

}  // namespace armor::contract
