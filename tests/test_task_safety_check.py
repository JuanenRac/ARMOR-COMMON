"""The guards the node projects run on their firmware sources (firmware_base/tests/check_task_safety.py and check_save_paths.py), tried on small stand-in projects:
the failures they exist for (a task that copies the whole settings onto a small stack, a stack below what the task needs, a short HTTP header buffer, a time zone that
needs a restart) must be caught, and the safe versions must pass."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "firmware_base" / "tests"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, BASE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


safety = load("check_task_safety")
saves = load("check_save_paths")

TELEMETRY_BAD = """
namespace armor::mqtt_link {
namespace {
void publish_telemetry() {
  const config::Settings current = store::settings();
  char topic[96];
  (void)current; (void)topic;
}
void telemetry_task(void*) { for (;;) publish_telemetry(); }
}
void start() { xTaskCreate(telemetry_task, "telemetry", %d, nullptr, 4, nullptr); }
}
"""
TELEMETRY_HEAP = TELEMETRY_BAD.replace("const config::Settings current = store::settings();", "const std::unique_ptr<config::Settings> current(new config::Settings(store::settings()));")


class Project:
    def __init__(self, test: unittest.TestCase, files: dict[str, str]):
        self.dir = tempfile.TemporaryDirectory()
        test.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        for relative, content in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")


class TaskSafetyTest(unittest.TestCase):
    def run_on(self, files: dict[str, str]):
        return safety.analyse(Project(self, files).root)

    def test_a_task_that_copies_the_settings_onto_a_small_stack_is_refused(self) -> None:
        two_copies = (TELEMETRY_BAD % 3072).replace("char topic[96];", "const config::Settings second = store::settings(); char topic[96];")
        _tasks, problems = self.run_on({"main/mqtt_link.cpp": two_copies})
        self.assertTrue(any("config::Settings copy" in p for p in problems), problems)

    def test_the_same_task_with_the_copy_on_the_heap_passes(self) -> None:
        tasks, problems = self.run_on({"main/mqtt_link.cpp": TELEMETRY_HEAP % 6144})
        self.assertEqual(problems, [])
        self.assertEqual([(t[0], t[1]) for t in tasks], [("telemetry", 6144)])

    def test_a_stack_below_what_the_task_needs_is_refused(self) -> None:
        _tasks, problems = self.run_on({"main/mqtt_link.cpp": TELEMETRY_HEAP % 5120})
        self.assertTrue(any("below the 6144" in p for p in problems), problems)

    def test_any_task_below_the_minimum_is_refused(self) -> None:
        _tasks, problems = self.run_on({"main/a.cpp": 'void t(void*){}\nvoid s(){ xTaskCreate(t, "tiny", 2048, nullptr, 1, nullptr); }\n'})
        self.assertTrue(any("2048" in p for p in problems), problems)

    def test_a_stack_that_is_not_a_literal_is_refused(self) -> None:
        _tasks, problems = self.run_on({"main/a.cpp": 'void t(void*){}\nvoid s(){ xTaskCreate(t, "odd", kWhoKnows, nullptr, 1, nullptr); }\n'})
        self.assertTrue(any("not a number" in p for p in problems), problems)

    def test_a_named_constant_is_resolved(self) -> None:
        tasks, problems = self.run_on({"main/a.cpp": 'constexpr unsigned kStack = 4096;\nvoid t(void*){}\nvoid s(){ xTaskCreate(t, "ok", kStack, nullptr, 1, nullptr); }\n'})
        self.assertEqual((problems, tasks[0][1]), ([], 4096))

    def test_a_big_array_on_a_task_stack_is_refused_and_a_small_one_is_not(self) -> None:
        big = 'void t(void*){ char payload[1600]; (void)payload; }\nvoid s(){ xTaskCreate(t, "big", 3072, nullptr, 1, nullptr); }\n'
        small = big.replace("1600", "200")
        self.assertTrue(self.run_on({"main/a.cpp": big})[1])
        self.assertEqual(self.run_on({"main/a.cpp": small})[1], [])

    def test_a_copy_marked_as_safe_with_a_reason_is_allowed(self) -> None:
        code = ('void t(void*){\n  // task-stack-ok: runs once at start, before the other tasks, in a 16 KB stack\n  const config::Settings s = store::settings();\n  (void)s;\n}\n'
                'void s(){ xTaskCreate(t, "once", 3072, nullptr, 1, nullptr); }\n')
        self.assertEqual(self.run_on({"main/a.cpp": code})[1], [])

    def test_a_copy_in_a_function_no_task_reaches_is_not_a_problem(self) -> None:
        code = ('void handler(){ const config::Settings s = store::settings(); (void)s; }\nvoid t(void*){}\nvoid s(){ xTaskCreate(t, "plain", 3072, nullptr, 1, nullptr); }\n')
        self.assertEqual(self.run_on({"main/a.cpp": code})[1], [])

    def test_a_settings_taken_by_value_as_a_parameter_counts(self) -> None:
        code = ('bool compare(config::Settings before, config::Settings after) { return before.language == after.language; }\n'
                'void t(void*){ compare(store::settings(), store::settings()); }\nvoid s(){ xTaskCreate(t, "cmp", 3072, nullptr, 1, nullptr); }\n')
        self.assertTrue(any("by value" in p for p in self.run_on({"main/a.cpp": code})[1]))

    def test_a_call_into_another_module_is_followed_by_its_namespace(self) -> None:
        files = {"main/worker.cpp": 'namespace armor::worker {\nvoid t(void*){ armor::saver::save(); }\nvoid s(){ xTaskCreate(t, "w", 3072, nullptr, 1, nullptr); }\n}\n',
                 "main/saver.cpp": 'namespace armor::saver {\nvoid save(){ config::Settings a; config::Settings b; (void)a; (void)b; }\n}\n'}
        self.assertTrue(any("save()" in p for p in self.run_on(files)[1]))

    def test_comments_and_strings_are_not_code(self) -> None:
        code = ('// config::Settings s = store::settings(); in a comment\nvoid t(void*){ const char* text = "config::Settings s = x;"; (void)text; }\n'
                'void s(){ xTaskCreate(t, "c", 3072, nullptr, 1, nullptr); }\n')
        self.assertEqual(self.run_on({"main/a.cpp": code})[1], [])

    def test_the_http_client_must_use_the_long_header_buffer(self) -> None:
        good = 'void check(){ esp_http_client_config_t config{}; config.buffer_size = header_buffer(); }\n'
        self.assertEqual(safety.http_buffer_problems(Path("."), safety.load(Project(self, {"main/github_update.cpp": good}).root)), [])
        for bad in ("config.buffer_size = 4096;", "config.buffer_size = 2048;"):
            files = safety.load(Project(self, {"main/github_update.cpp": f"void c(){{ {bad} }}\n"}).root)
            self.assertTrue(safety.http_buffer_problems(Path("."), files), bad)
        none = safety.load(Project(self, {"main/github_update.cpp": "void c(){}\n"}).root)
        self.assertTrue(safety.http_buffer_problems(Path("."), none))

    def test_a_short_buffer_constant_is_refused(self) -> None:
        project = Project(self, {"main/github_update.cpp": "void c(){ config.buffer_size = header_buffer(); }\n", "main/core/release_assets.hpp": "constexpr int kHeaderBufferExternal = 20480;\nconstexpr int kHeaderBufferInternal = 4096;\n"})
        self.assertTrue(any("kHeaderBufferInternal" in p for p in safety.http_buffer_problems(project.root, safety.load(project.root))))

    def test_without_any_task_the_scan_itself_fails(self) -> None:
        project = Project(self, {"main/a.cpp": "void f(){}\n"})
        self.assertEqual(safety.main(["x", str(project.root)]), 1)

    def test_the_real_shared_sources_pass(self) -> None:
        tasks, problems = safety.analyse(BASE.parent)
        self.assertEqual(problems, [])
        self.assertTrue(tasks)


GOOD_API = """
PutResult put_config(std::string_view document, config::Problems& problems, bool& restart_required) {
  const std::unique_ptr<config::Settings> before(new (std::nothrow) config::Settings(store::settings()));
  restart_required = needs_restart(*before, *before);
  if (before->time.zone != before->time.zone) clocksync::set_zone(before->time.zone);
  return PutResult::kSaved;
}
bool needs_restart(const config::Settings& before, const config::Settings& after) {
  a->time.zone = b->time.zone = "";
  return true;
}
"""
GOOD_CLOCK = "void start(const config::Settings& settings) {\n  set_zone(settings.time.zone);\n}\nvoid set_zone(const std::string& zone) {}\n"
GOOD_FILES = {
    "main/api_shared.cpp": GOOD_API, "main/clock_sync.cpp": GOOD_CLOCK, "main/web_server.cpp": "send_ok(r, restart_required);\nint restart_required;\n",
    "panel/text.js": '  savedRestart: ["a", "b", "c", "d", "e", "f", "g", "h"],\n', "panel/app.js": "restart_required savedRestart reboot()",
}


class SavePathsTest(unittest.TestCase):
    def check(self, files: dict[str, str]) -> list[str]:
        saves.ROOT = Project(self, files).root
        return saves.problems_of()

    def test_the_good_save_path_passes(self) -> None:
        self.assertEqual(self.check(GOOD_FILES), [])

    def test_a_save_that_does_not_apply_the_zone_is_caught(self) -> None:
        files = dict(GOOD_FILES, **{"main/api_shared.cpp": GOOD_API.replace("clocksync::set_zone", "other::call")})
        self.assertTrue(any("set_zone" in p for p in self.check(files)))

    def test_a_zone_that_asks_for_a_restart_is_caught(self) -> None:
        files = dict(GOOD_FILES, **{"main/api_shared.cpp": GOOD_API.replace('  a->time.zone = b->time.zone = "";\n', "")})
        self.assertTrue(any("compares the time zone" in p for p in self.check(files)))

    def test_a_clock_that_applies_the_zone_only_by_hand_is_caught(self) -> None:
        files = dict(GOOD_FILES, **{"main/clock_sync.cpp": "void start(const config::Settings& settings) {\n  setenv(\"TZ\", settings.time.zone.c_str(), 1);\n}\n"})
        self.assertTrue(any("start()" in p for p in self.check(files)))

    def test_a_settings_copy_in_put_config_is_caught(self) -> None:
        files = dict(GOOD_FILES, **{"main/api_shared.cpp": GOOD_API.replace("const std::unique_ptr<config::Settings> before(new (std::nothrow) config::Settings(store::settings()));",
                                                                           "const config::Settings before_copy = store::settings();\n  const std::unique_ptr<config::Settings> before(new (std::nothrow) config::Settings(before_copy));")})
        self.assertTrue(any("on the stack" in p for p in self.check(files)))

    def test_a_panel_without_the_restart_note_is_caught(self) -> None:
        for broken in (dict(GOOD_FILES, **{"panel/text.js": '  savedRestart: ["a", "b"],\n'}), dict(GOOD_FILES, **{"panel/app.js": "nothing"})):
            self.assertTrue(self.check(broken))


if __name__ == "__main__":
    unittest.main()
