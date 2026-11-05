"""The movement model shared by the observation services (src/armor_common/motion_core.py), and that the copies in ARMOR-SERVER-AI and ARMOR-VISION are the original."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


core = load("motion_core", ROOT / "src" / "armor_common" / "motion_core.py")
sync = load("sync_motion_core", ROOT / "tools" / "sync_motion_core.py")


def frame(width, height, value=100, box=None, box_value=220):
    pixels = bytearray([value]) * (width * height)
    if box:
        x0, y0, x1, y1 = box
        for y in range(y0, y1):
            for x in range(x0, x1):
                pixels[y * width + x] = box_value
    return bytes(pixels)


class MotionCoreTests(unittest.TestCase):
    def test_a_still_picture_has_no_movement(self):
        still = frame(64, 36)
        motion = core.analyze(still, still, 64, 36)
        self.assertEqual((motion.ratio, motion.cells, motion.extents), (0.0, frozenset(), ()))

    def test_the_change_of_the_whole_picture_is_not_movement(self):
        self.assertEqual(core.analyze(frame(64, 36, 100), frame(64, 36, 160), 64, 36).ratio, 0.0)

    def test_something_that_moved_is_found_and_given_as_a_rectangle(self):
        motion = core.analyze(frame(64, 36), frame(64, 36, box=(16, 8, 32, 20)), 64, 36)
        self.assertAlmostEqual(motion.ratio, 16 * 12 / (64 * 36))
        self.assertEqual(motion.extents, ((4, 2, 7, 4),))
        self.assertEqual(core.regions(motion.extents), [{"x": 0.25, "y": 0.2222, "w": 0.25, "h": 0.3333}])

    def test_regions_are_largest_first_and_limited(self):
        extents = ((0, 0, 0, 0), (2, 2, 5, 5), (8, 0, 9, 1))
        self.assertEqual([r["w"] for r in core.regions(extents)], [0.25, 0.125, 0.0625])
        self.assertEqual(len(core.regions(((i, 0, i, 0) for i in range(16)), limit=3)), 3)

    def test_a_mask_takes_pixels_out_of_everything(self):
        moved = frame(64, 36, box=(0, 0, 16, 12))
        mask = core.rect_mask([{"x": 0, "y": 0, "w": 0.25, "h": 0.34}], 64, 36)
        self.assertEqual(core.analyze(frame(64, 36), moved, 64, 36, mask=mask).ratio, 0.0)
        self.assertGreater(core.analyze(frame(64, 36), moved, 64, 36).ratio, 0.05)

    def test_too_few_pixels_under_a_mask_decide_nothing(self):
        mask = bytes([1] * 63 + [0] * (64 * 36 - 63))
        self.assertEqual(core.analyze(frame(64, 36), frame(64, 36, 0), 64, 36, mask=mask).ratio, 0.0)

    def test_rectangles_that_are_not_rectangles_are_left_out(self):
        self.assertIsNone(core.rect_mask([{"x": 2, "y": 0, "w": 1, "h": 1}, "x", None, (0, 0, 0, 1)], 64, 36))
        self.assertIsNone(core.rect_mask(None, 64, 36))

    def test_the_sizes_are_checked(self):
        with self.assertRaises(ValueError):
            core.analyze(b"\x00" * 10, b"\x00" * 10, 64, 36)
        with self.assertRaises(ValueError):
            core.analyze(frame(8, 8), frame(8, 8), 8, 8, mask=b"\x01")

    def test_other_picture_sizes_work(self):
        motion = core.analyze(frame(320, 180), frame(320, 180, box=(160, 90, 240, 135)), 320, 180)
        self.assertEqual(motion.extents, ((8, 4, 11, 6),))


class CopiesTests(unittest.TestCase):
    def test_the_copies_next_to_this_repository_are_the_original(self):
        problems, absent = sync.drift()
        self.assertEqual(problems, [], "run `python tools/sync_motion_core.py sync`")
        for project in absent:
            print(f"(not next to this repository: {project})")


if __name__ == "__main__":
    unittest.main()
