#!/usr/bin/env node
/**
 * seed_bridge.js — Compute all GA2 seeded parameters for a given email.
 * Uses the REAL seedrandom@3.0.5 (same as the exam grader).
 *
 * Usage:  node seed_bridge.js <email>
 * Output: JSON object with all parameters for Q01-Q10.
 */

const seedrandom = require("seedrandom");

const ALPHA = "abcdefghijklmnopqrstuvwxyz0123456789";
const KEYS  = ["port", "workers", "debug", "log_level", "api_key"];
const LEVELS = ["debug", "info", "warning", "error"];

function randStr(rng, n) {
  return Array.from({ length: n }, () => ALPHA[Math.floor(rng() * ALPHA.length)]).join("");
}

function randInt(rng, lo, hi) {
  return lo + Math.floor(rng() * (hi - lo + 1));
}

function coerce(k, v) {
  if (k === "port" || k === "workers") return parseInt(v, 10);
  if (k === "debug") return /^(1|true|yes|on)$/i.test(String(v));
  return String(v);
}

function computeAll(email) {
  const e = (email || "").trim().toLowerCase();

  // Q01: Metrics CORS origin
  const r1 = seedrandom(`q-fastapi-metrics-cors-server#${e}#`);
  const q01_origin = `https://dash-${randStr(r1, 6)}.example.com`;

  // Q02: OAuth JWT parameters
  const r2 = seedrandom(`q-oauth-jwks-verify-server#${e}#`);
  const q02_aud = `tds-${randStr(r2, 8)}.apps.exam.local`;
  const q02_sub = `sub-${randStr(r2, 12)}`;

  // Q03: Config layers
  const r3 = seedrandom(`q-config-precedence-server#${e}#`);
  const defaults = { port: 8000, workers: 1, debug: false, log_level: "info", api_key: "default-secret-000" };

  function makeLayer() {
    const layer = {};
    for (const k of KEYS) {
      if (r3() < 0.5) {
        if (k === "port")          layer[k] = randInt(r3, 8000, 9000);
        else if (k === "workers")  layer[k] = randInt(r3, 1, 16);
        else if (k === "debug")    layer[k] = r3() < 0.5;
        else if (k === "log_level") layer[k] = LEVELS[Math.floor(r3() * LEVELS.length)];
        else                       layer[k] = `key-${randStr(r3, 10)}`;
      }
    }
    return layer;
  }

  const fileYaml = makeLayer();
  const dotenv   = makeLayer();
  const osenv    = makeLayer();

  // Merge with alias handling (num_workers → workers)
  function alias(o) {
    return Object.fromEntries(Object.entries(o).map(([k, v]) => [k === "num_workers" ? "workers" : k, v]));
  }
  const merged = { ...defaults, ...alias(fileYaml), ...alias(dotenv), ...alias(osenv) };
  const baseEffective = {};
  for (const k of KEYS) baseEffective[k] = coerce(k, merged[k]);

  // Q05: Analytics API key
  const r5 = seedrandom(`q-deploy-analytics-platform-server#${e}#`);
  const q05_key = `ak_${randStr(r5, 24)}`;

  // Q09: Orders params
  const r9 = seedrandom(`q-api-idempotency-pagination-server#${e}#`);
  const q09_total     = randInt(r9, 40, 60);
  const q09_rateLimit = randInt(r9, 15, 20);

  // Q10: Middleware params
  const r10 = seedrandom(`q-middleware-ratelimit-cors-server#${e}#`);
  const q10_origin = `https://app-${randStr(r10, 6)}.example.com`;
  const q10_bucket = 8 + Math.floor(r10() * 8);

  return {
    q01: { allowedOrigin: q01_origin },
    q02: { iss: "https://idp.exam.local", aud: q02_aud, sub: q02_sub },
    q03: { defaults, fileYaml, dotenv, osenv, baseEffective },
    q05: { apiKey: q05_key },
    q09: { total: q09_total, rateLimit: q09_rateLimit },
    q10: { allowedOrigin: q10_origin, bucket: q10_bucket },
  };
}

// Main
const email = process.argv[2];
if (!email) {
  process.stderr.write("Usage: node seed_bridge.js <email>\n");
  process.exit(1);
}
const result = computeAll(email);
process.stdout.write(JSON.stringify(result));
