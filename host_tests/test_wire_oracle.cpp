// The C++ readers of the messages against the oracle: every case of conformance/wire_cases.tsv has the verdict of the Python validator, and the generated validator must say the same.
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
//
//   test_wire_oracle <wire_cases.tsv> [rewrites.tsv]
//
// For a case the Python validator accepts, the document is also read into its struct and written back; the text written must be accepted too and writing again must not change it. When a
// second file is named, the texts written are saved (schema <TAB> the case's number <TAB> the text) for tools/check_wire_rewrites.py, which compares them with the original documents.
#include <cstdio>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "armor_wire.hpp"

namespace {
int failures = 0;
void fail(const std::string& what) {
  if (++failures <= 20) std::cerr << "FAIL " << what << "\n";
}
}  // namespace

int main(int argc, char** argv) {
  if (argc < 2) { std::cerr << "usage: test_wire_oracle cases.tsv [rewrites.tsv]\n"; return 2; }
  std::ifstream in(argv[1], std::ios::binary);
  if (!in) { std::cerr << "cannot open " << argv[1] << "\n"; return 2; }
  std::ofstream rewrites;
  if (argc > 2) rewrites.open(argv[2], std::ios::binary);
  std::string line;
  std::size_t number = 0, accepted = 0, refused = 0, rewritten = 0;
  while (std::getline(in, line)) {
    ++number;
    if (!line.empty() && line.back() == '\r') line.pop_back();
    const std::size_t a = line.find('\t'), b = a == std::string::npos ? a : line.find('\t', a + 1);
    if (b == std::string::npos) { fail("line " + std::to_string(number) + " is not a case"); continue; }
    const std::string schema = line.substr(0, a);
    const bool expected = line[a + 1] == '1';
    const std::string text = line.substr(b + 1);
    const std::string where = "case " + std::to_string(number) + " (" + schema + ")";
    armor::json::Value value;
    if (!armor::json::parse(text, value)) { fail(where + ": the reader of the node does not read the document at all"); continue; }
    const bool got = armor::wire::validate_message(schema, value);
    if (got != expected) fail(where + ": the oracle says " + (expected ? "valid" : "invalid") + ", C++ says " + (got ? "valid" : "invalid") + ": " + text.substr(0, 200));
    got ? ++accepted : ++refused;
    if (!expected) {
      std::string out;
      if (armor::wire::rewrite_message(schema, value, out)) fail(where + ": an invalid document was read into a struct");
      continue;
    }
    std::string first;
    if (!armor::wire::rewrite_message(schema, value, first)) { fail(where + ": a valid document could not be read into its struct"); continue; }
    armor::json::Value again;
    if (!armor::json::parse(first, again) || !armor::wire::validate_message(schema, again)) { fail(where + ": what was written is not valid: " + first.substr(0, 200)); continue; }
    std::string second;
    if (!armor::wire::rewrite_message(schema, again, second) || second != first) { fail(where + ": writing twice changes the text"); continue; }
    ++rewritten;
    if (rewrites) rewrites << schema << '\t' << number << '\t' << first << '\n';
  }
  std::cout << "wire oracle: " << (number - failures) << " of " << number << " cases agree (" << accepted << " accepted, " << refused << " refused, " << rewritten << " written back)\n";
  if (number < 100) { std::cerr << "too few cases\n"; return 1; }
  return failures == 0 ? 0 : 1;
}
