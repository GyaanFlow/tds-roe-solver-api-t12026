"""Deterministic question engine for the Acme order ledger (q-ledger-agent-server).

The data rules come from the ledger root's own notes:
  * an order id can appear more than once; the row with the latest updated_at is current
  * business dates use the Asia/Kolkata timezone
  * only orders with status "paid" count as revenue
Money is converted with /rates `usd_per_unit` and reported in USD, rounded to the cent
after summation. Vocabulary (products, regions, customers, currencies) is learned from
each student's own data, so nothing here is specific to one student.
"""
from __future__ import annotations

import calendar
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

IST = timezone(timedelta(hours=5, minutes=30))
CENT = Decimal("0.01")
ACME_FIELDS = ("id", "customer", "region", "product", "qty", "amount", "currency", "status", "created_at", "updated_at")

_MONTH_NAMES = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3, "april": 4, "apr": 4,
    "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7, "august": 8, "aug": 8,
    "september": 9, "sept": 9, "sep": 9, "october": 10, "oct": 10, "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}
_FULL_MONTH = r"january|february|march|april|may|june|july|august|september|october|november|december"
_SHORT_MONTH = r"jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec"
_ORD = r"(?:st|nd|rd|th)?"
_CURRENCY_WORDS = {
    "usd": "USD", "dollar": "USD", "dollars": "USD", "us dollar": "USD", "us dollars": "USD",
    "eur": "EUR", "euro": "EUR", "euros": "EUR", "inr": "INR", "rupee": "INR", "rupees": "INR",
    "indian rupee": "INR", "indian rupees": "INR", "gbp": "GBP", "pound": "GBP", "pounds": "GBP",
}


class LedgerQuestionError(ValueError):
    pass


@dataclass(frozen=True)
class Order:
    id: str
    customer: str
    region: str
    product: str
    qty: Decimal
    amount: Decimal
    currency: str
    usd: Decimal
    status: str
    created: datetime
    day: date  # Asia/Kolkata business date


@dataclass
class Ledger:
    orders: list[Order]
    products: list[str]
    regions: list[str]
    customers: list[str]
    currencies: list[str]
    statuses: list[str]
    years: list[int]


# --------------------------------------------------------------------------- data

def _instant(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    # Naive timestamps are business-local per the ledger notes.
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=IST)


def _decimal(value: Any) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return Decimal(str(value).replace(",", "").replace("$", "").strip())
    except InvalidOperation:
        return None


def is_acme_row(row: Any) -> bool:
    return isinstance(row, dict) and all(key in row for key in ACME_FIELDS)


def build_ledger(rows: list[dict[str, Any]], rates: dict[str, Any] | None = None) -> Ledger:
    usd_per_unit = {"USD": Decimal(1)}
    for code, rate in (rates or {}).items():
        value = _decimal(rate)
        if value is not None:
            usd_per_unit[str(code).strip().upper()] = value

    # Latest updated_at wins (compared as instants: the feed mixes Z and +05:30).
    # On an exact tie the row seen later in the feed wins.
    current: dict[str, tuple[datetime, dict[str, Any]]] = {}
    for row in rows:
        if not is_acme_row(row):
            continue
        updated = _instant(row.get("updated_at")) or _instant(row.get("created_at"))
        if updated is None:
            continue
        key = str(row["id"]).strip()
        previous = current.get(key)
        if previous is None or updated >= previous[0]:
            current[key] = (updated, row)

    orders: list[Order] = []
    for key, (_, row) in current.items():
        created = _instant(row["created_at"])
        amount = _decimal(row["amount"])
        qty = _decimal(row["qty"])
        if created is None or amount is None:
            continue
        currency = str(row["currency"]).strip().upper()
        rate = usd_per_unit.get(currency)
        orders.append(Order(
            id=key,
            customer=str(row["customer"]).strip(),
            region=str(row["region"]).strip(),
            product=str(row["product"]).strip(),
            qty=qty if qty is not None else Decimal(0),
            amount=amount,
            currency=currency,
            usd=amount * rate if rate is not None else Decimal("NaN"),
            status=str(row["status"]).strip().lower(),
            created=created,
            day=created.astimezone(IST).date(),
        ))
    if not orders:
        raise LedgerQuestionError("The ledger contains no usable orders.")
    return Ledger(
        orders=orders,
        products=sorted({o.product for o in orders}),
        regions=sorted({o.region for o in orders}),
        customers=sorted({o.customer for o in orders}),
        currencies=sorted({o.currency for o in orders}),
        statuses=sorted({o.status for o in orders}),
        years=sorted({o.day.year for o in orders}),
    )


# ------------------------------------------------------------------------ parsing

@dataclass
class Query:
    measure: str = ""            # revenue | refund_amount | units | orders | customers | products | regions | avg_order | avg_units | max_order | min_order
    statuses: set[str] | None = None
    regions: set[str] = field(default_factory=set)
    not_regions: set[str] = field(default_factory=set)
    products: set[str] = field(default_factory=set)
    not_products: set[str] = field(default_factory=set)
    customers: set[str] = field(default_factory=set)
    currencies: set[str] = field(default_factory=set)
    start: date | None = None    # inclusive
    end: date | None = None      # exclusive
    group: str = ""              # product | customer | region | month | currency | day
    rank: str = ""               # max | min
    top_n: int = 1
    percent: bool = False
    all_products: bool = False   # "bought both X and Y"
    periods: list[tuple[date, date]] = field(default_factory=list)  # non-adjacent windows


def _phrase_regex(name: str) -> str:
    words = [re.escape(w) for w in re.findall(r"[a-z0-9]+", name.lower())]
    if not words:
        return r"(?!x)x"
    body = r"[\s\-_]*".join(words)
    return rf"(?<![a-z0-9]){body}(?:e?s)?(?:'s|s')?(?![a-z0-9])"


def _find_entities(text: str, names: list[str]) -> list[tuple[str, int, int]]:
    """Longest-name-first matching so 'Rice Cooker' never also matches 'Cooker'."""
    found: list[tuple[str, int, int]] = []
    taken: list[tuple[int, int]] = []
    for name in sorted(names, key=lambda n: -len(n)):
        for match in re.finditer(_phrase_regex(name), text):
            span = match.span()
            if any(span[0] < t[1] and t[0] < span[1] for t in taken):
                continue
            taken.append(span)
            found.append((name, *span))
    return found


def _negated(text: str, start: int) -> bool:
    window = text[max(0, start - 28):start]
    return bool(re.search(r"\b(?:excluding|exclude|except(?: for)?|other than|outside(?: of)?|apart from|besides|not|non)\W*(?:the\W+)?$", window))


def _month_end(year: int, month: int) -> date:
    return date(year + (month == 12), month % 12 + 1, 1)


@dataclass
class _Span:
    start: date
    end: date  # exclusive
    at: int
    to: int
    granular_day: bool = False


def _default_year(ledger: Ledger, month: int | None = None) -> int:
    if month is not None:
        years = [y for y in ledger.years if any(o.day.year == y and o.day.month == month for o in ledger.orders)]
        if years:
            return years[-1]
    return ledger.years[-1] if ledger.years else date.today().year


def _date_spans(q: str, ledger: Ledger) -> list[_Span]:
    spans: list[_Span] = []
    used: list[tuple[int, int]] = []

    def free(a: int, b: int) -> bool:
        return not any(a < y and x < b for x, y in used)

    def add(start: date, end: date, a: int, b: int, day: bool = False):
        used.append((a, b))
        spans.append(_Span(start, end, a, b, day))

    month_any = rf"(?:{_FULL_MONTH}|{_SHORT_MONTH})\.?"
    # ISO dates (2026-03-05, 2026/03/05)
    for m in re.finditer(r"\b(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})(?:t[\d:.]+z?)?\b", q):
        try:
            d = date(int(m[1]), int(m[2]), int(m[3]))
        except ValueError:
            continue
        add(d, d + timedelta(days=1), *m.span(), day=True)
    # March 5, 2026 / March 5th
    for m in re.finditer(rf"\b({month_any})\s+(\d{{1,2}}){_ORD}\b(?:,?\s*(20\d{{2}}))?", q):
        if not free(*m.span()):
            continue
        month = _MONTH_NAMES[m[1].rstrip(".")]
        year = int(m[3]) if m[3] else _default_year(ledger, month)
        try:
            d = date(year, month, int(m[2]))
        except ValueError:
            continue
        add(d, d + timedelta(days=1), *m.span(), day=True)
    # 5 March 2026 / 5th of March
    for m in re.finditer(rf"\b(\d{{1,2}}){_ORD}\s+(?:of\s+)?({month_any})(?:,?\s*(20\d{{2}}))?", q):
        if not free(*m.span()):
            continue
        month = _MONTH_NAMES[m[2].rstrip(".")]
        year = int(m[3]) if m[3] else _default_year(ledger, month)
        try:
            d = date(year, month, int(m[1]))
        except ValueError:
            continue
        add(d, d + timedelta(days=1), *m.span(), day=True)
    # 2026-03 / 03/2026
    for m in re.finditer(r"\b(20\d{2})[-/](\d{1,2})\b(?![-/]\d)", q):
        if free(*m.span()) and 1 <= int(m[2]) <= 12:
            add(date(int(m[1]), int(m[2]), 1), _month_end(int(m[1]), int(m[2])), *m.span())
    # Month [year] / month of year (full names always; short names and "may" need context)
    for m in re.finditer(rf"\b({_FULL_MONTH}|{_SHORT_MONTH})\b\.?(?:\s*(?:of\s+|,\s*)?(20\d{{2}}))?", q):
        if not free(*m.span()):
            continue
        word = m[1]
        if word == "may" or word in _SHORT_MONTH.split("|"):
            before = q[max(0, m.start() - 12):m.start()]
            if not m[2] and not re.search(r"(?:in|of|during|for|since|until|till|through|thru|before|after|from|to|between|and|or|by|,)\s*(?:the\s+month\s+of\s+)?$", before):
                continue
        month = _MONTH_NAMES[word]
        year = int(m[2]) if m[2] else _default_year(ledger, month)
        add(date(year, month, 1), _month_end(year, month), *m.span())
    # Quarters
    ordinal = {"first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "3rd": 3, "fourth": 4, "4th": 4, "last": 4, "final": 4}
    quarter_re = r"\bq([1-4])\b(?:\s*(?:of\s+)?(?:fy\s*)?(20\d{2}))?|\b(first|1st|second|2nd|third|3rd|fourth|4th|last|final)\s+quarter\b(?:\s*(?:of\s+)?(20\d{2}))?"
    for m in re.finditer(quarter_re, q):
        if not free(*m.span()):
            continue
        number = int(m[1]) if m[1] else ordinal[m[3]]
        year = int(m[2] or m[4]) if (m[2] or m[4]) else _default_year(ledger, 3 * number - 2)
        add(date(year, 3 * number - 2, 1), _month_end(year, 3 * number), *m.span())
    # Halves
    for m in re.finditer(r"\b(?:h([12])|(first|second|1st|2nd)\s+half)\b(?:\s*(?:of\s+)?(?:the\s+year\s+)?(20\d{2}))?", q):
        if not free(*m.span()):
            continue
        half = int(m[1]) if m[1] else (1 if m[2] in ("first", "1st") else 2)
        year = int(m[3]) if m[3] else _default_year(ledger, 6 * half - 5)
        add(date(year, 6 * half - 5, 1), _month_end(year, 6 * half), *m.span())
    # Bare years
    for m in re.finditer(r"\b(20\d{2})\b", q):
        if free(*m.span()):
            add(date(int(m[1]), 1, 1), date(int(m[1]) + 1, 1, 1), *m.span())
    return sorted(spans, key=lambda s: s.at)


def _apply_dates(q: str, ledger: Ledger, query: Query):
    spans = _date_spans(q, ledger)
    if not spans:
        return
    # Range "between A and B" / "from A to|through|until B" / "A - B"
    for first, second in zip(spans, spans[1:]):
        gap = q[first.to:second.at]
        before = q[max(0, first.at - 16):first.at]
        if re.fullmatch(r"\s*(?:and|to|through|thru|till|until|up to|-|–|—)\s*(?:the\s+end\s+of\s+|end\s+of\s+)?", gap) and (
            re.search(r"(?:between|from|of|for|during|in)\s+(?:the\s+)?(?:start\s+of\s+|beginning\s+of\s+)?$", before)
            or re.fullmatch(r"\s*(?:to|through|thru|till|until|-|–|—)\s*", gap)
        ):
            query.start, query.end = first.start, second.end
            return
    lower: date | None = None
    upper: date | None = None
    plain: list[_Span] = []
    for span in spans:
        before = q[max(0, span.at - 24):span.at]
        if re.search(r"(?:after|later than)\s+(?:the\s+end\s+of\s+)?$", before):
            lower = span.end
        elif re.search(r"(?:since|from|starting(?:\s+from|\s+in|\s+on)?|beginning|on or after|as of)\s+(?:the\s+start\s+of\s+)?$", before):
            lower = span.start
        elif re.search(r"(?:before|prior to|earlier than)\s+$", before):
            upper = span.start
        elif re.search(r"(?:until|till|through|thru|up to|up until|by|no later than|on or before|to the end of)\s+(?:the\s+end\s+of\s+)?$", before):
            upper = span.end
        else:
            plain.append(span)
    if lower or upper:
        query.start, query.end = lower, upper
        if plain and not (lower and upper):
            # "in 2026 since March" -> keep the containing window on the open side.
            container = plain[0]
            query.start = query.start or container.start
            query.end = query.end or container.end
        return
    if plain:
        # Several plain periods ("in March or April") are combined into one window.
        query.start = min(s.start for s in plain)
        query.end = max(s.end for s in plain)
        if len(plain) > 1 and not all(
            any(o.start == p.end or o.end == p.start for o in plain if o is not p) for p in plain
        ):
            # Non-adjacent periods: keep only rows within any of them.
            query.start, query.end = None, None
            query.periods = [(s.start, s.end) for s in plain]


def _has(q: str, pattern: str) -> bool:
    return re.search(pattern, q) is not None


def parse_question(question: str, ledger: Ledger) -> Query:
    q = " " + re.sub(r"\s+", " ", question.lower().replace("’", "'").replace("“", '"').replace("”", '"')) + " "
    query = Query()

    # ---- entities
    for name, a, _ in _find_entities(q, ledger.products):
        (query.not_products if _negated(q, a) else query.products).add(name)
    region_names = ledger.regions
    for name in sorted(region_names, key=lambda n: -len(n)):
        for m in re.finditer(rf"(?<![a-z0-9]){re.escape(name.lower())}(?:ern|ern region|\s+region|\s+zone)?(?![a-z0-9])", q):
            (query.not_regions if _negated(q, m.start()) else query.regions).add(name)
    # Customer ids are matched case-sensitively and must look like identifiers, so
    # an id such as "A" never matches the article in "bought a Juicer".
    for customer in ledger.customers:
        if (len(customer) >= 3 or re.search(r"\d", customer)) and re.search(
                rf"(?<![A-Za-z0-9]){re.escape(customer)}(?![A-Za-z0-9])", question):
            query.customers.add(customer)

    # Currency filters. Money is always answered in USD, so "in USD"/"in US dollars"
    # is a unit, not a filter, unless phrased as a property of the orders.
    cur_alt = "|".join(sorted((re.escape(w) for w in _CURRENCY_WORDS), key=len, reverse=True))
    for m in re.finditer(rf"(?<![a-z])({cur_alt})(?![a-z])", q):
        code = _CURRENCY_WORDS[m[1]]
        if code not in ledger.currencies:
            continue
        before, after = q[max(0, m.start() - 30):m.start()], q[m.end():m.end() + 30]
        property_phrase = (
            re.search(r"(?:paid|priced|billed|charged|denominated|transacted|invoiced|settled|placed|made|booked|recorded)\s+(?:in|with|using)\s+(?:the\s+)?$", before)
            or re.search(r"(?:currency|currency of|currency is|currency =|currency:)\s*$", before)
            or re.match(r"[\s\-]*(?:-?denominated|orders?|transactions?|sales|purchases|payments|invoices|currency|priced|billed)\b", after)
        )
        if code == "USD":
            if property_phrase:
                query.currencies.add(code)
        elif not re.search(r"(?:converted|convert|expressed|reported|answer|value|worth)\s+(?:to|in|into)\s+$", before):
            # Answers are always USD, so a non-USD currency names the orders' currency.
            query.currencies.add(code)

    # ---- dates
    _apply_dates(q, ledger, query)

    # ---- explicit status words
    statuses: set[str] = set()
    if _has(q, r"\b(?:refund\w*|returned|reimburs\w*|charge-?backs?)\b"):
        statuses.add("refunded")
    if _has(q, r"\b(?:void\w*|cancel\w*|annul\w*)\b"):
        statuses.add("void")
    if _has(q, r"\b(?:paid|completed|successful|settled|fulfilled)\b"):
        statuses.add("paid")
    any_status = _has(q, r"\b(?:all|any|every|regardless of|irrespective of|including all)\s+(?:order\s+)?status(?:es)?\b|\btotal number of orders\b|\ball orders\b|\bincluding (?:refunded|void\w*|cancel\w*)")

    # ---- percent / share
    query.percent = _has(q, r"\b(?:percent\w*|percentage|share|proportion|fraction|ratio)\b|%")

    # ---- grouping / ranking
    group_patterns = [
        ("product", r"\b(?:products?|items?|skus?|appliances?|models?|goods|merchandise)\b"),
        ("customer", r"\b(?:customers?|clients?|buyers?|shoppers?|purchasers?|accounts?)\b|\bwho\b"),
        ("region", r"\b(?:regions?|areas?|territor\w+|zones?|markets?|locations?)\b"),
        ("month", r"\bmonths?\b"),
        ("day", r"\b(?:days?|dates?)\b"),
        ("currency", r"\bcurrenc(?:y|ies)\b"),
    ]
    rank_max = r"\b(?:most|highest|largest|biggest|greatest|top|best|leading|max(?:imum)?|peak|strongest|best-?selling|popular|more|higher|greater|bigger)\b"
    rank_min = r"\b(?:least|lowest|smallest|fewest|worst|min(?:imum)?|weakest|bottom|slowest|fewer|less|lower)\b"
    which = r"\b(?:which|what|who|whose|name|identify|list|top)\b"
    has_rank = (_has(q, rank_max) or _has(q, rank_min)) and not _has(q, r"\b(?:more|less|fewer|greater|higher|lower) than\b")
    if has_rank and _has(q, which):
        # Prefer the noun closest after the interrogative ("which region's customers ...").
        best: tuple[int, str] | None = None
        for name, pattern in group_patterns:
            for m in re.finditer(pattern, q):
                lead = re.search(r"\b(?:which|what|who|whose|name|identify|list|top(?:\s+\d+|\s+\w+)?)\W+(?:[\w-]+\W+){0,3}$", q[:m.start()])
                if lead or m.group(0) == "who":
                    if best is None or m.start() < best[0]:
                        best = (m.start(), name)
                    break
        if best is None:
            for name, pattern in group_patterns:
                if _has(q, pattern):
                    best = (0, name)
                    break
        if best:
            query.group = best[1]
            query.rank = "min" if _has(q, rank_min) and not _has(q, r"\bat least\b") else "max"
            top = re.search(r"\btop\s+(\d+|two|three|four|five)\b", q)
            if top:
                query.top_n = {"two": 2, "three": 3, "four": 4, "five": 5}.get(top[1]) or int(top[1])

    # ---- measure
    money = r"\b(?:revenue|revenues|sales value|sales amount|turnover|income|earn\w*|gross|takings|money|dollars?|usd|value|worth|spen[dt]\w*|paid out|receipts|billings?|grossed|made|generat\w*|brought in|bring in|total sales|net sales|sales)\b|\$"
    count_words = r"\b(?:how many|number of|count|counts|total number|tally|quantity of orders)\b"
    units = r"\b(?:units?|quantity|quantities|qty|pieces|items sold|volume)\b"
    order_noun = r"\b(?:orders?|transactions?|purchases?|sales|bookings?|invoices?)\b"
    customer_noun = r"\b(?:customers?|clients?|buyers?|shoppers?|purchasers?|accounts?|people)\b"
    avg = r"\b(?:average|avg|mean|typical|per order|aov)\b"
    is_count = _has(q, count_words)
    refund_money = _has(q, r"\b(?:refund(?:ed)?\s+(?:amount|value|total|sum|money|revenue|dollars?|usd)|amount\s+refunded|value\s+of\s+refund\w*|refund\w*\s+(?:in|worth)\s+(?:usd|us dollars|dollars)|how much\b.*\brefund\w*|total\s+refund\w*|refund\w*\s+totall?ed|sum\s+of\s+refund\w*|money\s+(?:was\s+)?refunded|dollars?\s+(?:was\s+|were\s+)?refunded|usd\s+(?:was\s+|were\s+)?refunded)\b")

    if query.group:
        if _has(q, r"\brefund\w*|\breturn\w*") and not _has(q, money) and not refund_money:
            query.measure = "orders"
        elif refund_money or (_has(q, r"\brefund\w*") and _has(q, money)):
            query.measure = "refund_amount"
        elif _has(q, units) or _has(q, r"\b(?:sold the most|sells the most|sold most|best-?selling|most popular|popular|most sold|top-?selling|sold the least|least sold|moved)\b") and not _has(q, money):
            query.measure = "units"
        elif _has(q, r"\b(?:orders?|transactions?|purchases?|bookings?)\b") and (_has(q, r"\b(?:most|fewest|least|highest number|largest number|greatest number|lowest number)\s+(?:number\s+of\s+)?(?:\w+\s+)?(?:orders?|transactions?|purchases?|bookings?)\b") or is_count) and not _has(q, money):
            query.measure = "orders"
        elif query.group == "customer" and _has(q, r"\b(?:ordered|order|bought|buy|purchased)\s+(?:the\s+)?(?:most|least)\b") and not _has(q, money):
            query.measure = "orders"
        else:
            query.measure = "revenue"
    elif _has(q, avg) and _has(q, r"\b(?:units?|quantity|qty|items)\b") and not _has(q, r"\bvalue\b"):
        query.measure = "avg_units"
    elif _has(q, avg) and not (is_count and _has(q, customer_noun)):
        query.measure = "avg_order"
    elif _has(q, r"\b(?:largest|biggest|highest|most expensive|maximum|max)\s+(?:single\s+)?(?:order|transaction|purchase|sale)\b"):
        query.measure = "max_order"
    elif _has(q, r"\b(?:smallest|lowest|cheapest|minimum|min)\s+(?:single\s+)?(?:order|transaction|purchase|sale)\b"):
        query.measure = "min_order"
    elif is_count and _has(q, r"\b(?:different|distinct|unique)?\s*(?:products?|items?|skus?)\b") and _has(q, r"\b(?:different|distinct|unique|kinds?|types?)\b") and not _has(q, customer_noun):
        query.measure = "products"
    elif is_count and _has(q, r"\bregions?\b") and _has(q, r"\b(?:different|distinct|unique)\b"):
        query.measure = "regions"
    elif (is_count or _has(q, r"\b(?:distinct|unique)\b")) and _has(q, customer_noun):
        query.measure = "customers"
    elif refund_money:
        query.measure = "refund_amount"
    elif any(re.search(rf"\b(?:how many|number of|count of|total)\s+(?:[a-z]+\s+)?{_phrase_regex(p)}(?!\s+(?:orders?|transactions?|purchases?|refunds?|customers?|buyers?))", q)
             for p in query.products):
        # "How many Juicers were sold" counts units of the product, not orders.
        query.measure = "units"
    elif is_count and _has(q, order_noun):
        query.measure = "orders"
    elif is_count and _has(q, r"\brefund\w*|\breturns?\b|\bvoid\w*|\bcancel\w*") and not _has(q, units):
        query.measure = "orders"
    elif is_count and (_has(q, units) or query.products or _has(q, r"\b(?:sold|items)\b")):
        query.measure = "units"
    elif _has(q, units) and _has(q, r"\b(?:total|sum|sold|how much)\b"):
        query.measure = "units"
    elif is_count and _has(q, r"\brefund\w*|\breturns?\b|\bvoid\w*|\bcancel\w*"):
        query.measure = "orders"
    elif _has(q, r"\brefund\w*") and _has(q, r"\b(?:how much|total|sum|amount|value|usd|dollars?)\b|\$"):
        query.measure = "refund_amount"
    elif _has(q, money) or _has(q, r"\bhow much\b|\btotal\b"):
        query.measure = "revenue"
    elif is_count:
        query.measure = "orders"
    else:
        raise LedgerQuestionError("Could not identify what to measure (revenue, refunds, units, orders, customers).")

    # ---- status scope per measure
    if query.measure == "refund_amount":
        query.statuses = {"refunded"}
    elif query.measure in {"revenue", "avg_order", "max_order", "min_order"}:
        query.statuses = {"paid"} if not (statuses - {"paid"}) or "paid" in statuses else statuses
        if query.measure == "revenue" and statuses == {"refunded"}:
            query.measure, query.statuses = "refund_amount", {"refunded"}
    elif query.measure == "units":
        query.statuses = statuses or {"paid"}
    elif any_status:
        query.statuses = None
    elif statuses:
        query.statuses = statuses
    elif query.measure == "customers":
        buying = _has(q, r"\b(?:bought|buy|buying|purchas\w*|paying|paid|spent|spend\w*|shopp\w*|revenue|customers? who paid)\b")
        query.statuses = {"paid"} if buying else None
    elif query.measure == "orders" and _has(q, r"\b(?:sold|sales|purchases|revenue|completed|successful)\b"):
        query.statuses = {"paid"}
    else:
        query.statuses = None

    query.all_products = len(query.products) > 1 and query.measure == "customers" and _has(q, r"\b(?:both|all of|each of|as well as)\b")
    return query


# ---------------------------------------------------------------------- execution

def _money(value: Decimal) -> float:
    if value.is_nan():
        raise LedgerQuestionError("An order uses a currency with no USD rate.")
    return float(value.quantize(CENT, rounding=ROUND_HALF_UP))


def _select(ledger: Ledger, query: Query, *, ignore_entities: bool = False, ignore_group_entity: bool = False) -> list[Order]:
    periods = query.periods
    selected = []
    for order in ledger.orders:
        if query.statuses is not None and order.status not in query.statuses:
            continue
        if query.start and order.day < query.start:
            continue
        if query.end and order.day >= query.end:
            continue
        if periods and not any(a <= order.day < b for a, b in periods):
            continue
        if not ignore_entities:
            if query.regions and not (ignore_group_entity and query.group == "region") and order.region not in query.regions:
                continue
            if query.products and not query.all_products and not (ignore_group_entity and query.group == "product") and order.product not in query.products:
                continue
            if query.customers and not (ignore_group_entity and query.group == "customer") and order.customer not in query.customers:
                continue
            if query.currencies and order.currency not in query.currencies:
                continue
        if order.region in query.not_regions or order.product in query.not_products:
            continue
        selected.append(order)
    return selected


def _measure(orders: list[Order], measure: str) -> Decimal:
    if measure in {"revenue", "refund_amount"}:
        return sum((o.usd for o in orders), Decimal(0))
    if measure == "units":
        return sum((o.qty for o in orders), Decimal(0))
    if measure == "orders":
        return Decimal(len(orders))
    if measure == "customers":
        return Decimal(len({o.customer for o in orders}))
    raise LedgerQuestionError(f"Unsupported grouped measure {measure}.")


def _format(measure: str, value: Decimal) -> Any:
    if measure in {"revenue", "refund_amount", "avg_order", "max_order", "min_order"}:
        return _money(value)
    if measure == "avg_units":
        return float(value.quantize(CENT, rounding=ROUND_HALF_UP))
    integral = value.to_integral_value()
    return int(integral) if integral == value else float(value)


def execute(query: Query, ledger: Ledger) -> Any:
    if query.group:
        rows = _select(ledger, query, ignore_group_entity=True)
        groups: dict[str, list[Order]] = {}
        for order in rows:
            if query.group == "month":
                key = order.day.strftime("%B %Y") if len(ledger.years) > 1 else calendar.month_name[order.day.month]
            elif query.group == "day":
                key = order.day.isoformat()
            else:
                key = getattr(order, query.group)
            groups.setdefault(key, []).append(order)
        if query.group == "product" and query.products and len(query.products) > 1:
            groups = {k: v for k, v in groups.items() if k in query.products}
        if query.group == "region" and query.regions and len(query.regions) > 1:
            groups = {k: v for k, v in groups.items() if k in query.regions}
        if not groups:
            return None
        totals = {key: _measure(value, query.measure) for key, value in groups.items()}
        ordered = sorted(totals, key=lambda key: (totals[key], key) if query.rank == "min" else (-totals[key], key))
        return ordered[0] if query.top_n == 1 else ordered[:query.top_n]

    orders = _select(ledger, query)
    if query.measure == "customers" and query.all_products:
        sets = [{o.customer for o in orders if o.product == name} for name in query.products]
        return len(set.intersection(*sets)) if sets else 0
    if query.measure in {"avg_order", "avg_units"}:
        if not orders:
            return 0
        total = sum(((o.usd if query.measure == "avg_order" else o.qty) for o in orders), Decimal(0))
        return _format(query.measure, total / len(orders))
    if query.measure in {"max_order", "min_order"}:
        if not orders:
            return 0
        pick = max if query.measure == "max_order" else min
        return _money(pick(o.usd for o in orders))
    if query.measure == "products":
        return len({o.product for o in orders})
    if query.measure == "regions":
        return len({o.region for o in orders})
    value = _measure(orders, query.measure)
    if query.percent:
        whole = _measure(_select(ledger, query, ignore_entities=True), query.measure)
        if whole == 0:
            return 0
        return float((value * 100 / whole).quantize(CENT, rounding=ROUND_HALF_UP))
    return _format(query.measure, value)


def answer(question: str, ledger: Ledger) -> Any:
    return execute(parse_question(question, ledger), ledger)


def explain(question: str, ledger: Ledger) -> dict[str, Any]:
    query = parse_question(question, ledger)
    return {
        "measure": query.measure, "statuses": sorted(query.statuses) if query.statuses else "any",
        "regions": sorted(query.regions), "not_regions": sorted(query.not_regions),
        "products": sorted(query.products), "not_products": sorted(query.not_products),
        "customers": sorted(query.customers), "currencies": sorted(query.currencies),
        "start": query.start.isoformat() if query.start else None,
        "end_exclusive": query.end.isoformat() if query.end else None,
        "group": query.group, "rank": query.rank, "top_n": query.top_n, "percent": query.percent,
        "answer": execute(query, ledger),
    }
