"""Writes ARMOR-COMMON/firmware_base/core/ed25519_verify.hpp: SHA-512 and the verification of an Ed25519 signature, with the constants worked out here (not typed from memory)."""
from math import isqrt
from pathlib import Path

P = 2**255 - 19
D_INT = (-121665 * pow(121666, P - 2, P)) % P
I_INT = pow(2, (P - 1) // 4, P)
GY = (4 * pow(5, P - 2, P)) % P
# x of the base point: the even square root of (y^2 - 1) / (d y^2 + 1)
u = (GY * GY - 1) % P
v = (D_INT * GY * GY + 1) % P
x2 = (u * pow(v, P - 2, P)) % P
GX = pow(x2, (P + 3) // 8, P)
if (GX * GX - x2) % P != 0:
    GX = (GX * I_INT) % P
if GX % 2 != 0:
    GX = P - GX
assert (GX * GX - x2) % P == 0


def limbs(value: int) -> str:
    return ", ".join(f"0x{(value >> (16 * i)) & 0xffff:04x}" for i in range(16))


def primes(count: int):
    out, n = [], 2
    while len(out) < count:
        if all(n % p for p in out):
            out.append(n)
        n += 1
    return out


def iroot(n: int, k: int) -> int:
    lo, hi = 0, 1 << ((n.bit_length() // k) + 2)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid**k <= n:
            lo = mid
        else:
            hi = mid - 1
    return lo


# SHA-512: the first 64 bits of the fractional parts of the square roots (8 primes) and of the cube roots (80 primes)
H0 = [iroot(p << 128, 2) & (2**64 - 1) for p in primes(8)]
K = [iroot(p << 192, 3) & (2**64 - 1) for p in primes(80)]
assert H0[0] == 0x6a09e667f3bcc908 and K[0] == 0x428a2f98d728ae22 and K[79] == 0x6c44198c4a475817

DOC = """// Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
//
// SHA-512 and the verification of an Ed25519 signature (RFC 8032), written for the nodes that check what they download: nothing here signs, and nothing here depends on the chip, so a
// host test runs it against signatures made by another implementation. The field arithmetic is the one of TweetNaCl (16 limbs of 16 bits; public domain); the constants (the curve's d and
// 2d, the base point, the square root of -1, SHA-512's initial values and round constants) are written by tools/gen_ed25519.py from their definitions, not typed. It is not constant time
// and does not need to be: it only ever handles a public key, a public signature and a public message.
#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace armor::ed25519 {

// ---- SHA-512 ------------------------------------------------------------------------------------------------------------------------------------------------
namespace detail {

constexpr std::uint64_t kK[80] = {
@K@
};
constexpr std::uint64_t kH0[8] = {@H0@};

inline std::uint64_t rotr(std::uint64_t x, unsigned n) { return (x >> n) | (x << (64 - n)); }

inline void sha512_block(std::uint64_t h[8], const std::uint8_t* block) {
  std::uint64_t w[80];
  for (int i = 0; i < 16; ++i) {
    std::uint64_t v = 0;
    for (int j = 0; j < 8; ++j) v = (v << 8) | block[i * 8 + j];
    w[i] = v;
  }
  for (int i = 16; i < 80; ++i) {
    const std::uint64_t s0 = rotr(w[i - 15], 1) ^ rotr(w[i - 15], 8) ^ (w[i - 15] >> 7);
    const std::uint64_t s1 = rotr(w[i - 2], 19) ^ rotr(w[i - 2], 61) ^ (w[i - 2] >> 6);
    w[i] = w[i - 16] + s0 + w[i - 7] + s1;
  }
  std::uint64_t a = h[0], b = h[1], c = h[2], d = h[3], e = h[4], f = h[5], g = h[6], hh = h[7];
  for (int i = 0; i < 80; ++i) {
    const std::uint64_t t1 = hh + (rotr(e, 14) ^ rotr(e, 18) ^ rotr(e, 41)) + ((e & f) ^ (~e & g)) + kK[i] + w[i];
    const std::uint64_t t2 = (rotr(a, 28) ^ rotr(a, 34) ^ rotr(a, 39)) + ((a & b) ^ (a & c) ^ (b & c));
    hh = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
  }
  h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e; h[5] += f; h[6] += g; h[7] += hh;
}

}  // namespace detail

// The SHA-512 of up to three pieces put one after the other (what the signature hashes: R, the public key and the message).
inline void sha512(const std::uint8_t* a, std::size_t an, const std::uint8_t* b, std::size_t bn, const std::uint8_t* c, std::size_t cn, std::uint8_t out[64]) {
  std::uint64_t h[8];
  for (int i = 0; i < 8; ++i) h[i] = detail::kH0[i];
  std::uint8_t block[128];
  std::size_t filled = 0;
  std::uint64_t total = 0;
  const auto feed = [&](const std::uint8_t* data, std::size_t length) {
    total += length;
    while (length > 0) {
      const std::size_t take = length < 128 - filled ? length : 128 - filled;
      std::memcpy(block + filled, data, take);
      filled += take; data += take; length -= take;
      if (filled == 128) { detail::sha512_block(h, block); filled = 0; }
    }
  };
  if (an) feed(a, an);
  if (bn) feed(b, bn);
  if (cn) feed(c, cn);
  block[filled++] = 0x80;
  if (filled > 112) { std::memset(block + filled, 0, 128 - filled); detail::sha512_block(h, block); filled = 0; }
  std::memset(block + filled, 0, 128 - filled);
  const std::uint64_t bits = total * 8;
  for (int i = 0; i < 8; ++i) block[120 + i] = static_cast<std::uint8_t>(bits >> (56 - 8 * i));
  detail::sha512_block(h, block);
  for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) out[i * 8 + j] = static_cast<std::uint8_t>(h[i] >> (56 - 8 * j));
}

inline void sha512(const std::uint8_t* data, std::size_t length, std::uint8_t out[64]) { sha512(data, length, nullptr, 0, nullptr, 0, out); }

// ---- the curve ----------------------------------------------------------------------------------------------------------------------------------------------
namespace detail {

using gf = std::int64_t[16];
constexpr std::int64_t kGf1[16] = {1};
constexpr std::int64_t kD[16] = {@D@};
constexpr std::int64_t kD2[16] = {@D2@};
constexpr std::int64_t kX[16] = {@X@};
constexpr std::int64_t kY[16] = {@Y@};
constexpr std::int64_t kI[16] = {@I@};
constexpr std::int64_t kL[32] = {0xed, 0xd3, 0xf5, 0x5c, 0x1a, 0x63, 0x12, 0x58, 0xd6, 0x9c, 0xf7, 0xa2, 0xde, 0xf9, 0xde, 0x14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x10};

inline void set25519(gf r, const std::int64_t* a) { for (int i = 0; i < 16; ++i) r[i] = a[i]; }
inline void car25519(gf o) {
  for (int i = 0; i < 16; ++i) {
    o[i] += (1LL << 16);
    const std::int64_t c = o[i] >> 16;
    o[(i + 1) * (i < 15)] += c - 1 + 37 * (c - 1) * (i == 15);
    o[i] -= c * (1LL << 16);
  }
}
inline void sel25519(gf p, gf q, int b) {
  const std::int64_t c = ~(static_cast<std::int64_t>(b) - 1);
  for (int i = 0; i < 16; ++i) { const std::int64_t t = c & (p[i] ^ q[i]); p[i] ^= t; q[i] ^= t; }
}
inline void pack25519(std::uint8_t* o, const gf n) {
  gf m, t;
  for (int i = 0; i < 16; ++i) t[i] = n[i];
  car25519(t); car25519(t); car25519(t);
  for (int j = 0; j < 2; ++j) {
    m[0] = t[0] - 0xffed;
    for (int i = 1; i < 15; ++i) { m[i] = t[i] - 0xffff - ((m[i - 1] >> 16) & 1); m[i - 1] &= 0xffff; }
    m[15] = t[15] - 0x7fff - ((m[14] >> 16) & 1);
    const int b = static_cast<int>((m[15] >> 16) & 1);
    m[14] &= 0xffff;
    sel25519(t, m, 1 - b);
  }
  for (int i = 0; i < 16; ++i) { o[2 * i] = static_cast<std::uint8_t>(t[i] & 0xff); o[2 * i + 1] = static_cast<std::uint8_t>(t[i] >> 8); }
}
inline bool equal25519(const gf a, const gf b) { std::uint8_t c[32], d[32]; pack25519(c, a); pack25519(d, b); return std::memcmp(c, d, 32) == 0; }
inline std::uint8_t par25519(const gf a) { std::uint8_t d[32]; pack25519(d, a); return d[0] & 1; }
inline void unpack25519(gf o, const std::uint8_t* n) { for (int i = 0; i < 16; ++i) o[i] = n[2 * i] + (static_cast<std::int64_t>(n[2 * i + 1]) << 8); o[15] &= 0x7fff; }
inline void A(gf o, const gf a, const gf b) { for (int i = 0; i < 16; ++i) o[i] = a[i] + b[i]; }
inline void Z(gf o, const gf a, const gf b) { for (int i = 0; i < 16; ++i) o[i] = a[i] - b[i]; }
inline void M(gf o, const gf a, const gf b) {
  std::int64_t t[31];
  for (int i = 0; i < 31; ++i) t[i] = 0;
  for (int i = 0; i < 16; ++i) for (int j = 0; j < 16; ++j) t[i + j] += a[i] * b[j];
  for (int i = 0; i < 15; ++i) t[i] += 38 * t[i + 16];
  for (int i = 0; i < 16; ++i) o[i] = t[i];
  car25519(o); car25519(o);
}
inline void S(gf o, const gf a) { M(o, a, a); }
inline void inv25519(gf o, const gf i) {
  gf c;
  for (int a = 0; a < 16; ++a) c[a] = i[a];
  for (int a = 253; a >= 0; --a) { S(c, c); if (a != 2 && a != 4) M(c, c, i); }
  for (int a = 0; a < 16; ++a) o[a] = c[a];
}
inline void pow2523(gf o, const gf i) {
  gf c;
  for (int a = 0; a < 16; ++a) c[a] = i[a];
  for (int a = 250; a >= 0; --a) { S(c, c); if (a != 1) M(c, c, i); }
  for (int a = 0; a < 16; ++a) o[a] = c[a];
}
inline void add(gf p[4], gf q[4]) {
  gf a, b, c, d, t, e, f, g, h;
  Z(a, p[1], p[0]); Z(t, q[1], q[0]); M(a, a, t);
  A(b, p[0], p[1]); A(t, q[0], q[1]); M(b, b, t);
  M(c, p[3], q[3]); M(c, c, kD2);
  M(d, p[2], q[2]); A(d, d, d);
  Z(e, b, a); Z(f, d, c); A(g, d, c); A(h, b, a);
  M(p[0], e, f); M(p[1], h, g); M(p[2], g, f); M(p[3], e, h);
}
inline void cswap(gf p[4], gf q[4], std::uint8_t b) { for (int i = 0; i < 4; ++i) sel25519(p[i], q[i], b); }
inline void pack(std::uint8_t* r, gf p[4]) {
  gf tx, ty, zi;
  inv25519(zi, p[2]); M(tx, p[0], zi); M(ty, p[1], zi);
  pack25519(r, ty);
  r[31] ^= static_cast<std::uint8_t>(par25519(tx) << 7);
}
inline void scalarmult(gf p[4], gf q[4], const std::uint8_t* s) {
  const std::int64_t zero[16] = {0};
  set25519(p[0], zero); set25519(p[1], kGf1); set25519(p[2], kGf1); set25519(p[3], zero);
  for (int i = 255; i >= 0; --i) {
    const std::uint8_t b = (s[i / 8] >> (i & 7)) & 1;
    cswap(p, q, b); add(q, p); add(p, p); cswap(p, q, b);
  }
}
inline void scalarbase(gf p[4], const std::uint8_t* s) {
  gf q[4];
  set25519(q[0], kX); set25519(q[1], kY); set25519(q[2], kGf1); M(q[3], q[0], q[1]);
  scalarmult(p, q, s);
}
inline void modL(std::uint8_t* r, std::int64_t x[64]) {
  std::int64_t carry, j;
  for (int i = 63; i >= 32; --i) {
    carry = 0;
    for (j = i - 32; j < i - 12; ++j) { x[j] += carry - 16 * x[i] * kL[j - (i - 32)]; carry = (x[j] + 128) >> 8; x[j] -= carry * 256; }
    x[j] += carry;
    x[i] = 0;
  }
  carry = 0;
  for (j = 0; j < 32; ++j) { x[j] += carry - (x[31] >> 4) * kL[j]; carry = x[j] >> 8; x[j] &= 255; }
  for (j = 0; j < 32; ++j) x[j] -= carry * kL[j];
  for (int i = 0; i < 32; ++i) { x[i + 1] += x[i] >> 8; r[i] = static_cast<std::uint8_t>(x[i] & 255); }
}
inline void reduce(std::uint8_t* r) {
  std::int64_t x[64];
  for (int i = 0; i < 64; ++i) x[i] = r[i];
  for (int i = 0; i < 64; ++i) r[i] = 0;
  modL(r, x);
}
// The point -A of a public key, or false when the bytes are not a point of the curve.
inline bool unpackneg(gf r[4], const std::uint8_t p[32]) {
  gf t, chk, num, den, den2, den4, den6;
  const std::int64_t zero[16] = {0};
  set25519(r[2], kGf1);
  unpack25519(r[1], p);
  S(num, r[1]); M(den, num, kD); Z(num, num, r[2]); A(den, r[2], den);
  S(den2, den); S(den4, den2); M(den6, den4, den2);
  M(t, den6, num); M(t, t, den);
  pow2523(t, t);
  M(t, t, num); M(t, t, den); M(t, t, den);
  M(r[0], t, den);
  S(chk, r[0]); M(chk, chk, den);
  if (!equal25519(chk, num)) M(r[0], r[0], kI);
  S(chk, r[0]); M(chk, chk, den);
  if (!equal25519(chk, num)) return false;
  if (par25519(r[0]) == (p[31] >> 7)) Z(r[0], zero, r[0]);
  M(r[3], r[0], r[1]);
  return true;
}

}  // namespace detail

// True when `signature` (64 bytes: R and S) is the Ed25519 signature of the `length` bytes of `message` by the owner of `public_key` (32 bytes).
inline bool verify(const std::uint8_t signature[64], const std::uint8_t* message, std::size_t length, const std::uint8_t public_key[32]) {
  using namespace detail;
  if (signature[63] & 0xe0) return false;   // S must be below 2^253 (and, below, the signature is compared as a whole)
  gf p[4], q[4];
  if (!unpackneg(q, public_key)) return false;
  std::uint8_t h[64];
  sha512(signature, 32, public_key, 32, message, length, h);
  reduce(h);
  scalarmult(p, q, h);
  scalarbase(q, signature + 32);
  add(p, q);
  std::uint8_t t[32];
  pack(t, p);
  std::uint8_t difference = 0;
  for (int i = 0; i < 32; ++i) difference |= static_cast<std::uint8_t>(signature[i] ^ t[i]);
  return difference == 0;
}

}  // namespace armor::ed25519
"""

k_lines = []
for i in range(0, 80, 4):
    k_lines.append("    " + ", ".join(f"0x{v:016x}ULL" for v in K[i:i + 4]) + ",")
text = (DOC
        .replace("@K@", "\n".join(k_lines))
        .replace("@H0@", ", ".join(f"0x{v:016x}ULL" for v in H0))
        .replace("@D@", limbs(D_INT)).replace("@D2@", limbs((2 * D_INT) % P)).replace("@X@", limbs(GX)).replace("@Y@", limbs(GY)).replace("@I@", limbs(I_INT)))
out = Path("core/ed25519_verify.hpp")
out.write_text("// ARMOR - Ed25519 verification and SHA-512 (generated by tools/gen_ed25519.py: do not edit by hand).\n" + text, encoding="utf-8")
print("written", out.stat().st_size, "bytes")
Path("tools/gen_ed25519.py").write_text(Path(__file__).read_text(encoding="utf-8").replace("", "").replace('Path("core/ed25519_verify.hpp")', 'Path("core/ed25519_verify.hpp")'), encoding="utf-8")
