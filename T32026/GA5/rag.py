"""Q1 ``q-rag-colosseum-server``: provider-free RAG over the student's 50-passage knowledge base.

The KB is regenerated from the email seed (see ``kb.py``), so every passage, its entity and its slot
values are known exactly. A question is answered in four steps:

1. strip prompt-injection clauses from the question (it is only ever *data*),
2. find the entity (named alias, then lexical TF-IDF fallback),
3. detect the asked attribute (quorum, port, timeout, ...) and read its value from the entity's own
   passage, abstaining when that passage has no such attribute,
4. for several entities ("compare A and B") combine each passage's value and state the comparison.

Scores are TF-IDF cosine similarities scaled into [0, 1]; ``confidence`` is high only when answering.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from T32026.GA5.kb import rag_knowledge_base

# --------------------------------------------------------------------------- entity table
# (primary aliases, secondary aliases) for the 50 templates, in template order.
ENTITIES: list[tuple[str, list[str], list[str]]] = [
    ("Raft", ["raft"], ["etcd"]),
    ("Multi-Paxos", ["multi-paxos", "multipaxos", "multi paxos", "paxos"], ["chubby", "zookeeper"]),
    ("Gossip protocol", ["gossip", "epidemic", "phi accrual", "phi-accrual"], []),
    ("SWIM", ["swim"], ["consul"]),
    ("Two-phase commit", ["two-phase commit", "two phase commit", "2pc", "three-phase commit", "3pc"], []),
    ("Saga pattern", ["saga", "sagas"], ["cadence"]),
    ("Consistent hashing", ["consistent hashing", "consistent hash", "hash ring"], ["dynamo"]),
    ("Rendezvous hashing", ["rendezvous", "highest random weight", "hrw"], []),
    ("Vector clocks", ["vector clock", "vector clocks", "version vector"], ["riak"]),
    ("Hybrid logical clocks", ["hybrid logical clock", "hybrid logical clocks", "hlc"], []),
    ("Stochastic gradient descent", ["stochastic gradient descent", "sgd"], []),
    ("AdamW", ["adamw", "adam w"], ["adam"]),
    ("Transformer encoder", ["transformer encoder", "transformer encoders", "encoder stack", "bidirectional encoder"], ["encoder", "encoders"]),
    ("Autoregressive decoder", ["autoregressive", "transformer decoder", "decoder-only", "decoder only"], ["decoder", "decoders", "llama"]),
    ("Logistic regression", ["logistic regression", "logistic"], ["sigmoid"]),
    ("Support vector machine", ["support vector", "svm", "svms"], []),
    ("Multi-layer perceptron", ["multi-layer perceptron", "multilayer perceptron", "perceptron", "mlp"], ["feedforward"]),
    ("Residual network", ["residual convolutional", "residual network", "resnet", "convnext"], ["residual"]),
    ("Batch normalization", ["batch normalization", "batchnorm", "batch norm"], []),
    ("Layer normalization", ["layer normalization", "layernorm", "layer norm"], []),
    ("PostgreSQL", ["postgresql", "postgres", "pgbouncer"], []),
    ("MySQL InnoDB", ["mysql", "innodb"], []),
    ("B+ tree", ["b+ tree", "b+tree", "b-tree", "btree", "b plus tree"], []),
    ("LSM tree", ["log-structured merge", "lsm", "rocksdb", "sstable"], []),
    ("MongoDB", ["mongodb", "mongo", "wiredtiger"], []),
    ("Apache Cassandra", ["apache cassandra", "cassandra", "cql"], []),
    ("Redis", ["redis"], []),
    ("Memcached", ["memcached"], []),
    ("Write-ahead logging", ["write-ahead", "write ahead", "wal", "aries"], []),
    ("Shadow paging", ["shadow paging", "shadow page", "shadow copy"], []),
    ("TCP", ["transmission control protocol", "tcp"], []),
    ("QUIC", ["quic"], []),
    ("DNS", ["domain name system", "dns", "dnssec"], []),
    ("Multicast DNS", ["multicast dns", "mdns", "bonjour", "avahi"], []),
    ("HTTP/2", ["http/2", "http2", "http 2", "hpack"], []),
    ("HTTP/3", ["http/3", "http3", "http 3", "qpack"], []),
    ("TLS 1.3", ["tls 1.3", "tls1.3", "tls v1.3", "transport layer security"], []),
    ("TLS 1.2", ["tls 1.2", "tls1.2", "tls v1.2"], []),
    ("BGP", ["border gateway protocol", "bgp"], []),
    ("OSPF", ["open shortest path first", "ospf"], []),
    ("Public key cryptography", ["public key cryptography", "public-key cryptography", "public key", "rsa"], []),
    ("Elliptic curve cryptography", ["elliptic curve", "ecc", "ecdsa", "ed25519"], []),
    ("Password hashing", ["credential storage", "password hashing", "secure credential", "salting", "argon2"], []),
    ("PBKDF2", ["pbkdf2"], []),
    ("Web application firewall", ["web application firewall", "waf"], []),
    ("API gateway rate limiting", ["api gateway", "api gateways", "token bucket"], ["kong"]),
    ("AES", ["advanced encryption standard", "aes-gcm", "aes"], []),
    ("ChaCha20-Poly1305", ["chacha20", "poly1305", "chacha"], []),
    ("OAuth PKCE", ["pkce", "proof key for code exchange", "oauth"], []),
    ("JSON Web Tokens", ["json web token", "json web tokens", "jwt"], []),
]

# attribute -> slot name, with the words that ask for it
ATTRIBUTES: list[tuple[str, str, str]] = [
    # (slot, strong cues, weak hints)
    ("QUORUM", r"\bquorum\b|\backnowledg\w*|\bretr(?:y|ies)\b|\bacceptors?\b|how many (?:nodes|services|replicas)", r"\breplicas?\b|\bparticipants?\b|\bmembers\b"),
    ("HEARTBEAT_MS", r"\bheartbeats?\b|\bping interval\b|\bprobe interval\b|\bread repair\b|\brepair interval\b|\binterval\b", r"(?!x)x"),
    ("TIMEOUT_MS", r"\btime[- ]?outs?\b|\bttl\b|\blease\b|\bdeadline\b|\bwait (?:time|duration)\b|\bretry-after\b|\bdead interval\b|\bkeepalive\b|\brto\b|\blatency budget\b", r"\bwindow\b|\bexpir\w*|\bskew\b|\bhandshake\b"),
    ("THRESHOLD", r"\bthreshold\b|\bratio\b|\bsaturation\b|\bdropout\b|\bprobability\b|\bslack\b|\bburst\b|\bvariance\b|\bcorrelation\b|\butili[sz]ation\b", r"\bcapacity\b|\bcredits?\b"),
    ("BATCH_SIZE", r"\bbatch(?:es)?\b|\bchunks?\b|\bbytes per\b|\brecords per\b|\bper fsync\b|\bper step\b|\btokens per\b", r"\bgroups?\b|\bexamples\b|\bsamples\b"),
    ("LEARNING_RATE", r"\blearning[- ]rate\b|\blr\b|\bstep size\b|\bwarm-?up\b", r"(?!x)x"),
    ("LAYER_COUNT", r"\blayers?\b|\bblocks?\b", r"\bdepth\b|\bstack\b"),
    ("PORT", r"\bports?\b|\blisten\w*|\bbind\w*", r"(?!x)x"),
    ("KEY_BITS", r"\bkey (?:size|length|bits?)\b|\bbits?\b|\bkey-size\b|\bsecurity level\b|\bmodulus\b", r"(?!x)x"),
    ("HASH_ALG", r"\bhash(?:es|ing)?\b|\bdigests?\b|\bsha(?:-?\d+)?\b|\bblake2?\b", r"\balgorithms?\b|\bprimitives?\b|\bfunctions?\b"),
]
_ATTR_STRONG = {slot: re.compile(strong, re.I) for slot, strong, _ in ATTRIBUTES}
_ATTR_WEAK = {slot: re.compile(weak, re.I) for slot, _, weak in ATTRIBUTES}
_ATTR_RE = {slot: re.compile(f"(?:{strong})|(?:{weak})", re.I) for slot, strong, weak in ATTRIBUTES}

# words that never count as content
_STOP = set("""a an the of to in on for with by from at as is are was were be been being do does did what which who whom whose how
when where why that this these those it its into over under about per than then so such can could should would will shall may might
must not no yes and or but if else value values number default configured used use using need needs required require requires
tell me please give state specify say kb knowledge base passage passages system according stated state
explain describe overview summarize summary mean means meaning purpose regarding about know does doing work works""".split())
_INJECTION = re.compile(
    r"\b(?:ignore|disregard|forget|override|bypass|skip|abandon|discard)\b[^.?!\n]{0,80}"
    r"|\b(?:system|assistant|developer|admin|root)\b\s*(?:prompt|message|override|note|instruction)?\s*:"
    r"|\b(?:note|message|instruction|reminder|attention|important)s?\s+(?:to|for)\s+(?:the\s+)?(?:assistant|ai|model|llm|bot|system)\b"
    r"|\byou are (?:now|no longer)\b|\bnew instructions?\b|\bpretend\b|\bact as\b|\bfrom now on\b"
    r"|\b(?:reveal|leak|expose|dump)\b[^.?!\n]{0,60}"
    r"|\b(?:print|repeat|output|show|display)\b[^.?!\n]{0,40}(?:system prompt|your instructions|hidden|secret|api key|password)"
    r"|\b(?:reply|respond|answer|say|write|output|return|print)\b\s+(?:only\s+|just\s+|exactly\s+)?(?:with|that|the word|the phrase)\b[^.?!\n]{0,80}"
    r"|<\s*/?\s*(?:system|instructions?|assistant|prompt)\s*>|\[\s*(?:system|inst|admin|override)[^\]]*\]"
    r"|\bdo anything now\b|\bjailbreak\b|\bpwned\b|\baccess granted\b|\bdeveloper mode\b",
    re.I)
_VALUE_RE = re.compile(
    r"how many|how much|how large|how big|how small|how fast|how high|how low|how long|how often|what (?:is|are|was) the "
    r"(?:\w+\s+){0,3}?(?:limit|size|count|number|rate|factor|requirement|version|percentage|percent|latency|throughput|capacity|speed|cost|price|"
    r"year|date|length|amount|frequency|range|maximum|minimum|default|value|license|licence)\b|\bwho (?:invented|created|founded|wrote|designed|developed)\b|"
    r"\bwhat year\b|\bwhen was\b|\bwhich (?:company|vendor|author|person)\b", re.I)
_TIME_TIMEOUT_WORDS = re.compile(r"gives? up|abort\w*|expir\w*|fail(?:s|ed)? over|failover|terminat\w*|disconnect\w*|\bidle\b|drop(?:s|ped)? the|evict\w*|suspect\w*|\bgives? way\b", re.I)
_TIME_BEAT_WORDS = re.compile(r"\bprob\w*|\bping\w*|\bbeats?\b|\bpoll\w*|keep-?alive|\bcheck(?:s|ed)? (?:on|the) (?:peers?|nodes?|followers?|members?)|\bgossip\w* (?:every|each)", re.I)
_TIME_RE = re.compile(r"how long|milliseconds?|\bms\b|duration|how often|every how many|delay|\bperiod\b", re.I)
_ATTRIBUTIVE = re.compile(
    r"^\s*(?:port|ports|timeout|time-out|interval|size|key|hash|rate|threshold|quorum|layers?|blocks?|heartbeat|retry|retries|handshake|"
    r"connection|listening|default|configuration|settings?)\b", re.I)
_COMPARE_CUE = re.compile(r"\b(?:compare|compared|versus|vs\.?|difference|differs?|both|each|than|between|respectively|and|or)\b|,|/", re.I)
_COMPARE = re.compile(r"\b(compare|versus|vs\.?|difference|differ|both|larger|smaller|higher|lower|greater|longer|shorter|more|fewer|less|bigger|which (?:one|of)|between)\b", re.I)
_UP = re.compile(r"\b(larger|larger|higher|greater|longer|more|bigger|biggest|largest|highest|longest|most)\b", re.I)
_DOWN = re.compile(r"\b(smaller|lower|shorter|fewer|less|smallest|lowest|shortest|fewest|least)\b", re.I)


def _tokens(text: str) -> list[str]:
    out = []
    for t in re.findall(r"[a-z0-9][a-z0-9+./#-]*", text.lower()):
        t = t.strip(".-/")
        if not t:
            continue
        out.append(t)
        if t.endswith("s") and len(t) > 3:
            out.append(t[:-1])
    return out


def _content(text: str) -> list[str]:
    return [t for t in _tokens(text) if t not in _STOP and len(t) > 1]


def strip_injection(question: str) -> str:
    """Remove embedded instructions; the remainder is the real question."""
    text = str(question or "")
    # parentheticals/brackets that carry an instruction are dropped whole
    text = re.sub(r"[\(\[\{][^\)\]\}]*[\)\]\}]", lambda m: " " if _INJECTION.search(m.group()) else m.group(), text)
    # then any sentence that issues an instruction
    sentences = re.split(r"(?<=[.?!])\s+|\n+", text)
    kept = [x for x in sentences if x.strip() and not _INJECTION.search(x)]
    if not kept:
        return ""
    cleaned = " ".join(kept)
    cleaned = re.sub(r"\(\s*\)|\[\s*\]|\{\s*\}", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip(" ,;:-")


@dataclass
class Passage:
    index: int
    text: str
    domain: str
    slots: dict[str, str]
    entity: str
    primary: list[str]
    secondary: list[str]
    sentences: list[str] = field(default_factory=list)
    tf: Counter = field(default_factory=Counter)
    norm: float = 0.0


class KnowledgeBase:
    def __init__(self, email: str):
        raw = rag_knowledge_base(email)
        self.passages: list[Passage] = []
        for i, (text, domain, slots) in enumerate(zip(raw["passages"], raw["domains"], raw["tokens"])):
            name, primary, secondary = ENTITIES[i]
            sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
            self.passages.append(Passage(i, text, domain, slots, name, primary, secondary, sents))
        df: Counter = Counter()
        for p in self.passages:
            p.tf = Counter(_content(p.text))
            df.update(p.tf.keys())
        n = len(self.passages)
        self.idf = {t: math.log(1 + n / c) for t, c in df.items()}
        # in how many passages does a word stem occur? (rare words name concepts, common ones are generic)
        stem_df: Counter = Counter()
        for p in self.passages:
            stem_df.update({t[:5] for t in p.tf})
        self.stem_df = stem_df
        for p in self.passages:
            p.norm = math.sqrt(sum((c * self.idf[t]) ** 2 for t, c in p.tf.items())) or 1.0

    # -- scoring ---------------------------------------------------------------------------
    def cosine(self, question: str) -> list[float]:
        q = Counter(_content(question))
        qn = math.sqrt(sum((c * self.idf.get(t, 1.0)) ** 2 for t, c in q.items())) or 1.0
        scores = []
        for p in self.passages:
            dot = sum(c * self.idf.get(t, 1.0) * p.tf.get(t, 0) * self.idf.get(t, 1.0) for t, c in q.items())
            scores.append(dot / (qn * p.norm))
        return scores

    # -- entity detection ------------------------------------------------------------------
    @staticmethod
    def _alias_hits(text_lc: str, aliases: list[str]) -> int:
        best = 0
        for alias in aliases:
            pat = r"(?<![a-z0-9+])" + re.escape(alias) + r"(?![a-z0-9])"
            if re.search(pat, text_lc):
                best = max(best, len(alias))
        return best

    def entities_in(self, question: str) -> list[tuple[Passage, float]]:
        lc = question.lower()
        found: list[tuple[Passage, float]] = []
        for p in self.passages:
            primary = self._alias_hits(lc, p.primary)
            secondary = self._alias_hits(lc, p.secondary)
            if primary:
                weight = 10 + primary / 100
                # "What TCP port does DNS bind to?": TCP modifies "port", it is not the subject
                for alias in p.primary:
                    m = re.search(r"(?<![a-z0-9+])" + re.escape(alias) + r"(?![a-z0-9])(.*)$", lc)
                    if m and len(alias) == primary and _ATTRIBUTIVE.match(m.group(1)):
                        weight -= 6
                        break
                found.append((p, weight))
            elif secondary:
                found.append((p, 3 + secondary / 100))
        # a longer alias shadows a contained shorter one ("tls 1.3" vs "tls", "mdns" vs "dns", "http/3" vs "http")
        keep = []
        for p, w in found:
            longest = max((a for a in p.primary + p.secondary if a in lc), key=len, default="")
            shadowed = any(
                other is not p and longest and longest in (max((a for a in other.primary + other.secondary if a in lc), key=len, default=""))
                and len(max((a for a in other.primary + other.secondary if a in lc), key=len, default="")) > len(longest)
                for other, _ in found
            )
            if not shadowed:
                keep.append((p, w))
        return sorted(keep, key=lambda x: -x[1])

    # -- attribute detection ---------------------------------------------------------------
    @staticmethod
    def weak_attributes_in(question: str) -> list[str]:
        return [slot for slot, rx in _ATTR_WEAK.items() if rx.search(question)]

    @staticmethod
    def attributes_in(question: str) -> list[str]:
        found = [slot for slot, rx in _ATTR_STRONG.items() if rx.search(question)]
        # "how long", "in milliseconds", "how often" ask for a time-valued slot without naming it
        if _TIME_RE.search(question) and "HEARTBEAT_MS" not in found and "TIMEOUT_MS" not in found:
            if _TIME_TIMEOUT_WORDS.search(question):
                found += ["TIMEOUT_MS"]            # "before X gives up", "after how many ms does X abort"
            elif _TIME_BEAT_WORDS.search(question):
                found += ["HEARTBEAT_MS"]          # "how often does X probe peers"
            elif re.search(r"how often|every how many|per second|period", question, re.I):
                found += ["HEARTBEAT_MS", "TIMEOUT_MS"]
            else:
                found += ["TIMEOUT_MS", "HEARTBEAT_MS"]
        return found


def _unit(slot: str, sentence: str, value: str) -> str:
    if slot in ("HEARTBEAT_MS", "TIMEOUT_MS") and re.search(re.escape(value) + r"\s*ms", sentence):
        return f"{value}ms"
    return value


def _slot_sentence(p: Passage, slot: str) -> str | None:
    value = p.slots.get(slot)
    if value is None:
        return None
    for s in p.sentences:
        if value in s:
            return s
    return None


def _best_sentence(p: Passage, q_terms: set[str]) -> tuple[str, float]:
    best, best_score = p.sentences[0], -1.0
    for s in p.sentences:
        terms = set(_content(s))
        score = len(q_terms & terms) / (1 + 0.15 * len(terms))
        if score > best_score:
            best, best_score = s, score
    return best, best_score


def _pick_slot(p: Passage, attrs: list[str], q_terms: set[str]) -> str | None:
    """Which of the passage's value slots does the question ask for?"""
    slots = [s for s in p.slots]
    if not slots:
        return None
    ranked = []
    for slot in slots:
        sentence = _slot_sentence(p, slot) or ""
        overlap = len(q_terms & set(_content(sentence)))
        asked = 5 if slot in attrs else 0
        ranked.append((asked + overlap, slot))
    ranked.sort(reverse=True)
    top_score, top_slot = ranked[0]
    if attrs and not any(s in attrs for s in slots):
        return None  # question asks for an attribute this passage does not have
    return top_slot if top_score > 0 else None


def _int_top_k(value: Any) -> int:
    try:
        k = int(float(value))
    except (TypeError, ValueError, OverflowError):
        k = 3
    return max(1, min(k, 50))


def _combine(p: Passage, attrs: list[str], clean: str) -> tuple[str, list[str]] | None:
    """Two attributes of one entity in a single question ("port and timeout for Redis")."""
    if not re.search(r"\band\b|,|\bboth\b|\bplus\b|\balso\b", clean, re.I):
        return None
    slots = [a for a in dict.fromkeys(attrs) if a in p.slots]
    # "timeout"/"interval" style synonyms must not be double counted when the passage has one time slot
    if len(slots) < 2:
        return None
    sentences = []
    for slot in slots:
        sentence = _slot_sentence(p, slot)
        if sentence and sentence not in sentences:
            sentences.append(sentence)
    return (" ".join(sentences), slots) if len(sentences) >= 2 else None


def _reverse_lookup(kb: KnowledgeBase, clean: str, attrs: list[str]) -> tuple[str, list[int]] | None:
    """"Which system listens on port 6379?" -> passages whose asked slot holds that value."""
    values = re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])|SHA-256|SHA-3|BLAKE2", clean, re.I)
    if not values or not re.search(r"\bwhich\b|\bwhat\b[^?]{0,40}\b(?:system|service|protocol|database|algorithm|model|optimizer)\b", clean, re.I):
        return None
    hits = []
    for p in kb.passages:
        for slot, v in p.slots.items():
            if any(v.lower() == x.lower() for x in values) and (not attrs or slot in attrs):
                hits.append((p, slot))
    if not hits or len(hits) > 3:
        return None
    sentences = [_slot_sentence(p, slot) for p, slot in hits]
    return " ".join(s for s in sentences if s), [p.index for p, _ in hits]


def answer_question(kb: KnowledgeBase, question: str, top_k: int = 3) -> dict[str, Any]:
    top_k = _int_top_k(top_k)
    clean = strip_injection(str(question or ""))
    if len(_content(clean)) < 1:
        return _abstain(kb, str(question or ""), top_k)

    entities = kb.entities_in(clean)
    # the entity's own name must not trigger attribute detection ("multi-LAYER perceptron", "BATCH normalization")
    attr_text = clean.lower()
    for ent, _ in entities:
        for alias in sorted([*ent.primary, *ent.secondary, ent.entity.lower()], key=len, reverse=True):
            attr_text = re.sub(r"(?<![a-z0-9+])" + re.escape(alias) + r"(?![a-z0-9])", " ", attr_text)
    attrs = kb.attributes_in(attr_text)
    weak_attrs = kb.weak_attributes_in(attr_text)

    def attrs_for(passage: Passage) -> list[str]:
        """Strong cues always apply; a weak hint ("algorithm", "window") counts only if this passage has that slot."""
        return attrs or [a for a in weak_attrs if a in passage.slots]

    q_terms = set(_content(clean))
    scores = kb.cosine(clean)
    primary = [e for e in entities if e[1] >= 10]
    cue = bool(_COMPARE_CUE.search(clean))

    answer: str | None = None
    order: list[int] = []
    confidence = 0.0

    # several named entities and a comparison cue -> one fact per passage plus the verdict
    if len(primary) >= 2 and cue or (len(entities) >= 2 and _COMPARE.search(clean)):
        picked = (primary if len(primary) >= 2 else entities)[:3]
        parts = []
        for p, _ in picked:
            slot = _pick_slot(p, attrs_for(p), q_terms - set(_content(" ".join(p.primary + p.secondary))))
            if slot is None:
                continue
            sentence = _slot_sentence(p, slot)
            parts.append((p, slot, _unit(slot, sentence or "", p.slots[slot]), sentence))
        if len(parts) >= 2:
            lead = "; ".join(f"{p.entity}: {sent}" for p, _, _, sent in parts)
            verdict = _verdict(clean, parts)
            answer = lead + (f" {verdict}" if verdict else "")
            order = [p.index for p, _, _, _ in parts]
            confidence = 0.85

    # several names but no comparison: the subject is the entity that actually has the asked attribute
    if answer is None and len(primary) >= 2 and not cue:
        with_attr = [e for e in primary if not attrs_for(e[0]) or any(a in e[0].slots for a in attrs_for(e[0]))]
        if with_attr:
            entities = with_attr + [e for e in entities if e not in with_attr]

    if answer is None and entities:
        p, weight = entities[0]
        removable = set(_content(" ".join(p.primary + p.secondary)))
        pattrs = attrs_for(p)
        both = _combine(p, pattrs, clean)
        if both is not None:
            answer, confidence, order = both[0], 0.88, [p.index]
        else:
            residual = _residual_terms(p, q_terms - removable)
            slot = _pick_slot(p, pattrs, q_terms - removable)
            if pattrs and slot is None and not any(a in p.slots for a in pattrs):
                return _abstain(kb, clean, top_k, near=p.index)  # near-domain question the KB cannot answer
            if pattrs and slot is not None:
                sentence = _slot_sentence(p, slot)
                if _asks_about_valueless_concept(kb, p, sentence or "", q_terms - removable):
                    return _abstain(kb, clean, top_k, near=p.index)
                answer = sentence
                confidence = 0.9 if weight >= 10 else 0.7
                order = [p.index]
            elif _VALUE_RE.search(clean):
                # wants a value but names no known attribute: only a slot sentence that really matches may answer
                sentence = _slot_sentence(p, slot) if slot else None
                overlap = len(residual & set(_content(sentence or ""))) if sentence else 0
                if sentence and overlap >= 2:
                    answer, confidence, order = sentence, 0.75, [p.index]
                else:
                    return _abstain(kb, clean, top_k, near=p.index)
            elif not residual:
                if weak_attrs:
                    return _abstain(kb, clean, top_k, near=p.index)  # "What is the depth of Raft?": a value the KB does not state
                answer, confidence, order = p.sentences[0], 0.8 if weight >= 10 else 0.6, [p.index]  # "What is X?"
            else:
                sentence, overlap = _best_sentence(p, residual)
                matched = len(residual & set(_content(sentence)))
                if matched < 1 or matched / len(residual) < 0.5:
                    return _abstain(kb, clean, top_k, near=p.index)
                answer, confidence, order = sentence, 0.8 if weight >= 10 else 0.6, [p.index]

    if answer is None:
        reverse = _reverse_lookup(kb, clean, attrs)
        if reverse is not None:
            answer, order = reverse
            confidence = 0.75

    if answer is None:
        ranked = sorted(range(len(scores)), key=lambda i: -scores[i])
        best = ranked[0]
        coverage = len(q_terms & set(kb.passages[best].tf)) / max(1, len(q_terms))
        if scores[best] < 0.22 or coverage < 0.6:
            return _abstain(kb, clean, top_k)
        p = kb.passages[best]
        slot = _pick_slot(p, attrs_for(p), q_terms)
        if attrs_for(p) and slot is None:
            return _abstain(kb, clean, top_k, near=best)
        answer = (_slot_sentence(p, slot) if slot else _best_sentence(p, q_terms)[0])
        confidence, order = 0.65, [best]

    if not answer:
        return _abstain(kb, clean, top_k)
    # fill sources by descending relevance; chosen passages first
    rest = [i for i in sorted(range(len(scores)), key=lambda i: -scores[i]) if i not in order]
    sources = (order + rest)[:top_k]
    out_scores = _scale([scores[i] for i in sources], boost=set(range(min(len(order), len(sources)))))
    return {"answer": answer, "sources": sources, "scores": out_scores, "confidence": round(confidence, 2)}


def _residual_terms(p: Passage, terms: set[str]) -> set[str]:
    name = {t for chunk in [p.entity, *p.primary, *p.secondary] for t in re.split(r"[^a-z0-9]+", chunk.lower()) if t}
    return {t for t in terms if t not in _GENERIC and t not in name and not any(rx.search(t) for rx in _ATTR_RE.values()) and len(t) > 2}


def _stem(token: str) -> str:
    return token[:5]


# generic nouns that never name a specific concept ("acknowledging NODES", "default SIZE")
_GENERIC = set("""node nodes member members server servers replica replicas instance instances system systems data request requests
client clients connection connections size count maximum minimum amount total average typical standard setting settings
parameter parameters configuration configured config limit limits level levels period duration""".split())


def _asks_about_valueless_concept(kb: KnowledgeBase, p: Passage, slot_sentence: str, q_terms: set[str]) -> bool:
    """Near-domain trap: "What is the Raft *snapshot* interval?" matches Raft's heartbeat interval,
    but "snapshot" only occurs in a sentence that carries no value. The qualifier word names a
    concept the passage mentions without quantifying, so the question is unanswerable."""
    name_tokens = {t for chunk in [p.entity, *p.primary, *p.secondary] for part in re.split(r"[^a-z0-9]+", chunk.lower()) for t in (part,) if part}
    name_stems = {_stem(t) for t in name_tokens}
    first = {_stem(t) for t in _content(p.sentences[0])}  # the entity's own description, never a "concept"
    modifiers = {t for t in q_terms
                 if len(t) >= 5 and not any(rx.search(t) for rx in _ATTR_RE.values())
                 and _stem(t) not in name_stems and _stem(t) not in first and t not in _GENERIC
                 and kb.stem_df.get(_stem(t), 0) <= 2}  # only rare words name a concept ('commit' is everywhere)
    if not modifiers:
        return False
    in_slot = {_stem(t) for t in _content(slot_sentence)}
    others = " ".join(s for s in p.sentences if s != slot_sentence and not any(v in s for v in p.slots.values()))
    in_other = {_stem(t) for t in _content(others)}
    unmatched = {m for m in modifiers if _stem(m) not in in_slot}
    return bool(unmatched) and all(_stem(m) in in_other for m in unmatched) and not (modifiers - unmatched)


def _verdict(question: str, parts: list[tuple[Passage, str, str, str]]) -> str:
    nums = []
    for p, slot, value, _ in parts:
        m = re.match(r"-?\d+(?:\.\d+)?", value)
        nums.append(float(m.group()) if m else None)
    if any(n is None for n in nums) or len(nums) < 2:
        return ""
    if len(set(nums)) == 1:
        return f"Both are {parts[0][2]}."
    if _UP.search(question):
        i = max(range(len(nums)), key=lambda k: nums[k])
        return f"The larger value is {parts[i][0].entity} ({parts[i][2]})."
    if _DOWN.search(question):
        i = min(range(len(nums)), key=lambda k: nums[k])
        return f"The smaller value is {parts[i][0].entity} ({parts[i][2]})."
    return ""


def _abstain(kb: KnowledgeBase, question: str, top_k: int, near: int | None = None) -> dict[str, Any]:
    return {"answer": None, "sources": [], "scores": [], "confidence": 0.1}


def _scale(raw: list[float], boost: set[int]) -> list[float]:
    """Cosine-like scores in [0, 1], strictly non-increasing, 4 decimals."""
    out = []
    for i, s in enumerate(raw):
        v = max(0.0, min(1.0, s))
        out.append(round(max(v, 0.5 - 0.02 * i) if i in boost else v, 4))
    for i in range(1, len(out)):
        out[i] = min(out[i], out[i - 1])
    return out


@lru_cache(maxsize=256)
def knowledge_base(email: str) -> KnowledgeBase:
    return KnowledgeBase(str(email or "").strip().lower())
