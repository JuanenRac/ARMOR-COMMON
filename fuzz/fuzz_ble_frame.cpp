// libFuzzer target: the Bluetooth set-up channel. Bytes are fed in arbitrary slices to the message assembler, and every message it gives is read as a request.
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "../firmware_base/core/ble_frame.hpp"

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data, std::size_t size) {
  if (size == 0) return 0;
  armor::ble::Assembler assembler;
  std::size_t position = 1;
  const std::size_t slice = 1 + (data[0] % 23);   // the first byte chooses how the rest is cut, as the radio would
  std::string message;
  while (position < size) {
    const std::size_t count = std::min(slice, size - position);
    bool have = assembler.feed(data + position, count, message);
    position += count;
    while (have) {
      armor::ble::Request request;
      if (armor::ble::parse_request(message, request) && (request.op.empty() || request.op.size() > 32 || request.id < 0)) std::abort();
      have = assembler.take(message);
    }
    if (assembler.pending() > armor::ble::kMaxMessage + 4096) std::abort();   // the buffer cannot grow past one message and what one write brings
  }
  return 0;
}
