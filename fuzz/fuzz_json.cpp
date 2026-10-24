// libFuzzer target: the JSON parser every node uses. Any input must either be refused or give a document that survives being written and read again with the same shape.
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string_view>

#include "../firmware_base/core/json.hpp"

namespace {
using armor::json::Type;
using armor::json::Value;
using armor::json::Writer;

void emit(const Value& value, Writer& out) {
  switch (value.type) {
    case Type::kNull: out.null(); break;
    case Type::kBool: out.boolean(value.boolean); break;
    case Type::kNumber: out.number(value.number); break;
    case Type::kString: out.string(value.text); break;
    case Type::kArray:
      out.begin_array();
      for (const Value& item : value.items) emit(item, out);
      out.end_array();
      break;
    case Type::kObject:
      out.begin_object();
      for (std::size_t i = 0; i < value.items.size(); ++i) { out.key(value.names[i]); emit(value.items[i], out); }
      out.end_object();
      break;
  }
}

bool same_shape(const Value& a, const Value& b) {
  if (a.type != b.type || a.items.size() != b.items.size() || a.names != b.names) return false;
  if (a.type == Type::kString && a.text != b.text) return false;
  if (a.type == Type::kBool && a.boolean != b.boolean) return false;
  for (std::size_t i = 0; i < a.items.size(); ++i) if (!same_shape(a.items[i], b.items[i])) return false;
  return true;
}
}  // namespace

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data, std::size_t size) {
  const std::string_view text(reinterpret_cast<const char*>(data), size);
  Value document;
  if (!armor::json::parse(text, document)) return 0;
  Writer writer;
  emit(document, writer);
  Value again;
  if (!armor::json::parse(writer.str(), again) || !same_shape(document, again)) std::abort();
  // the accessors must not trip on any shape
  (void)document.string_or("id", "");
  (void)document.integer_or("n", 0, -5, 5);
  return 0;
}
