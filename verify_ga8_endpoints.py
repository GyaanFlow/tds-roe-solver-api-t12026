"""
verify_ga8_endpoints.py — Comprehensive Test Suite for GA8 Endpoints & Solvers.
"""

import hashlib
import json
import pytest
from starlette.testclient import TestClient

from hf_space.app import app
from T22026.GA8.solvers import (
    crc32c_hex,
    parse_rfc3339_timestamp,
    build_corpus_decision,
    bqml_decision,
    BQMLStore,
    promote_decision,
    adapt_decision,
    quantize_decision,
    QuantizeStore,
    pipeline_decision,
    PipelineStore,
    verify_bundle_decision,
    solve_q8_lora,
    solve_q9_mlflow,
    solve_q10_carbon,
)

client = TestClient(app)
TEST_EMAIL = "23f1000805@ds.study.iitm.ac.in"


# ===========================================================================
# 1. CRC32C & Timestamp Utilities
# ===========================================================================
def test_crc32c_hex():
    data = b"123456789"
    # Standard CRC32C check value for "123456789" is 0xe3069283
    assert crc32c_hex(data) == "e3069283"


def test_rfc3339_timestamp_parser():
    res1 = parse_rfc3339_timestamp("2026-01-02T05:30:00+05:30")
    assert res1 is not None
    assert res1[1] == "2026-01-02T00:00:00.000Z"

    # Hour 14 requires min 00
    assert parse_rfc3339_timestamp("2026-01-02T00:00:00+14:00") is not None
    assert parse_rfc3339_timestamp("2026-01-02T00:00:00+14:30") is None

    # Invalid calendar day
    assert parse_rfc3339_timestamp("2026-02-29T00:00:00Z") is None


# ===========================================================================
# 2. Q1: POST /build-corpus
# ===========================================================================
def test_q1_build_corpus_basic():
    content = (
        '{"id":"r1","entity":"User A","eventTime":"2026-01-01T10:00:00Z","revision":1,"text":"apple banana"}\n'
        '{"id":"r2","entity":"User B","eventTime":"2026-01-01T11:00:00Z","revision":1,"text":"cherry date"}\n'
    )
    crc = crc32c_hex(content.encode("utf-8"))

    payload = {
        "policy": {
            "minTime": "2026-01-01T00:00:00Z",
            "maxTime": "2026-01-02T00:00:00Z",
            "contaminationThreshold": 0.8,
        },
        "objects": [
            {
                "uri": "gs://bucket/object",
                "generation": "123",
                "fetchedGeneration": "123",
                "crc32c": crc,
                "schemaId": "training-v1",
                "content": content,
            }
        ],
    }

    code, resp = build_corpus_decision(payload)
    assert code == 200
    assert "splits" in resp
    assert "digests" in resp
    assert len(resp["rejectedObjects"]) == 0


def test_q1_build_corpus_deduplication():
    # Two rows with same [entity, eventTime, text], different revisions
    content = (
        '{"id":"r1","entity":"User A","eventTime":"2026-01-01T10:00:00Z","revision":1,"text":"apple banana"}\n'
        '{"id":"r2","entity":"User A","eventTime":"2026-01-01T10:00:00Z","revision":2,"text":"apple banana"}\n'
    )
    crc = crc32c_hex(content.encode("utf-8"))
    payload = {
        "policy": {
            "minTime": "2026-01-01T00:00:00Z",
            "maxTime": "2026-01-02T00:00:00Z",
            "contaminationThreshold": 0.8,
        },
        "objects": [{
            "uri": "gs://bucket/object",
            "generation": "10",
            "fetchedGeneration": "10",
            "crc32c": crc,
            "schemaId": "training-v1",
            "content": content,
        }],
    }
    code, resp = build_corpus_decision(payload)
    assert code == 200
    # r1 should be rejected as DUPLICATE, r2 kept
    rej_ids = [r["id"] for r in resp["rejectedRows"]]
    assert "r1" in rej_ids


# ===========================================================================
# 3. Q2: POST /bqml
# ===========================================================================
def test_q2_bqml_lifecycle():
    store = BQMLStore()
    select_payload = {
        "phase": "select",
        "runId": "run-test-1",
        "forbiddenFeatures": ["leakage_feat"],
        "numTrialsLimit": 5,
        "rows": [
            {
                "id": "row1",
                "entity": "E1",
                "eventTime": "2026-01-01T10:00:00Z",
                "predictionTime": "2026-01-01T12:00:00Z",
                "version": 1,
                "split": "TRAIN",
                "features": {
                    "f1": {"value": "v1", "availableAt": "2026-01-01T11:00:00Z"},
                    "leakage_feat": {"value": "bad", "availableAt": "2026-01-01T11:00:00Z"},
                },
            },
            {
                "id": "row2",
                "entity": "E2",
                "eventTime": "2026-01-01T10:00:00Z",
                "predictionTime": "2026-01-01T12:00:00Z",
                "version": 1,
                "split": "EVAL",
                "features": {
                    "f1": {"value": "v2", "availableAt": "2026-01-01T11:00:00Z"},
                    "leakage_feat": {"value": "bad", "availableAt": "2026-01-01T11:00:00Z"},
                },
            },
        ],
        "trials": [
            {"trialId": 1, "status": "SUCCEEDED", "evalMetric": 0.85},
            {"trialId": 2, "status": "SUCCEEDED", "evalMetric": 0.95},
        ],
    }

    code, resp = bqml_decision(select_payload, store=store)
    assert code == 200
    assert resp["selectedTrialId"] == 2
    assert resp["featureNames"] == ["f1"]  # leakage_feat filtered
    dataset_dig = resp["datasetDigest"]

    # Phase 2: evaluate
    eval_payload = {
        "phase": "evaluate",
        "runId": "run-test-1",
        "selectedTrialId": 2,
        "datasetDigest": dataset_dig,
        "metricFloor": 0.8,
        "requiredSlices": {"critical": 0.8},
        "rows": [
            {"label": 1, "prediction": 1, "slice": "critical"},
            {"label": 0, "prediction": 0, "slice": "critical"},
        ],
        "bytesProcessed": 500,
        "maxBytes": 1000,
    }
    code2, resp2 = bqml_decision(eval_payload, store=store)
    assert code2 == 200
    assert resp2["decision"] == "admit"
    assert resp2["criticalSlicePass"] is True


# ===========================================================================
# 4. Q3: POST /promote
# ===========================================================================
def test_q3_promote_champion():
    payload = {
        "asOf": "2026-01-01T12:00:00Z",
        "championVersion": "1",
        "policy": {
            "datasetDigest": "data_hash_64",
            "schemaDigest": "schema_hash_64",
            "maxAgeSeconds": 3600,
            "accuracyFloor": 0.8,
            "requiredSlices": {"critical": 0.75},
            "maxLatencyMs": 100,
            "maxSizeBytes": 1000000,
            "minImprovement": 0.05,
        },
        "versions": [
            {
                "version": "1",
                "artifactDigest": "art1",
                "evaluation": {
                    "createdAt": "2026-01-01T11:30:00Z",
                    "artifactDigest": "art1",
                    "datasetDigest": "data_hash_64",
                    "schemaDigest": "schema_hash_64",
                    "accuracy": 0.85,
                    "latencyMs": 50,
                    "sizeBytes": 500000,
                    "slices": {"critical": 0.80},
                },
            },
            {
                "version": "2",
                "artifactDigest": "art2",
                "evaluation": {
                    "createdAt": "2026-01-01T11:45:00Z",
                    "artifactDigest": "art2",
                    "datasetDigest": "data_hash_64",
                    "schemaDigest": "schema_hash_64",
                    "accuracy": 0.95,  # +0.10 improvement >= 0.05
                    "latencyMs": 45,
                    "sizeBytes": 450000,
                    "slices": {"critical": 0.90},
                },
            },
        ],
    }
    code, resp = promote_decision(payload)
    assert code == 200
    assert resp["action"] == "promote"
    assert resp["selectedVersion"] == "2"
    assert resp["aliasMutation"] == {"alias": "champion", "version": "2"}


# ===========================================================================
# 5. Q4: POST /adapt
# ===========================================================================
def test_q4_adapt_choose_and_repair():
    choose_payload = {
        "operation": "choose",
        "policy": {
            "minQuality": 0.8,
            "freshnessRequired": True,
            "maxLatencyMs": 100,
            "maxMemoryMb": 1024,
            "maxLabeledExamples": 100,
            "maxTotalCost": 1000,
            "horizonRequests": 1000,
        },
        "candidates": [
            {
                "name": "prompt_only",
                "available": True,
                "quality": 0.85,
                "freshness": True,
                "latencyMs": 50,
                "memoryMb": 256,
                "labeledExamples": 0,
                "oneTimeCost": 10,
                "recurringCost": 0.01,
            },
            {
                "name": "retrieval",
                "available": True,
                "quality": 0.90,
                "freshness": True,
                "latencyMs": 60,
                "memoryMb": 512,
                "labeledExamples": 0,
                "oneTimeCost": 20,
                "recurringCost": 0.02,
            },
            {
                "name": "lora",
                "available": True,
                "quality": 0.95,
                "freshness": False,
                "latencyMs": 70,
                "memoryMb": 512,
                "labeledExamples": 50,
                "oneTimeCost": 50,
                "recurringCost": 0.01,
            },
            {
                "name": "qlora",
                "available": True,
                "quality": 0.95,
                "freshness": False,
                "latencyMs": 70,
                "memoryMb": 256,
                "labeledExamples": 50,
                "oneTimeCost": 50,
                "recurringCost": 0.01,
            },
        ],
    }
    code, resp = adapt_decision(choose_payload)
    assert code == 200
    assert resp["selected"] == "prompt_only"


# ===========================================================================
# 6. Q5: POST /quantize
# ===========================================================================
def test_q5_quantize_freeze_and_select():
    store = QuantizeStore()
    freeze_payload = {
        "phase": "freeze",
        "freezeId": "freeze-1",
        "calibrationDigest": "calib_1",
        "tokenizerDigest": "tok_1",
        "allowedUnsupportedReasons": [],
        "candidates": [
            {
                "name": "int8",
                "files": {"model.safetensors": "dummy_binary_safetensors_data"},
                "loadable": True,
                "calibrationDigest": "calib_1",
                "tokenizerDigest": "tok_1",
            }
        ],
    }
    code, resp = quantize_decision(freeze_payload, store=store)
    assert code == 200
    assert resp["candidates"][0]["status"] == "frozen"


# ===========================================================================
# 7. Q6: POST /pipeline
# ===========================================================================
def test_q6_pipeline_dag():
    store = PipelineStore()
    payload = {
        "session": "sess-test",
        "revision": 1,
        "inputs": {
            "generation": "1",
            "checksum": "chk",
            "canonicalData": "data",
            "prepareCode": "prep",
            "prepareConfig": "cfg",
            "trainCode": "train",
            "trainConfig": "tcfg",
            "runtime": "py311",
            "evaluateCode": "eval",
            "evaluateConfig": "ecfg",
            "schemaDigest": "sch",
            "publishConfig": "pcfg",
        },
        "events": [],
    }
    code, resp = pipeline_decision(payload, store=store)
    assert code == 200
    assert resp["revision"] == 1
    assert len(resp["nodes"]) == 6
    assert resp["nodes"][0]["node"] == "verify_data"
    assert resp["nodes"][0]["action"] == "rerun"


# ===========================================================================
# 8. Q7: POST /verify-bundle
# ===========================================================================
def test_q7_verify_bundle():
    manifest = {
        "task": "classification",
        "baseRevision": "a" * 40,
        "datasetDigest": "d" * 64,
        "codeDigest": "c" * 64,
        "trainingConfigDigest": "t" * 64,
        "modelArtifactDigest": hashlib.sha256(b"adapter_weights").hexdigest(),
        "evaluationArtifactDigest": hashlib.sha256(
            json.dumps({
                "modelArtifactDigest": hashlib.sha256(b"adapter_weights").hexdigest(),
                "accuracy": 0.9,
                "slices": {"critical": 0.85},
            }, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }
    eval_json = json.dumps({
        "modelArtifactDigest": manifest["modelArtifactDigest"],
        "accuracy": 0.9,
        "slices": {"critical": 0.85},
    }, separators=(",", ":"))

    inv_list = [
        {"name": "README.md", "bytes": len(b"dummy"), "sha256": hashlib.sha256(b"dummy").hexdigest()},
        {"name": "adapter_config.json", "bytes": len(b'{"r":16,"target_modules":["q_proj"]}'), "sha256": hashlib.sha256(b'{"r":16,"target_modules":["q_proj"]}').hexdigest()},
        {"name": "adapter_model.safetensors", "bytes": len(b"adapter_weights"), "sha256": manifest["modelArtifactDigest"]},
        {"name": "evaluation.json", "bytes": len(eval_json.encode("utf-8")), "sha256": manifest["evaluationArtifactDigest"]},
        {"name": "training_manifest.json", "bytes": len(json.dumps(manifest, separators=(",", ":")).encode("utf-8")), "sha256": hashlib.sha256(json.dumps(manifest, separators=(",", ":")).encode("utf-8")).hexdigest()},
    ]
    inv_list = sorted(inv_list, key=lambda x: x["name"])

    readme_content = f"""# Model Card
<!-- tds-model-card {json.dumps({
    "task": manifest["task"],
    "baseRevision": manifest["baseRevision"],
    "datasetDigest": manifest["datasetDigest"],
    "modelArtifactDigest": manifest["modelArtifactDigest"],
    "license": "mit",
    "intendedUse": "research",
    "limitations": "none"
}, separators=(',', ':'))} -->
"""
    # Fix README entry in inventory
    inv_list[0]["bytes"] = len(readme_content.encode("utf-8"))
    inv_list[0]["sha256"] = hashlib.sha256(readme_content.encode("utf-8")).hexdigest()

    payload = {
        "policy": {
            "requiredSlices": ["critical"],
            "license": "mit",
            "intendedUse": "research",
            "limitations": "none",
        },
        "files": {
            "README.md": readme_content,
            "training_manifest.json": json.dumps(manifest, separators=(",", ":")),
            "evaluation.json": eval_json,
            "inventory.json": json.dumps(inv_list, separators=(",", ":")),
            "adapter_model.safetensors": "adapter_weights",
            "adapter_config.json": '{"r":16,"target_modules":["q_proj"]}',
        },
    }

    code, resp = verify_bundle_decision(payload)
    assert code == 200
    assert resp["decision"] == "admit"
    assert len(resp["violations"]) == 0


# ===========================================================================
# 9. Q8, Q9, Q10 Solvers
# ===========================================================================
def test_q8_lora():
    res = solve_q8_lora(TEST_EMAIL)
    assert res["trainable_params"] > 0
    assert res["adapter_file_size_bytes"] == res["trainable_params"] * 4


def test_q9_mlflow():
    res = solve_q9_mlflow(TEST_EMAIL)
    assert "final_loss" in res
    assert "run_id" in res
    assert "mean_last_10_loss" in res


def test_q10_carbon():
    res = solve_q10_carbon(TEST_EMAIL)
    assert res["co2_kg"] > 0
    assert "co2_eq_emissions:" in res["yaml_frontmatter"]


# ===========================================================================
# 10. Multi-Tenant ASGI Integration
# ===========================================================================
def test_asgi_multi_tenant_routes():
    # Test bare route
    r1 = client.post(f"/ga8/{TEST_EMAIL}/build-corpus", json={})
    assert r1.status_code == 400

    # Test solve routes
    r2 = client.get(f"/ga8/{TEST_EMAIL}/solve/q8")
    assert r2.status_code == 200
    assert "trainable_params" in r2.json()

    r3 = client.get(f"/ga8/{TEST_EMAIL}/solve/q10")
    assert r3.status_code == 200
    assert "co2_kg" in r3.json()
