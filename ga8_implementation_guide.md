# GA8 MLOps & LLM Systems Gateway — Complete Implementation Guide

> **Reference Repository**: [`GyaanFlow/tds-roe-solver-api-t12026`](https://github.com/GyaanFlow/tds-roe-solver-api-t12026)  
> **Source Exam URL**: `https://exam.sanand.workers.dev/exam-tds-2026-05-ga8.js`

---

## 1. Architectural Overview

GA8 tests production MLOps, LLM fine-tuning, quantization, model registry governance, and CI/CD pipelines. Unlike GA5 (which uses LLMs), **all 10 GA8 questions are 100% deterministic rule engines and PRNG mathematical simulations**. No external API keys or LLM calls are needed.

### Multi-Tenant Routing Model

Every student submits a base URL prefixed with their email:
```text
https://<domain>/ga8/{email}/<endpoint>
```

| Question | Question ID | Method & Path | State / Type |
| :--- | :--- | :--- | :--- |
| **Q1** | `q-immutable-training-corpus-server` | `POST /build-corpus` | Stateless Deterministic Policy Engine |
| **Q2** | `q-leakage-safe-bqml-server` | `POST /bqml` | Stateful Two-Phase Gate (`select` $\to$ `evaluate`) |
| **Q3** | `q-mlflow-evidence-promotion-server` | `POST /promote` | Stateless Promotion Policy Gate |
| **Q4** | `q-peft-repair-server` | `POST /adapt` | Dual-Mode Solver (`choose` & `repair`) |
| **Q5** | `q-quantized-model-admission-server` | `POST /quantize` | Stateful Two-Phase Gate (`freeze` $\to$ `select`) |
| **Q6** | `q-content-addressed-pipeline-server` | `POST /pipeline` | Stateful 6-Stage DAG Controller |
| **Q7** | `q-verifiable-model-bundle-server` | `POST /verify-bundle` | Stateless Model Distribution Verifier |
| **Q8** | `q-lora-quant-budget-server` | `GET /solve/q8` | ARC4 PRNG Parameter & Safetensors Calculator |
| **Q9** | `q-mlflow-fingerprint-server` | `GET /solve/q9` | ARC4 PRNG Training Loop & MLflow Run ID Simulator |
| **Q10** | `q-modelcard-carbon-server` | `GET /solve/q10` | ARC4 PRNG Green AI Carbon & YAML Frontmatter Generator |

---

## 2. Common Utilities & Shared Standards

### 2.1 Pure Python CRC32C (Castagnoli Polynomial `0x1EDC6F41`)

The standard `zlib.crc32` uses IEEE 802.3, whereas Google Cloud Storage uses CRC32C (Castagnoli). Use the lookup table implementation:

```python
def _make_crc32c_table() -> list[int]:
    table = []
    for i in range(256):
        crc = i
        for _ in range(8):
            crc = (crc >> 1) ^ 0x82F63B78 if (crc & 1) else (crc >> 1)
        table.append(crc)
    return table

_CRC32C_TABLE = _make_crc32c_table()

def crc32c_hex(data: bytes) -> str:
    crc = 0xFFFFFFFF
    for b in data:
        crc = _CRC32C_TABLE[(crc ^ b) & 0xFF] ^ (crc >> 8)
    return f"{crc ^ 0xFFFFFFFF:08x}"
```

### 2.2 Strict RFC 3339 Timestamp Parsing & UTC Normalization

Timestamps must conform to `YYYY-MM-DDTHH:mm:ss[.sss](Z|±HH:mm)`:
- Fraction: 1 to 3 digits (padded to 3 ms digits in normalized form).
- Max offset: `14:00` (hour 14 strictly requires minute `00`).
- Valid calendar days (e.g. reject Feb 29 on non-leap years).

```python
import re
from datetime import datetime, timezone
from typing import Optional, Tuple

_TS_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?(Z|([+-])(\d{2}):(\d{2}))$")

def parse_rfc3339_timestamp(ts: str) -> Optional[Tuple[datetime, str]]:
    if not isinstance(ts, str) or not ts:
        return None
    m = _TS_RE.match(ts)
    if not m:
        return None
    year, month, day, hour, minute, second, frac, tz_str, sign, tz_h, tz_m = m.groups()
    try:
        y, mo, d = int(year), int(month), int(day)
        h, mi, s = int(hour), int(minute), int(second)
        ms = int(frac.ljust(3, "0")[:3]) if frac else 0
        if tz_str == "Z":
            offset_mins = 0
        else:
            off_h, off_m = int(tz_h), int(tz_m)
            if off_h > 14 or off_m > 59 or (off_h == 14 and off_m != 0):
                return None
            offset_mins = (off_h * 60 + off_m) * (1 if sign == "+" else -1)

        dt_local = datetime(y, mo, d, h, mi, s, ms * 1000, tzinfo=timezone.utc)
        utc_ts = dt_local.timestamp() - (offset_mins * 60)
        dt_utc = datetime.fromtimestamp(utc_ts, tz=timezone.utc)
        norm_str = f"{dt_utc.year:04d}-{dt_utc.month:02d}-{dt_utc.day:02d}T{dt_utc.hour:02d}:{dt_utc.minute:02d}:{dt_utc.second:02d}.{int(dt_utc.microsecond / 1000):03d}Z"
        return dt_utc, norm_str
    except Exception:
        return None
```

### 2.3 Shared ARC4 PRNG (`seedrandom`)

Questions 8, 9, 10 use David Bau's ARC4-based `Math.seedrandom(seed)`. Ensure RC4-drop[256] discard is executed during key setup.

---

## 3. Detailed Question Specifications

---

### Q1 — `POST /build-corpus` (Immutable Training Corpus)

#### Grader Checks
1. Validates GCS objects (`uri` matching `gs://bucket/object`, valid generation decimal strings, CRC32C checksum match, `schemaId == "training-v1"`).
2. Parses JSONL rows (`id, entity, eventTime, revision, text`).
3. Canonicalizes `entity` and `text` with Unicode NFKC, lowercase, trimmed, collapsed whitespace.
4. Deduplicates rows by `[entity, eventTime, text]`. Keeps highest revision, breaking ties with UTF-8-byte-smallest ID. Losers tagged `DUPLICATE`.
5. Validates window `minTime <= eventTime <= maxTime`. If policy invalid, tag `POLICY_INVALID`; if outside window, tag `OUT_OF_WINDOW`.
6. Hash splits valid rows: `bucket = firstByte(SHA256(UTF8(entity))) % 10`
   - `0..5` $\to$ **train**
   - `6..7` $\to$ **validation**
   - `8..9` $\to$ **test**
7. Jaccard Contamination: Computes lowercase alphanumeric word-set Jaccard similarity of each validation and test row against **every** train row. If $\ge \text{contaminationThreshold}$, row is rejected with `TRAIN_CONTAMINATION`.
8. Serializes each split as compact newline-terminated JSON sorted by ID bytes, and outputs SHA-256 digests.

#### Request Schema
```json
{
  "policy": {
    "minTime": "2026-01-01T00:00:00Z",
    "maxTime": "2026-01-02T00:00:00Z",
    "contaminationThreshold": 0.8
  },
  "objects": [{
    "uri": "gs://bucket/object",
    "generation": "123",
    "fetchedGeneration": "123",
    "crc32c": "e3069283",
    "schemaId": "training-v1",
    "content": "{\"id\":\"r1\",\"entity\":\"User A\",\"eventTime\":\"2026-01-01T10:00:00Z\",\"revision\":1,\"text\":\"hello\"}\n"
  }]
}
```

#### Response Schema (HTTP 200)
```json
{
  "splits": {
    "train": [{"id":"r1","entity":"user a","eventTime":"2026-01-01T10:00:00.000Z","revision":1,"text":"hello"}],
    "validation": [],
    "test": []
  },
  "rejectedObjects": [],
  "rejectedRows": [],
  "digests": {
    "train": "33b74737fa1819385966eb13998971f54cfef653068fbf10cb7cfa557ae1aa03",
    "validation": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "test": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "lineage": [{
    "uri": "gs://bucket/object",
    "generation": "123",
    "crc32c": "e3069283",
    "schemaId": "training-v1"
  }]
}
```

---

### Q2 — `POST /bqml` (Leakage-Safe BigQuery ML Gate)

#### Grader Checks
Stateful two-phase gate:
1. **Phase `select`**:
   - Deduplicates rows by `[entity, UTC(eventTime)]` (highest version, smallest ID).
   - Filters features: must be present in all retained rows, not in `forbiddenFeatures`, and `availableAt <= predictionTime` in every row.
   - Selects successful trial with highest `evalMetric` (breaking ties with smallest integer `trialId`).
   - Computes `datasetDigest = sha256(compact_json({trainRowIds, evalRowIds, featureNames}))`.
   - Persists state under `(tenant, runId)`. Replay with identical input returns same JSON; different input returns **HTTP 409** `{"error": "RUN_ID_CONFLICT"}`.
2. **Phase `evaluate`**:
   - Verifies `runId`, `selectedTrialId`, and `datasetDigest` match stored phase 1 record (else `INVALID_LINEAGE`).
   - Computes aggregate accuracy and slice accuracies, rounded to **12 decimal places**.
   - Verifies `aggregate >= metricFloor` and each slice $\ge \text{requiredSlices}[slice]$ (else `AGGREGATE_FLOOR`, `SLICE_FLOOR:<slice>`, `MISSING_SLICE:<slice>`).
   - Verifies `bytesProcessed <= maxBytes` (else `BYTE_LIMIT`).
   - Admits only when all checks pass.

---

### Q3 — `POST /promote` (MLflow Model Promotion Gate)

#### Grader Checks
1. Binds evidence: `datasetDigest` and `schemaDigest` match policy; `artifactDigest` matches version.
2. Age check: `asOf - maxAgeSeconds <= createdAt <= asOf` (tags `FUTURE_EVALUATION` or `STALE_EVALUATION`).
3. Slices & Gates: `accuracy >= accuracyFloor`, `latencyMs <= maxLatencyMs`, `sizeBytes <= maxSizeBytes`, and all `requiredSlices` meet floors.
4. Champion Eligibility: If champion fails any gate, returns `action: "block"` and `selectedVersion: null`.
5. Promotion Decision: Ranks eligible versions by `accuracy desc -> latency asc -> size asc -> version asc`.
   - Challenger improvement $= \text{round}(\text{challenger.accuracy} - \text{champion.accuracy}, 12)$.
   - If improvement $\ge \text{minImprovement}$: returns `action: "promote"`, `selectedVersion: challenger_id`, `aliasMutation: {"alias": "champion", "version": challenger_id}`.
   - Else: returns `action: "retain"`, `selectedVersion: champion_id`, `aliasMutation: null`.

---

### Q4 — `POST /adapt` (PEFT Choice & Training Repair)

#### Operation 1: `"choose"`
- Evaluates candidates in priority order: `prompt_only -> retrieval -> lora -> qlora`.
- Computes `totalCost = round(oneTimeCost + horizonRequests * recurringCost, 12)`.
- Enforces quality, freshness, latency, memory, data, and cost ceilings. Returns first eligible candidate in priority order.

#### Operation 2: `"repair"`
- Loss Masking: Assistant tokens with `padding == false` keep `id`; all other tokens (system, user, padding) get `-100`.
- Trainable Params: Filters parameters with target in `allowedTargets` and name ending in `.lora_A.weight` or `.lora_B.weight`.
- Verification Checks: `templateApplications == 1`, `inferenceMode == false`, `artifactFiles == ["adapter_config.json", "adapter_model.safetensors"]`, `dropoutActiveDuringEval == false`, `checkpointComplete == true`, `trainRowIds` & `evalRowIds` disjoint, and `resumeTolerance` verification.

---

### Q5 — `POST /quantize` (Quantized Model Admission Gate)

#### Phase 1: `"freeze"`
- Computes inventory SHA-256 and bytes for each file in candidate packages.
- Binds `packageDigest = sha256(compact_json(inventory))`.
- Enforces calibration & tokenizer digests and `loadable: true` $\to$ status `"frozen"`.

#### Phase 2: `"select"`
- Verifies candidate inventory matches stored freeze record (else `INVALID_MANIFEST` / `INVALID_LINEAGE`).
- Computes candidate aggregate and slice accuracies on test rows.
- Checks `totalBytes <= maxBytes` and `latencyMs <= maxLatencyMs`.
- Ranks admitted candidates by `bytes asc -> latencyMs asc -> candidateOrder index`.

---

### Q6 — `POST /pipeline` (Content-Addressed DAG Pipeline)

#### DAG Structure
$$\text{verify\_data} \to \text{prepare} \to \text{train} \to \text{evaluate} \to \text{register} \to \text{publish}$$

#### Content-Addressed Dependency Keys
- `verify_data`: `sha256([generation, checksum])`
- `prepare`: `sha256([canonicalData, prepareCode, prepareConfig])`
- `train`: `sha256([prepareArtifact, trainCode, trainConfig, runtime])`
- `evaluate`: `sha256([trainArtifact, canonicalData, evaluateCode, evaluateConfig])`
- `register`: `sha256([evaluateArtifact, schemaDigest])`
- `publish`: `sha256([registerArtifact, publishConfig])`

#### Transition & Receipt Rules
- Node actions: `reuse` (`CACHE_HIT`), `rerun` (`CACHE_MISS` or `RETRYABLE_FAILURE`), `block` (`RUNNING`, `TERMINAL_FAILURE`, `UPSTREAM_TERMINAL`, `UPSTREAM_PENDING`).
- Register & Publish nodes require receipt format `receipt:<node>:<key>`.
- Any state conflict triggers whole-batch rollback and returns **HTTP 409**.

---

### Q7 — `POST /verify-bundle` (Model Bundle & Model Card Verifier)

#### Grader Checks
1. Required files: `README.md`, `training_manifest.json`, `evaluation.json`, `inventory.json`, `adapter_model.safetensors`, `adapter_config.json`.
2. Blocks unsafe extensions: `.bin`, `.pt`, `.pth`, `.pkl`, `.pickle` ($\to$ `UNSAFE_WEIGHTS`).
3. Recomputes inventory digests and matches `inventory.json`.
4. Validates `adapter_config.json` (`r > 0`, non-empty `target_modules`).
5. Validates `training_manifest.json` digests against `adapter_model.safetensors` and `evaluation.json`.
6. Extracts HTML comment model card marker in `README.md`:
   ```markdown
   <!-- tds-model-card {"task":"...", "baseRevision":"...", ...} -->
   ```
   Requires exactly 1 valid marker matching policy and manifest fields.

---

### Q8, Q9, Q10 — Automated Calculators & Solvers

#### Q8: LoRA Parameter & Safetensors Size (`q-lora-quant-budget-server`)
- Seed: `${email.trim().toLowerCase()}#q-lora-quant-budget-server`
- Module parameter counting formula for LLaMA projections:
  - `q_proj`, `k_proj`, `v_proj`, `o_proj`: $2 \times r \times \text{hidden\_size}$
  - `gate_proj`, `up_proj`, `down_proj`: $r \times (\text{hidden\_size} + \text{intermediate\_size})$
- Adapter safetensors file size $= \text{trainable\_params} \times 4$ bytes.
- Submission output format:
  ```json
  {
    "trainable_params": 9355264,
    "adapter_file_size_bytes": 37421056
  }
  ```

#### Q9: PyTorch Training Loop & MLflow Fingerprint (`q-mlflow-fingerprint-server`)
- Seed: `${email.trim().toLowerCase()}#q-mlflow-fingerprint-server#${version}`
- Simulates exact step-level gradient descent on synthetic dataset $X (200 \times 8)$.
- Supports optimizers: `SGD` (with momentum & weight decay), `AdamW` (decoupled weight decay, $\beta_1, \beta_2, \epsilon$), `RMSprop`.
- Computes `final_loss`, `mean_last_10_loss`, and `run_id = md5(f"{email}#mlflow_run#{num_steps}#{final_loss}")`.
- Submission output format:
  ```json
  {
    "final_loss": 0.72047,
    "run_id": "89ecfae88107ef4f89d31135ef580556",
    "mean_last_10_loss": 0.70617
  }
  ```

#### Q10: Green AI & Model Card Carbon Frontmatter (`q-modelcard-carbon-server`)
- Seed: `${email.trim().toLowerCase()}#q-modelcard-carbon-server#${version}`
- Formulas:
  $$\text{energy\_kWh} = \frac{\text{TDP} \times \text{num\_gpus} \times \text{gpu\_hours} \times \text{PUE}}{1000}$$
  $$\text{co2\_kg} = \text{round}\left(\frac{\text{energy\_kWh} \times \text{grid\_intensity}}{1000}, 3\right)$$
- Submission output format:
  ```yaml
  ---
  co2_eq_emissions:
    emissions: 312.212
    source: codecarbon
    training_type: fine-tuning
    geographical_location: asia-south1
    hardware_used: NVIDIA A100
  ---
  ```

---

## 4. Verification Checklist

1. **Bare & Tenant Routes**: Endpoints must respond at both `/ga8/{endpoint}` and `/ga8/{email}/{endpoint}`.
2. **Deterministic PRNG**: Seeding must use David Bau's ARC4 (not Alea).
3. **HTTP Status Codes**:
   - Malformed / missing input: `400 {"error": "INVALID_INPUT"}` or `400 {"error": "INVALID_REQUEST"}`.
   - Stateful replay mismatch: `409 {"error": "RUN_ID_CONFLICT"}` / `FREEZE_ID_CONFLICT` / `REVISION_CONFLICT`.
4. **Float Rounding**: Always round float accuracy, latency, and cost calculations to 12 decimal places.
