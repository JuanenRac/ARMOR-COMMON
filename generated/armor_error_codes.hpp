// Generated from openapi/armor-server.yaml by tools/generate_rest_types.py. Do not edit.
#pragma once
#include <array>
#include <string_view>

namespace armor::contract {

inline constexpr std::array<std::string_view, 27> kApiErrorCodes = {"invalid_request", "not_found", "conflict", "rate_limited", "forbidden", "unauthorized", "out_of_scope", "remote_policy", "wrong_password", "totp_locked", "totp_setup_required", "elevation_required", "admin_required", "bad_code", "bad_proof", "wrong_pin", "pin_locked", "pin_not_set", "pin_required", "confirmation_required", "node_offline", "unknown_node", "unknown_operation", "no_image_for_board", "no_image_in_release", "wrong_board", "wrong_node_kind"};
inline constexpr std::array<std::string_view, 3> kPinErrorCodes = {"wrong_pin", "pin_locked", "pin_not_set"};

}  // namespace armor::contract
