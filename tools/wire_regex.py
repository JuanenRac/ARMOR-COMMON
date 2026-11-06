"""A tiny regular-expression compiler for the patterns of the contracts: it turns each pattern into a table of states that a few lines of C++ can run.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

A pattern of a schema is anchored (``^`` ... ``$``) and uses a small subset: literals, ``.``, ``\\S``, ``\\d`` and escaped punctuation, character classes with ranges, groups (also
``(?: ...)``), alternation, and the quantifiers ``?``, ``*``, ``+``, ``{m}`` and ``{m,n}``. Anything else is refused, so a pattern that the firmware could not honour never passes silently.
The meaning is the one of ``armor_common.schema`` (ASCII classes, ``.`` is any character but the line feed); ``run`` below is the reference run that the tests compare with Python's ``re``.

The table is a Thompson automaton over code points: a state either takes one code point that is (or is not) in a set of ranges, splits in two, or accepts. Running it needs no
recursion and no allocation beyond one flag per state, which is what a node can afford.
"""
from __future__ import annotations

from dataclasses import dataclass, field

WHITESPACE = [(9, 13), (32, 32)]   # Python's ASCII \s: space, \t \n \v \f \r


class UnsupportedPattern(ValueError):
    pass


@dataclass
class Automaton:
    sets: list[tuple[bool, tuple[tuple[int, int], ...]]] = field(default_factory=list)   # (negated, ranges)
    # state: (op, a, b): op 0 = take one code point in sets[a], go to b; op 1 = split into a and b; op 2 = accept
    states: list[tuple[int, int, int]] = field(default_factory=list)
    start: int = 0


# ---- the syntax tree -------------------------------------------------------------------------------------------------------------------------------------------------------------

def _parse(pattern: str):
    if not (pattern.startswith("^") and pattern.endswith("$")) or pattern.endswith("\\$"):
        raise UnsupportedPattern(f"{pattern!r}: a pattern must be anchored with ^ and $")
    body = pattern[1:-1]
    pos = 0

    def peek() -> str:
        return body[pos] if pos < len(body) else ""

    def escape(in_class: bool):
        nonlocal pos
        pos += 1
        if pos >= len(body):
            raise UnsupportedPattern(f"{pattern!r}: dangling backslash")
        char = body[pos]
        pos += 1
        if char == "S":
            return ("set", True, tuple(WHITESPACE))
        if char == "d":
            return ("set", False, ((48, 57),))
        if char in ".-/+*?()[]{}|^$\\@:_ ":
            return ("lit", ord(char))
        raise UnsupportedPattern(f"{pattern!r}: unsupported escape \\{char}")

    def char_class():
        nonlocal pos
        pos += 1   # [
        negated = False
        if peek() == "^":
            negated = True
            pos += 1
        ranges: list[tuple[int, int]] = []
        first = True
        while True:
            if pos >= len(body):
                raise UnsupportedPattern(f"{pattern!r}: unterminated class")
            char = body[pos]
            if char == "]" and not first:
                pos += 1
                break
            first = False
            if char == "\\":
                item = escape(True)
                if item[0] == "set":
                    if item[1]:
                        raise UnsupportedPattern(f"{pattern!r}: a negated class inside a class")
                    ranges.extend(item[2])
                    continue
                low = item[1]
            else:
                low = ord(char)
                pos += 1
            if peek() == "-" and pos + 1 < len(body) and body[pos + 1] != "]":
                pos += 1
                if peek() == "\\":
                    high_item = escape(True)
                    if high_item[0] != "lit":
                        raise UnsupportedPattern(f"{pattern!r}: bad range")
                    high = high_item[1]
                else:
                    high = ord(peek())
                    pos += 1
                if high < low:
                    raise UnsupportedPattern(f"{pattern!r}: reversed range")
                ranges.append((low, high))
            else:
                ranges.append((low, low))
        return ("set", negated, tuple(sorted(ranges)))

    def atom():
        nonlocal pos
        char = peek()
        if char == "(":
            pos += 1
            if body.startswith("?:", pos):
                pos += 2
            node = alternation()
            if peek() != ")":
                raise UnsupportedPattern(f"{pattern!r}: unbalanced parenthesis")
            pos += 1
            return node
        if char == "[":
            return char_class()
        if char == ".":
            pos += 1
            return ("set", True, ((10, 10),))
        if char == "\\":
            return escape(False)
        if char in "*+?{|)":
            raise UnsupportedPattern(f"{pattern!r}: nothing to repeat at {pos}")
        pos += 1
        return ("lit", ord(char))

    def quantified():
        nonlocal pos
        node = atom()
        repeated = False
        while True:
            char = peek()
            if repeated and char in ("?", "*", "+", "{"):
                raise UnsupportedPattern(f"{pattern!r}: a quantifier after a quantifier")
            repeated = char in ("?", "*", "+", "{")
            if char == "?":
                pos += 1
                node = ("repeat", node, 0, 1)
            elif char == "*":
                pos += 1
                node = ("repeat", node, 0, None)
            elif char == "+":
                pos += 1
                node = ("repeat", node, 1, None)
            elif char == "{":
                end = body.find("}", pos)
                if end < 0:
                    raise UnsupportedPattern(f"{pattern!r}: unterminated {{")
                spec = body[pos + 1:end]
                pos = end + 1
                low, _, high = spec.partition(",")
                if not low.isdigit() or (_ and high and not high.isdigit()):
                    raise UnsupportedPattern(f"{pattern!r}: bad quantifier {{{spec}}}")
                upper = (int(high) if high else None) if _ else int(low)
                if upper is not None and upper < int(low):
                    raise UnsupportedPattern(f"{pattern!r}: bad quantifier {{{spec}}}")
                node = ("repeat", node, int(low), upper)
            else:
                return node

    def sequence():
        parts = []
        while pos < len(body) and peek() not in "|)":
            parts.append(quantified())
        return ("seq", parts)

    def alternation():
        nonlocal pos
        branches = [sequence()]
        while peek() == "|":
            pos += 1
            branches.append(sequence())
        return branches[0] if len(branches) == 1 else ("alt", branches)

    tree = alternation()
    if pos != len(body):
        raise UnsupportedPattern(f"{pattern!r}: unbalanced parenthesis")
    return tree


# ---- the automaton ---------------------------------------------------------------------------------------------------------------------------------------------------------------

def compile_pattern(pattern: str) -> Automaton:
    tree = _parse(pattern)
    auto = Automaton()

    def add_set(negated: bool, ranges) -> int:
        entry = (negated, tuple(ranges))
        if entry not in auto.sets:
            auto.sets.append(entry)
        return auto.sets.index(entry)

    def new(op: int, a: int = -1, b: int = -1) -> int:
        auto.states.append((op, a, b))
        return len(auto.states) - 1

    def patch(state: int, which: int, target: int) -> None:
        op, a, b = auto.states[state]
        auto.states[state] = (op, target, b) if which == 0 else (op, a, target)

    # build(node, next_state) -> entry state; built backwards so that `next_state` is always known
    def build(node, nxt: int) -> int:
        kind = node[0]
        if kind == "lit":
            return new(0, add_set(False, [(node[1], node[1])]), nxt)
        if kind == "set":
            return new(0, add_set(node[1], node[2]), nxt)
        if kind == "seq":
            for part in reversed(node[1]):
                nxt = build(part, nxt)
            return nxt
        if kind == "alt":
            entries = [build(branch, nxt) for branch in node[1]]
            entry = entries[-1]
            for other in reversed(entries[:-1]):
                entry = new(1, other, entry)
            return entry
        if kind == "repeat":
            _, inner, low, high = node
            if high is None:   # inner{low,} = inner x low, then inner*
                loop = new(1, -1, nxt)
                body_entry = build(inner, loop)
                patch(loop, 0, body_entry)
                entry = loop
                for _ in range(low):
                    entry = build(inner, entry)
                return entry
            entry = nxt   # optional copies, from the last one back
            for _ in range(high - low):
                entry = new(1, build(inner, entry), nxt)
            for _ in range(low):
                entry = build(inner, entry)
            return entry
        raise AssertionError(kind)

    accept = new(2)
    auto.start = build(tree, accept)
    return auto


def run(auto: Automaton, text: str) -> bool:
    """The reference run: does the whole text match? (The C++ run does exactly this.)"""
    def closure(states: set[int]) -> set[int]:
        out: set[int] = set()
        stack = list(states)
        while stack:
            s = stack.pop()
            if s in out:
                continue
            out.add(s)
            op, a, b = auto.states[s]
            if op == 1:
                stack += [a, b]
        return out

    current = closure({auto.start})
    for char in text:
        code = ord(char)
        step: set[int] = set()
        for s in current:
            op, a, b = auto.states[s]
            if op != 0:
                continue
            negated, ranges = auto.sets[a]
            inside = any(low <= code <= high for low, high in ranges)
            if inside != negated:
                step.add(b)
        current = closure(step)
        if not current:
            return False
    return any(auto.states[s][0] == 2 for s in current)
