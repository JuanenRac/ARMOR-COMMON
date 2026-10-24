// libFuzzer target: the Improv serial parser of the nodes. Any stream of bytes must give only packets with a right checksum, and any packet's data must be refused or read as a command.
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
#include <cstddef>
#include <cstdint>
#include <cstdlib>

#include "../firmware_base/core/improv.hpp"

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data, std::size_t size) {
  armor::improv::Parser parser;
  for (std::size_t i = 0; i < size; ++i) {
    const auto packet = parser.feed(data[i]);
    if (!packet) continue;
    armor::improv::Rpc rpc;
    const armor::improv::Error error = armor::improv::parse_rpc(packet->data, rpc);
    if (error == armor::improv::Error::kNone && rpc.command == armor::improv::Command::kWifiSettings && (rpc.ssid.empty() || rpc.ssid.size() > 32 || rpc.password.size() > 63)) std::abort();
  }
  return 0;
}
