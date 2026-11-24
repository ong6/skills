import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("proof_ledger", ROOT / "scripts" / "proof_ledger.py")
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


def skill(root: Path, name: str, body: str = "steps\n") -> Path:
    folder = root / name
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Use for x; not y.\n---\n{body}")
    return folder


class ProofLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skills = self.root / "skills"
        self.book = self.root / "proofs.json"

    def tearDown(self):
        self.tmp.cleanup()

    def states(self, *models, usage=None):
        return {r["skill"]: r["state"] for r in ledger.stale(self.book, [self.skills], list(models), usage)}

    def test_hash_ignores_tests_and_caches_but_not_references(self):
        folder = skill(self.skills, "demo")
        before = ledger.skill_hash(folder)
        (folder / "tests").mkdir()
        (folder / "tests" / "test_x.py").write_text("x = 1\n")
        (folder / "__pycache__").mkdir()
        (folder / "__pycache__" / "x.pyc").write_bytes(b"\0")
        self.assertEqual(before, ledger.skill_hash(folder))
        (folder / "references").mkdir()
        (folder / "references" / "a.md").write_text("more\n")
        self.assertNotEqual(before, ledger.skill_hash(folder))

    def test_states_cover_never_other_model_edited_and_current(self):
        for name in ("never", "old-model", "edited", "fine"):
            skill(self.skills, name)
        ledger.record(self.book, self.skills / "old-model", ["model-a"], "keep", "evals/a", "2026-01-01")
        ledger.record(self.book, self.skills / "edited", ["model-b"], "keep", "evals/b", "2026-01-02")
        ledger.record(self.book, self.skills / "fine", ["model-b"], "keep", "evals/c", "2026-01-03")
        (self.skills / "edited" / "SKILL.md").write_text("---\nname: edited\ndescription: Use for x; not y.\n---\nnew\n")
        self.assertEqual({"never": "never proven", "old-model": "other model",
                          "edited": "edited since proof", "fine": "current"}, self.states("model-b"))

    def test_every_model_that_runs_the_skill_must_be_covered(self):
        skill(self.skills, "demo")
        ledger.record(self.book, self.skills / "demo", ["big"], "keep", "evals/a", "2026-01-01")
        self.assertEqual("other model", self.states("big", "small")["demo"])
        ledger.record(self.book, self.skills / "demo", ["big", "small"], "keep", "evals/b", "2026-02-01")
        self.assertEqual("current", self.states("big", "small")["demo"])

    def test_retire_and_restore_decisions_are_not_proofs(self):
        skill(self.skills, "demo")
        ledger.record(self.book, self.skills / "demo", ["m"], "retire", "evals/a", "2026-01-01")
        self.assertEqual("never proven", self.states("m")["demo"])

    def test_order_is_worst_state_then_most_used(self):
        for name in ("quiet", "busy", "fine"):
            skill(self.skills, name)
        ledger.record(self.book, self.skills / "fine", ["m"], "keep", "evals/a", "2026-01-01")
        usage = {"quiet": {"days_used": 1}, "busy": {"days_used": 9}, "fine": {"days_used": 30}}
        rows = ledger.stale(self.book, [self.skills], ["m"], usage)
        self.assertEqual(["busy", "quiet", "fine"], [r["skill"] for r in rows])

    def test_record_rejects_bad_input_and_keeps_history(self):
        folder = skill(self.skills, "demo")
        with self.assertRaises(ValueError):
            ledger.record(self.book, folder, ["m"], "maybe", "evals/a", "2026-01-01")
        with self.assertRaises(ValueError):
            ledger.record(self.book, folder, ["m"], "keep", "evals/a", "yesterday")
        with self.assertRaises(ValueError):
            ledger.record(self.book, self.root / "missing", ["m"], "keep", "evals/a", "2026-01-01")
        ledger.record(self.book, folder, ["m"], "keep", "evals/a", "2026-01-01")
        ledger.record(self.book, folder, ["m"], "keep", "evals/b", "2026-01-02")
        self.assertEqual(2, len(json.loads(self.book.read_text())["proofs"]))

    def test_a_proof_without_a_hash_cannot_vouch_for_current_content(self):
        folder = skill(self.skills, "demo")
        ledger.record(self.book, folder, ["m"], "keep", "evals/a", "2026-01-01", sha256="unknown")
        row = ledger.stale(self.book, [self.skills], ["m"])[0]
        self.assertEqual(("edited since proof", None), (row["state"], row["edited"]))

    def test_a_ledger_of_another_shape_is_refused(self):
        self.book.write_text('{"version": 9}')
        skill(self.skills, "demo")
        with self.assertRaises(ValueError):
            ledger.stale(self.book, [self.skills], ["m"])


if __name__ == "__main__":
    unittest.main()
