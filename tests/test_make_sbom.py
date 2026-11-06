"""The bill of materials of a Node.js project: what it lists, that it is the same twice, and that a published one is compared with the lock file."""
import base64
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import make_sbom  # noqa: E402

SHA512 = "sha512-" + base64.b64encode(hashlib.sha512(b"one").digest()).decode()
LOCK = {
    "name": "demo", "lockfileVersion": 3,
    "packages": {
        "": {"name": "demo", "version": "1.0.0"},
        "node_modules/left-pad": {"version": "1.3.0", "integrity": SHA512, "license": "MIT"},
        "node_modules/@scope/tool": {"version": "2.0.0", "license": "(MIT OR Apache-2.0)", "dev": True},
        "node_modules/left-pad/node_modules/inner": {"version": "0.1.0", "integrity": "not-an-integrity"},
        "node_modules/linked": {"resolved": "../linked", "link": True},
    },
}


def project(folder: str, lock: dict | None = None) -> Path:
    root = Path(folder)
    (root / "armor.project.json").write_text(json.dumps({"name": "ARMOR-DEMO", "version": "0.1.2"}), encoding="utf-8")
    (root / "package-lock.json").write_text(json.dumps(LOCK if lock is None else lock), encoding="utf-8")
    return root


class SbomTests(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.root = project(holder.name)

    def test_it_lists_every_installed_package_with_its_hash_and_licence_and_leaves_out_the_root_and_the_links(self):
        document = make_sbom.build(self.root)
        self.assertEqual((document["bomFormat"], document["specVersion"]), ("CycloneDX", "1.5"))
        self.assertEqual([c["purl"] for c in document["components"]], ["pkg:npm/%40scope/tool@2.0.0", "pkg:npm/inner@0.1.0", "pkg:npm/left-pad@1.3.0"])
        by_name = {c["name"]: c for c in document["components"]}
        self.assertEqual(by_name["left-pad"]["hashes"], [{"alg": "SHA-512", "content": hashlib.sha512(b"one").hexdigest()}])
        self.assertEqual(by_name["left-pad"]["licenses"], [{"license": {"id": "MIT"}}])
        self.assertEqual(by_name["@scope/tool"]["licenses"], [{"expression": "(MIT OR Apache-2.0)"}])
        self.assertEqual((by_name["@scope/tool"]["scope"], by_name["left-pad"]["scope"]), ("optional", "required"))
        self.assertNotIn("hashes", by_name["inner"])   # a value that is not an integrity string is not turned into a hash
        self.assertEqual(document["metadata"]["component"]["name"], "ARMOR-DEMO")

    def test_it_is_the_same_twice_and_changes_with_the_lock_file(self):
        first = json.dumps(make_sbom.build(self.root), sort_keys=True)
        self.assertEqual(first, json.dumps(make_sbom.build(self.root), sort_keys=True))
        (self.root / "package-lock.json").write_text(json.dumps({**LOCK, "extra": 1}), encoding="utf-8")
        self.assertNotEqual(json.loads(first)["serialNumber"], make_sbom.build(self.root)["serialNumber"])

    def test_a_published_bill_is_compared_with_the_lock_file(self):
        published = self.root / "sbom.json"
        self.assertEqual(make_sbom.main([str(self.root), "--output", str(published)]), 0)
        self.assertEqual(make_sbom.check(self.root, published), [])
        document = json.loads(published.read_text(encoding="utf-8"))
        document["components"] = [c for c in document["components"] if c["name"] != "inner"]
        document["components"][0]["hashes"] = [{"alg": "SHA-512", "content": "00"}]
        document["components"].append({"purl": "pkg:npm/extra@9.9.9"})
        published.write_text(json.dumps(document), encoding="utf-8")
        problems = make_sbom.check(self.root, published)
        self.assertEqual(len(problems), 3)
        self.assertTrue(any("missing" in p and "inner" in p for p in problems))
        self.assertTrue(any("not in the lock file" in p and "extra" in p for p in problems))

    def test_an_existing_file_is_never_overwritten_and_a_bad_project_is_refused(self):
        target = self.root / "sbom.json"
        target.write_text("keep", encoding="utf-8")
        self.assertEqual(make_sbom.main([str(self.root), "--output", str(target)]), 2)
        self.assertEqual(target.read_text(encoding="utf-8"), "keep")
        (self.root / "package-lock.json").write_text(json.dumps({"lockfileVersion": 1, "dependencies": {}}), encoding="utf-8")
        with self.assertRaises(make_sbom.SbomError):
            make_sbom.build(self.root)
        self.assertEqual(make_sbom.main([str(self.root)]), 2)
        self.assertEqual(make_sbom.main([str(self.root), "--check", str(self.root / "nothing.json")]), 1)


if __name__ == "__main__":
    unittest.main()
