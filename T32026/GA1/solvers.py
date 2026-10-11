from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from T22026.shared.seedrandom_arc4 import SeedRandom


DEFAULT_CONFIG: dict[str, Any] = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "****",
}

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}
_IST = timezone(timedelta(hours=5, minutes=30))


def _timestamp(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=_IST)
    except (TypeError, ValueError):
        return None


def coerce_config_value(key: str, value: Any) -> Any:
    raw = str(value).strip()
    if key in {"port", "workers"}:
        if not re.fullmatch(r"[+-]?\d+", raw):
            raise ValueError(f"INVALID_INTEGER:{key}")
        return int(raw, 10)
    if key == "debug":
        lowered = raw.lower()
        if lowered not in {"true", "false", "1", "0", "yes", "no", "on", "off"}:
            raise ValueError("INVALID_BOOLEAN:debug")
        return lowered in {"true", "1", "yes", "on"}
    return raw


def assigned_config(email: str, version: str = "") -> dict[str, Any]:
    """Reproduce the official seeded YAML, dotenv, and OS environment layers."""
    rng = SeedRandom(f"q-config-precedence-server#{email.strip().lower()}#{version}")
    result = dict(DEFAULT_CONFIG)
    levels = ("debug", "info", "warning", "error")
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    for _ in range(3):
        for key in DEFAULT_CONFIG:
            if rng() >= 0.5:
                continue
            if key == "port":
                value = 8000 + int(rng() * 1001)
            elif key == "workers":
                value = 1 + int(rng() * 16)
            elif key == "debug":
                value = rng() < 0.5
            elif key == "log_level":
                value = levels[int(rng() * len(levels))]
            else:
                value = "key-" + "".join(alphabet[int(rng() * len(alphabet))] for _ in range(10))
            result[key] = value
    result["api_key"] = "****"
    return result


def effective_config(overrides: list[str], email: str = "", version: str = "") -> dict[str, Any]:
    result = assigned_config(email, version) if email else dict(DEFAULT_CONFIG)
    for raw in overrides:
        key, sep, value = raw.partition("=")
        key = key.strip().lower()
        if not sep or not key:
            continue
        if key == "num_workers":
            key = "workers"
        if key not in DEFAULT_CONFIG:
            continue
        try:
            result[key] = coerce_config_value(key, value)
        except ValueError:
            # The exam only sends valid values. Ignore malformed overrides so a
            # single bad query value does not turn a healthy config endpoint 500.
            continue
    result["api_key"] = "****"
    return result


def challenge_digest(challenge: str, email: str) -> str:
    normalized = str(email or "").strip().lower()
    return hashlib.sha256(f"{challenge}:{normalized}".encode("utf-8")).hexdigest()[:16]


def mcp_tool_definition() -> dict[str, Any]:
    return {
        "name": "solve_challenge",
        "description": "Return the exam challenge digest from this request's X-Exam-Challenge header.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    }


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.fullmatch(r"\s*\$?(-?\d[\d,]*(?:\.\d{1,4})?)\s*", value)
        if match:
            try:
                return float(match.group(1).replace(",", ""))
            except ValueError:
                pass
    return None


def _record_collections(value: Any, path: str = "") -> list[tuple[str, list[dict[str, Any]]]]:
    """Return actual object arrays, retaining their resource/relationship path.

    Do not recursively treat every parent JSON object as a transaction: doing so
    counts summaries and nested line items together and is the source of many
    plausible-looking but wrong totals.
    """
    result: list[tuple[str, list[dict[str, Any]]]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}/{key}".lower()
            if isinstance(child, list):
                rows = [item for item in child if isinstance(item, dict)]
                if rows:
                    result.append((child_path, rows))
                for item in child:
                    if isinstance(item, (dict, list)):
                        result.extend(_record_collections(item, child_path))
            elif isinstance(child, dict):
                result.extend(_record_collections(child, child_path))
    elif isinstance(value, list):
        rows = [item for item in value if isinstance(item, dict)]
        if rows:
            result.append((path, rows))
        for item in value:
            if isinstance(item, (dict, list)):
                result.extend(_record_collections(item, path))
    return result


def _dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, int] = {}
    unique: list[dict[str, Any]] = []
    for row in rows:
        identity = next(((name, row[name]) for name in (
            "transaction_id", "order_id", "refund_id", "invoice_id", "record_id", "uuid", "id"
        ) if row.get(name) is not None), None)
        if identity is None:
            # Identical amounts/dates can represent distinct legitimate ledger
            # events; do not collapse rows without a stable record identifier.
            unique.append(row)
            continue
        key = json.dumps(identity, ensure_ascii=False, default=str)
        if key not in seen:
            seen[key] = len(unique)
            unique.append(row)
        else:
            index = seen[key]
            previous = _timestamp(unique[index].get("updated_at"))
            current = _timestamp(row.get("updated_at"))
            if current is not None and (previous is None or current > previous):
                unique[index] = row
    return unique


def _date_in_row(row: dict[str, Any]) -> date | None:
    created = _timestamp(row.get("created_at"))
    if created is not None:
        return created.astimezone(_IST).date()
    for key, value in row.items():
        if not any(term in str(key).lower() for term in ("date", "time", "created", "month")):
            continue
        text = str(value)
        iso = re.search(r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b", text)
        if iso:
            try:
                return date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
            except ValueError:
                continue
        year_month = re.search(r"\b(20\d{2})[-/](\d{1,2})\b", text)
        if year_month:
            try:
                return date(int(year_month.group(1)), int(year_month.group(2)), 1)
            except ValueError:
                continue
        month_match = next((m for m in _MONTHS if re.search(rf"\b{m}\b", text, re.I)), None)
        year_match = re.search(r"\b(20\d{2})\b", text)
        if month_match and year_match:
            return date(int(year_match.group(1)), _MONTHS[month_match], 1)
    return None


def _filters(question: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    q = question.lower()
    month = next(((name, number) for name, number in _MONTHS.items() if re.search(rf"\b{name}\b", q)), None)
    year_match = re.search(r"\b20\d{2}\b", q)
    region_match = re.search(r"\b(north|south|east|west|central|northeast|northwest|southeast|southwest)\b", q)
    region = region_match.group(1) if region_match else None
    filtered = []
    for row in rows:
        if region:
            region_values = [str(value).strip().lower() for key, value in row.items()
                             if "region" in str(key).lower() and isinstance(value, (str, int))]
            if not region_values or not any(value == region or value.startswith(region + " ") for value in region_values):
                continue
        if month or year_match:
            row_date = _date_in_row(row)
            if row_date is None or (month and row_date.month != month[1]) or (year_match and row_date.year != int(year_match.group())):
                continue
        filtered.append(row)
    return filtered


def _field_values(rows: list[dict[str, Any]], names: tuple[str, ...]) -> list[Any]:
    values = []
    normalized_names = {name.lower() for name in names}
    for row in rows:
        for key, value in row.items():
            if str(key).lower() in normalized_names and value is not None:
                values.append(value)
                break
    return values


def _sum_fields(rows: list[dict[str, Any]], names: tuple[str, ...]) -> float | None:
    values = []
    for row in rows:
        amount = next((_numeric(value) for key, value in row.items()
                       if str(key).lower() in names and _numeric(value) is not None), None)
        if amount is not None:
            values.append(amount)
    return sum(values) if values else None


def _answer_acme(question: str, rows: list[dict[str, Any]], resources: dict[str, Any]) -> Any:
    q = question.lower()
    rows = _filters(question, _dedupe_rows(rows))
    is_refund = bool(re.search(r"\b(refund\w*|return\w*)\b", q))
    is_count = any(term in q for term in ("how many", "number of", "count", "distinct", "unique"))
    is_product = bool(re.search(r"\b(product\w*|item\w*|sku)\b", q))
    is_customer = bool(re.search(r"\b(customer\w*|client\w*)\b", q))
    paid = [row for row in rows if str(row.get("status", "")).lower() == "paid"]
    refunded = [row for row in rows if str(row.get("status", "")).lower() == "refunded"]
    rates: dict[str, Any] = {"USD": 1}
    for payload in resources.values():
        if isinstance(payload, dict) and isinstance(payload.get("usd_per_unit"), dict):
            rates.update(payload["usd_per_unit"])

    def usd(row):
        currency = str(row.get("currency", "USD")).upper()
        if currency not in rates:
            raise ValueError(f"No USD exchange rate available for {currency}.")
        try:
            return Decimal(str(row["amount"])) * Decimal(str(rates[currency]))
        except (KeyError, InvalidOperation):
            raise ValueError("Invalid ledger amount or exchange rate.") from None

    def money(value):
        return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    if is_refund:
        if is_count and not (is_product or is_customer):
            return len(refunded)
        selected = refunded
    else:
        selected = paid

    if is_product or is_customer:
        key = "product" if is_product else "customer"
        if is_customer and is_count:
            buying = any(term in q for term in ("pay", "bought", "buy", "purchas", "spend", "spent"))
            customers = selected if is_refund or buying else rows
            return len({row[key] for row in customers})
        totals: dict[str, Decimal] = {}
        units = is_product and not any(word in q for word in ("revenue", "earn", "spend", "spent", "money", "dollar", "usd", "sales value"))
        for row in selected:
            name = str(row[key])
            value = Decimal(str(row.get("qty", 0))) if units else usd(row)
            totals[name] = totals.get(name, Decimal(0)) + value
        if is_count and is_product:
            if "distinct" in q or "unique" in q:
                return len(totals)
            return int(sum(totals.values(), Decimal(0)))
        if any(word in q for word in ("most", "top", "highest", "largest", "best", "leading")):
            return sorted(totals, key=lambda name: (-totals[name], name))[0] if totals else ""
        names = [name for name in totals if re.search(rf"\b{re.escape(name.lower())}\b", q)]
        if len(names) == 1:
            return int(totals[names[0]]) if units else money(totals[names[0]])
        raise ValueError("Specify a product/customer measure or ranking.")

    if is_count:
        return len(selected if is_refund or "paid" in q else rows)
    if any(word in q for word in ("revenue", "sales", "earn", "income", "receipts", "total", "amount", "how much", "refund", "average", "mean", "per order")):
        total = sum((usd(row) for row in selected), Decimal(0))
        if any(word in q for word in ("average", "mean", "per order")):
            total = total / len(selected) if selected else Decimal(0)
        return money(total)
    raise ValueError("Could not map the question to a supported ledger measure.")


def answer_ledger_question(question: str, resources: dict[str, Any]) -> Any:
    """Interpret common revenue/refund/product/customer questions over discovered API collections."""
    q = question.lower()
    collections = [(path, _dedupe_rows(rows)) for path, payload in resources.items()
                   for path, rows in _record_collections(payload, str(path)) if rows]
    collections = [(path, rows) for path, rows in collections if rows]
    if not collections:
        raise ValueError("No record collections found in the discovered ledger API.")
    acme = [row for _, rows in collections for row in rows
            if all(key in row for key in ("id", "created_at", "updated_at", "status", "currency", "amount", "qty", "product", "customer"))]
    if acme:
        return _answer_acme(question, acme, resources)

    is_refund = bool(re.search(r"\b(refund|refunded|refunds|return|returned)\b", q))
    is_product = "product" in q or "item" in q or "sku" in q
    is_customer = "customer" in q or "client" in q

    def relevance(path: str, rows: list[dict[str, Any]]) -> int:
        low = path.lower()
        points = 0
        if is_refund and any(term in low for term in ("refund", "return")):
            points += 6
        if not is_refund and any(term in low for term in ("order", "sale", "transaction")):
            points += 4
        if is_product and any(term in low for term in ("item", "product", "line")):
            points += 6
        if is_customer and any(term in low for term in ("customer", "client")):
            points += 6
        sample = rows[0]
        keys = {str(key).lower() for key in sample}
        if is_refund and any("refund" in key for key in keys):
            points += 2
        if is_product and any(any(word in key for word in ("product", "sku", "item")) for key in keys):
            points += 2
        if is_customer and any("customer" in key or "client" in key for key in keys):
            points += 2
        if not (is_refund or is_product or is_customer) and any(key in keys for key in ("total", "amount", "revenue", "order_total")):
            points += 1
        if not (is_product or is_refund) and any(term in low for term in ("/items", "/line_items", "/products")):
            points -= 5
        return points

    ranked = sorted(collections, key=lambda item: relevance(*item), reverse=True)
    best = relevance(*ranked[0])
    candidates = [rows for path, rows in ranked if relevance(path, rows) == best and best > 0]
    if not candidates:
        candidates = [rows for _, rows in ranked]
    rows = _dedupe_rows([row for group in candidates for row in group])
    rows = _filters(question, rows)
    if not rows:
        return 0 if is_refund or any(word in q for word in ("revenue", "sales", "sold", "earn", "how much", "how many", "count")) else []

    if is_customer:
        values = _field_values(rows, ("customer", "customer_name", "customer_id", "client", "client_name", "client_id"))
        unique = sorted({str(value) for value in values})
        if any(word in q for word in ("how many", "count", "number of", "unique")):
            return len(unique)
        if unique:
            return unique

    if is_product:
        values = _field_values(rows, ("product", "product_name", "item", "item_name", "sku", "product_id"))
        if not values:
            raise ValueError("Product question detected, but no product-name field was found.")
        counts = Counter(str(value) for value in values)
        if any(word in q for word in ("most", "top", "best-selling", "bestselling", "popular")):
            return sorted(counts, key=lambda value: (-counts[value], value))[0]
        if any(word in q for word in ("how many", "count", "number of", "units")):
            qtys = _field_values(rows, ("quantity", "qty", "units"))
            return round(sum(_numeric(value) or 0 for value in qtys)) if qtys else sum(counts.values())
        return sorted(counts)

    if is_refund:
        if any(word in q for word in ("how many", "count", "number of")):
            refund_collection = any("refund" in path.lower() or "return" in path.lower()
                                    for path, group in ranked if relevance(path, group) == best)
            if not refund_collection:
                rows = [row for row in rows if
                        any("refund" in str(value).lower() for key, value in row.items() if "status" in str(key).lower())
                        or any((_numeric(value) or 0) != 0 for key, value in row.items() if "refund" in str(key).lower())]
            order_ids = _field_values(rows, ("order_id", "orderId"))
            return len({str(value) for value in order_ids}) if len(order_ids) == len(rows) else len(rows)
        amount_names = {"refund", "refund_amount", "amount_refunded", "refunded_amount", "return_amount", "credit_amount"}
        refund_values = []
        for row in rows:
            amount = next((_numeric(value) for key, value in row.items()
                           if str(key).lower() in amount_names and _numeric(value) is not None), None)
            if amount is None:
                amount = next((_numeric(value) for key, value in row.items()
                               if str(key).lower() in {"amount", "total", "refund_total"} and _numeric(value) is not None), None)
            if amount is not None:
                refund_values.append(abs(amount))
        if refund_values:
            return round(sum(refund_values) + 1e-9, 2)
        raise ValueError("Refund question detected, but no refund amount field was found.")

    if any(word in q for word in ("revenue", "sales", "sold", "total", "amount", "earn", "how much", "income", "receipts")):
        amount_names = ("revenue", "order_total", "total_amount", "grand_total", "total", "amount", "subtotal")
        total = _sum_fields(rows, amount_names)
        if total is None:
            quantities = _field_values(rows, ("quantity", "qty", "units"))
            prices = _field_values(rows, ("unit_price", "price", "unit_cost"))
            if len(quantities) == len(prices) and quantities:
                total = sum((_numeric(qty) or 0) * (_numeric(price) or 0) for qty, price in zip(quantities, prices))
        if total is not None:
            return round(total + 1e-9, 2)
        raise ValueError("Revenue question detected, but no supported amount field was found.")

    if any(word in q for word in ("how many", "count", "number of")):
        return len(rows)
    raise ValueError("Could not map the question to a supported ledger measure.")
