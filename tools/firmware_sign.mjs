// A.R.M.O.R. - signs what a release publishes, with the Ed25519 key of the releases. The key is NEVER in a repository: it is read from ARMOR_FIRMWARE_KEY or ~/.armor/firmware_ed25519.pem.
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
//
//   node firmware_sign.mjs --public                                   the public key (64 hex digits), to compare with core/fw_trust.hpp
//   node firmware_sign.mjs <file>                                     the signature (128 hex digits) of the SHA-256 of the file                      (what `<image>.sig` holds)
//   node firmware_sign.mjs --digest <sha256 hex>                      the same for a SHA-256 that is already known
//   node firmware_sign.mjs --manifest <project> <board> <version> <sha256 hex>
//                                                                      the signature of the text `armor-fw/1|<project>|<board>|<version>|<sha256>`  (what `<image>.sig2` holds)
//   node firmware_sign.mjs --message <text>                           the signature of any text (for the tests of the verifiers)
//
// The second form signs the hash alone: it is what the nodes before the manifest check verify. The manifest binds the hash to the project, the board and the version, so a signed image
// of the past, or of another board, cannot be presented as the newest one.
import { createHash, createPrivateKey, createPublicKey, sign } from "node:crypto";
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";

const keyPath = process.env.ARMOR_FIRMWARE_KEY || path.join(homedir(), ".armor", "firmware_ed25519.pem");
const key = createPrivateKey(readFileSync(keyPath));
const [mode, ...rest] = process.argv.slice(2);
const hex = /^[0-9a-f]{64}$/;

if (mode === "--public") {
  process.stdout.write(createPublicKey(key).export({ format: "der", type: "spki" }).subarray(-32).toString("hex") + "\n");
} else if (mode === "--digest") {
  if (!hex.test(rest[0] ?? "")) throw new Error("a SHA-256 of 64 lowercase hex digits is needed");
  process.stdout.write(sign(null, Buffer.from(rest[0], "hex"), key).toString("hex") + "\n");
} else if (mode === "--manifest") {
  const [project, board, version, sha256] = rest;
  if (!project || !board || !version || !hex.test(sha256 ?? "")) throw new Error("--manifest needs <project> <board> <version> <sha256 hex>");
  if ([project, board, version].some(part => /[|\s]/.test(part))) throw new Error("a part of the manifest cannot hold a space or a '|'");
  process.stdout.write(sign(null, Buffer.from(`armor-fw/1|${project}|${board}|${version}|${sha256}`, "utf8"), key).toString("hex") + "\n");
} else if (mode === "--message") {
  process.stdout.write(sign(null, Buffer.from(rest.join(" "), "utf8"), key).toString("hex") + "\n");
} else if (mode && !mode.startsWith("--")) {
  process.stdout.write(sign(null, createHash("sha256").update(readFileSync(mode)).digest(), key).toString("hex") + "\n");
} else {
  process.stderr.write("usage: see the head of this file\n");
  process.exit(2);
}
