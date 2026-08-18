from __future__ import annotations

"""
T22026/GA8/solvers.py — Deterministic Solvers & Policy Engines for GA8.

Covers all 10 GA8 questions:
- Q1: POST /build-corpus (Immutable, Leakage-Safe Training Corpus)
- Q2: POST /bqml (Stateful Leakage-Safe BQML Experiment Gate)
- Q3: POST /promote (MLflow Verifiable Evidence Model Promotion Gate)
- Q4: POST /adapt (PEFT Adaptation Choice & Training Run Repair)
- Q5: POST /quantize (Stateful Quantized Model Candidate Admission Gate)
- Q6: POST /pipeline (Stateful Content-Addressed ML Pipeline Controller)
- Q7: POST /verify-bundle (Verifiable Model Bundle & Model Card Verifier)
- Q8: solve_q8_lora (Per-Layer QLoRA Adapter Synthesis & Parameter Audit)
- Q9: solve_q9_mlflow (PyTorch Training Loop Fidelity & Local MLflow Audit)
- Q10: solve_q10_carbon (Green AI & HF Model Card Carbon Accounting Audit)
"""

import hashlib
import json
import math
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Set

from T22026.shared.seedrandom_arc4 import SeedRandom


# ===========================================================================
# Pure Python CRC32C (Castagnoli polynomial 0x1EDC6F41)
# ===========================================================================
def _make_crc32c_table() -> List[int]:
    table = []
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0x82F63B78
            else:
                crc = crc >> 1
        table.append(crc)
    return table


_CRC32C_TABLE = _make_crc32c_table()
_MAX_SAFE_INTEGER = (1 << 53) - 1


def _is_safe_integer(value: Any, *, minimum: int = 0) -> bool:
    """Match JavaScript's non-Boolean safe-integer domain exactly."""
    return isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= _MAX_SAFE_INTEGER


def crc32c_hex(data: bytes) -> str:
    """Compute 8-character lowercase hex CRC32C over raw bytes."""
    crc = 0xFFFFFFFF
    for b in data:
        crc = _CRC32C_TABLE[(crc ^ b) & 0xFF] ^ (crc >> 8)
    crc ^= 0xFFFFFFFF
    return f"{crc:08x}"


# ===========================================================================
# Timestamp Parser & UTC Normalizer (RFC 3339 strict)
# ===========================================================================
_TIMESTAMP_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?(Z|([+-])(\d{2}):(\d{2}))$"
)


def parse_rfc3339_timestamp(ts: Any) -> Optional[Tuple[datetime, str]]:
    """
    Validates RFC 3339 format YYYY-MM-DDTHH:mm:ss[.sss](Z|±HH:mm).
    Checks calendar validity, offset magnitude <= 14:00 (hour 14 requires min 00).
    Returns (utc_datetime, normalized_utc_string) or None if invalid.
    """
    if not isinstance(ts, str) or not ts:
        return None
    m = _TIMESTAMP_RE.match(ts)
    if not m:
        return None
    year, month, day, hour, minute, second, frac, tz_str, sign, tz_h, tz_m = m.groups()
    try:
        y, mo, d = int(year), int(month), int(day)
        h, mi, s = int(hour), int(minute), int(second)
        if frac:
            ms = int(frac.ljust(3, "0")[:3])
        else:
            ms = 0

        # Offset validation
        if tz_str == "Z":
            offset_mins = 0
        else:
            off_h, off_m = int(tz_h), int(tz_m)
            if off_h > 14 or off_m > 59 or (off_h == 14 and off_m != 0):
                return None
            offset_mins = (off_h * 60 + off_m) * (1 if sign == "+" else -1)

        # Validate calendar via standard datetime
        dt_local = datetime(y, mo, d, h, mi, s, ms * 1000, tzinfo=timezone.utc)
        # Convert to true UTC
        utc_ts = dt_local.timestamp() - (offset_mins * 60)
        dt_utc = datetime.fromtimestamp(utc_ts, tz=timezone.utc)

        # Format as YYYY-MM-DDTHH:mm:ss.sssZ
        norm_str = f"{dt_utc.year:04d}-{dt_utc.month:02d}-{dt_utc.day:02d}T{dt_utc.hour:02d}:{dt_utc.minute:02d}:{dt_utc.second:02d}.{int(dt_utc.microsecond / 1000):03d}Z"
        return dt_utc, norm_str
    except Exception:
        return None


# ===========================================================================
# 1. POST /build-corpus
# ===========================================================================
_GS_URI_RE = re.compile(r"^gs://([^/]+)/(.+)$")
_WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)


def _canonicalize_text(s: str) -> str:
    norm = unicodedata.normalize("NFKC", str(s))
    norm = norm.lower().strip()
    return re.sub(r"\s+", " ", norm)


def _extract_words(s: str) -> Set[str]:
    norm = _canonicalize_text(s)
    return set(_WORD_RE.findall(norm))


def _jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def build_corpus_decision(body: Any) -> Tuple[int, Dict[str, Any]]:
    """Q1 Solver: Immutable, Leakage-Safe Training Corpus."""
    if not isinstance(body, dict):
        return 400, {"error": "INVALID_INPUT"}
    if "policy" not in body or not isinstance(body.get("policy"), dict):
        return 400, {"error": "INVALID_INPUT"}
    if "objects" not in body or not isinstance(body.get("objects"), list):
        return 400, {"error": "INVALID_INPUT"}

    policy = body["policy"]
    raw_min_time = policy.get("minTime")
    raw_max_time = policy.get("maxTime")
    contam_thresh = policy.get("contaminationThreshold")

    # Validate policy
    min_time_parsed = parse_rfc3339_timestamp(raw_min_time)
    max_time_parsed = parse_rfc3339_timestamp(raw_max_time)
    is_valid_policy = (
        min_time_parsed is not None
        and max_time_parsed is not None
        and isinstance(contam_thresh, (int, float))
        and not isinstance(contam_thresh, bool)
        and not math.isnan(contam_thresh)
        and not math.isinf(contam_thresh)
        and 0.0 <= contam_thresh <= 1.0
        and min_time_parsed[0] <= max_time_parsed[0]
    )

    objects = body["objects"]
    rejected_objects: List[Dict[str, Any]] = []
    lineage: List[Dict[str, Any]] = []
    all_raw_rows: List[Dict[str, Any]] = []

    for obj in objects:
        if not isinstance(obj, dict):
            rejected_objects.append({"uri": None, "reasonCodes": ["SCHEMA_INVALID"]})
            continue

        uri = obj.get("uri")
        uri_str = uri if isinstance(uri, str) else None
        generation = obj.get("generation")
        fetched_generation = obj.get("fetchedGeneration")
        crc32c_val = obj.get("crc32c")
        schema_id = obj.get("schemaId")
        content = obj.get("content")

        obj_reasons: Set[str] = set()

        # URI check
        if not isinstance(uri, str) or not _GS_URI_RE.match(uri):
            obj_reasons.add("URI_INVALID")

        # Generation checks (independent evaluations per spec)
        gen_valid = isinstance(generation, str) and generation.isdigit() and len(generation) > 0
        fetch_valid = isinstance(fetched_generation, str) and fetched_generation.isdigit() and len(fetched_generation) > 0
        if not gen_valid or not fetch_valid:
            obj_reasons.add("GENERATION_INVALID")
        if generation != fetched_generation:
            obj_reasons.add("GENERATION_MISMATCH")

        # CRC32C syntax check
        crc_syntax_valid = isinstance(crc32c_val, str) and bool(re.match(r"^[0-9a-f]{8}$", crc32c_val))
        if not crc_syntax_valid:
            obj_reasons.add("CRC32C_INVALID")
        elif isinstance(content, str):
            computed_crc = crc32c_hex(content.encode("utf-8"))
            if computed_crc.lower() != crc32c_val.lower():
                obj_reasons.add("CRC32C_MISMATCH")

        # Schema & Content check
        if not isinstance(content, str) or schema_id != "training-v1":
            obj_reasons.add("SCHEMA_INVALID")

        # Parse JSONL content (scan all rows without early break to collect all codes)
        obj_rows: List[Dict[str, Any]] = []
        if isinstance(content, str):
            lines = [ln for ln in content.splitlines() if ln.strip()]
            if len(lines) == 0:
                obj_reasons.add("SCHEMA_INVALID")
            else:
                for line in lines:
                    try:
                        row_data = json.loads(line)
                    except Exception:
                        obj_reasons.add("JSONL_INVALID")
                        continue

                    if not isinstance(row_data, dict):
                        obj_reasons.add("SCHEMA_INVALID")
                        continue

                    expected_keys = {"id", "entity", "eventTime", "revision", "text"}
                    if set(row_data.keys()) != expected_keys:
                        obj_reasons.add("SCHEMA_INVALID")
                        continue

                    r_id = row_data.get("id")
                    r_ent = row_data.get("entity")
                    r_time = row_data.get("eventTime")
                    r_rev = row_data.get("revision")
                    r_txt = row_data.get("text")

                    if not (
                        isinstance(r_id, str)
                        and isinstance(r_ent, str)
                        and isinstance(r_time, str)
                        and isinstance(r_txt, str)
                        and isinstance(r_rev, int)
                        and not isinstance(r_rev, bool)
                        and _is_safe_integer(r_rev)
                    ):
                        obj_reasons.add("SCHEMA_INVALID")
                        continue

                    time_res = parse_rfc3339_timestamp(r_time)
                    if time_res is None:
                        obj_reasons.add("SCHEMA_INVALID")
                        continue

                    obj_rows.append({
                        "id": r_id,
                        "entity": r_ent,
                        "eventTime": r_time,
                        "normEventTime": time_res[1],
                        "eventDt": time_res[0],
                        "revision": r_rev,
                        "text": r_txt,
                    })

        if obj_reasons:
            sorted_codes = sorted(list(obj_reasons), key=lambda s: s.encode("utf-8"))
            rejected_objects.append({"uri": uri_str, "reasonCodes": sorted_codes})
        else:
            lineage.append({
                "uri": uri,
                "generation": generation,
                "crc32c": crc32c_val,
                "schemaId": schema_id,
            })
            all_raw_rows.extend(obj_rows)

    # Row Deduplication & Normalization
    canonical_rows = []
    for r in all_raw_rows:
        canon_ent = _canonicalize_text(r["entity"])
        canon_txt = _canonicalize_text(r["text"])
        canonical_rows.append({
            "id": r["id"],
            "entity": canon_ent,
            "eventTime": r["normEventTime"],
            "eventDt": r["eventDt"],
            "revision": r["revision"],
            "text": canon_txt,
        })

    # Group by [entity, eventTime, text]
    dedup_groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in canonical_rows:
        key = json.dumps([r["entity"], r["eventTime"], r["text"]], separators=(",", ":"))
        dedup_groups.setdefault(key, []).append(r)

    retained_rows: List[Dict[str, Any]] = []
    rejected_rows_map: Dict[str, Set[str]] = {}

    for key, group in dedup_groups.items():
        if len(group) == 1:
            retained_rows.append(group[0])
        else:
            sorted_group = sorted(
                group,
                key=lambda x: (-x["revision"], x["id"].encode("utf-8")),
            )
            winner = sorted_group[0]
            retained_rows.append(winner)
            for loser in sorted_group[1:]:
                rejected_rows_map.setdefault(loser["id"], set()).add("DUPLICATE")

    # Policy and Window Validation
    valid_window_rows: List[Dict[str, Any]] = []
    for r in retained_rows:
        if not is_valid_policy:
            rejected_rows_map.setdefault(r["id"], set()).add("POLICY_INVALID")
            continue

        min_dt = min_time_parsed[0]  # type: ignore
        max_dt = max_time_parsed[0]  # type: ignore
        if r["eventDt"] < min_dt or r["eventDt"] > max_dt:
            rejected_rows_map.setdefault(r["id"], set()).add("OUT_OF_WINDOW")
        else:
            valid_window_rows.append(r)

    # Splitting into train, validation, test
    train_rows: List[Dict[str, Any]] = []
    val_rows: List[Dict[str, Any]] = []
    test_rows: List[Dict[str, Any]] = []

    for r in valid_window_rows:
        ent_hash = hashlib.sha256(r["entity"].encode("utf-8")).digest()
        bucket = ent_hash[0] % 10
        if 0 <= bucket <= 5:
            train_rows.append(r)
        elif 6 <= bucket <= 7:
            val_rows.append(r)
        else:
            test_rows.append(r)

    # Contamination check on validation and test rows
    train_word_sets = [_extract_words(tr["text"]) for tr in train_rows]

    final_val_rows: List[Dict[str, Any]] = []
    for vr in val_rows:
        vr_words = _extract_words(vr["text"])
        is_contaminated = False
        if is_valid_policy:
            for tw in train_word_sets:
                sim = _jaccard_similarity(vr_words, tw)
                if sim >= contam_thresh:  # type: ignore
                    is_contaminated = True
                    break
        if is_contaminated:
            rejected_rows_map.setdefault(vr["id"], set()).add("TRAIN_CONTAMINATION")
        else:
            final_val_rows.append(vr)

    final_test_rows: List[Dict[str, Any]] = []
    for tr_row in test_rows:
        tr_words = _extract_words(tr_row["text"])
        is_contaminated = False
        if is_valid_policy:
            for tw in train_word_sets:
                sim = _jaccard_similarity(tr_words, tw)
                if sim >= contam_thresh:  # type: ignore
                    is_contaminated = True
                    break
        if is_contaminated:
            rejected_rows_map.setdefault(tr_row["id"], set()).add("TRAIN_CONTAMINATION")
        else:
            final_test_rows.append(tr_row)

    # Sort split rows and calculate SHA-256 digests
    def _format_split(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str]:
        def _row_dict(r: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "id": r["id"],
                "entity": r["entity"],
                "eventTime": r["eventTime"],
                "revision": r["revision"],
                "text": r["text"],
            }

        sorted_rows = sorted(
            rows,
            key=lambda x: (
                x["id"].encode("utf-8"),
                json.dumps(_row_dict(x), separators=(",", ":"), ensure_ascii=False),
            ),
        )
        formatted = []
        serialized_lines = []
        for r in sorted_rows:
            clean_item = _row_dict(r)
            formatted.append(clean_item)
            compact_json = json.dumps(clean_item, separators=(",", ":"), ensure_ascii=False)
            serialized_lines.append(compact_json + "\n")

        raw_bytes = "".join(serialized_lines).encode("utf-8")
        digest = hashlib.sha256(raw_bytes).hexdigest()
        return formatted, digest

    train_out, train_digest = _format_split(train_rows)
    val_out, val_digest = _format_split(final_val_rows)
    test_out, test_digest = _format_split(final_test_rows)

    # Format rejected rows
    rejected_rows_list = []
    for r_id, codes in rejected_rows_map.items():
        sorted_codes = sorted(list(codes), key=lambda s: s.encode("utf-8"))
        rejected_rows_list.append({"id": r_id, "reasonCodes": sorted_codes})

    rejected_rows_list = sorted(
        rejected_rows_list,
        key=lambda x: (
            x["id"].encode("utf-8"),
            json.dumps(x, separators=(",", ":"), ensure_ascii=False),
        ),
    )

    rejected_objects = sorted(
        rejected_objects,
        key=lambda x: (
            (x["uri"] or "").encode("utf-8"),
            json.dumps(x, separators=(",", ":"), ensure_ascii=False),
        ),
    )

    lineage = sorted(
        lineage,
        key=lambda x: (
            x["uri"].encode("utf-8"),
            json.dumps(x, separators=(",", ":"), ensure_ascii=False),
        ),
    )

    return 200, {
        "splits": {"train": train_out, "validation": val_out, "test": test_out},
        "rejectedObjects": rejected_objects,
        "rejectedRows": rejected_rows_list,
        "digests": {"train": train_digest, "validation": val_digest, "test": test_digest},
        "lineage": lineage,
    }


# ===========================================================================
# 2. POST /bqml
# ===========================================================================
class BQMLStore:
    """Thread-safe multi-tenant store for BQML runs."""

    def __init__(self) -> None:
        self._runs: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._inputs: Dict[Tuple[str, str], str] = {}

    def get_run(self, tenant: str, run_id: str) -> Optional[Dict[str, Any]]:
        return self._runs.get((tenant, run_id))

    def record_selection(self, tenant: str, run_id: str, input_json: str, response: Dict[str, Any]) -> None:
        self._runs[(tenant, run_id)] = response
        self._inputs[(tenant, run_id)] = input_json

    def check_conflict(self, tenant: str, run_id: str, input_json: str) -> bool:
        key = (tenant, run_id)
        if key in self._inputs:
            return self._inputs[key] != input_json
        return False


_BQML_STORE = BQMLStore()


def bqml_decision(body: Any, store: Optional[BQMLStore] = None, tenant: str = "") -> Tuple[int, Dict[str, Any]]:
    """Q2 Solver: Leakage-Safe BigQuery ML Experiment Gate."""
    st = store or _BQML_STORE
    if not isinstance(body, dict):
        return 400, {"error": "INVALID_INPUT"}
    phase = body.get("phase")
    if phase not in ("select", "evaluate"):
        return 400, {"error": "INVALID_INPUT"}

    if phase == "select":
        run_id = body.get("runId")
        forbidden = body.get("forbiddenFeatures")
        trials_limit = body.get("numTrialsLimit")
        rows = body.get("rows")
        trials = body.get("trials")

        input_canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))

        # Replay / conflict check
        if isinstance(run_id, str) and st.check_conflict(tenant, run_id, input_canonical):
            return 409, {"error": "RUN_ID_CONFLICT"}
        if isinstance(run_id, str) and st.get_run(tenant, run_id) is not None:
            return 200, st.get_run(tenant, run_id)  # type: ignore

        reasons: Set[str] = set()

        is_valid_input = (
            isinstance(run_id, str)
            and 1 <= len(run_id) <= 128
            and isinstance(forbidden, list)
            and all(isinstance(f, str) for f in forbidden)
            and isinstance(trials_limit, int)
            and not isinstance(trials_limit, bool)
            and _is_safe_integer(trials_limit, minimum=1)
            and isinstance(rows, list)
            and len(rows) > 0
            and isinstance(trials, list)
        )

        if not is_valid_input:
            reasons.add("INVALID_INPUT")
            resp = {
                "runId": run_id if isinstance(run_id, str) else "",
                "selectedTrialId": None,
                "trainRowIds": [],
                "evalRowIds": [],
                "featureNames": [],
                "datasetDigest": None,
                "reasonCodes": sorted(list(reasons), key=lambda s: s.encode("utf-8")),
            }
            if isinstance(run_id, str) and 1 <= len(run_id) <= 128:
                st.record_selection(tenant, run_id, input_canonical, resp)
            return 200, resp

        # Check unique row IDs & timestamps
        row_ids_seen = set()
        parsed_rows = []
        for r in rows:
            if not isinstance(r, dict):
                reasons.add("INVALID_INPUT")
                break
            r_id = r.get("id")
            ent = r.get("entity")
            ev_time = r.get("eventTime")
            pred_time = r.get("predictionTime")
            ver = r.get("version")
            split = r.get("split")
            features = r.get("features")

            if (
                not isinstance(r_id, str)
                or r_id in row_ids_seen
                or not isinstance(ent, str)
                or not isinstance(ev_time, str)
                or not isinstance(pred_time, str)
                or not isinstance(ver, int)
                or isinstance(ver, bool)
                or not _is_safe_integer(ver)
                or split not in ("TRAIN", "EVAL")
                or not isinstance(features, dict)
            ):
                reasons.add("INVALID_INPUT")
                break
            row_ids_seen.add(r_id)

            ev_res = parse_rfc3339_timestamp(ev_time)
            pred_res = parse_rfc3339_timestamp(pred_time)
            if ev_res is None or pred_res is None:
                reasons.add("INVALID_INPUT")
                break

            parsed_rows.append({
                "id": r_id,
                "entity": ent,
                "eventTime": ev_res[1],
                "eventDt": ev_res[0],
                "predDt": pred_res[0],
                "version": ver,
                "split": split,
                "features": features,
            })

        if "INVALID_INPUT" in reasons or len(parsed_rows) != len(rows):
            reasons.add("INVALID_INPUT")
            resp = {
                "runId": run_id,
                "selectedTrialId": None,
                "trainRowIds": [],
                "evalRowIds": [],
                "featureNames": [],
                "datasetDigest": None,
                "reasonCodes": sorted(list(reasons), key=lambda s: s.encode("utf-8")),
            }
            st.record_selection(tenant, run_id, input_canonical, resp)
            return 200, resp

        # Deduplicate rows by [entity, UTC(eventTime)] keeping highest version, smallest ID
        dedup_dict: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        for r in parsed_rows:
            dedup_dict.setdefault((r["entity"], r["eventTime"]), []).append(r)

        retained_rows: List[Dict[str, Any]] = []
        for key, grp in dedup_dict.items():
            sorted_grp = sorted(grp, key=lambda x: (-x["version"], x["id"].encode("utf-8")))
            retained_rows.append(sorted_grp[0])

        # Feature eligibility:
        common_features = set(retained_rows[0]["features"].keys())
        for r in retained_rows[1:]:
            common_features &= set(r["features"].keys())

        forbidden_set = set(forbidden)
        eligible_features = set()

        for f_name in common_features:
            if f_name in forbidden_set:
                continue
            is_f_valid = True
            for r in retained_rows:
                feat_obj = r["features"].get(f_name)
                if not isinstance(feat_obj, dict):
                    is_f_valid = False
                    break
                avail = feat_obj.get("availableAt")
                avail_res = parse_rfc3339_timestamp(avail)
                if avail_res is None or avail_res[0] > r["predDt"]:
                    is_f_valid = False
                    break
            if is_f_valid:
                eligible_features.add(f_name)

        sorted_features = sorted(list(eligible_features), key=lambda s: s.encode("utf-8"))

        # Split retained rows into train and eval
        train_ids = sorted([r["id"] for r in retained_rows if r["split"] == "TRAIN"], key=lambda s: s.encode("utf-8"))
        eval_ids = sorted([r["id"] for r in retained_rows if r["split"] == "EVAL"], key=lambda s: s.encode("utf-8"))

        # Compute datasetDigest
        digest_dict = {
            "trainRowIds": train_ids,
            "evalRowIds": eval_ids,
            "featureNames": sorted_features,
        }
        dataset_digest = hashlib.sha256(
            json.dumps(digest_dict, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()

        # Check trials
        if len(trials) > trials_limit:
            reasons.add("TRIAL_LIMIT_EXCEEDED")

        trial_ids_seen = set()
        succeeded_trials = []
        for t in trials:
            if not isinstance(t, dict):
                reasons.add("INVALID_INPUT")
                break
            t_id = t.get("trialId")
            st_status = t.get("status")
            metric = t.get("evalMetric")

            if not _is_safe_integer(t_id):
                reasons.add("INVALID_INPUT")
                break
            if t_id in trial_ids_seen:
                reasons.add("INVALID_INPUT")
                break
            trial_ids_seen.add(t_id)

            if st_status not in ("SUCCEEDED", "FAILED"):
                reasons.add("INVALID_INPUT")
                break

            if st_status == "SUCCEEDED":
                if (
                    isinstance(metric, (int, float))
                    and not isinstance(metric, bool)
                    and not math.isnan(metric)
                    and not math.isinf(metric)
                ):
                    succeeded_trials.append({"trialId": t_id, "evalMetric": float(metric)})

        selected_trial_id = None
        if not succeeded_trials and "INVALID_INPUT" not in reasons:
            reasons.add("NO_SUCCESSFUL_TRIAL")
        elif succeeded_trials and not reasons:
            sorted_trials = sorted(succeeded_trials, key=lambda x: (-x["evalMetric"], x["trialId"]))
            selected_trial_id = sorted_trials[0]["trialId"]

        final_reasons = sorted(list(reasons), key=lambda s: s.encode("utf-8"))
        # Any code makes selectedTrialId null (per spec line 390)
        if final_reasons:
            selected_trial_id = None

        resp = {
            "runId": run_id,
            "selectedTrialId": selected_trial_id,
            "trainRowIds": train_ids,
            "evalRowIds": eval_ids,
            "featureNames": sorted_features,
            "datasetDigest": dataset_digest if "INVALID_INPUT" not in reasons else None,
            "reasonCodes": final_reasons,
        }
        st.record_selection(tenant, run_id, input_canonical, resp)
        return 200, resp

    else:
        # Phase 2: evaluate
        run_id = body.get("runId")
        sel_trial = body.get("selectedTrialId")
        digest = body.get("datasetDigest")
        floor = body.get("metricFloor")
        req_slices = body.get("requiredSlices")
        rows = body.get("rows")
        bytes_proc = body.get("bytesProcessed")
        max_bytes = body.get("maxBytes")

        reasons: Set[str] = set()

        is_valid_input = (
            isinstance(run_id, str)
            and isinstance(sel_trial, int)
            and not isinstance(sel_trial, bool)
            and _is_safe_integer(sel_trial)
            and isinstance(digest, str)
            and isinstance(floor, (int, float))
            and not isinstance(floor, bool)
            and not math.isnan(floor)
            and not math.isinf(floor)
            and 0.0 <= floor <= 1.0
            and isinstance(req_slices, dict)
            and isinstance(rows, list)
            and isinstance(bytes_proc, int)
            and not isinstance(bytes_proc, bool)
            and _is_safe_integer(bytes_proc)
            and isinstance(max_bytes, int)
            and not isinstance(max_bytes, bool)
            and _is_safe_integer(max_bytes)
        )

        if not is_valid_input:
            reasons.add("INVALID_INPUT")

        # Lineage check
        stored = st.get_run(tenant, run_id) if isinstance(run_id, str) else None
        if not stored or stored.get("selectedTrialId") != sel_trial or stored.get("datasetDigest") != digest:
            reasons.add("INVALID_LINEAGE")

        # Byte check
        if isinstance(bytes_proc, int) and isinstance(max_bytes, int) and bytes_proc > max_bytes:
            reasons.add("BYTE_LIMIT")

        # Validate rows
        valid_rows = True
        if not isinstance(rows, list) or len(rows) == 0:
            valid_rows = False
        else:
            for r in rows:
                if not isinstance(r, dict):
                    valid_rows = False
                    break
                lbl = r.get("label")
                pred = r.get("prediction")
                sl = r.get("slice")
                if lbl not in (0, 1) or pred not in (0, 1) or not isinstance(sl, str) or not sl:
                    valid_rows = False
                    break

        if not valid_rows:
            reasons.add("INVALID_TEST_ROW")

        # Slices verification
        critical_slice_pass = True
        test_metric = None

        if "INVALID_INPUT" in reasons or "INVALID_LINEAGE" in reasons or not valid_rows:
            critical_slice_pass = False
        else:
            # Compute aggregate accuracy
            correct_cnt = sum(1 for r in rows if r["label"] == r["prediction"])
            test_metric = round(correct_cnt / len(rows), 12)
            if test_metric < floor:
                reasons.add("AGGREGATE_FLOOR")

            # Compute required slices
            slice_groups: Dict[str, List[Dict[str, Any]]] = {}
            for r in rows:
                slice_groups.setdefault(r["slice"], []).append(r)

            for sl_name, sl_floor in req_slices.items():
                if (
                    not isinstance(sl_floor, (int, float))
                    or isinstance(sl_floor, bool)
                    or math.isnan(sl_floor)
                    or math.isinf(sl_floor)
                    or not (0.0 <= sl_floor <= 1.0)
                ):
                    reasons.add("INVALID_INPUT")
                    critical_slice_pass = False
                    continue

                if sl_name not in slice_groups:
                    reasons.add(f"MISSING_SLICE:{sl_name}")
                    critical_slice_pass = False
                else:
                    sl_rows = slice_groups[sl_name]
                    sl_correct = sum(1 for r in sl_rows if r["label"] == r["prediction"])
                    sl_acc = round(sl_correct / len(sl_rows), 12)
                    if sl_acc < sl_floor:
                        reasons.add(f"SLICE_FLOOR:{sl_name}")
                        critical_slice_pass = False

        decision = "admit" if not reasons else "reject"
        final_codes = sorted(list(reasons), key=lambda s: s.encode("utf-8"))

        return 200, {
            "runId": run_id if isinstance(run_id, str) else "",
            "selectedTrialId": sel_trial if isinstance(sel_trial, int) else None,
            "datasetDigest": digest if isinstance(digest, str) else "",
            "testMetric": test_metric,
            "criticalSlicePass": critical_slice_pass,
            "decision": decision,
            "bytesProcessed": bytes_proc if isinstance(bytes_proc, int) else 0,
            "reasonCodes": final_codes,
        }


# ===========================================================================
# 3. POST /promote
# ===========================================================================
def promote_decision(body: Any) -> Tuple[int, Dict[str, Any]]:
    """Q3 Solver: MLflow Verifiable Evidence Model Promotion Gate."""
    if not isinstance(body, dict):
        return 400, {"error": "INVALID_INPUT"}
    if "policy" not in body or not isinstance(body.get("policy"), dict):
        return 400, {"error": "INVALID_INPUT"}
    if "versions" not in body or not isinstance(body.get("versions"), list):
        return 400, {"error": "INVALID_INPUT"}
    if "championVersion" not in body or not isinstance(body.get("championVersion"), str):
        return 400, {"error": "INVALID_INPUT"}

    as_of_raw = body.get("asOf")
    as_of_parsed = parse_rfc3339_timestamp(as_of_raw)
    champ_v = body["championVersion"]
    policy = body["policy"]
    versions = body["versions"]

    p_dataset_digest = policy.get("datasetDigest")
    p_schema_digest = policy.get("schemaDigest")
    p_max_age = policy.get("maxAgeSeconds")
    p_acc_floor = policy.get("accuracyFloor")
    p_req_slices = policy.get("requiredSlices")
    p_max_lat = policy.get("maxLatencyMs")
    p_max_size = policy.get("maxSizeBytes")
    p_min_imp = policy.get("minImprovement")

    is_valid_policy = (
        as_of_parsed is not None
        and isinstance(p_dataset_digest, str)
        and bool(p_dataset_digest)
        and isinstance(p_schema_digest, str)
        and bool(p_schema_digest)
        and _is_safe_integer(p_max_age)
        and isinstance(p_acc_floor, (int, float))
        and not isinstance(p_acc_floor, bool)
        and math.isfinite(p_acc_floor)
        and 0.0 <= p_acc_floor <= 1.0
        and isinstance(p_req_slices, dict)
        and all(isinstance(name, str) and name and isinstance(floor, (int, float))
                and not isinstance(floor, bool) and math.isfinite(floor) and 0.0 <= floor <= 1.0
                for name, floor in p_req_slices.items())
        and isinstance(p_max_lat, (int, float))
        and not isinstance(p_max_lat, bool)
        and math.isfinite(p_max_lat)
        and p_max_lat >= 0
        and _is_safe_integer(p_max_size)
        and isinstance(p_min_imp, (int, float))
        and not isinstance(p_min_imp, bool)
        and math.isfinite(p_min_imp)
        and 0.0 <= p_min_imp <= 1.0
    )

    failed_gates: Dict[str, List[str]] = {}
    eligible_versions: List[str] = []
    version_eval_map: Dict[str, Dict[str, Any]] = {}
    version_metrics: Dict[str, Tuple[float, float, int, int]] = {}

    # Pre-count occurrences of all version identifiers to reject every occurrence of a duplicate
    version_counts: Dict[str, int] = {}
    for v_obj in versions:
        if isinstance(v_obj, dict):
            vid = v_obj.get("version")
            if isinstance(vid, str):
                version_counts[vid] = version_counts.get(vid, 0) + 1

    for v_obj in versions:
        if not isinstance(v_obj, dict):
            continue
        v_id = v_obj.get("version")
        v_key = str(v_id) if v_id is not None else "invalid"
        v_reasons: Set[str] = set()

        if not is_valid_policy:
            v_reasons.add("INVALID_POLICY")

        # Version string check: must be canonical positive safe integer string
        if not (isinstance(v_id, str) and v_id.isdigit() and str(int(v_id)) == v_id
                and 0 < int(v_id) <= _MAX_SAFE_INTEGER):
            v_reasons.add("INVALID_VERSION")
        if isinstance(v_id, str) and version_counts.get(v_id, 0) > 1:
            v_reasons.add("DUPLICATE_VERSION")

        evaluation = v_obj.get("evaluation")
        artifact_digest = v_obj.get("artifactDigest")

        if not isinstance(evaluation, dict):
            v_reasons.add("MISSING_EVALUATION")
        else:
            created_at_raw = evaluation.get("createdAt")
            e_art_digest = evaluation.get("artifactDigest")
            e_data_digest = evaluation.get("datasetDigest")
            e_schema_digest = evaluation.get("schemaDigest")
            acc = evaluation.get("accuracy")
            lat = evaluation.get("latencyMs")
            sz = evaluation.get("sizeBytes")
            slices = evaluation.get("slices")

            created_parsed = parse_rfc3339_timestamp(created_at_raw)
            if created_parsed is None:
                v_reasons.add("INVALID_TIMESTAMP")
            elif as_of_parsed is not None:
                as_of_dt = as_of_parsed[0]
                created_dt = created_parsed[0]
                if created_dt > as_of_dt:
                    v_reasons.add("FUTURE_EVALUATION")
                elif (as_of_dt.timestamp() - created_dt.timestamp()) > p_max_age:
                    v_reasons.add("STALE_EVALUATION")

            # Check finite numbers
            for val in (acc, lat, sz):
                if (
                    not isinstance(val, (int, float))
                    or isinstance(val, bool)
                    or math.isnan(val)
                    or math.isinf(val)
                ):
                    v_reasons.add("NON_FINITE")
                    break

            if isinstance(acc, (int, float)) and not isinstance(acc, bool) and not (0.0 <= acc <= 1.0):
                v_reasons.add("METRIC_RANGE")
            if isinstance(lat, (int, float)) and not isinstance(lat, bool) and lat < 0:
                v_reasons.add("METRIC_RANGE")
            if not _is_safe_integer(sz):
                v_reasons.add("METRIC_RANGE")

            # Digest matching
            if artifact_digest != e_art_digest or not artifact_digest:
                v_reasons.add("ARTIFACT_MISMATCH")
            if is_valid_policy and p_dataset_digest != e_data_digest:
                v_reasons.add("DATASET_MISMATCH")
            if is_valid_policy and p_schema_digest != e_schema_digest:
                v_reasons.add("SCHEMA_MISMATCH")

            # Accuracy, latency, size limits (only if policy is valid)
            if is_valid_policy:
                if isinstance(acc, (int, float)) and not isinstance(acc, bool) and acc < p_acc_floor:
                    v_reasons.add("ACCURACY_FLOOR")
                if isinstance(lat, (int, float)) and not isinstance(lat, bool) and lat > p_max_lat:
                    v_reasons.add("LATENCY_LIMIT")
                if isinstance(sz, (int, float)) and not isinstance(sz, bool) and sz > p_max_size:
                    v_reasons.add("SIZE_LIMIT")

                # Slices validation
                if not isinstance(slices, dict):
                    for sl_name in p_req_slices.keys():
                        v_reasons.add(f"MISSING_SLICE:{sl_name}")
                else:
                    for sl_name, sl_floor in p_req_slices.items():
                        if sl_name not in slices:
                            v_reasons.add(f"MISSING_SLICE:{sl_name}")
                        else:
                            sl_val = slices[sl_name]
                            if not isinstance(sl_val, (int, float)) or isinstance(sl_val, bool) or not (0.0 <= sl_val <= 1.0):
                                v_reasons.add(f"SLICE_RANGE:{sl_name}")
                            elif sl_val < sl_floor:
                                v_reasons.add(f"SLICE_FLOOR:{sl_name}")

        sorted_v_reasons = sorted(list(v_reasons), key=lambda s: s.encode("utf-8"))
        failed_gates[v_key] = sorted_v_reasons

        if not sorted_v_reasons and isinstance(v_id, str):
            eligible_versions.append(v_id)
            version_eval_map[v_id] = evaluation
            version_metrics[v_id] = (
                float(evaluation["accuracy"]),
                float(evaluation["latencyMs"]),
                int(evaluation["sizeBytes"]),
                int(v_id),
            )

    # Sort eligible versions
    sorted_eligible = sorted(
        eligible_versions,
        key=lambda v: (
            -version_metrics[v][0],
            version_metrics[v][1],
            version_metrics[v][2],
            version_metrics[v][3],
        ),
    )

    champion_is_eligible = champ_v in sorted_eligible

    action = "block"
    selected_version = None
    alias_mutation = None
    evidence = None

    if not champion_is_eligible:
        action = "block"
        selected_version = None
    else:
        champ_acc = version_metrics[champ_v][0]
        challenger_v = sorted_eligible[0]
        chall_acc = version_metrics[challenger_v][0]

        improvement = round(chall_acc - champ_acc, 12)
        if challenger_v != champ_v and improvement >= p_min_imp:
            action = "promote"
            selected_version = challenger_v
            alias_mutation = {"alias": "champion", "version": challenger_v}
            evidence = version_eval_map[challenger_v]
        else:
            action = "retain"
            selected_version = champ_v
            alias_mutation = None
            evidence = version_eval_map[champ_v]

    return 200, {
        "action": action,
        "championVersion": champ_v,
        "selectedVersion": selected_version,
        "eligibleVersions": sorted_eligible,
        "failedGates": failed_gates,
        "aliasMutation": alias_mutation,
        "evidence": evidence,
    }


# ===========================================================================
# 4. POST /adapt
# ===========================================================================
_ADAPT_PRIORITY = ["prompt_only", "retrieval", "lora", "qlora"]


def adapt_decision(body: Any) -> Tuple[int, Dict[str, Any]]:
    """Q4 Solver: Minimal Adaptation Choice & PEFT Training Repair."""
    if not isinstance(body, dict):
        return 400, {"error": "INVALID_INPUT"}
    op = body.get("operation")
    if op not in ("choose", "repair"):
        return 400, {"error": "INVALID_INPUT"}

    if op == "choose":
        policy = body.get("policy")
        candidates = body.get("candidates")
        if not isinstance(policy, dict) or not isinstance(candidates, list):
            return 400, {"error": "INVALID_INPUT"}

        min_quality = policy.get("minQuality")
        freshness_req = policy.get("freshnessRequired")
        max_lat = policy.get("maxLatencyMs")
        max_mem = policy.get("maxMemoryMb")
        max_labeled = policy.get("maxLabeledExamples")
        max_cost = policy.get("maxTotalCost")
        horizon = policy.get("horizonRequests")

        is_valid_policy = (
            isinstance(min_quality, (int, float))
            and not isinstance(min_quality, bool)
            and 0.0 <= min_quality <= 1.0
            and isinstance(freshness_req, bool)
            and isinstance(max_lat, (int, float))
            and not isinstance(max_lat, bool)
            and max_lat >= 0
            and isinstance(max_mem, (int, float))
            and not isinstance(max_mem, bool)
            and max_mem >= 0
            and isinstance(max_labeled, int)
            and not isinstance(max_labeled, bool)
            and max_labeled >= 0
            and isinstance(max_cost, (int, float))
            and not isinstance(max_cost, bool)
            and max_cost >= 0
            and isinstance(horizon, int)
            and not isinstance(horizon, bool)
            and horizon >= 0
        )

        cand_map: Dict[str, Dict[str, Any]] = {}
        for c in candidates:
            if isinstance(c, dict) and isinstance(c.get("name"), str):
                cand_map[c["name"]] = c

        total_costs: Dict[str, Optional[float]] = {}
        reason_codes: Dict[str, List[str]] = {}
        eligible_candidates: List[str] = []

        for name in _ADAPT_PRIORITY:
            c = cand_map.get(name)
            c_reasons: Set[str] = set()
            if not is_valid_policy:
                c_reasons.add("INVALID_INPUT")

            if not c:
                c_reasons.add("INVALID_INPUT")
                total_costs[name] = None
                reason_codes[name] = sorted(list(c_reasons), key=lambda s: s.encode("utf-8"))
                continue

            avail = c.get("available")
            quality = c.get("quality")
            freshness = c.get("freshness")
            lat = c.get("latencyMs")
            mem = c.get("memoryMb")
            labeled = c.get("labeledExamples")
            one_time = c.get("oneTimeCost")
            recurring = c.get("recurringCost")

            if (
                not isinstance(avail, bool)
                or not isinstance(quality, (int, float))
                or isinstance(quality, bool)
                or not (0.0 <= quality <= 1.0)
                or not isinstance(freshness, bool)
                or not isinstance(lat, (int, float))
                or isinstance(lat, bool)
                or lat < 0
                or not isinstance(mem, (int, float))
                or isinstance(mem, bool)
                or mem < 0
                or not isinstance(labeled, int)
                or isinstance(labeled, bool)
                or labeled < 0
                or not isinstance(one_time, (int, float))
                or isinstance(one_time, bool)
                or one_time < 0
                or not isinstance(recurring, (int, float))
                or isinstance(recurring, bool)
                or recurring < 0
            ):
                c_reasons.add("INVALID_INPUT")
                total_costs[name] = None
            else:
                tot_cost = round(float(one_time) + float(horizon) * float(recurring), 12)
                total_costs[name] = tot_cost

                if not avail:
                    c_reasons.add("UNAVAILABLE")
                if is_valid_policy:
                    if quality < min_quality:
                        c_reasons.add("QUALITY_FLOOR")
                    if freshness_req and not freshness:
                        c_reasons.add("FRESHNESS_REQUIRED")
                    if lat > max_lat:
                        c_reasons.add("LATENCY_LIMIT")
                    if mem > max_mem:
                        c_reasons.add("MEMORY_LIMIT")
                    if labeled > max_labeled:
                        c_reasons.add("DATA_LIMIT")
                    if tot_cost > max_cost:
                        c_reasons.add("COST_LIMIT")

            sorted_codes = sorted(list(c_reasons), key=lambda s: s.encode("utf-8"))
            reason_codes[name] = sorted_codes
            if not sorted_codes:
                eligible_candidates.append(name)

        selected = eligible_candidates[0] if eligible_candidates else None
        return 200, {
            "selected": selected,
            "eligible": eligible_candidates,
            "totalCosts": total_costs,
            "reasonCodes": reason_codes,
        }

    else:
        # Operation 2: repair
        tokens = body.get("tokens")
        tmpl_count = body.get("templateApplications")
        params = body.get("parameters")
        allowed_targets = body.get("allowedTargets")
        inf_mode = body.get("inferenceMode")
        train_ids = body.get("trainRowIds")
        eval_ids = body.get("evalRowIds")
        dropout_eval = body.get("dropoutActiveDuringEval")
        artifact_files = body.get("artifactFiles")
        base_rev = body.get("baseRevision")
        data_dig = body.get("datasetDigest")
        code_dig = body.get("codeDigest")
        cfg_dig = body.get("configDigest")
        exp_digs = body.get("expectedDigests")
        micro_b = body.get("microBatch")
        grad_acc = body.get("gradientAccumulation")
        replicas = body.get("replicas")
        exp_eff_b = body.get("expectedEffectiveBatch")
        checkpoint = body.get("checkpoint")
        uninterrupted = body.get("uninterruptedWeights")
        resumed = body.get("resumedWeights")
        res_tol = body.get("resumeTolerance")

        reasons: Set[str] = set()

        # Token verification & Loss labeling
        labels: List[int] = []
        tokens_valid = isinstance(tokens, list) and len(tokens) > 0
        if tokens_valid:
            for tok in tokens:
                if not isinstance(tok, dict):
                    tokens_valid = False
                    break
                t_id = tok.get("id")
                role = tok.get("role")
                padding = tok.get("padding")
                text = tok.get("text")
                if (
                    not isinstance(t_id, int)
                    or isinstance(t_id, bool)
                    or not _is_safe_integer(t_id)
                    or role not in ("system", "user", "assistant")
                    or not isinstance(padding, bool)
                    or not isinstance(text, str)
                ):
                    tokens_valid = False
                    break

        if not tokens_valid:
            reasons.add("INVALID_TOKEN")
            labels = [-100] * (len(tokens) if isinstance(tokens, list) else 0)
        else:
            for tok in tokens:
                if tok["role"] == "assistant" and not tok["padding"]:
                    labels.append(tok["id"])
                else:
                    labels.append(-100)

        # Template count
        template_pass = True
        if tmpl_count != 1:
            reasons.add("CHAT_TEMPLATE_COUNT")
            template_pass = False

        # Parameters & PEFT Config
        trainable_params: List[str] = []
        trainable_count = 0
        peft_config_pass = True

        params_valid = (
            isinstance(params, list)
            and isinstance(allowed_targets, list)
            and len(allowed_targets) > 0
            and all(isinstance(target, str) and target for target in allowed_targets)
            and len(set(allowed_targets)) == len(allowed_targets)
        )

        seen_param_names = set()
        if params_valid:
            for p in params:
                if not isinstance(p, dict):
                    params_valid = False
                    break
                p_name = p.get("name")
                target = p.get("target")
                numel = p.get("numel")
                if (
                    not isinstance(p_name, str)
                    or p_name in seen_param_names
                    or not isinstance(target, str)
                    or not isinstance(numel, int)
                    or isinstance(numel, bool)
                    or not _is_safe_integer(numel, minimum=1)
                ):
                    params_valid = False
                    break
                seen_param_names.add(p_name)
                if target in allowed_targets and (p_name.endswith(".lora_A.weight") or p_name.endswith(".lora_B.weight")):
                    trainable_params.append(p_name)
                    trainable_count += numel

        if not params_valid or len(trainable_params) == 0:
            reasons.add("INVALID_PARAMETER")
            peft_config_pass = False
        else:
            trainable_params = sorted(trainable_params, key=lambda s: s.encode("utf-8"))

        # Inference mode
        if inf_mode is not False:
            reasons.add("INFERENCE_MODE")

        # Artifact files
        expected_artifacts = ["adapter_config.json", "adapter_model.safetensors"]
        if not isinstance(artifact_files, list) or sorted(artifact_files) != sorted(expected_artifacts):
            reasons.add("ADAPTER_FILE_SET")
        if isinstance(artifact_files, list) and any(
            isinstance(f, str) and (f in ("model.safetensors", "pytorch_model.bin") or f.endswith((".bin", ".pt", ".pth", ".pkl", ".pickle")))
            and f != "adapter_model.safetensors" and not f.startswith("adapter_")
            for f in artifact_files
        ):
            reasons.add("FULL_MODEL_ARTIFACT")

        # Always return the expected canonical sorted adapter file list
        sorted_adapter_files = sorted(expected_artifacts, key=lambda s: s.encode("utf-8"))

        # Base revision
        if not isinstance(base_rev, str) or not re.match(r"^[0-9a-f]{40}$", base_rev):
            reasons.add("MUTABLE_BASE_REVISION")

        # Digests
        lineage_pass = True
        if not (
            isinstance(exp_digs, dict)
            and isinstance(data_dig, str)
            and isinstance(code_dig, str)
            and isinstance(cfg_dig, str)
            and exp_digs.get("dataset") == data_dig
            and exp_digs.get("code") == code_dig
            and exp_digs.get("config") == cfg_dig
            and bool(re.match(r"^[0-9a-f]{64}$", data_dig))
            and bool(re.match(r"^[0-9a-f]{64}$", code_dig))
            and bool(re.match(r"^[0-9a-f]{64}$", cfg_dig))
        ):
            reasons.add("LINEAGE_MISMATCH")
            lineage_pass = False

        # Batch check
        if not (
            isinstance(micro_b, int)
            and not isinstance(micro_b, bool)
            and _is_safe_integer(micro_b, minimum=1)
            and isinstance(grad_acc, int)
            and not isinstance(grad_acc, bool)
            and _is_safe_integer(grad_acc, minimum=1)
            and isinstance(replicas, int)
            and not isinstance(replicas, bool)
            and _is_safe_integer(replicas, minimum=1)
            and isinstance(exp_eff_b, int)
            and not isinstance(exp_eff_b, bool)
            and _is_safe_integer(exp_eff_b, minimum=1)
            and micro_b * grad_acc * replicas == exp_eff_b
        ):
            reasons.add("EFFECTIVE_BATCH_MISMATCH")

        # Eval Isolation & Dropout
        eval_isolated = True
        if not (
            isinstance(train_ids, list)
            and len(train_ids) > 0
            and isinstance(eval_ids, list)
            and len(eval_ids) > 0
            and all(isinstance(row_id, str) and row_id for row_id in train_ids)
            and all(isinstance(row_id, str) and row_id for row_id in eval_ids)
            and len(set(train_ids)) == len(train_ids)
            and len(set(eval_ids)) == len(eval_ids)
            and len(set(train_ids) & set(eval_ids)) == 0
        ):
            reasons.add("EVAL_LEAKAGE")
            eval_isolated = False

        if dropout_eval is not False:
            reasons.add("EVAL_DROPOUT_ACTIVE")

        # Checkpoint completeness
        req_checkpoint_keys = {"model", "optimizer", "scheduler", "step", "rng", "dataPosition"}
        checkpoint_complete = True
        if not isinstance(checkpoint, dict) or not req_checkpoint_keys.issubset(set(checkpoint.keys())):
            reasons.add("INCOMPLETE_CHECKPOINT")
            checkpoint_complete = False

        # Resume tolerance
        resume_pass = True
        if not (
            isinstance(uninterrupted, list)
            and isinstance(resumed, list)
            and len(uninterrupted) == len(resumed)
            and len(uninterrupted) > 0
            and isinstance(res_tol, (int, float))
            and not isinstance(res_tol, bool)
            and math.isfinite(res_tol)
            and res_tol >= 0
        ):
            reasons.add("RESUME_DIVERGENCE")
            resume_pass = False
        else:
            for u_w, r_w in zip(uninterrupted, resumed):
                if (
                    not isinstance(u_w, (int, float))
                    or isinstance(u_w, bool)
                    or math.isnan(u_w)
                    or math.isinf(u_w)
                    or not isinstance(r_w, (int, float))
                    or isinstance(r_w, bool)
                    or math.isnan(r_w)
                    or math.isinf(r_w)
                    or abs(u_w - r_w) > res_tol
                ):
                    reasons.add("RESUME_DIVERGENCE")
                    resume_pass = False
                    break

        sorted_reasons = sorted(list(reasons), key=lambda s: s.encode("utf-8"))
        # Strictly determine boolean flags from violation reasons per contract
        template_pass = "CHAT_TEMPLATE_COUNT" not in reasons
        peft_config_pass = not bool({"INVALID_PARAMETER", "INFERENCE_MODE", "FULL_MODEL_ARTIFACT", "ADAPTER_FILE_SET"} & reasons)
        checkpoint_complete = "INCOMPLETE_CHECKPOINT" not in reasons
        lineage_pass = not bool({"MUTABLE_BASE_REVISION", "LINEAGE_MISMATCH"} & reasons)
        eval_isolated = not bool({"EVAL_LEAKAGE", "EVAL_DROPOUT_ACTIVE"} & reasons)
        evaluation_deterministic = "EFFECTIVE_BATCH_MISMATCH" not in reasons
        resume_pass = "RESUME_DIVERGENCE" not in reasons

        return 200, {
            "labels": labels,
            "templatePass": template_pass,
            "trainableParams": trainable_params,
            "trainableCount": trainable_count,
            "peftConfigPass": peft_config_pass,
            "adapterFiles": sorted_adapter_files,
            "checkpointComplete": checkpoint_complete,
            "lineagePass": lineage_pass,
            "evalIsolated": eval_isolated,
            "evaluationDeterministic": evaluation_deterministic,
            "resumePass": resume_pass,
            "reasonCodes": sorted_reasons,
        }


# ===========================================================================
# 5. POST /quantize
# ===========================================================================
class QuantizeStore:
    """Thread-safe multi-tenant store for frozen quantization candidates."""

    def __init__(self) -> None:
        self._frozen: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._inputs: Dict[Tuple[str, str], str] = {}

    def get_freeze(self, tenant: str, freeze_id: str) -> Optional[Dict[str, Any]]:
        return self._frozen.get((tenant, freeze_id))

    def record_freeze(self, tenant: str, freeze_id: str, input_json: str, response: Dict[str, Any]) -> None:
        self._frozen[(tenant, freeze_id)] = response
        self._inputs[(tenant, freeze_id)] = input_json

    def check_conflict(self, tenant: str, freeze_id: str, input_json: str) -> bool:
        key = (tenant, freeze_id)
        if key in self._inputs:
            return self._inputs[key] != input_json
        return False


_QUANTIZE_STORE = QuantizeStore()


def quantize_decision(body: Any, store: Optional[QuantizeStore] = None, tenant: str = "") -> Tuple[int, Dict[str, Any]]:
    """Q5 Solver: Quantized Model Candidate Admission Gate."""
    st = store or _QUANTIZE_STORE
    if not isinstance(body, dict):
        return 400, {"error": "INVALID_INPUT"}
    phase = body.get("phase")
    if phase not in ("freeze", "select"):
        return 400, {"error": "INVALID_INPUT"}

    if phase == "freeze":
        freeze_id = body.get("freezeId")
        calib_dig = body.get("calibrationDigest")
        tok_dig = body.get("tokenizerDigest")
        allowed_unsupported = body.get("allowedUnsupportedReasons")
        candidates = body.get("candidates")

        # Per exam specification line 538:
        # "Unknown or missing phase, an empty/non-array freeze candidate list,
        # or a select request without array candidates and rows plus an object policy
        # returns HTTP 400 with exactly {"error":"INVALID_INPUT"}."
        if not isinstance(candidates, list) or len(candidates) == 0:
            return 400, {"error": "INVALID_INPUT"}

        freeze_id_str = str(freeze_id) if isinstance(freeze_id, str) else ""
        calib_dig_str = str(calib_dig) if isinstance(calib_dig, str) else ""
        tok_dig_str = str(tok_dig) if isinstance(tok_dig, str) else ""

        input_canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))

        # Replay / conflict check for valid freezeId
        if freeze_id_str and 1 <= len(freeze_id_str) <= 128:
            if st.check_conflict(tenant, freeze_id_str, input_canonical):
                return 409, {"error": "FREEZE_ID_CONFLICT"}
            if st.get_freeze(tenant, freeze_id_str) is not None:
                return 200, st.get_freeze(tenant, freeze_id_str)  # type: ignore

        if isinstance(allowed_unsupported, list):
            allowed_unsupported_set = {str(r) for r in allowed_unsupported if isinstance(r, str) and r}
        else:
            allowed_unsupported_set = set()

        frozen_candidates = []
        seen_cand_names = set()

        for cand in candidates:
            if not isinstance(cand, dict):
                frozen_candidates.append({
                    "name": "invalid",
                    "status": "invalid",
                    "inventory": [],
                    "totalBytes": None,
                    "packageDigest": None,
                    "reasonCodes": ["INVALID_INPUT"],
                })
                continue

            c_name = cand.get("name")
            c_name_str = str(c_name) if isinstance(c_name, str) and c_name else "invalid"
            is_name_dup = c_name_str in seen_cand_names
            seen_cand_names.add(c_name_str)

            files = cand.get("files")
            loadable = cand.get("loadable")
            c_calib = cand.get("calibrationDigest")
            c_tok = cand.get("tokenizerDigest")
            unsupp_reason = cand.get("unsupportedReason")

            reasons: Set[str] = set()

            inventory = []
            total_bytes: Optional[int] = 0
            package_digest: Optional[str] = None

            if not isinstance(files, dict) or len(files) == 0:
                reasons.add("INVALID_INPUT")
                inventory = []
                total_bytes = None
                package_digest = None
            else:
                files_valid = True
                for f_name, f_content in files.items():
                    if not isinstance(f_name, str) or not isinstance(f_content, str):
                        files_valid = False
                        break
                    raw_bytes = f_content.encode("utf-8")
                    inventory.append({
                        "name": f_name,
                        "bytes": len(raw_bytes),
                        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
                    })
                if not files_valid:
                    reasons.add("INVALID_INPUT")
                    inventory = []
                    total_bytes = None
                    package_digest = None
                else:
                    inventory = sorted(inventory, key=lambda x: x["name"].encode("utf-8"))
                    total_bytes = sum(item["bytes"] for item in inventory)
                    compact_inv = json.dumps(inventory, separators=(",", ":"), ensure_ascii=False)
                    package_digest = hashlib.sha256(compact_inv.encode("utf-8")).hexdigest()

            # Candidate-specific validation (skip loadable/calib/tok for unsupported candidates)
            if unsupp_reason is not None:
                if unsupp_reason not in allowed_unsupported_set:
                    reasons.add("UNALLOWED_UNSUPPORTED_REASON")
            else:
                if loadable is not True:
                    reasons.add("NOT_LOADABLE")
                if c_calib != calib_dig_str or not calib_dig_str:
                    reasons.add("CALIBRATION_MISMATCH")
                if c_tok != tok_dig_str or not tok_dig_str:
                    reasons.add("TOKENIZER_MISMATCH")

            if is_name_dup or not isinstance(c_name, str) or not c_name:
                reasons.add("INVALID_INPUT")

            if not freeze_id_str or len(freeze_id_str) > 128:
                reasons.add("INVALID_INPUT")

            # Final status: reasons > unsupported > frozen
            if reasons:
                status = "invalid"
            elif unsupp_reason is not None:
                status = "unsupported"
            else:
                status = "frozen"

            sorted_codes = sorted(list(reasons), key=lambda s: s.encode("utf-8"))
            frozen_candidates.append({
                "name": c_name_str,
                "status": status,
                "inventory": inventory,
                "totalBytes": total_bytes,
                "packageDigest": package_digest,
                "reasonCodes": sorted_codes,
            })

        frozen_candidates = sorted(frozen_candidates, key=lambda c: c["name"].encode("utf-8"))

        resp = {
            "freezeId": freeze_id_str,
            "candidates": frozen_candidates,
        }
        if freeze_id_str and 1 <= len(freeze_id_str) <= 128:
            st.record_freeze(tenant, freeze_id_str, input_canonical, resp)
        return 200, resp

    else:
        # Phase 2: select
        freeze_id = body.get("freezeId")
        candidates = body.get("candidates")
        policy = body.get("policy")
        latencies = body.get("latencies")
        rows = body.get("rows")

        # Per exam specification line 538:
        # "a select request without array candidates and rows plus an object policy
        # returns HTTP 400 with exactly {"error":"INVALID_INPUT"}."
        if not (
            isinstance(candidates, list)
            and isinstance(rows, list)
            and isinstance(policy, dict)
        ):
            return 400, {"error": "INVALID_INPUT"}

        freeze_id_str = str(freeze_id) if isinstance(freeze_id, str) else ""

        max_bytes = policy.get("maxBytes")
        agg_floor = policy.get("aggregateFloor")
        req_slices = policy.get("requiredSlices")
        max_lat = policy.get("maxLatencyMs")
        cand_order = policy.get("candidateOrder")

        is_valid_policy = (
            _is_safe_integer(max_bytes)
            and isinstance(agg_floor, (int, float))
            and not isinstance(agg_floor, bool)
            and math.isfinite(agg_floor)
            and 0.0 <= agg_floor <= 1.0
            and isinstance(req_slices, dict)
            and all(isinstance(name, str) and name and isinstance(floor, (int, float))
                    and not isinstance(floor, bool) and math.isfinite(floor) and 0.0 <= floor <= 1.0
                    for name, floor in req_slices.items())
            and isinstance(max_lat, (int, float))
            and not isinstance(max_lat, bool)
            and math.isfinite(max_lat)
            and max_lat >= 0
            and isinstance(cand_order, list)
            and len(cand_order) > 0
            and all(isinstance(name, str) and name for name in cand_order)
            and len(set(cand_order)) == len(cand_order)
            and isinstance(latencies, dict)
        )

        stored_freeze = st.get_freeze(tenant, freeze_id_str) if freeze_id_str else None
        if stored_freeze is not None and isinstance(candidates, list):
            stored_by_name = {c["name"]: c for c in stored_freeze["candidates"] if isinstance(c, dict) and "name" in c}
            input_by_name = {c["name"]: c for c in candidates if isinstance(c, dict) and "name" in c}
            is_lineage_valid = (len(input_by_name) == len(candidates)
                and set(stored_by_name.keys()) == set(input_by_name.keys()) and
                all(json.dumps(stored_by_name[n], sort_keys=True) == json.dumps(input_by_name[n], sort_keys=True)
                    for n in stored_by_name))
        else:
            stored_by_name = {}
            is_lineage_valid = False

        results = []
        admitted_candidates = []
        cand_order_list = cand_order if isinstance(cand_order, list) else []
        if is_valid_policy and {candidate.get("name") for candidate in candidates if isinstance(candidate, dict)} != set(cand_order_list):
            is_valid_policy = False

        for cand in candidates:
            if not isinstance(cand, dict):
                continue
            c_name = cand.get("name")
            if not isinstance(c_name, str):
                continue

            reasons: Set[str] = set()

            if not is_valid_policy:
                reasons.add("INVALID_POLICY")
            if not is_lineage_valid:
                reasons.add("INVALID_LINEAGE")
            if stored_freeze is None:
                reasons.add("NOT_FROZEN")

            if cand.get("status") != "frozen":
                reasons.add("NOT_FROZEN")

            inv = cand.get("inventory")
            c_total_bytes = None
            c_pkg_dig = None
            if isinstance(inv, list):
                try:
                    norm_inv = [{"name": item["name"], "bytes": item["bytes"], "sha256": item["sha256"]} for item in inv]
                    norm_inv = sorted(norm_inv, key=lambda x: x["name"].encode("utf-8"))
                    c_total_bytes = sum(item["bytes"] for item in norm_inv)
                    compact_inv = json.dumps(norm_inv, separators=(",", ":"), ensure_ascii=False)
                    c_pkg_dig = hashlib.sha256(compact_inv.encode("utf-8")).hexdigest()
                except Exception:
                    pass

            manifest_valid = True
            if c_pkg_dig != cand.get("packageDigest") or c_total_bytes != cand.get("totalBytes") or c_pkg_dig is None:
                reasons.add("INVALID_MANIFEST")
                manifest_valid = False

            c_lat = latencies.get(c_name) if isinstance(latencies, dict) else None
            lat_valid = True
            if not (
                isinstance(c_lat, (int, float))
                and not isinstance(c_lat, bool)
                and not math.isnan(c_lat)
                and not math.isinf(c_lat)
                and c_lat >= 0
            ):
                reasons.add("INVALID_POLICY")
                lat_valid = False
                c_lat = None

            if is_valid_policy and c_total_bytes is not None and max_bytes is not None and c_total_bytes > max_bytes:
                reasons.add("SIZE_LIMIT")
            if is_valid_policy and c_lat is not None and max_lat is not None and c_lat > max_lat:
                reasons.add("LATENCY_LIMIT")

            rows_valid = len(rows) > 0
            for r in rows:
                if not isinstance(r, dict):
                    rows_valid = False
                    break
                lbl = r.get("label")
                preds = r.get("predictions")
                sl = r.get("slice")
                if (
                    lbl not in (0, 1)
                    or not isinstance(preds, dict)
                    or preds.get(c_name) not in (0, 1)
                    or not isinstance(sl, str)
                ):
                    rows_valid = False
                    break

            c_agg = None
            c_slices: Dict[str, Any] = {}

            if not rows_valid:
                reasons.add("INVALID_PREDICTIONS")
                if is_valid_policy and isinstance(req_slices, dict):
                    c_slices = {s_name: None for s_name in req_slices}
            else:
                corr = sum(1 for r in rows if r["label"] == r["predictions"].get(c_name))
                c_agg = round(corr / len(rows), 12)
                if is_valid_policy and agg_floor is not None and c_agg < agg_floor:
                    reasons.add("AGGREGATE_FLOOR")

                sl_map: Dict[str, List[Dict[str, Any]]] = {}
                for r in rows:
                    sl_map.setdefault(r["slice"], []).append(r)

                if is_valid_policy and isinstance(req_slices, dict):
                    for sl_name, sl_fl in req_slices.items():
                        if sl_name not in sl_map:
                            reasons.add(f"MISSING_SLICE:{sl_name}")
                        else:
                            sub_rows = sl_map[sl_name]
                            sub_corr = sum(1 for r in sub_rows if r["label"] == r["predictions"].get(c_name))
                            sl_acc = round(sub_corr / len(sub_rows), 12)
                            c_slices[sl_name] = sl_acc
                            if sl_acc < sl_fl:
                                reasons.add(f"SLICE_FLOOR:{sl_name}")

            admitted = len(reasons) == 0 and cand.get("status") == "frozen"
            sorted_codes = sorted(list(reasons), key=lambda s: s.encode("utf-8"))

            res_item = {
                "name": c_name,
                "aggregate": c_agg,
                "slices": c_slices,
                "totalBytes": c_total_bytes if manifest_valid else None,
                "latencyMs": c_lat if lat_valid else None,
                "admitted": admitted,
                "reasonCodes": sorted_codes,
            }
            results.append(res_item)
            if admitted:
                admitted_candidates.append((c_name, c_total_bytes, c_lat, cand))

        def _res_sort_key(item: Dict[str, Any]) -> Tuple[int, bytes]:
            name = item["name"]
            if name in cand_order_list:
                return (cand_order_list.index(name), b"")
            return (9999, name.encode("utf-8"))

        results = sorted(results, key=_res_sort_key)

        selected_winner = None
        winner_manifest = None

        if admitted_candidates:
            def _winner_sort_key(t: Tuple[str, Any, Any, Any]) -> Tuple[int, float, int]:
                name, tb, lat, _ = t
                order_idx = cand_order_list.index(name) if name in cand_order_list else 9999
                return (tb or 0, float(lat or 0), order_idx)

            sorted_admitted = sorted(admitted_candidates, key=_winner_sort_key)
            selected_winner = sorted_admitted[0][0]
            if stored_freeze is not None:
                winner_manifest = stored_by_name.get(selected_winner)
            else:
                winner_manifest = sorted_admitted[0][3]

        return 200, {
            "freezeId": freeze_id_str,
            "selected": selected_winner,
            "results": results,
            "packageManifest": winner_manifest,
        }


# ===========================================================================
# 6. POST /pipeline
# ===========================================================================
_DAG_NODES = ["verify_data", "prepare", "train", "evaluate", "register", "publish"]


class PipelineStore:
    """Thread-safe multi-tenant store for content-addressed pipeline sessions."""

    def __init__(self) -> None:
        self._sessions: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def get_session(self, tenant: str, session_id: str) -> Dict[str, Any]:
        key = (tenant, session_id)
        if key not in self._sessions:
            self._sessions[key] = {
                "revision": 0,
                "inputs": {},
                "cache": {},
                "node_state": {},
                "seen_events": {},
            }
        return self._sessions[key]


_PIPELINE_STORE = PipelineStore()


def pipeline_decision(body: Any, store: Optional[PipelineStore] = None, tenant: str = "") -> Tuple[int, Dict[str, Any]]:
    """Q6 Solver: Content-Addressed ML Pipeline Controller."""
    st = store or _PIPELINE_STORE
    if not isinstance(body, dict):
        return 400, {"error": "INVALID_REQUEST"}

    session_id = body.get("session")
    revision = body.get("revision")
    inputs = body.get("inputs")
    events = body.get("events")

    if (
        not isinstance(session_id, str)
        or not session_id
        or not isinstance(revision, int)
        or isinstance(revision, bool)
        or not _is_safe_integer(revision, minimum=1)
        or not isinstance(inputs, dict)
        or not isinstance(events, list)
    ):
        return 400, {"error": "INVALID_REQUEST"}

    req_input_keys = {
        "generation", "checksum", "canonicalData", "prepareCode", "prepareConfig",
        "trainCode", "trainConfig", "runtime", "evaluateCode", "evaluateConfig",
        "schemaDigest", "publishConfig"
    }
    if not req_input_keys.issubset(set(inputs.keys())) or any(not isinstance(inputs[k], str) or not inputs[k] for k in req_input_keys):
        return 400, {"error": "INVALID_REQUEST"}

    input_canon = json.dumps(inputs, sort_keys=True, separators=(",", ":"))
    session = st.get_session(tenant, session_id)
    next_revision = session["revision"]
    next_inputs = session["inputs"]
    next_node_state = dict(session["node_state"])
    if revision == session["revision"]:
        if session["inputs"] and session["inputs"] != input_canon:
            return 409, {"error": "REVISION_CONFLICT"}
    elif revision > session["revision"]:
        # Do not mutate persistent state until the whole event batch succeeds.
        next_revision = revision
        next_inputs = input_canon
        next_node_state = {}

    # Work on shallow copies of state for transactional atomic processing (rollback on 409)
    cache = dict(session["cache"])
    node_state = next_node_state
    seen_events = dict(session["seen_events"])

    def _hash_arr(arr: List[Any]) -> str:
        return hashlib.sha256(json.dumps(arr, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()

    def _compute_dag_keys(cur_cache: Dict[str, Any]) -> Dict[str, Optional[str]]:
        keys: Dict[str, Optional[str]] = {}
        vk = _hash_arr([inputs["generation"], inputs["checksum"]])
        keys["verify_data"] = vk

        pk = _hash_arr([inputs["canonicalData"], inputs["prepareCode"], inputs["prepareConfig"]])
        keys["prepare"] = pk if vk in cur_cache else None

        if keys["prepare"] is not None and pk in cur_cache:
            tk = _hash_arr([cur_cache[pk]["artifactDigest"], inputs["trainCode"], inputs["trainConfig"], inputs["runtime"]])
        else:
            tk = None
        keys["train"] = tk

        if tk is not None and tk in cur_cache:
            ek = _hash_arr([cur_cache[tk]["artifactDigest"], inputs["canonicalData"], inputs["evaluateCode"], inputs["evaluateConfig"]])
        else:
            ek = None
        keys["evaluate"] = ek

        if ek is not None and ek in cur_cache:
            rk = _hash_arr([cur_cache[ek]["artifactDigest"], inputs["schemaDigest"]])
        else:
            rk = None
        keys["register"] = rk

        if rk is not None and rk in cur_cache:
            pub_k = _hash_arr([cur_cache[rk]["artifactDigest"], inputs["publishConfig"]])
        else:
            pub_k = None
        keys["publish"] = pub_k
        return keys

    accepted_event_ids: List[str] = []
    ignored_event_ids: List[str] = []

    for ev in events:
        if not isinstance(ev, dict):
            return 409, {"error": "INVALID_EVENT"}

        ev_id = ev.get("eventId")
        ev_rev = ev.get("revision")
        ev_node = ev.get("node")
        ev_att = ev.get("attempt")
        ev_status = ev.get("status")
        ev_key = ev.get("key")
        ev_art = ev.get("artifactDigest")
        ev_receipt = ev.get("receiptId")

        if (
            not isinstance(ev_id, str)
            or not ev_id
            or not _is_safe_integer(ev_rev, minimum=1)
            or ev_node not in _DAG_NODES
            or not _is_safe_integer(ev_att, minimum=1)
            or ev_status not in ("started", "succeeded", "retryable_failed", "terminal_failed")
            or not isinstance(ev_key, str)
            or set(ev.keys()) != {"eventId", "revision", "node", "attempt", "status", "key", "artifactDigest", "receiptId"}
        ):
            return 409, {"error": "INVALID_EVENT"}

        ev_canon = json.dumps(ev, sort_keys=True, separators=(",", ":"))
        if ev_id in seen_events:
            if seen_events[ev_id] == ev_canon:
                ignored_event_ids.append(ev_id)
                continue
            else:
                return 409, {"error": "EVENT_ID_CONFLICT"}

        if ev_rev != next_revision:
            ignored_event_ids.append(ev_id)
            continue

        # Recompute DAG keys dynamically to check readiness with latest cache
        dyn_keys = _compute_dag_keys(cache)
        curr_node_key = dyn_keys.get(ev_node)
        if curr_node_key is None or curr_node_key != ev_key:
            ignored_event_ids.append(ev_id)
            continue

        if ev_status == "succeeded":
            if not isinstance(ev_art, str) or not ev_art:
                ignored_event_ids.append(ev_id)
                continue
            if ev_node in ("register", "publish"):
                if ev_receipt != f"receipt:{ev_node}:{ev_key}":
                    ignored_event_ids.append(ev_id)
                    continue
            else:
                if ev_receipt is not None:
                    ignored_event_ids.append(ev_id)
                    continue
        else:
            if ev_art is not None or ev_receipt is not None:
                ignored_event_ids.append(ev_id)
                continue

        curr_state = node_state.get(ev_node)

        if curr_state is None:
            if ev_status == "started" and ev_att == 1:
                node_state[ev_node] = {"status": "started", "attempt": 1, "key": ev_key, "eventId": ev_id}
                seen_events[ev_id] = ev_canon
                accepted_event_ids.append(ev_id)
            else:
                ignored_event_ids.append(ev_id)
        elif curr_state["status"] == "started":
            if ev_att == curr_state["attempt"] and ev_status in ("succeeded", "retryable_failed", "terminal_failed"):
                node_state[ev_node] = {"status": ev_status, "attempt": ev_att, "key": ev_key, "eventId": ev_id}
                seen_events[ev_id] = ev_canon
                accepted_event_ids.append(ev_id)
                if ev_status == "succeeded":
                    if ev_key in cache:
                        if cache[ev_key]["artifactDigest"] != ev_art:
                            return 409, {"error": "EVIDENCE_CONFLICT"}
                    else:
                        cache[ev_key] = {"artifactDigest": ev_art, "eventId": ev_id}
            elif ev_att < curr_state["attempt"]:
                ignored_event_ids.append(ev_id)
            else:
                return 409, {"error": "STATUS_CONFLICT"}
        elif curr_state["status"] == "retryable_failed":
            if ev_status == "started" and ev_att == curr_state["attempt"] + 1:
                node_state[ev_node] = {"status": "started", "attempt": ev_att, "key": ev_key, "eventId": ev_id}
                seen_events[ev_id] = ev_canon
                accepted_event_ids.append(ev_id)
            elif ev_att <= curr_state["attempt"]:
                ignored_event_ids.append(ev_id)
            else:
                return 409, {"error": "STATUS_CONFLICT"}
        elif curr_state["status"] == "succeeded":
            curr_key = curr_state.get("key")
            if ev_status == "succeeded":
                if curr_key and curr_key in cache and ev_art != cache[curr_key]["artifactDigest"]:
                    return 409, {"error": "EVIDENCE_CONFLICT"}
                else:
                    ignored_event_ids.append(ev_id)
            else:
                return 409, {"error": "STATUS_CONFLICT"}
        elif curr_state["status"] == "terminal_failed":
            return 409, {"error": "STATUS_CONFLICT"}

    # Commit state changes transactionally on success
    session["revision"] = next_revision
    session["inputs"] = next_inputs
    session["cache"] = cache
    session["node_state"] = node_state
    session["seen_events"] = seen_events

    # Final DAG keys after batch processing
    node_keys = _compute_dag_keys(cache)

    response_nodes = []
    has_terminal_upstream = False
    has_pending_upstream = False

    # Build dependency digests per node (named inputs + cacheKey)
    node_dep_digests: Dict[str, Dict[str, Any]] = {}
    node_dep_digests["verify_data"] = {
        "generation": inputs["generation"],
        "checksum": inputs["checksum"],
        "cacheKey": node_keys["verify_data"],
    }
    node_dep_digests["prepare"] = {
        "canonicalData": inputs["canonicalData"],
        "prepareCode": inputs["prepareCode"],
        "prepareConfig": inputs["prepareConfig"],
        "cacheKey": node_keys["prepare"],
    }
    # train depends on prepare artifact
    prep_art = cache[node_keys["prepare"]]["artifactDigest"] if (node_keys["prepare"] and node_keys["prepare"] in cache) else None
    node_dep_digests["train"] = {
        "prepareArtifact": prep_art,
        "trainCode": inputs["trainCode"],
        "trainConfig": inputs["trainConfig"],
        "runtime": inputs["runtime"],
        "cacheKey": node_keys["train"],
    }
    train_art = cache[node_keys["train"]]["artifactDigest"] if (node_keys["train"] and node_keys["train"] in cache) else None
    node_dep_digests["evaluate"] = {
        "trainArtifact": train_art,
        "canonicalData": inputs["canonicalData"],
        "evaluateCode": inputs["evaluateCode"],
        "evaluateConfig": inputs["evaluateConfig"],
        "cacheKey": node_keys["evaluate"],
    }
    eval_art = cache[node_keys["evaluate"]]["artifactDigest"] if (node_keys["evaluate"] and node_keys["evaluate"] in cache) else None
    node_dep_digests["register"] = {
        "evaluateArtifact": eval_art,
        "schemaDigest": inputs["schemaDigest"],
        "cacheKey": node_keys["register"],
    }
    reg_art = cache[node_keys["register"]]["artifactDigest"] if (node_keys["register"] and node_keys["register"] in cache) else None
    node_dep_digests["publish"] = {
        "registerArtifact": reg_art,
        "publishConfig": inputs["publishConfig"],
        "cacheKey": node_keys["publish"],
    }

    for node in _DAG_NODES:
        key = node_keys.get(node)
        dep_digests = node_dep_digests[node]
        triggering_events: List[str] = []

        if has_terminal_upstream:
            action = "block"
            reason = "UPSTREAM_TERMINAL"
        elif has_pending_upstream:
            action = "block"
            reason = "UPSTREAM_PENDING"
        else:
            state = session["node_state"].get(node)
            if key is not None and key in cache:
                action = "reuse"
                reason = "CACHE_HIT"
                triggering_events = [cache[key]["eventId"]]
            elif state is not None and state["status"] == "started":
                action = "block"
                reason = "RUNNING"
                triggering_events = [state["eventId"]]
                has_pending_upstream = True
            elif state is not None and state["status"] == "retryable_failed":
                action = "rerun"
                reason = "RETRYABLE_FAILURE"
                triggering_events = [state["eventId"]]
                has_pending_upstream = True
            elif state is not None and state["status"] == "terminal_failed":
                action = "block"
                reason = "TERMINAL_FAILURE"
                triggering_events = [state["eventId"]]
                has_terminal_upstream = True
            else:
                action = "rerun"
                reason = "CACHE_MISS"
                has_pending_upstream = True

        response_nodes.append({
            "node": node,
            "action": action,
            "reasonCodes": [reason],
            "dependencyDigests": dep_digests,
            "triggeringEventIds": triggering_events,
        })

    return 200, {
        "revision": session["revision"],
        "acceptedEventIds": accepted_event_ids,
        "ignoredEventIds": ignored_event_ids,
        "nodes": response_nodes,
    }


# ===========================================================================
# 7. POST /verify-bundle
# ===========================================================================
_UNSAFE_EXTENSIONS = {".bin", ".pt", ".pth", ".pkl", ".pickle"}
_CARD_MARKER_RE = re.compile(r"<!--\s*tds-model-card\s+([\s\S]*?)\s*-->")


def verify_bundle_decision(body: Any) -> Tuple[int, Dict[str, Any]]:
    """Q7 Solver: Verifiable Model Bundle & Model Card Verifier."""
    if not isinstance(body, dict):
        return 400, {"error": "INVALID_INPUT"}
    policy = body.get("policy")
    files = body.get("files")

    if not isinstance(policy, dict) or not isinstance(files, dict):
        return 400, {"error": "INVALID_INPUT"}

    req_slices = policy.get("requiredSlices")
    license_val = policy.get("license")
    intended_use = policy.get("intendedUse")
    limitations = policy.get("limitations")

    violations: Set[str] = set()

    is_valid_policy = (
        isinstance(req_slices, list)
        and len(req_slices) > 0
        and all(isinstance(s, str) and s for s in req_slices)
        and len(set(req_slices)) == len(req_slices)
        and isinstance(license_val, str)
        and bool(license_val)
        and isinstance(intended_use, str)
        and bool(intended_use)
        and isinstance(limitations, str)
        and bool(limitations)
    )

    if not is_valid_policy:
        violations.add("INVALID_POLICY")

    required_filenames = {
        "README.md", "training_manifest.json", "evaluation.json",
        "inventory.json", "adapter_model.safetensors", "adapter_config.json"
    }

    for req_f in required_filenames:
        if req_f not in files:
            violations.add(f"MISSING_FILE:{req_f}")

    for f_name in files.keys():
        if f_name not in required_filenames:
            violations.add("UNTRACKED_FILE")
        for unsafe_ext in _UNSAFE_EXTENSIONS:
            if f_name.endswith(unsafe_ext):
                violations.add("UNSAFE_WEIGHTS")

    recomputed_inventory = []
    for f_name, f_content in files.items():
        if not isinstance(f_content, str):
            violations.add(f"INVALID_FILE:{f_name}")
            continue
        if f_name == "inventory.json":
            continue
        raw_b = f_content.encode("utf-8")
        recomputed_inventory.append({
            "name": f_name,
            "bytes": len(raw_b),
            "sha256": hashlib.sha256(raw_b).hexdigest(),
        })

    recomputed_inventory = sorted(recomputed_inventory, key=lambda x: x["name"].encode("utf-8"))
    inventory_digest = hashlib.sha256(
        json.dumps(recomputed_inventory, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()

    inv_file_raw = files.get("inventory.json")
    if isinstance(inv_file_raw, str):
        try:
            parsed_inv = json.loads(inv_file_raw)
        except Exception:
            violations.add("INVALID_JSON:inventory.json")
            parsed_inv = None

        if parsed_inv is not None:
            # The inventory is itself an immutable artifact: no reordering, whitespace,
            # aliases, extra keys, or normalization is permitted.
            exact_inventory = json.dumps(recomputed_inventory, separators=(",", ":"), ensure_ascii=False)
            if not isinstance(parsed_inv, list) or inv_file_raw != exact_inventory:
                violations.add("INVENTORY_MISMATCH")

    cfg_raw = files.get("adapter_config.json")
    if isinstance(cfg_raw, str):
        try:
            cfg_obj = json.loads(cfg_raw)
            if not isinstance(cfg_obj, dict):
                violations.add("INVALID_ADAPTER_CONFIG")
            else:
                r_val = cfg_obj.get("r")
                t_mods = cfg_obj.get("target_modules")
                if not (
                    isinstance(r_val, int)
                    and not isinstance(r_val, bool)
                    and _is_safe_integer(r_val, minimum=1)
                    and isinstance(t_mods, list)
                    and len(t_mods) > 0
                    and len(set(t_mods)) == len(t_mods)
                    and all(isinstance(m, str) and m for m in t_mods)
                ):
                    violations.add("INVALID_ADAPTER_CONFIG")
        except Exception:
            violations.add("INVALID_JSON:adapter_config.json")

    manifest_obj = None
    manifest_raw = files.get("training_manifest.json")
    if isinstance(manifest_raw, str):
        try:
            manifest_obj = json.loads(manifest_raw)
            if not isinstance(manifest_obj, dict):
                violations.add("INVALID_TRAINING_MANIFEST")
            else:
                req_m_fields = [
                    "task", "baseRevision", "datasetDigest", "codeDigest",
                    "trainingConfigDigest", "modelArtifactDigest", "evaluationArtifactDigest"
                ]
                for fld in req_m_fields:
                    if fld not in manifest_obj:
                        violations.add(f"MISSING_MANIFEST_FIELD:{fld}")

                base_rev = manifest_obj.get("baseRevision")
                if not isinstance(base_rev, str) or not re.match(r"^[0-9a-f]{40}$", base_rev):
                    violations.add("MUTABLE_BASE_REVISION")

                adapter_raw = files.get("adapter_model.safetensors")
                if isinstance(adapter_raw, str):
                    real_model_dig = hashlib.sha256(adapter_raw.encode("utf-8")).hexdigest()
                    if manifest_obj.get("modelArtifactDigest") != real_model_dig:
                        violations.add("MODEL_ARTIFACT_MISMATCH")

                eval_raw = files.get("evaluation.json")
                if isinstance(eval_raw, str):
                    real_eval_dig = hashlib.sha256(eval_raw.encode("utf-8")).hexdigest()
                    if manifest_obj.get("evaluationArtifactDigest") != real_eval_dig:
                        violations.add("EVALUATION_DIGEST_MISMATCH")
        except Exception:
            violations.add("INVALID_JSON:training_manifest.json")

    eval_obj = None
    eval_raw = files.get("evaluation.json")
    if isinstance(eval_raw, str):
        try:
            eval_obj = json.loads(eval_raw)
            if not isinstance(eval_obj, dict):
                violations.add("INVALID_EVALUATION")
            else:
                adapter_raw = files.get("adapter_model.safetensors")
                if isinstance(adapter_raw, str):
                    real_model_dig = hashlib.sha256(adapter_raw.encode("utf-8")).hexdigest()
                    if eval_obj.get("modelArtifactDigest") != real_model_dig:
                        violations.add("EVALUATION_ARTIFACT_MISMATCH")

                agg_acc = eval_obj.get("accuracy")
                if (not isinstance(agg_acc, (int, float)) or isinstance(agg_acc, bool)
                        or not math.isfinite(agg_acc) or not (0.0 <= agg_acc <= 1.0)):
                    violations.add("INVALID_AGGREGATE")

                slices_obj = eval_obj.get("slices")
                if not isinstance(slices_obj, dict):
                    if is_valid_policy:
                        for s_name in req_slices:
                            violations.add(f"MISSING_SLICE:{s_name}")
                elif is_valid_policy:
                    for s_name in req_slices:
                        if s_name not in slices_obj:
                            violations.add(f"MISSING_SLICE:{s_name}")
                        else:
                            sl_val = slices_obj[s_name]
                            if (not isinstance(sl_val, (int, float)) or isinstance(sl_val, bool)
                                    or not math.isfinite(sl_val) or not (0.0 <= sl_val <= 1.0)):
                                violations.add(f"SLICE_RANGE:{s_name}")
        except Exception:
            violations.add("INVALID_JSON:evaluation.json")

    readme_raw = files.get("README.md")
    if isinstance(readme_raw, str):
        markers = _CARD_MARKER_RE.findall(readme_raw)
        if len(markers) == 0:
            violations.add("MODEL_CARD_COUNT")
            violations.add("MISSING_MODEL_CARD")
        elif len(markers) > 1:
            violations.add("MODEL_CARD_COUNT")
        else:
            card_payload = markers[0]
            try:
                card_obj = json.loads(card_payload)
                if not isinstance(card_obj, dict):
                    violations.add("INVALID_MODEL_CARD")
                else:
                    if (
                        not manifest_obj
                        or card_obj.get("task") != manifest_obj.get("task")
                        or card_obj.get("baseRevision") != manifest_obj.get("baseRevision")
                        or card_obj.get("datasetDigest") != manifest_obj.get("datasetDigest")
                        or card_obj.get("modelArtifactDigest") != manifest_obj.get("modelArtifactDigest")
                        or card_obj.get("license") != license_val
                        or card_obj.get("intendedUse") != intended_use
                        or card_obj.get("limitations") != limitations
                    ):
                        violations.add("MODEL_CARD_MISMATCH")
            except Exception:
                violations.add("INVALID_MODEL_CARD")

    decision = "admit" if not violations else "reject"
    sorted_violations = sorted(list(violations), key=lambda s: s.encode("utf-8"))

    return 200, {
        "decision": decision,
        "violations": sorted_violations,
        "inventoryDigest": inventory_digest,
    }


# ===========================================================================
# 8. Q8 Solver: Per-Layer QLoRA Adapter Synthesis & Parameter Audit
# ===========================================================================
_Q8_HIDDEN_SIZES = [2048, 3072, 4096]
_Q8_TARGET_MODULES = [
    ["q_proj", "v_proj"],
    ["q_proj", "k_proj", "v_proj", "o_proj"],
    ["q_proj", "v_proj", "gate_proj", "up_proj"],
    ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
]
_Q8_RANKS = [4, 8, 16, 32]


def solve_q8_lora(email: str) -> Dict[str, Any]:
    """Q8 Generator & Solver: Calculate trainable parameter count and adapter bytes."""
    seed_str = f"{email.strip().lower()}#q-lora-quant-budget-server"
    rng = SeedRandom(seed_str)

    hidden_size = _Q8_HIDDEN_SIZES[math.floor(rng() * len(_Q8_HIDDEN_SIZES))]
    num_layers = 24 + math.floor(rng() * 9)
    num_heads = hidden_size // 64
    intermediate_size = 4 * hidden_size

    base_config = {
        "model_type": "llama",
        "hidden_size": hidden_size,
        "num_hidden_layers": num_layers,
        "num_attention_heads": num_heads,
        "intermediate_size": intermediate_size,
        "vocab_size": 32000,
    }

    layers = []
    total_trainable_params = 0

    def _module_param_count(mod: str, r: int, h: int, inter: int) -> int:
        if mod in ("q_proj", "k_proj", "v_proj", "o_proj"):
            return 2 * r * h
        elif mod in ("gate_proj", "up_proj", "down_proj"):
            return r * (h + inter)
        return 0

    for n in range(num_layers):
        if rng() < 0.25:
            layers.append({"layer_idx": n, "freeze": True, "target_modules": [], "lora_rank": 0, "lora_alpha": 0})
        else:
            mods = _Q8_TARGET_MODULES[math.floor(rng() * len(_Q8_TARGET_MODULES))]
            r = _Q8_RANKS[math.floor(rng() * len(_Q8_RANKS))]
            alpha = r * 2
            layers.append({"layer_idx": n, "freeze": False, "target_modules": mods, "lora_rank": r, "lora_alpha": alpha})
            for m in mods:
                total_trainable_params += _module_param_count(m, r, hidden_size, intermediate_size)

    adapter_bytes = total_trainable_params * 4

    return {
        "email": email,
        "base_config": base_config,
        "layers": layers,
        "trainable_params": total_trainable_params,
        "adapter_file_size_bytes": adapter_bytes,
    }


# ===========================================================================
# 9. Q9 Solver: PyTorch Training Loop Fidelity & MLflow Audit
# ===========================================================================
def solve_q9_mlflow(email: str, version: str = "") -> Dict[str, Any]:
    """Q9 Generator & Solver: Exact training loop simulation and fingerprint extraction."""
    seed_str = f"{email.strip().lower()}#q-mlflow-fingerprint-server#{version}"
    rng = SeedRandom(seed_str)

    m, u = 200, 8
    X = []
    for _ in range(m):
        row = [round((rng() - 0.5) * 4, 6) for _ in range(u)]
        X.append(row)

    e = [round((rng() - 0.5) * 2, 4) for _ in range(u)]
    o = round((rng() - 0.5) * 2, 4)
    n = [round(0.05 + 0.1 * rng(), 4) for _ in range(u)]

    y = []
    for f_idx in range(m):
        row = X[f_idx]
        val = o + sum(e[a] * row[a] for a in range(u))
        val += 0.8 * math.sin(row[0] * row[1])
        val += 0.5 * (row[2] ** 2 - row[3])
        val += 0.6 * math.tanh(row[4] + row[5])
        noise = sum(n[a] * (rng() - 0.5) for a in range(u))
        val += noise
        y.append(round(val, 6))

    lr = round(0.01 + rng() * 0.05, 4)
    batch_size = [16, 32, 64][math.floor(rng() * 3)]
    num_steps = 150 + math.floor(rng() * 251)
    weight_decay = round(0.001 + rng() * 0.02, 4)

    opt_types = ["SGD", "AdamW", "RMSprop"]
    opt_name = opt_types[math.floor(rng() * len(opt_types))]
    opt_cfg: Dict[str, Any] = {"name": opt_name}
    if opt_name == "SGD":
        opt_cfg["momentum"] = round(0.8 + 0.15 * rng(), 2)
        opt_cfg["dampening"] = 0
        opt_cfg["nesterov"] = False
    elif opt_name == "AdamW":
        opt_cfg["beta1"] = 0.9
        opt_cfg["beta2"] = round(0.99 + 0.009 * rng(), 4)
        opt_cfg["eps"] = 1e-8
    elif opt_name == "RMSprop":
        opt_cfg["alpha"] = round(0.9 + 0.09 * rng(), 3)
        opt_cfg["eps"] = 1e-8
        opt_cfg["momentum"] = round(0.8 + 0.1 * rng(), 2) if rng() > 0.5 else 0

    init_schemes = ["kaiming_uniform", "xavier_normal", "custom_seeded"]
    scheme = init_schemes[math.floor(rng() * len(init_schemes))]
    init_W = []
    init_b = 0.0

    if scheme == "kaiming_uniform":
        f = math.sqrt(1 / u)
        init_W = [round((rng() - 0.5) * 2 * f, 6) for _ in range(u)]
        init_b = round((rng() - 0.5) * 2 * f, 6)
    elif scheme == "xavier_normal":
        f = math.sqrt(2 / (u + 1))
        def _bm():
            c, i = 0.0, 0.0
            while c == 0.0:
                c = rng()
            while i == 0.0:
                i = rng()
            return math.sqrt(-2 * math.log(c)) * math.cos(2 * math.pi * i)
        init_W = [round(f * _bm(), 6) for _ in range(u)]
        init_b = round(f * _bm(), 6)
    else:
        init_W = [round((rng() - 0.5) * 1.5, 6) for _ in range(u)]
        init_b = round((rng() - 0.5) * 1.5, 6)

    sched_types = ["cosine", "step"]
    sched_type = sched_types[math.floor(rng() * len(sched_types))]
    sched_cfg: Dict[str, Any] = {"type": sched_type}
    if sched_type == "cosine":
        sched_cfg["lr_min"] = round(lr * 0.1, 6)
    else:
        sched_cfg["step_size"] = math.floor(num_steps / 3)
        sched_cfg["gamma"] = 0.5

    W = list(init_W)
    b = float(init_b)

    v_W = [0.0] * u
    v_b = 0.0
    m_W = [0.0] * u
    m_b = 0.0
    v_sq_W = [0.0] * u
    v_sq_b = 0.0

    step_losses = []

    for step_i in range(num_steps):
        if sched_type == "cosine":
            lr_i = sched_cfg["lr_min"] + 0.5 * (lr - sched_cfg["lr_min"]) * (1 + math.cos(step_i * math.pi / num_steps))
        else:
            lr_i = lr * (sched_cfg["gamma"] ** math.floor(step_i / sched_cfg["step_size"]))

        idx = (step_i * batch_size) % m
        batch_indices = [(idx + j) % m for j in range(batch_size)]

        loss_sum = 0.0
        grad_W = [0.0] * u
        grad_b = 0.0

        for b_idx in batch_indices:
            x_row = X[b_idx]
            y_target = y[b_idx]
            y_hat = sum(x_row[k] * W[k] for k in range(u)) + b
            err = y_hat - y_target
            loss_sum += err ** 2

            scale = 2.0 * err / batch_size
            for k in range(u):
                grad_W[k] += scale * x_row[k]
            grad_b += scale

        step_loss = loss_sum / batch_size
        step_losses.append(step_loss)

        if opt_name == "SGD":
            momentum = opt_cfg.get("momentum", 0.0)
            for k in range(u):
                g = grad_W[k] + weight_decay * W[k]
                v_W[k] = momentum * v_W[k] + g
                W[k] -= lr_i * v_W[k]
            g_b = grad_b
            v_b = momentum * v_b + g_b
            b -= lr_i * v_b
        elif opt_name == "AdamW":
            beta1 = opt_cfg["beta1"]
            beta2 = opt_cfg["beta2"]
            eps = opt_cfg["eps"]
            t_step = step_i + 1

            for k in range(u):
                W[k] -= lr_i * weight_decay * W[k]
                m_W[k] = beta1 * m_W[k] + (1 - beta1) * grad_W[k]
                v_sq_W[k] = beta2 * v_sq_W[k] + (1 - beta2) * (grad_W[k] ** 2)
                m_hat = m_W[k] / (1 - beta1 ** t_step)
                v_hat = v_sq_W[k] / (1 - beta2 ** t_step)
                W[k] -= lr_i * m_hat / (math.sqrt(v_hat) + eps)

            m_b = beta1 * m_b + (1 - beta1) * grad_b
            v_sq_b = beta2 * v_sq_b + (1 - beta2) * (grad_b ** 2)
            m_b_hat = m_b / (1 - beta1 ** t_step)
            v_b_hat = v_sq_b / (1 - beta2 ** t_step)
            b -= lr_i * m_b_hat / (math.sqrt(v_b_hat) + eps)
        elif opt_name == "RMSprop":
            alpha = opt_cfg["alpha"]
            eps = opt_cfg["eps"]
            momentum = opt_cfg.get("momentum", 0.0)
            for k in range(u):
                g = grad_W[k] + weight_decay * W[k]
                v_sq_W[k] = alpha * v_sq_W[k] + (1 - alpha) * (g ** 2)
                if momentum > 0:
                    v_W[k] = momentum * v_W[k] + g / (math.sqrt(v_sq_W[k]) + eps)
                    W[k] -= lr_i * v_W[k]
                else:
                    W[k] -= lr_i * g / (math.sqrt(v_sq_W[k]) + eps)
            v_sq_b = alpha * v_sq_b + (1 - alpha) * (grad_b ** 2)
            if momentum > 0:
                v_b = momentum * v_b + grad_b / (math.sqrt(v_sq_b) + eps)
                b -= lr_i * v_b
            else:
                b -= lr_i * grad_b / (math.sqrt(v_sq_b) + eps)

    final_loss = round(step_losses[-1], 5)
    mean_last_10 = round(sum(step_losses[-10:]) / 10.0, 5)
    run_id = hashlib.md5(f"{email}#mlflow_run#{num_steps}#{final_loss}".encode("utf-8")).hexdigest()

    return {
        "final_loss": final_loss,
        "run_id": run_id,
        "mean_last_10_loss": mean_last_10,
    }


# ===========================================================================
# 10. Q10 Solver: Green AI & HF Model Card Carbon Accounting Audit
# ===========================================================================
_Q10_TDP = {
    "NVIDIA A100": 400,
    "NVIDIA V100": 300,
    "NVIDIA T4": 70,
    "NVIDIA H100": 700,
    "NVIDIA L40S": 350,
    "NVIDIA RTX 4090": 450,
}
_Q10_GRID = {
    "us-central1": 350,
    "europe-west4": 200,
    "asia-south1": 650,
    "us-east1": 420,
    "europe-north1": 120,
    "ap-southeast1": 480,
}


def solve_q10_carbon(email: str, version: str = "") -> Dict[str, Any]:
    """Q10 Generator & Solver: Carbon emissions and Hugging Face Model Card YAML frontmatter."""
    seed_str = f"{email.strip().lower()}#q-modelcard-carbon-server#{version}"
    rng = SeedRandom(seed_str)

    gpu_types = list(_Q10_TDP.keys())
    regions = list(_Q10_GRID.keys())
    train_types = ["pre-training", "fine-tuning"]

    gpu_type = gpu_types[math.floor(rng() * len(gpu_types))]
    gpu_hours = round(12.5 + rng() * 467.5, 1)
    num_gpus = 1 + math.floor(rng() * 8)
    region = regions[math.floor(rng() * len(regions))]
    pue = round(1.1 + rng() * 0.5, 2)
    training_type = train_types[math.floor(rng() * len(train_types))]

    tdp = _Q10_TDP[gpu_type]
    grid_intensity = _Q10_GRID[region]

    energy_kwh = (tdp * num_gpus * gpu_hours * pue) / 1000.0
    co2_kg = round((energy_kwh * grid_intensity) / 1000.0, 3)

    yaml_frontmatter = f"""---
co2_eq_emissions:
  emissions: {co2_kg}
  source: codecarbon
  training_type: {training_type}
  geographical_location: {region}
  hardware_used: {gpu_type}
---"""

    return {
        "email": email,
        "run_log": {
            "gpu_type": gpu_type,
            "gpu_hours": gpu_hours,
            "num_gpus": num_gpus,
            "region": region,
            "power_usage_effectiveness": pue,
            "training_type": training_type,
        },
        "energy_kWh": round(energy_kwh, 4),
        "co2_kg": co2_kg,
        "yaml_frontmatter": yaml_frontmatter,
    }
