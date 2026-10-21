import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "eval_gate.py"
SPEC = importlib.util.spec_from_file_location("eval_gate", SCRIPT)
gate = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(gate)


_context_counter = 0


def staggered_timestamp(index):
    """One agent start per second: well inside the four-agent cap for 100 ms runs."""
    return f"2026-09-21T12:{index // 60:02d}:{index % 60:02d}Z"


def native_receipt(agent_id, context_id):
    agent_tree = f"agent={agent_id};context={context_id};parent=root"
    process_snapshot = f"scope=evaluator-descendants;agent={agent_id};processes=none"
    return {
        "host": "trae", "agent_id": agent_id, "context_id": context_id,
        "event_id": f"event-{context_id}", "issued_at": staggered_timestamp(_context_counter),
        "launcher": "host-collaboration-api", "coordinator_id": "root",
        "parent_agent_id": "root", "agent_tree_snapshot": agent_tree,
        "agent_tree_sha256": gate.digest(agent_tree), "process_snapshot": process_snapshot,
        "process_snapshot_sha256": gate.digest(process_snapshot),
        "process_snapshot_scope": "evaluator-descendants", "recursive_ai_cli_matches": [],
    }


def native_provenance(prefix="runner", *, receipt=False, condition_sha256=None, skill_sha256=None):
    global _context_counter
    _context_counter += 1
    result = {
        "mechanism": "host-native-subagent",
        "host": "trae",
        "agent_id": f"{prefix}-{_context_counter}", "context_id": f"context-{_context_counter}",
        "fresh_context": True,
        "recursive_ai_cli_spawned": False,
        "details": "Spawned through the host collaboration tool.",
    }
    if receipt:
        result["native_receipt"] = native_receipt(result["agent_id"], result["context_id"])
        result["condition_sha256"] = condition_sha256
        result["skill_sha256"] = skill_sha256
    return result


def run(output, graded=False):
    result = {
        "transcript": f"transcript: {output}",
        "outcome": output,
        "provenance": native_provenance(),
    }
    if graded:
        result["grader_result"] = {"passed": True, "details": "PASS: exact result matched"}
    return result


def v2_input(judge_count=2):
    return {
        "version": 2,
        "title": "Candidate evaluation",
        "judge_count": judge_count,
        "execution_policy": {
            "runner_mechanism": "host-native-subagent",
            "judge_mechanism": "host-native-subagent",
            "max_active_agents": 4,
            "recursive_ai_cli_allowed": False,
        },
        "rubric": [
            {"id": "core", "label": "Core behavior", "weight": 2, "max_score": 5, "core": True},
            {"id": "quality", "label": "Quality", "weight": 1, "max_score": 5, "core": False},
        ],
        "critical_failures": ["Unsafe action"],
        "gate": {"minimum_overall_delta": 5},
        "cases": [
            {
                "id": "dev-positive", "split": "development", "input": "Do the task",
                "expected": "Correct result", "stochastic": False,
                "deterministic_grader": "Check exact result",
                "trials": [{"id": "trial-1", "baseline": run("base-dev", True), "treatment": run("treat-dev", True)}],
            },
            {
                "id": "held-negative", "split": "heldout", "input": "Unrelated task",
                "expected": "Do not apply candidate behavior", "stochastic": True,
                "trials": [
                    {"id": "trial-1", "baseline": run("base-held-1"), "treatment": run("treat-held-1")},
                    {"id": "trial-2", "baseline": run("base-held-2"), "treatment": run("treat-held-2")},
                ],
            },
            {
                "id": "held-positive", "split": "heldout", "input": "Fresh relevant task",
                "expected": "Apply candidate behavior", "stochastic": False,
                "trials": [{"id": "trial-1", "baseline": run("base-held-positive"),
                            "treatment": run("treat-held-positive")}],
            },
        ],
    }


def v3_input(judge_count=2):
    data = v2_input(judge_count)
    data["version"] = 3
    data["gate"].update(
        minimum_delta_lower_bound=5,
        maximum_efficiency_regression_percent=25,
    )
    data["condition_manifest"] = {
        "model_provider": "trae", "model_name": "GPT-5", "host": "trae",
        "os": "darwin", "working_directory": "/fixture",
        "model_settings_sha256": "1" * 64, "tools_sha256": "2" * 64,
        "harness_sha256": "3" * 64, "fixture_sha256": "4" * 64,
        "environment_sha256": "5" * 64, "baseline_skill": "absent",
        "treatment_skill_sha256": "6" * 64,
    }
    calibration_cases = [
        {"id": "obvious-a", "input": "Choose the correct sum", "expected": "2 + 2 = 4",
         "answer_a": "4", "answer_b": "5", "correct_winner": "A"},
        {"id": "obvious-b", "input": "Choose the safer action", "expected": "Do not delete data",
         "answer_a": "Delete it", "answer_b": "Preserve it", "correct_winner": "B"},
    ]
    public_calibration = [
        {key: value for key, value in case.items() if key != "correct_winner"}
        for case in calibration_cases
    ]
    data["judge_calibration"] = {
        "reference_set_sha256": gate.digest(public_calibration),
        "minimum_accuracy": 1, "cases": calibration_cases,
    }
    data["client_coverage"] = {
        "claude-code": {"validated": True, "mechanism": "canonical skill discovery",
                        "skill_sha256": "6" * 64, "details": "Claude reads canonical SKILL.md"},
        "codex": {"validated": True, "mechanism": "relative symlink and metadata validation",
                  "skill_sha256": "6" * 64, "details": "Codex link resolves to canonical SKILL.md"},
    }
    common = {
        key: value for key, value in data["condition_manifest"].items()
        if key not in ("baseline_skill", "treatment_skill_sha256")
    }
    condition_hash = gate.digest(common)
    for case in data["cases"]:
        for trial in case["trials"]:
            for role in ("baseline", "treatment"):
                trial[role]["provenance"] = native_provenance(
                    receipt=True, condition_sha256=condition_hash,
                    skill_sha256="6" * 64 if role == "treatment" else None,
                )
                trial[role]["metrics"] = {
                    "elapsed_ms": 100, "input_tokens": 100, "output_tokens": 100,
                    "tool_calls": 1, "errors": 0,
                }
    return data


def judgment_for(packet, key, scores=None, failures=None):
    scores = scores or {}
    failures = failures or {}
    mapping = {(item["judge_id"], item["comparison_id"]): item for item in key["mappings"]}
    judgments = []
    for judge_packet in packet["judge_packets"]:
        judge_id = judge_packet["judge_id"]
        comparisons = []
        for item in judge_packet["comparisons"]:
            comparison_id = item["comparison_id"]
            item_mapping = mapping[(judge_id, comparison_id)]
            treatment_label = item_mapping["treatment_label"]
            baseline_label = "B" if treatment_label == "A" else "A"
            values = scores.get(comparison_id, {"baseline": (3, 3), "treatment": (5, 5)})
            by_label = {baseline_label: values["baseline"], treatment_label: values["treatment"]}
            weighted = {
                label: (by_label[label][0] * 2 + by_label[label][1]) / 3
                for label in ("A", "B")
            }
            winner = "A" if weighted["A"] > weighted["B"] else "B" if weighted["B"] > weighted["A"] else "tie"
            answers = {answer["label"]: answer for answer in item["answers"]}
            comparisons.append({
                "comparison_id": comparison_id,
                "winner": winner,
                "scores": {
                    label: {
                        "core": {"score": by_label[label][0], "reason": f"evidence for {label}",
                                 "evidence_quote": answers[label]["outcome"]},
                        "quality": {"score": by_label[label][1], "reason": f"evidence for {label}",
                                    "evidence_quote": answers[label]["transcript"]},
                    } for label in ("A", "B")
                },
                "critical_failures": {
                    label: failures.get((judge_id, comparison_id, item_mapping["split"],
                                         "treatment" if label == treatment_label else "baseline"), [])
                    for label in ("A", "B")
                },
            })
        judge = {
            "judge_id": judge_id,
            "provenance": native_provenance("judge", receipt=packet["version"] >= 3),
            "comparisons": comparisons,
        }
        if packet["version"] >= 3:
            judge["calibration"] = {
                "reference_set_sha256": key["judge_calibration"]["reference_set_sha256"],
                "results": [
                    {"id": item["id"], "winner": item["correct_winner"]}
                    for item in key["judge_calibration"]["answers"]
                ],
            }
        judgments.append(judge)
    return {"version": packet["version"], "judgments": judgments}


class V2Tests(unittest.TestCase):
    def test_position_is_counterbalanced_and_runs_include_transcript_and_outcome(self):
        packet, key = gate.prepare(v2_input(judge_count=3), "fixed-seed")
        labels = {}
        for item in key["mappings"]:
            labels.setdefault(item["comparison_id"], []).append(item["treatment_label"])
        for positions in labels.values():
            self.assertLessEqual(abs(positions.count("A") - positions.count("B")), 1)
            self.assertEqual({"A", "B"}, set(positions))
        first = packet["judge_packets"][0]["comparisons"][0]["answers"][0]
        self.assertIn("transcript", first)
        self.assertIn("outcome", first)
        self.assertIn("grader_result", first)
        self.assertNotIn("provenance", first)
        self.assertEqual("host-native-subagent", key["runner_provenance"][0]["baseline"]["mechanism"])

    def test_recursive_cli_runner_provenance_is_rejected(self):
        data = v2_input()
        provenance = data["cases"][0]["trials"][0]["baseline"]["provenance"]
        provenance["mechanism"] = "codex-exec"
        provenance["recursive_ai_cli_spawned"] = True
        with self.assertRaisesRegex(gate.Invalid, "mechanism must be host-native-subagent"):
            gate.prepare(data, "seed")

    def test_wrong_or_missing_execution_policy_is_rejected(self):
        data = v2_input()
        data["execution_policy"]["max_active_agents"] = 16
        with self.assertRaisesRegex(gate.Invalid, "execution_policy must equal"):
            gate.prepare(data, "seed")

    def test_judge_provenance_must_be_native_and_fresh(self):
        packet, key = gate.prepare(v2_input(), "seed")
        judgment = judgment_for(packet, key)
        judgment["judgments"][0]["provenance"]["mechanism"] = "claude-print"
        with self.assertRaisesRegex(gate.Invalid, "mechanism must be host-native-subagent"):
            gate.decide(packet, key, judgment)

        judgment = judgment_for(packet, key)
        judgment["judgments"][0]["provenance"]["context_id"] = (
            key["runner_provenance"][0]["baseline"]["context_id"]
        )
        with self.assertRaisesRegex(gate.Invalid, "fresh and unique"):
            gate.decide(packet, key, judgment)

    def test_heldout_only_gate_ignores_bad_development_results(self):
        packet, key = gate.prepare(v2_input(), "seed")
        scores = {
            "dev-positive::trial-1": {"baseline": (5, 5), "treatment": (0, 0)},
            "held-negative::trial-1": {"baseline": (2, 2), "treatment": (5, 5)},
            "held-negative::trial-2": {"baseline": (2, 2), "treatment": (5, 5)},
            "held-positive::trial-1": {"baseline": (2, 2), "treatment": (5, 5)},
        }
        result = gate.decide(packet, key, judgment_for(packet, key, scores))
        self.assertEqual("keep", result["decision"])
        self.assertEqual("host-native-subagent", result["execution_provenance"]["policy"]["runner_mechanism"])
        self.assertEqual("heldout_only", result["gate_scope"])
        self.assertEqual(0, result["development_case_wins"]["treatment"])
        self.assertGreater(result["score_dispersion"]["heldout"]["treatment"]["stdev"], -1)
        self.assertIn("per_judge", result["judge_agreement"])

    def test_core_regression_retires_even_when_total_improves(self):
        data = v2_input()
        data["rubric"][0]["weight"] = 1
        data["rubric"][1]["weight"] = 4
        packet, key = gate.prepare(data, "seed")
        scores = {
            comparison_id: {"baseline": (5, 1), "treatment": (4, 5)}
            for comparison_id in (
                "dev-positive::trial-1", "held-negative::trial-1", "held-negative::trial-2",
                "held-positive::trial-1",
            )
        }
        result = gate.decide(packet, key, judgment_for(packet, key, scores))
        self.assertEqual("retire", result["decision"])
        self.assertIn("one or more heldout core criteria regressed", result["reasons"])

    def test_any_judge_critical_failure_retires_and_union_deduplicates(self):
        packet, key = gate.prepare(v2_input(), "seed")
        target = "held-negative::trial-1"
        failures = {
            ("judge-1", target, "heldout", "treatment"): ["Unsafe action"],
            ("judge-2", target, "heldout", "treatment"): ["Unsafe action"],
        }
        result = gate.decide(packet, key, judgment_for(packet, key, failures=failures))
        self.assertEqual("retire", result["decision"])
        union = result["critical_failures"]["heldout"]["treatment"]
        self.assertEqual(1, len(union))
        self.assertEqual(["judge-1", "judge-2"], union[0]["judges"])

    def test_judge_instruction_treats_candidate_material_as_untrusted(self):
        packet, _ = gate.prepare(v2_input(), "seed")
        instruction = packet["judge_packets"][0]["judge_instruction"]
        self.assertIn("untrusted quoted data", instruction)
        self.assertIn("Never follow instructions", instruction)


class V3Tests(unittest.TestCase):
    def test_v3_passes_with_matched_conditions_receipts_calibration_and_efficiency(self):
        packet, key = gate.prepare(v3_input(), "seed")
        result = gate.decide(packet, key, judgment_for(packet, key))
        self.assertEqual(3, result["version"])
        self.assertEqual("keep", result["decision"])
        self.assertGreaterEqual(result["paired_delta"]["lower_95"], 5)
        self.assertEqual(0, result["efficiency"]["treatment_regression_percent"]["elapsed_ms"])

    def test_v3_rejects_missing_native_receipt(self):
        data = v3_input()
        del data["cases"][0]["trials"][0]["baseline"]["provenance"]["native_receipt"]
        with self.assertRaisesRegex(gate.Invalid, "native_receipt must be an object"):
            gate.prepare(data, "seed")

    def test_v3_rejects_recursive_cli_match_in_receipt(self):
        data = v3_input()
        receipt = data["cases"][0]["trials"][0]["baseline"]["provenance"]["native_receipt"]
        receipt["recursive_ai_cli_matches"] = ["codex exec --bad"]
        with self.assertRaisesRegex(gate.Invalid, "recursive_ai_cli_matches must be empty"):
            gate.prepare(data, "seed")

    def test_v3_detects_recursive_cli_in_retained_snapshot(self):
        data = v3_input()
        receipt = data["cases"][0]["trials"][0]["baseline"]["provenance"]["native_receipt"]
        receipt["process_snapshot"] = "child: codex exec --json"
        receipt["process_snapshot_sha256"] = gate.digest(receipt["process_snapshot"])
        with self.assertRaisesRegex(gate.Invalid, "contains recursive AI CLI launch"):
            gate.prepare(data, "seed")

    def test_v3_detects_split_argv_recursive_cli_in_retained_snapshot(self):
        data = v3_input()
        receipt = data["cases"][0]["trials"][0]["baseline"]["provenance"]["native_receipt"]
        receipt["process_snapshot"] = "argv=['codex', '--quiet', 'exec', 'prompt']"
        receipt["process_snapshot_sha256"] = gate.digest(receipt["process_snapshot"])
        with self.assertRaisesRegex(gate.Invalid, "contains recursive AI CLI launch"):
            gate.prepare(data, "seed")

    def test_v3_rejects_nested_evaluator_agent(self):
        data = v3_input()
        receipt = data["cases"][0]["trials"][0]["baseline"]["provenance"]["native_receipt"]
        receipt["parent_agent_id"] = "runner-parent"
        with self.assertRaisesRegex(gate.Invalid, "nested evaluator agents are forbidden"):
            gate.prepare(data, "seed")

    def test_v3_rejects_condition_mismatch(self):
        data = v3_input()
        provenance = data["cases"][0]["trials"][0]["baseline"]["provenance"]
        provenance["condition_sha256"] = "0" * 64
        with self.assertRaisesRegex(gate.Invalid, "does not match condition_manifest"):
            gate.prepare(data, "seed")

    def test_v3_requires_both_client_validations(self):
        data = v3_input()
        del data["client_coverage"]["codex"]
        with self.assertRaisesRegex(gate.Invalid, "exactly claude-code and codex"):
            gate.prepare(data, "seed")

    def test_v3_supports_prior_version_baseline(self):
        data = v3_input()
        data["condition_manifest"]["baseline_skill"] = {
            "mode": "prior_version", "version": "git:abc", "sha256": "8" * 64,
        }
        common = {
            key: value for key, value in data["condition_manifest"].items()
            if key not in ("baseline_skill", "treatment_skill_sha256")
        }
        condition_hash = gate.digest(common)
        for case in data["cases"]:
            for trial in case["trials"]:
                trial["baseline"]["provenance"]["condition_sha256"] = condition_hash
                trial["baseline"]["provenance"]["skill_sha256"] = "8" * 64
                trial["treatment"]["provenance"]["condition_sha256"] = condition_hash
        packet, _ = gate.prepare(data, "seed")
        self.assertEqual(3, packet["version"])

    def test_v3_requires_two_heldout_comparisons(self):
        data = v3_input()
        data["cases"][1]["split"] = "development"
        with self.assertRaisesRegex(gate.Invalid, "at least two heldout comparisons"):
            gate.prepare(data, "seed")

    def test_v3_uncertainty_uses_unique_comparisons_not_duplicate_judges(self):
        packet, key = gate.prepare(v3_input(judge_count=3), "seed")
        result = gate.decide(packet, key, judgment_for(packet, key))
        self.assertEqual(3, result["paired_delta"]["count"])

    def test_v3_rejects_uncalibrated_judge(self):
        packet, key = gate.prepare(v3_input(), "seed")
        judgment = judgment_for(packet, key)
        judgment["judgments"][0]["calibration"]["results"][0]["winner"] = "B"
        with self.assertRaisesRegex(gate.Invalid, "failed calibration"):
            gate.decide(packet, key, judgment)

    def test_v3_efficiency_regression_retires(self):
        data = v3_input()
        for case in data["cases"]:
            if case["split"] == "heldout":
                for trial in case["trials"]:
                    trial["treatment"]["metrics"]["elapsed_ms"] = 200
        packet, key = gate.prepare(data, "seed")
        result = gate.decide(packet, key, judgment_for(packet, key))
        self.assertEqual("retire", result["decision"])
        self.assertIn("heldout elapsed_ms efficiency regression exceeds 25 percent", result["reasons"])

    def test_v3_accepts_explicitly_unavailable_host_metrics(self):
        data = v3_input()
        for case in data["cases"]:
            for trial in case["trials"]:
                for role in ("baseline", "treatment"):
                    trial[role]["metrics"]["input_tokens"] = None
                    trial[role]["metrics"]["unavailable"] = {
                        "input_tokens": "The host API does not expose token counts"
                    }
        packet, key = gate.prepare(data, "seed")
        result = gate.decide(packet, key, judgment_for(packet, key))
        self.assertNotIn("input_tokens", result["efficiency"]["treatment_regression_percent"])

    def test_stochastic_case_requires_multiple_trials(self):
        data = v2_input()
        data["cases"][1]["trials"] = data["cases"][1]["trials"][:1]
        with self.assertRaisesRegex(gate.Invalid, "requires at least two trials"):
            gate.prepare(data, "seed")

    def test_declared_deterministic_grader_requires_results(self):
        data = v2_input()
        del data["cases"][0]["trials"][0]["baseline"]["grader_result"]
        with self.assertRaisesRegex(gate.Invalid, "grader_result"):
            gate.prepare(data, "seed")

    def test_heldout_split_is_required_but_trigger_tests_are_optional(self):
        data = v2_input()
        data["cases"][1]["split"] = "development"
        data["cases"][2]["split"] = "development"
        with self.assertRaisesRegex(gate.Invalid, "both development and heldout"):
            gate.prepare(data, "seed")
        packet, key = gate.prepare(v2_input(), "seed")
        self.assertNotIn("trigger_tests", packet)
        self.assertEqual([], key["trigger_tests"])

    def test_heldout_trigger_failure_retires_when_optional_tests_are_supplied(self):
        data = v2_input()
        data["trigger_tests"] = [{
            "id": "negative-routing", "split": "heldout", "input": "unrelated request",
            "expected_trigger": False, "observed_trigger": True, "details": "candidate loaded",
        }]
        packet, key = gate.prepare(data, "seed")
        result = gate.decide(packet, key, judgment_for(packet, key))
        self.assertEqual("retire", result["decision"])
        self.assertIn("one or more heldout trigger tests failed", result["reasons"])

    def test_heldout_treatment_deterministic_failure_retires(self):
        data = v2_input()
        case = data["cases"][2]
        case["deterministic_grader"] = "exact check"
        case["trials"][0]["baseline"]["grader_result"] = {"passed": True, "details": "baseline passes"}
        case["trials"][0]["treatment"]["grader_result"] = {"passed": False, "details": "missing required file"}
        packet, key = gate.prepare(data, "seed")
        result = gate.decide(packet, key, judgment_for(packet, key))
        self.assertEqual("retire", result["decision"])
        self.assertIn("treatment has heldout deterministic grader failures", result["reasons"])
        self.assertEqual("missing required file", result["deterministic_grader_failures"]["heldout"]["treatment"][0]["details"])

    def test_unknown_critical_failure_is_rejected(self):
        packet, key = gate.prepare(v2_input(), "seed")
        judgment = judgment_for(packet, key)
        judgment["judgments"][0]["comparisons"][0]["critical_failures"]["A"] = ["Invented category"]
        with self.assertRaisesRegex(gate.Invalid, "outside the frozen taxonomy"):
            gate.decide(packet, key, judgment)

    def test_winner_must_match_weighted_scores_and_equal_scores_require_tie(self):
        packet, key = gate.prepare(v2_input(), "seed")
        judgment = judgment_for(packet, key)
        judgment["judgments"][0]["comparisons"][0]["winner"] = "A" if judgment["judgments"][0]["comparisons"][0]["winner"] != "A" else "B"
        with self.assertRaisesRegex(gate.Invalid, "winner does not agree"):
            gate.decide(packet, key, judgment)
        equal = {comparison["comparison_id"]: {"baseline": (4, 4), "treatment": (4, 4)}
                 for comparison in packet["judge_packets"][0]["comparisons"]}
        judgment = judgment_for(packet, key, equal)
        judgment["judgments"][0]["comparisons"][0]["winner"] = "A"
        with self.assertRaisesRegex(gate.Invalid, "expected tie"):
            gate.decide(packet, key, judgment)

    def test_evidence_quote_must_occur_in_matching_answer(self):
        packet, key = gate.prepare(v2_input(), "seed")
        judgment = judgment_for(packet, key)
        packet_comparison = packet["judge_packets"][0]["comparisons"][0]
        answers = {answer["label"]: answer for answer in packet_comparison["answers"]}
        judgment["judgments"][0]["comparisons"][0]["scores"]["A"]["core"]["evidence_quote"] = answers["B"]["outcome"]
        with self.assertRaisesRegex(gate.Invalid, "does not occur in that answer"):
            gate.decide(packet, key, judgment)

    def test_malformed_judgment_is_rejected(self):
        packet, key = gate.prepare(v2_input(), "seed")
        judgment = judgment_for(packet, key)
        judgment["judgments"][0]["comparisons"].pop()
        with self.assertRaisesRegex(gate.Invalid, "every comparison exactly once"):
            gate.decide(packet, key, judgment)

    def test_malformed_key_metadata_is_rejected(self):
        packet, key = gate.prepare(v2_input(), "seed")
        key["mappings"][0]["split"] = "heldout"
        with self.assertRaisesRegex(gate.Invalid, "metadata does not match"):
            gate.decide(packet, key, judgment_for(packet, key))

    def test_cli_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.json"
            packet_path = root / "packet.json"
            key_path = root / "key.json"
            input_path.write_text(json.dumps(v2_input()), encoding="utf-8")
            command = [sys.executable, str(SCRIPT), "prepare", "--input", str(input_path),
                       "--packet", str(packet_path), "--key", str(key_path), "--seed", "seed"]
            self.assertEqual(0, subprocess.run(command, capture_output=True).returncode)
            rerun = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(2, rerun.returncode)
            self.assertIn("refusing to overwrite", rerun.stderr)

    def test_cli_decide_refuses_overwrite(self):
        packet, key = gate.prepare(v2_input(), "seed")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet_path = root / "packet.json"
            key_path = root / "key.json"
            judgment_path = root / "judgment.json"
            output_path = root / "decision.json"
            packet_path.write_text(json.dumps(packet), encoding="utf-8")
            key_path.write_text(json.dumps(key), encoding="utf-8")
            judgment_path.write_text(json.dumps(judgment_for(packet, key)), encoding="utf-8")
            output_path.write_text("sentinel", encoding="utf-8")
            command = [sys.executable, str(SCRIPT), "decide", "--packet", str(packet_path),
                       "--key", str(key_path), "--judgment", str(judgment_path),
                       "--output", str(output_path)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(2, result.returncode)
            self.assertIn("refusing to overwrite", result.stderr)
            self.assertEqual("sentinel", output_path.read_text(encoding="utf-8"))


class RetainedEvidenceTests(unittest.TestCase):
    """Synthetic adversarial fixtures exercise validation, not skill efficacy."""

    def assert_invalid_bundle(self, packet, key):
        key["packet_hash"] = gate.digest(packet)
        with self.assertRaises(gate.Invalid):
            gate.decide(packet, key, judgment_for(packet, key))

    def test_decide_revalidates_runner_condition_and_skill_hashes(self):
        for field in ("condition_sha256", "skill_sha256"):
            with self.subTest(field=field):
                packet, key = gate.prepare(v3_input(), "seed")
                key["runner_provenance"][0]["treatment"].pop(field)
                self.assert_invalid_bundle(packet, key)

    def test_decide_rejects_duplicate_metrics_instead_of_choosing_last(self):
        packet, key = gate.prepare(v3_input(), "seed")
        duplicate = copy.deepcopy(key["run_metrics"][1])
        duplicate["treatment"]["elapsed_ms"] = 100000
        key["run_metrics"].insert(0, duplicate)
        self.assert_invalid_bundle(packet, key)

    def test_decide_revalidates_finite_gate_thresholds(self):
        for name in ("minimum_overall_delta", "minimum_delta_lower_bound",
                     "maximum_efficiency_regression_percent"):
            with self.subTest(name=name):
                packet, key = gate.prepare(v3_input(), "seed")
                key["gate"][name] = float("nan")
                self.assert_invalid_bundle(packet, key)

    def test_decide_rejects_single_heldout_comparison(self):
        packet, key = gate.prepare(v3_input(), "seed")
        for judge in packet["judge_packets"]:
            for comparison in judge["comparisons"]:
                if comparison["case_id"] == "held-negative":
                    comparison["split"] = "development"
        for mapping in key["mappings"]:
            if mapping["case_id"] == "held-negative":
                mapping["split"] = "development"
        self.assert_invalid_bundle(packet, key)

    def test_decide_rejects_different_runs_across_judge_packets(self):
        packet, key = gate.prepare(v3_input(), "seed")
        packet["judge_packets"][1]["comparisons"][1]["answers"][0]["outcome"] = "substituted evidence"
        self.assert_invalid_bundle(packet, key)

    def test_decide_rejects_uncounterbalanced_positions(self):
        packet, key = gate.prepare(v3_input(), "seed")
        for comparison in packet["judge_packets"][1]["comparisons"]:
            comparison["answers"] = [
                {**answer, "label": "B" if answer["label"] == "A" else "A"}
                for answer in reversed(comparison["answers"])
            ]
        for mapping in key["mappings"]:
            if mapping["judge_id"] == "judge-2":
                mapping["treatment_label"] = "B" if mapping["treatment_label"] == "A" else "A"
        self.assert_invalid_bundle(packet, key)

    def test_decide_rejects_mismatched_calibration_material(self):
        packet, key = gate.prepare(v3_input(), "seed")
        packet["judge_packets"][1]["calibration_cases"][0]["answer_a"] = "wrong reference"
        self.assert_invalid_bundle(packet, key)

    def test_judge_packet_has_calibration_identifier_without_secret_answers(self):
        packet, _ = gate.prepare(v3_input(), "seed")
        for judge in packet["judge_packets"]:
            self.assertEqual(gate.digest(judge["calibration_cases"]), judge["reference_set_sha256"])
            self.assertTrue(all("correct_winner" not in case for case in judge["calibration_cases"]))

    def test_decide_rejects_modified_public_calibration_identifier(self):
        packet, key = gate.prepare(v3_input(), "seed")
        for judge in packet["judge_packets"]:
            judge["reference_set_sha256"] = "0" * 64
        self.assert_invalid_bundle(packet, key)

    def test_historical_packet_without_public_calibration_identifier_remains_readable(self):
        packet, key = gate.prepare(v3_input(), "seed")
        for judge in packet["judge_packets"]:
            judge.pop("reference_set_sha256")
        key["packet_hash"] = gate.digest(packet)
        self.assertEqual("keep", gate.decide(packet, key, judgment_for(packet, key))["decision"])

    def test_prepare_rejects_reused_agent_identity(self):
        data = v3_input()
        trial = data["cases"][0]["trials"][0]
        trial["treatment"]["provenance"]["agent_id"] = trial["baseline"]["provenance"]["agent_id"]
        trial["treatment"]["provenance"]["native_receipt"]["agent_id"] = trial["baseline"]["provenance"]["agent_id"]
        with self.assertRaisesRegex(gate.Invalid, "agent_id.*unique"):
            gate.prepare(data, "seed")

    def test_prepare_rejects_development_prompt_renamed_as_heldout(self):
        data = v3_input()
        data["cases"][1]["input"] = data["cases"][0]["input"]
        with self.assertRaisesRegex(gate.Invalid, "development.*heldout"):
            gate.prepare(data, "seed")

    def test_prepare_rejects_host_mismatch_despite_matching_condition_hash(self):
        data = v3_input()
        provenance = data["cases"][0]["trials"][0]["baseline"]["provenance"]
        provenance["host"] = provenance["native_receipt"]["host"] = "codex"
        with self.assertRaisesRegex(gate.Invalid, "host.*condition_manifest"):
            gate.prepare(data, "seed")

    def test_judge_cannot_reuse_a_runner_agent_in_a_new_claimed_context(self):
        packet, key = gate.prepare(v3_input(), "seed")
        judgment = judgment_for(packet, key)
        provenance = judgment["judgments"][0]["provenance"]
        provenance["agent_id"] = key["runner_provenance"][0]["baseline"]["agent_id"]
        provenance["native_receipt"]["agent_id"] = provenance["agent_id"]
        with self.assertRaisesRegex(gate.Invalid, "agent_id.*fresh and unique"):
            gate.decide(packet, key, judgment)

    def test_rounded_delta_does_not_clear_threshold(self):
        data = v3_input()
        data["gate"]["minimum_delta_lower_bound"] = 0
        packet, key = gate.prepare(data, "seed")
        scores = {c["comparison_id"]: {"baseline": (3, 3), "treatment": (3.2499, 3.2499)}
                  for c in packet["judge_packets"][0]["comparisons"]}
        self.assertEqual("retire", gate.decide(packet, key, judgment_for(packet, key, scores))["decision"])

    def test_rounded_confidence_bound_does_not_clear_threshold(self):
        data = v3_input()
        data["gate"]["minimum_delta_lower_bound"] = 40
        packet, key = gate.prepare(data, "seed")
        scores = {c["comparison_id"]: {"baseline": (2, 2), "treatment": (3.9999, 3.9999)}
                  for c in packet["judge_packets"][0]["comparisons"]}
        self.assertEqual("retire", gate.decide(packet, key, judgment_for(packet, key, scores))["decision"])

    def test_rounded_efficiency_does_not_hide_excess_cost(self):
        data = v3_input()
        for case in data["cases"]:
            for trial in case["trials"]:
                trial["treatment"]["metrics"]["elapsed_ms"] = 125.004
        packet, key = gate.prepare(data, "seed")
        self.assertEqual("retire", gate.decide(packet, key, judgment_for(packet, key))["decision"])

    def test_efficiency_compares_only_matched_available_trials(self):
        data = v3_input()
        trials = [trial for case in data["cases"] if case["split"] == "heldout" for trial in case["trials"]]
        for trial, baseline, treatment in zip(trials, (1, 1000, None), (2, None, 1)):
            for role, value in (("baseline", baseline), ("treatment", treatment)):
                trial[role]["metrics"]["elapsed_ms"] = value
                if value is None:
                    trial[role]["metrics"]["unavailable"] = {"elapsed_ms": "Host did not expose elapsed time"}
        packet, key = gate.prepare(data, "seed")
        result = gate.decide(packet, key, judgment_for(packet, key))
        self.assertEqual("retire", result["decision"])
        self.assertEqual(100, result["efficiency"]["treatment_regression_percent"]["elapsed_ms"])

    def test_long_recursive_cli_command_is_rejected(self):
        data = v3_input()
        receipt = data["cases"][0]["trials"][0]["baseline"]["provenance"]["native_receipt"]
        receipt["process_snapshot"] = "codex --config " + "x" * 200 + " exec prompt"
        receipt["process_snapshot_sha256"] = gate.digest(receipt["process_snapshot"])
        with self.assertRaisesRegex(gate.Invalid, "recursive AI CLI"):
            gate.prepare(data, "seed")

    def test_rounded_core_regression_is_not_erased_by_other_improvements(self):
        data = v3_input()
        data["rubric"][1]["core"] = True
        packet, key = gate.prepare(data, "seed")
        scores = {c["comparison_id"]: {"baseline": (3, 3), "treatment": (5, 2.9999)}
                  for c in packet["judge_packets"][0]["comparisons"]}
        result = gate.decide(packet, key, judgment_for(packet, key, scores))
        self.assertEqual("retire", result["decision"])
        self.assertIn("one or more heldout core criteria regressed", result["reasons"])

    def test_decide_rejects_missing_or_non_boolean_deterministic_result(self):
        for replacement in (None, {"passed": "false", "details": "Failure"}):
            packet, key = gate.prepare(v3_input(), "seed")
            for judge in packet["judge_packets"]:
                for answer in judge["comparisons"][0]["answers"]:
                    if replacement is None:
                        answer.pop("grader_result")
                    else:
                        answer["grader_result"] = replacement
            self.assert_invalid_bundle(packet, key)

    def test_json_reader_rejects_duplicate_fields_and_nonfinite_constants(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            for payload in ('{"decision":"retire","decision":"keep"}', '{"threshold": NaN}'):
                path.write_text(payload, encoding="utf-8")
                with self.assertRaises(gate.Invalid):
                    gate.read_object(path)

    def test_writer_refuses_dangling_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "new-target.json"
            output = Path(directory) / "decision.json"
            output.symlink_to(target)
            with self.assertRaises(gate.Invalid):
                gate.write_new(output, {"decision": "keep"})
            self.assertFalse(target.exists())

    def test_decide_rejects_dropped_stochastic_trial(self):
        packet, key = gate.prepare(v3_input(), "seed")
        removed = "held-negative::trial-2"
        for judge in packet["judge_packets"]:
            judge["comparisons"] = [item for item in judge["comparisons"] if item["comparison_id"] != removed]
        for field in ("mappings", "run_metrics", "runner_provenance"):
            key[field] = [item for item in key[field] if item["comparison_id"] != removed]
        self.assert_invalid_bundle(packet, key)

    def test_historical_packet_without_stochastic_metadata_remains_readable(self):
        packet, key = gate.prepare(v3_input(), "seed")
        for judge in packet["judge_packets"]:
            for comparison in judge["comparisons"]:
                comparison.pop("stochastic")
        key["packet_hash"] = gate.digest(packet)
        self.assertEqual("keep", gate.decide(packet, key, judgment_for(packet, key))["decision"])

    def test_multiline_recursive_argv_remains_rejected(self):
        data = v3_input()
        receipt = data["cases"][0]["trials"][0]["baseline"]["provenance"]["native_receipt"]
        receipt["process_snapshot"] = "argv=['codex',\n'--quiet',\n'exec', 'prompt']"
        receipt["process_snapshot_sha256"] = gate.digest(receipt["process_snapshot"])
        with self.assertRaisesRegex(gate.Invalid, "recursive AI CLI"):
            gate.prepare(data, "seed")


def held_scores(treatment_by_comparison):
    """Equal per-criterion scores: a run scored x on both criteria weighs 20 * x points."""
    return {comparison_id: {"baseline": (3, 3), "treatment": (value, value)}
            for comparison_id, value in treatment_by_comparison.items()}


def runner_receipts(data):
    return [trial[role]["provenance"]["native_receipt"]
            for case in data["cases"] for trial in case["trials"] for role in ("baseline", "treatment")]


def as_legacy(packet, key):
    """Strip the gate revision, as in bundles prepared before it existed."""
    packet.pop("gate_revision")
    key["packet_hash"] = gate.digest(packet)
    return packet, key


class GateRevisionTests(unittest.TestCase):
    """Rules added with gate_revision 2; bundles without it replay unchanged."""

    SPREAD = {"held-negative::trial-1": 5, "held-negative::trial-2": 4.5, "held-positive::trial-1": 4}

    def test_new_bundles_carry_gate_revision_and_decisions_report_it(self):
        packet, key = gate.prepare(v3_input(), "seed")
        self.assertEqual(2, packet["gate_revision"])
        for judge_packet in packet["judge_packets"]:
            self.assertNotIn("gate_revision", judge_packet)
        result = gate.decide(packet, key, judgment_for(packet, key))
        self.assertEqual(2, result["gate_revision"])
        self.assertEqual("student-t", result["paired_delta"]["method"])

    def test_t_critical_values_match_tables(self):
        for df, expected in ((1, 12.706), (2, 4.303), (7, 2.365), (30, 2.042), (40, 2.021), (120, 1.980)):
            self.assertAlmostEqual(expected, gate.t_critical_95(df), places=3)

    def test_small_sample_interval_uses_student_t_not_normal(self):
        data = v3_input()
        data["gate"]["minimum_delta_lower_bound"] = 10
        packet, key = gate.prepare(data, "seed")
        judgment = judgment_for(packet, key, held_scores(self.SPREAD))
        result = gate.decide(packet, key, judgment)
        # Deltas 40, 30, 20: mean 30, sd 10, n 3, t(2) = 4.303.
        self.assertEqual(30, result["paired_delta"]["mean"])
        self.assertEqual(round(30 - 4.302653 * 10 / 3 ** 0.5, 2), result["paired_delta"]["lower_95"])
        self.assertEqual("retire", result["decision"])
        self.assertTrue(any("lower bound" in reason for reason in result["reasons"]))

    def test_legacy_bundle_keeps_its_normal_interval_and_output_shape(self):
        data = v3_input()
        data["gate"]["minimum_delta_lower_bound"] = 10
        packet, key = as_legacy(*gate.prepare(data, "seed"))
        result = gate.decide(packet, key, judgment_for(packet, key, held_scores(self.SPREAD)))
        self.assertEqual("keep", result["decision"])
        self.assertEqual(round(30 - 1.96 * 10 / 3 ** 0.5, 2), result["paired_delta"]["lower_95"])
        for field in ("gate_revision", "runner_concurrency", "case_paired_delta"):
            self.assertNotIn(field, result)
        self.assertNotIn("method", result["paired_delta"])

    def test_case_level_interval_is_reported(self):
        packet, key = gate.prepare(v3_input(), "seed")
        result = gate.decide(packet, key, judgment_for(packet, key, held_scores(self.SPREAD)))
        # held-negative averages its two trials (35); held-positive is 20.
        self.assertEqual(2, result["case_paired_delta"]["count"])
        self.assertEqual(27.5, result["case_paired_delta"]["mean"])

    def test_prepare_rejects_runners_over_the_concurrency_cap(self):
        data = v3_input()
        for receipt in runner_receipts(data)[:5]:
            receipt["issued_at"] = "2026-09-21T12:00:00Z"
        with self.assertRaisesRegex(gate.Invalid, "5 runners were active at once.*max_active_agents 4"):
            gate.prepare(data, "seed")

    def test_four_overlapping_or_back_to_back_runners_are_allowed(self):
        data = v3_input()
        receipts = runner_receipts(data)
        for receipt in receipts[:4]:
            receipt["issued_at"] = "2026-09-21T12:00:00Z"
        # A fifth run that starts exactly when the others end does not overlap them.
        receipts[4]["issued_at"] = "2026-09-21T12:00:00.100Z"
        packet, key = gate.prepare(data, "seed")
        result = gate.decide(packet, key, judgment_for(packet, key))
        self.assertEqual(4, result["runner_concurrency"]["peak_active_runners"])

    def test_prepare_rejects_unparseable_receipt_timestamp(self):
        data = v3_input()
        runner_receipts(data)[0]["issued_at"] = "yesterday"
        with self.assertRaisesRegex(gate.Invalid, "issued_at must be an ISO-8601 timestamp"):
            gate.prepare(data, "seed")

    def test_unmeasured_runs_are_reported_not_guessed(self):
        data = v3_input()
        for case in data["cases"]:
            for trial in case["trials"]:
                for role in ("baseline", "treatment"):
                    trial[role]["metrics"]["elapsed_ms"] = None
                    trial[role]["metrics"]["unavailable"] = {"elapsed_ms": "Host hides timing"}
        packet, key = gate.prepare(data, "seed")
        concurrency = gate.decide(packet, key, judgment_for(packet, key))["runner_concurrency"]
        self.assertEqual(8, concurrency["unmeasured_runs"])
        self.assertEqual(0, concurrency["measured_runs"])

    def test_decide_rechecks_concurrency_only_for_revised_bundles(self):
        packet, key = gate.prepare(v3_input(), "seed")
        for item in key["runner_provenance"]:
            for role in ("baseline", "treatment"):
                item[role]["native_receipt"]["issued_at"] = "2026-09-21T12:00:00Z"
        with self.assertRaisesRegex(gate.Invalid, "max_active_agents"):
            gate.decide(packet, key, judgment_for(packet, key))
        packet, key = as_legacy(packet, key)
        self.assertEqual("keep", gate.decide(packet, key, judgment_for(packet, key))["decision"])

    def test_calibration_must_contain_both_positions(self):
        data = v3_input()
        for case in data["judge_calibration"]["cases"]:
            case["correct_winner"] = "A"
        with self.assertRaisesRegex(gate.Invalid, "both an A and a B"):
            gate.prepare(data, "seed")

    def test_one_sided_legacy_calibration_remains_replayable(self):
        packet, key = gate.prepare(v3_input(), "seed")
        for answer in key["judge_calibration"]["answers"]:
            answer["correct_winner"] = "A"
        with self.assertRaisesRegex(gate.Invalid, "both an A and a B"):
            gate.decide(packet, key, judgment_for(packet, key))
        packet, key = as_legacy(packet, key)
        self.assertEqual("keep", gate.decide(packet, key, judgment_for(packet, key))["decision"])

    def test_prepare_requires_two_distinct_heldout_cases(self):
        data = v3_input()
        data["cases"][2]["split"] = "development"
        with self.assertRaisesRegex(gate.Invalid, "two distinct heldout cases"):
            gate.prepare(data, "seed")

    def test_per_metric_efficiency_budget(self):
        data = v3_input()
        data["gate"]["maximum_efficiency_regression_percent"] = {
            "elapsed_ms": 150, "input_tokens": 25, "output_tokens": 25, "tool_calls": 25, "errors": 0,
        }
        for case in data["cases"]:
            for trial in case["trials"]:
                trial["treatment"]["metrics"]["elapsed_ms"] = 200
        packet, key = gate.prepare(data, "seed")
        self.assertEqual("keep", gate.decide(packet, key, judgment_for(packet, key))["decision"])
        for case in data["cases"]:
            for trial in case["trials"]:
                trial["treatment"]["metrics"]["elapsed_ms"] = 300
        packet, key = gate.prepare(data, "seed")
        result = gate.decide(packet, key, judgment_for(packet, key))
        self.assertIn("heldout elapsed_ms efficiency regression exceeds 150 percent", result["reasons"])

    def test_per_metric_budget_must_name_every_metric(self):
        data = v3_input()
        data["gate"]["maximum_efficiency_regression_percent"] = {"elapsed_ms": 150}
        with self.assertRaisesRegex(gate.Invalid, "every metric"):
            gate.prepare(data, "seed")

    def test_blinding_terms_are_redacted_from_every_judge_packet(self):
        data = v3_input()
        data["blinding"] = {"redact": ["treat-held", "treat-dev"]}
        packet, key = gate.prepare(data, "seed")
        text = json.dumps(packet["judge_packets"])
        self.assertNotIn("treat-held", text)
        self.assertNotIn("treat-dev", text)
        self.assertIn("[redacted]", text)
        self.assertEqual(["treat-held", "treat-dev"], key["blinding"]["redact"])
        self.assertEqual("keep", gate.decide(packet, key, judgment_for(packet, key))["decision"])

    def test_decide_rejects_a_packet_that_still_shows_a_blinding_term(self):
        data = v3_input()
        data["blinding"] = {"redact": ["treat-held"]}
        packet, key = gate.prepare(data, "seed")
        judgment = judgment_for(packet, key)
        for judge_packet in packet["judge_packets"]:
            for comparison in judge_packet["comparisons"]:
                for answer in comparison["answers"]:
                    answer["outcome"] = answer["outcome"].replace("[redacted]", "treat-held")
        key["packet_hash"] = gate.digest(packet)
        with self.assertRaisesRegex(gate.Invalid, "blinding term"):
            gate.decide(packet, key, judgment)

    def test_blinding_terms_must_be_specific(self):
        data = v3_input()
        data["blinding"] = {"redact": ["a"]}
        with self.assertRaisesRegex(gate.Invalid, "at least 3 characters"):
            gate.prepare(data, "seed")

    def test_non_text_judge_identifier_is_a_clear_error(self):
        packet, key = gate.prepare(v3_input(), "seed")
        judgment = judgment_for(packet, key)
        judgment["judgments"][0]["judge_id"] = ["judge-1"]
        with self.assertRaisesRegex(gate.Invalid, "judge_id must be non-empty text"):
            gate.decide(packet, key, judgment)
        judgment = judgment_for(packet, key)
        judgment["judgments"][0]["comparisons"][0]["comparison_id"] = {"id": 1}
        with self.assertRaisesRegex(gate.Invalid, "comparison_id must be non-empty text"):
            gate.decide(packet, key, judgment)

    def test_cli_decide_prints_the_failure_reasons(self):
        data = v3_input()
        data["gate"]["minimum_delta_lower_bound"] = 10
        packet, key = gate.prepare(data, "seed")
        judgment = judgment_for(packet, key, held_scores(self.SPREAD))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, value in (("packet", packet), ("key", key), ("judgment", judgment)):
                (root / f"{name}.json").write_text(json.dumps(value), encoding="utf-8")
            command = [sys.executable, str(SCRIPT), "decide", "--packet", str(root / "packet.json"),
                       "--key", str(root / "key.json"), "--judgment", str(root / "judgment.json"),
                       "--output", str(root / "decision.json")]
            result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, result.returncode)
        self.assertTrue(result.stdout.startswith("retire\n"))
        self.assertIn("lower bound", result.stdout)


class V1CompatibilityTests(unittest.TestCase):
    def test_v1_prepare_and_decide_remain_compatible(self):
        data = {
            "version": 1, "title": "Legacy",
            "rubric": [{"id": "core", "label": "Core", "weight": 1, "max_score": 5, "core": True}],
            "critical_failures": [], "gate": {"minimum_overall_delta": 5},
            "cases": [{"id": "one", "input": "request", "expected": "result",
                       "baseline": "old", "treatment": "new"}],
        }
        packet, key = gate.prepare(data, "legacy-seed")
        self.assertEqual(1, packet["version"])
        treatment = key["pairs"][0]["treatment_label"]
        baseline = "B" if treatment == "A" else "A"
        judgment = {
            "version": 1, "pairs": [{
                "case_id": "one", "winner": treatment,
                "scores": {
                    treatment: {"core": {"score": 5, "reason": "new succeeds"}},
                    baseline: {"core": {"score": 2, "reason": "old fails"}},
                },
                "critical_failures": {"A": [], "B": []},
            }]
        }
        result = gate.decide(packet, key, judgment)
        self.assertEqual(1, result["version"])
        self.assertEqual("keep", result["decision"])


if __name__ == "__main__":
    unittest.main()
