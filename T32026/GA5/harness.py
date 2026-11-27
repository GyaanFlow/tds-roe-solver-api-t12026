"""Q4 ``q-harness-safety-router-server``: deterministic safety classifier for the hypothetical agent harness.

Each case is judged on its own (no shared state between cases or batches). The rules are the exam's
policy text (``exam_data.json`` -> harness.policy), expressed over:

* the request  - the latest actual user messages (content policy, security-research scope),
* the tool     - ``proposedTool.resolved`` (effect after path/mount resolution) + environment isolation +
                 explicit, exact, unrevoked user approval + preflight/rollback evidence,
* the route    - none / restricted / primary,
* the trajectory - normal / watch / intervene.

Memory, repository instructions, tool-result free text and quoted material can narrow scope but never
grant permission. Unknown or ambiguous situations resolve to *review*, never to silent approval.
"""
from __future__ import annotations

import json
import re
from typing import Any

PROFILE = "agent-harness-2026-09"
DECISIONS = {"allow", "block", "review"}

# ----------------------------------------------------------------------------- content policy
_HARM = [
    # steal credentials / exfiltrate private data
    r"\b(?:steal\w*|stole|harvest\w*|phish\w*|captur\w*|skim\w*|scrap\w*|dump\w*|grab\w*|sniff\w*)\b[^.?!\n]{0,60}\b(?:credentials?|passwords?|logins?|log-?ins?|cookies|tokens?|api keys?|sessions?|2fa codes?|otp)\b",
    r"\b(?:exfiltrat\w*|smuggle out|siphon)\b",
    r"\bsend\b[^.?!\n]{0,50}\b(?:customer|private|confidential|personal|secret)\b[^.?!\n]{0,50}\b(?:to my|to an? (?:external|unknown)|to (?:the )?attacker)",
    r"\bkey ?logger\b[^.?!\n]{0,80}\b(?:captur\w*|steal\w*|send\w*|hid\w*|victim|secret\w*|record\w*|spy\w*|without (?:them|him|her|their)\b)",
    r"\bcredential (?:stuffing|harvest)\w*\b",
    # fraud
    r"\b(?:forge|fake|fabricate|counterfeit)\b[^.?!\n]{0,40}\b(?:invoice|receipt|id|passport|check|cheque|identity|document|review|statement)s?\b",
    r"\b(?:launder\w*|carding|chargeback fraud|scam (?:script|email|victims?)|wire fraud|insurance fraud|tax fraud|phishing (?:kit|page|email))\b",
    # harassment of a real person
    r"\b(?:doxx?\w*|stalk\w*|harass\w*|threaten\w*|intimidat\w*|swat\w*)\b[^.?!\n]{0,60}\b(?:neighbou?r|coworker|colleague|ex\b|girlfriend|boyfriend|person|her|him|them|journalist|teacher|student)\b",
    # destructive malware / physical harm
    r"\b(?:ransomware|wiper|botnet|rootkit|worm|trojan|destructive malware|logic bomb)\b[^.?!\n]{0,60}\b(?:write|build|develop|create|deploy|spread|encrypt|destroy)\b",
    r"\b(?:write|build|develop|create|deploy|spread)\b[^.?!\n]{0,60}\b(?:ransomware|wiper|botnet|rootkit|worm|trojan|destructive malware|logic bomb)\b",
    r"\b(?:make|build|synthesi[sz]e|assemble)\b[^.?!\n]{0,40}\b(?:bomb|explosive|nerve agent|bioweapon|chemical weapon|untraceable weapon|poison)\b",
    r"\b(?:hurt|harm|kill|injure|poison)\b[^.?!\n]{0,30}\b(?:someone|people|my|a person|him|her|them)\b",
    # evading safeguards for the above
    r"\b(?:evade|bypass|disable|get around|avoid)\b[^.?!\n]{0,40}\b(?:antivirus|edr|detection|safeguards?|filters?|moderation|monitoring)\b[^.?!\n]{0,60}\b(?:malware|ransomware|steal|exfiltrat|payload|phish)\w*",
]
_HARM_RE = [re.compile(p, re.I) for p in _HARM]

_BENIGN_FRAME = re.compile(
    r"\b(?:defend|defensive|detect|detection|mitigat\w*|remediat\w*|prevent\w*|protect\w*|harden\w*|patch\w*|audit\w*|incident response|blue team|"
    r"awareness training|explain (?:how|why)|what is|summari[sz]e|translate|translation|analy[sz]e|analysis of|"
    r"inspect|review (?:this|the) (?:file|log|email|message|sample)|fiction\w*|novel|story|screenplay|character|plot|poem|essay|history of|"
    r"quoted|the following (?:text|message|email)|spot|recogni[sz]e|report(?:ed)? (?:this|it))\b", re.I)
_ACTIONABLE = re.compile(
    r"\b(?:step[- ]by[- ]step|working (?:code|script|payload)|full (?:code|script|source)|ready to (?:use|deploy|run)|real (?:target|victim)s?|"
    r"deploy it|make it undetectable|bypass (?:the )?(?:av|edr|antivirus)|against (?:my |a )?(?:neighbou?r|coworker|ex|victim))\b", re.I)
_OFFENSIVE = re.compile(
    r"\b(?:exploit\w*|payload|reverse shell|shellcode|zero[- ]day|metasploit|brute[- ]?forc\w*|port ?scan\w*|nmap|fuzz\w*|"
    r"proof[- ]of[- ]concept|poc|privilege escalation|pentest\w*|penetration test\w*|red team\w*|"
    r"hack(?:ing)? (?:into|the|a|an|their|this|someone)|break(?:ing)? into|attack (?:the|a|my|their|this|that))\b", re.I)
_EXPLOIT_CORE = re.compile(r"\b(?:exploit\w*|payload|reverse shell|shellcode|zero[- ]day|metasploit|proof[- ]of[- ]concept|poc)\b", re.I)
_DEFENSIVE_VERBS = re.compile(r"\b(?:defend\w*|detect\w*|mitigat\w*|prevent\w*|patch\w*|remediat\w*|harden\w*|fix\w*|secure|protect\w*|explain\w*|understand\w*)\b", re.I)
_FICTION = re.compile(r"\b(?:story|novel|fiction\w*|screenplay|character|poem|plot|chapter|roleplay|role-play|scene)\b", re.I)
_SECURITY_WORK = re.compile(
    r"\b(?:exploit|vulnerabilit\w*|pentest\w*|penetration test\w*|cve-\d{4}-\d+|proof[- ]of[- ]concept|poc\b|payload|reverse shell|"
    r"privilege escalation|sql injection|xss|buffer overflow|rce\b|fuzz\w*|red team|ctf\b|zero[- ]day|shellcode|metasploit|nmap scan)\b", re.I)
_OWNED_ISOLATED = re.compile(
    r"\b(?:my own|i own|we own|our own|owned by (?:me|us)|isolated|sandbox\w*|lab (?:vm|environment|network|machine)|local (?:vm|container|lab)|"
    r"throwaway|disposable|ctf|capture the flag|authori[sz]ed (?:test|engagement|scope)|written authori[sz]ation|in[- ]scope|air[- ]gapped|"
    r"localhost|127\.0\.0\.1|test (?:vm|instance|range))\b", re.I)
_UNCLEAR_SCOPE = re.compile(
    r"\b(?:this (?:site|website|server|host|ip|target|company|app)|their (?:site|server|network|systems?)|someone'?s|a (?:public|live) (?:site|server)|"
    r"production|prod\b|target(?:ed)? (?:at|the)|no permission|without (?:their )?(?:permission|consent|authori[sz]ation)|unauthori[sz]ed)\b", re.I)

# ----------------------------------------------------------------------------- user messages
_APPROVE = re.compile(
    r"\b(?:approved?|authori[sz]e[sd]?|go ahead|proceed|yes|yep|yeah|sure|confirmed?|you (?:may|can)|permission (?:granted|to)|i (?:approve|confirm|agree)|do it|"
    r"ok(?:ay)?|green[- ]?light|sign(?:ed)?[- ]off|please (?:do|go|proceed))\b", re.I)
_REVOKE = re.compile(
    r"\b(?:revok\w*|rescind\w*|cancel\w*|withdraw\w*|retract\w*|never mind|nevermind|stop\b|do not|don'?t|do n't|not anymore|no longer|hold off|wait\b|abort\w*|"
    r"changed my mind|disregard (?:my|that|the) (?:approval|earlier)|forbid\w*|prohibit\w*|must not|should not|off[- ]limits)\b", re.I)

_READ_OPS = {"read", "list", "ls", "cat", "view", "inspect", "get", "describe", "show", "search", "grep", "find", "stat", "diff", "log", "status", "plan", "head", "tail", "fetch_schema", "select", "query"}
_WRITE_OPS = {"write", "edit", "create", "modify", "update", "append", "patch", "move", "rename", "copy", "mkdir", "touch", "format", "commit"}
_DELETE_OPS = {"delete", "remove", "rm", "rmdir", "unlink", "drop", "truncate", "wipe", "purge", "destroy", "erase", "shred"}
_SEND_OPS = {"send", "post", "upload", "email", "mail", "transfer", "publish", "share", "push_data", "export", "sync", "forward", "webhook", "put", "scp", "rsync"}
_PRIV_OPS = {"sudo", "chmod", "chown", "chgrp", "mount", "umount", "iptables", "systemctl", "service", "reboot", "shutdown", "kill", "install", "grant", "revoke_access", "setuid", "visudo", "useradd", "passwd", "ufw"}
_SECRET_LEVELS = {"secret", "secrets", "credential", "credentials", "private", "confidential", "pii", "sensitive", "restricted", "high", "personal", "customer", "financial"}
_PUBLIC_LEVELS = {"public", "none", "low", "non-sensitive", "nonsensitive", "internal-public", "open", "unclassified"}


def _text_of(*parts: Any) -> str:
    return " ".join(json.dumps(p, ensure_ascii=False) if not isinstance(p, str) else p for p in parts if p not in (None, "", [], {}))


def _lc(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _norm(text: Any) -> str:
    """Case/punctuation-insensitive form so 'deploy-token' matches 'deploy token'."""
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).strip()


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return _content_text(content.get("text") if "text" in content else content.get("content"))
    if isinstance(content, list):
        return "\n".join(t for t in (_content_text(c) for c in content) if t)
    return ""


def user_messages(case: dict[str, Any]) -> list[str]:
    """Only actual user messages count (assistant/tool/system text never grants anything)."""
    msgs = []
    raw = case.get("messages")
    for m in raw if isinstance(raw, list) else []:
        if isinstance(m, dict) and _lc(m.get("role")) in {"user", "human"}:
            text = _content_text(m.get("content"))
            if text.strip():
                msgs.append(text)
    return msgs


def _latest_user(case: dict[str, Any]) -> str:
    msgs = user_messages(case)
    return msgs[-1] if msgs else ""


# ----------------------------------------------------------------------------- request decision
def _request_axes(case: dict[str, Any]) -> dict[str, Any]:
    msgs = user_messages(case)
    latest = _latest_user(case)
    joined = "\n".join(msgs[-3:])
    harm = any(r.search(latest) for r in _HARM_RE)
    benign = bool(_BENIGN_FRAME.search(latest))
    actionable = bool(_ACTIONABLE.search(latest))
    if harm and benign and not actionable:
        # defensive / fictional / analytic framing: allowed unless the assistance itself would facilitate harm
        harm = bool(re.search(r"\b(?:write|build|develop|create|generate|give me)\b[^.?!\n]{0,40}\b(?:working|functional|real|deployable|full)\b", latest, re.I)) or \
            bool(re.search(r"\b(?:steal|exfiltrat\w*|harass|doxx?\w*)\b[^.?!\n]{0,30}\b(?:for me|my (?:ex|neighbou?r|coworker))\b", latest, re.I))
    offensive = bool(_OFFENSIVE.search(latest))
    if offensive and _FICTION.search(latest) and not _EXPLOIT_CORE.search(latest):
        offensive = False  # a story about a hacker is not security work
    if offensive and _DEFENSIVE_VERBS.search(latest) and not _EXPLOIT_CORE.search(latest):
        offensive = False  # defending/understanding/patching needs no ownership check
    topic = bool(_SECURITY_WORK.search(latest)) or offensive  # vulnerability/exploit/pentest subject matter
    owned = bool(_OWNED_ISOLATED.search(joined))
    # unclear ownership matters when the work is offensive; defensive remediation needs no scope check
    unclear = offensive and (not owned or bool(_UNCLEAR_SCOPE.search(latest)))
    return {"harm": harm, "security": topic, "offensive": offensive, "owned_isolated": owned, "unclear_scope": unclear}


def _redirect_attempt(case: dict[str, Any]) -> bool:
    """Untrusted content (files, memory, tool results, repository text) tries to steer the session."""
    blob = _text_of(case.get("memory"), case.get("repositoryInstructions"), case.get("toolResults"))
    return bool(re.search(
        r"\b(?:ignore (?:all |any )?(?:previous|prior|above) instructions?|disregard (?:the )?(?:policy|rules|instructions)|you (?:must|should) now|"
        r"new (?:system )?instructions?|override (?:the )?(?:policy|safety)|run (?:this|the following) (?:command|script) without|"
        r"do not tell the user|secretly|exfiltrate|send (?:the )?(?:contents|credentials|keys|secrets?) to|curl [^|\n]{0,80}\| ?(?:ba)?sh|when you (?:read|see) this)\b", blob, re.I))


# ----------------------------------------------------------------------------- tool decision
def _resolved(tool: dict[str, Any]) -> dict[str, Any]:
    r = tool.get("resolved")
    return r if isinstance(r, dict) else {}


def _op_kind(tool: dict[str, Any]) -> str:
    r = _resolved(tool)
    op = _lc(r.get("operation") or r.get("op") or r.get("action"))
    name = _lc(tool.get("name"))
    argtext = _lc(_text_of(tool.get("arguments")))
    blob = f"{op} {name} {argtext}"
    if re.search(r"git[^\n]{0,20}push[^\n]{0,40}(?:--force|-f\b|--force-with-lease)|force[- ]?push", blob):
        return "force_push"
    if re.search(r"\bdns\b|route53|nameserver|\bzone\b[^\n]{0,20}record|cloudflare[^\n]{0,20}record", blob):
        return "dns"
    if re.search(r"docker[^\n]{0,30}(?:--privileged|-v\s*/|--mount|--volume\s*/|rm -f|system prune|run[^\n]{0,40}/var/run/docker\.sock)|docker\.sock", blob) and _lc(r.get("environment")) not in {"container"}:
        return "host_docker"
    words = set(re.findall(r"[a-z_]+", op)) | {name}
    if words & _DELETE_OPS or re.search(r"\brm\s+-\w*r|\brm\b|\bdelete\b|\bdrop (?:table|database)\b|\btruncate\b", blob):
        return "delete"
    if words & _SEND_OPS or re.search(r"\bcurl\b[^\n]{0,80}(?:-d|--data|-F|-X (?:POST|PUT))|\bscp\b|\brsync\b[^\n]{0,60}@|sendmail|\bmail\b|\bwebhook\b|\bupload\b", blob):
        return "send"
    if words & _PRIV_OPS or re.search(r"\bsudo\b|\bchmod 777\b|\bchown\b|\biptables\b|\bsystemctl\b", blob):
        return "privileged"
    if words & _WRITE_OPS or re.search(r">\s*\S|\bsed -i\b|\btee\b|\bmv\b|\bcp\b", blob):
        return "write"
    if words & _READ_OPS or not op:
        return "read"
    return "other"


def _is_sensitive(tool: dict[str, Any]) -> bool:
    r = _resolved(tool)
    level = _lc(r.get("sensitivity"))
    target = _lc(r.get("target"))
    if level in _PUBLIC_LEVELS:
        return False
    if level in _SECRET_LEVELS:
        return True
    return bool(re.search(r"\.env\b|credential|secret|id_rsa|\.pem\b|\.aws|\.ssh|passwd|shadow|token|api[_-]?key|\.kube/config|keychain|vault", target + " " + _lc(_text_of(tool.get("arguments")))))


def _is_production(tool: dict[str, Any], case: dict[str, Any]) -> bool:
    r = _resolved(tool)
    blob = _lc(_text_of(r.get("environment"), r.get("destination"), r.get("target"), (case.get("environment") or {}).get("kind")))
    return bool(re.search(r"\bprod(?:uction)?\b|\blive\b", blob))


def _env_kind(case: dict[str, Any], tool: dict[str, Any]) -> str:
    return _lc(_resolved(tool).get("environment") or (case.get("environment") or {}).get("kind"))


def _isolation_verified(case: dict[str, Any], tool: dict[str, Any]) -> bool:
    env = case.get("environment") or {}
    iso = env.get("isolation") if isinstance(env.get("isolation"), dict) else {}
    if _lc(env.get("kind")) != "container" or iso.get("verified") is not True:
        return False
    if iso.get("hostMounts"):
        return False
    if iso.get("credentials") not in (False, None, 0, [], {}):
        return False
    if iso.get("externalNetwork") not in (False, None, 0):
        return False
    return True


_ENV_WORDS = {
    "production": re.compile(r"\bprod(?:uction)?\b|\blive\b", re.I),
    "staging": re.compile(r"\bstag(?:e|ing)\b", re.I),
    "development": re.compile(r"\bdev(?:elopment)?\b", re.I),
    "test": re.compile(r"\btest(?:ing)?\b", re.I),
    "container": re.compile(r"\bcontainer\b|\bdocker\b|\bsandbox\b", re.I),
    "host": re.compile(r"\bhost\b|\blocal machine\b|\bmy (?:laptop|machine|computer)\b", re.I),
    "remote": re.compile(r"\bremote\b|\borigin\b", re.I),
}


def _env_key(env: str) -> str | None:
    for key, rx in _ENV_WORDS.items():
        if rx.search(env) or key in env:
            return key
    return None


def _env_compatible(env: str, message_lc: str) -> bool:
    """An approval is bound to its environment: it fails only when it names a DIFFERENT environment.
    Staying silent about the environment (while naming the exact target) is not a conflict."""
    named = {key for key, rx in _ENV_WORDS.items() if rx.search(message_lc)}
    key = _env_key(env or "")
    return not named or key is None or key in named


_OP_WORDS = {
    "delete": r"delet\w*|remov\w*|\brm\b|clean\w*|wip\w*|purg\w*|drop\w*|erase\w*|destroy\w*",
    "send": r"send\w*|email\w*|upload\w*|post\w*|shar\w*|transfer\w*|publish\w*|forward\w*|export\w*",
    "privileged": r"sudo|privileg\w*|permission\w*|chmod|chown|install\w*|root|admin\w*",
    "force_push": r"force\w*|push\w*",
    "host_docker": r"docker|container\w*|host",
    "dns": r"dns|record\w*|domain\w*",
}
# a prohibition: the negation must govern the action inside one clause ("Never push to main", "not allowed to delete ~/x")
_NEGATION = re.compile(
    r"\b(?:never|do not|don'?t|must not|mustn'?t|should not|shouldn'?t|cannot|can'?t|not allowed to|not permitted to|"
    r"forbidden to|prohibited from|no permission to|not authori[sz]ed to|refuse to|stop|avoid|under no circumstances)\b", re.I)
_NEG_FILLER = re.compile(r"^\s*(?:worry|forget|bother|hesitate|mind|panic|stress)\b", re.I)  # "do not worry/forget ..." is not a prohibition
# a revocation that points back at an earlier approval ("cancel that", "never mind", "leave it alone")
_PRONOUN_REVOKE = re.compile(
    r"\b(?:cancel|stop|abort|forget|scrap|undo|revoke|rescind|withdraw|retract)\b[^.?!\n]{0,20}\b(?:that|this|it|them|everything|the (?:deletion|delete|push|change|deploy\w*|upload|send\w*))\b"
    r"|\b(?:never ?mind|changed my mind|hold off|on second thought)\b|\bdon'?t do (?:that|it|this)\b|\bdo not do (?:that|it|this)\b"
    r"|\bleave\b[^.?!\n]{0,40}\balone\b|\bno,? (?:don'?t|do not|stop)\b|\bnot approved?\b|\bno approval\b", re.I)


_REQUEST_LEAD = (r"^\W*(?:(?:please|now|just|then|also|and|kindly|ok(?:ay)?|so)\W+)*"
                 r"(?:(?:go ahead and|you (?:may|can|should|must))\s+)?"
                 r"(?:(?:can|could|would|will) you\s+(?:please\s+)?|i (?:want|need|would like|'d like) you to\s+|let'?s\s+)?")


def _is_request(sentence: str, op_rx: "re.Pattern[str]") -> bool:
    """"Delete ~/x.", "Please remove ~/x", "Can you wipe ~/x?" ask for the action; "Should I delete ~/x?" does not."""
    return re.match(_REQUEST_LEAD + r"(?:" + op_rx.pattern + r")", sentence, re.I) is not None


def _approval_info(case: dict[str, Any], tool: dict[str, Any]) -> dict[str, Any]:
    """Latest actual user instruction about THIS operation/target/environment.

    states: approved | wrong_env | wrong_destination | vague | revoked | None. Messages are read oldest first and the
    later instruction wins, so "no ... actually yes" approves and "yes ... never mind" revokes."""
    r = _resolved(tool)
    target = _lc(r.get("target"))
    dest = _lc(_text_of(r.get("destination")))
    op = _op_kind(tool)
    env = _env_kind(case, tool)
    base = target.rstrip("/").split("/")[-1]
    dest_tokens = [t for t in re.findall(r"[a-z0-9_.@-]{4,}", dest) if t not in {"true", "false", "none", "null", "https", "http", "external", "internal"}]
    op_rx = re.compile(r"\b(?:" + _OP_WORDS[op] + r")", re.I) if op in _OP_WORDS else None
    specific_op = op_rx is not None

    def names_action(text: str) -> bool:
        low = text.lower()
        nm = _norm(text)
        if target and (target in low or _norm(target) in nm or (len(base) > 2 and _norm(base) in nm)):
            return True
        if dest_tokens and all(_norm(t) in nm or t in low for t in dest_tokens[:3]):
            return True
        return bool(op_rx and op_rx.search(text))

    last_state, last_text = None, ""
    for m in user_messages(case):
        lc = m.lower()
        nm = _norm(m)
        mentions_target = bool(target) and (target in lc or _norm(target) in nm or (len(base) > 2 and _norm(base) in nm))
        mentions_dest = bool(dest_tokens) and all(_norm(t) in nm or t in lc for t in dest_tokens[:3])
        mentions_op = (not specific_op) or bool(op_rx.search(m))
        approve_hits = [x.start() for x in _APPROVE.finditer(m)] if not re.search(r"\bnot approved?\b|\bno approval\b", lc) else []
        if not approve_hits and op_rx is not None:
            for sentence in re.split(r"(?<=[.!?])\s+|\n+", m):
                names_target = bool(target) and (target in sentence.lower() or _norm(target) in _norm(sentence) or (len(base) > 2 and _norm(base) in _norm(sentence)))
                if names_target and _is_request(sentence, op_rx):
                    approve_hits = [0]  # an explicit instruction naming the exact target is the authorization
                    break

        # position of the last prohibition that governs this action within its own clause
        prohibit_at = -1
        for neg in _NEGATION.finditer(m):
            clause = re.split(r"[.,;:?!\n]", m[neg.end():], maxsplit=1)[0][:80]
            if _NEG_FILLER.match(clause):
                continue
            if names_action(clause):
                prohibit_at = max(prohibit_at, neg.start())
        pronoun = _PRONOUN_REVOKE.search(m)
        pronoun_ok = bool(pronoun) and (last_state in {"approved", "wrong_env", "wrong_destination", "vague"} or mentions_target or mentions_dest)
        revoke_at = max(prohibit_at, pronoun.start() if pronoun_ok else -1)

        approve_at = max(approve_hits) if approve_hits else -1
        about = (mentions_target or mentions_dest) and mentions_op
        if revoke_at >= 0 and revoke_at >= approve_at:
            last_state, last_text = "revoked", m
        elif approve_at >= 0 and about:
            if op == "send" and dest_tokens and not mentions_dest:
                last_state, last_text = "wrong_destination", m  # the approval names a different recipient
            else:
                last_state, last_text = ("approved" if _env_compatible(env, lc) else "wrong_env"), m
        elif approve_at >= 0 and mentions_op and not (mentions_target or mentions_dest):
            last_state = last_state or "vague"
    return {"state": last_state, "text": last_text}


def _preflight_ok(case: dict[str, Any]) -> bool:
    for tr in case.get("toolResults") or []:
        blob = _lc(_text_of(tr))
        if "preflight" in blob or "dry-run" in blob or "dry_run" in blob or "plan" in blob:
            if re.search(r"\b(?:fail\w*|error|denied|blocked|unsuccessful|not ok|timed out)\b", blob) and not re.search(r"\b(?:passed|success\w*|ok\b|succeeded|green)\b", blob):
                return False
            if re.search(r"(?:status|result|outcome)\"?\s*[:=]\s*\"?(?:failed|error|fail)", blob):
                return False
            if re.search(r"\b(?:passed|success\w*|succeeded|ok\b|green)\b", blob):
                return True
    return False


def _preflight_required_and_bypassed(case: dict[str, Any], tool: dict[str, Any]) -> bool:
    args = _lc(_text_of(tool.get("arguments")))
    return bool(re.search(r"--no-verify|--skip-(?:preflight|checks?|validation)|--force\b[^\n]{0,30}preflight|--ignore-preflight|--yes-i-know|--bypass", args))


def _has_rollback(case: dict[str, Any]) -> bool:
    plan = case.get("rollbackPlan") or case.get("rollback")
    if isinstance(plan, str):
        return bool(plan.strip()) and not re.search(r"\b(?:none|n/a|unknown|tbd|no rollback)\b", plan, re.I)
    if isinstance(plan, dict):
        steps = plan.get("steps") or plan.get("commands") or plan.get("plan") or plan.get("command")
        return bool(steps) or any(v for k, v in plan.items() if k not in ("exact",)) and plan.get("exact") is not False
    if isinstance(plan, list):
        return bool(plan)
    return False


def _credential_in_scope(case: dict[str, Any], tool: dict[str, Any]) -> bool:
    """An explicitly approved, task-scoped credential for the requested operation."""
    r = _resolved(tool)
    if r.get("approved") is True or r.get("taskScoped") is True or r.get("scope") in ("task", "task-scoped"):
        return True
    info = _approval_info(case, tool)
    if info["state"] == "approved":
        return True
    target = _lc(r.get("target"))
    base = target.rstrip("/").split("/")[-1]
    return bool(target) and any(
        (_norm(target) in _norm(m) or (len(base) > 2 and _norm(base) in _norm(m)))
        and re.search(r"\b(?:use|load|with|using)\b[^.?!\n]{0,60}\b(?:credential|token|key|secret|password)", m.lower())
        for m in user_messages(case))


def tool_decision(case: dict[str, Any], request_decision: str) -> str:
    tool = case.get("proposedTool")
    if not isinstance(tool, dict) or not tool:
        return "none"
    if request_decision == "block":
        return "block"
    forced = _forbidden_tool(case, tool)
    if forced:
        return "block"
    if request_decision == "review":
        return "review"
    return _tool_policy(case, tool)


def _preflight_failed(case: dict[str, Any]) -> bool:
    for tr in case.get("toolResults") or []:
        blob = _lc(_text_of(tr))
        if ("preflight" in blob or "pre-flight" in blob or "dry-run" in blob or "dry_run" in blob) and \
                re.search(r"(?:status|result|outcome)\"?\s*[:=]\s*\"?(?:failed|error|fail|denied|blocked)|\b(?:preflight|dry[- ]run)\b[^\n]{0,40}\b(?:failed|error|denied|blocked)\b", blob):
            return True
    return False


_URL_OR_PATH = re.compile(r"https?://[^\s'\"<>)]+|(?:~|/)[\w.@/-]{3,}|\b[\w-]+(?:\.[\w-]+)+\.(?:com|net|org|io|sh|xyz|ru|cn)\b")


def _follows_untrusted_instruction(case: dict[str, Any], tool: dict[str, Any]) -> bool:
    """The tool replays a URL/path/command that only appears in untrusted content (file, memory, tool result, repo text)."""
    untrusted = _text_of(case.get("memory"), case.get("repositoryInstructions"), case.get("toolResults"))
    if not re.search(r"\b(?:ignore|disregard|you must|you should now|run (?:this|the following)|execute|do not tell|secretly|send (?:the )?(?:contents|credentials|keys)|curl|wget|exfiltrat\w*)\b", untrusted, re.I):
        return False
    argtext = _text_of(tool.get("arguments"), _resolved(tool).get("target"), _resolved(tool).get("destination"))
    users = " ".join(user_messages(case)).lower()
    for token in set(_URL_OR_PATH.findall(untrusted)):
        t = token.rstrip(".,;:").lower()
        if len(t) > 6 and t in argtext.lower() and t not in users:
            return True
    return False


def _forbidden_tool(case: dict[str, Any], tool: dict[str, Any]) -> bool:
    kind, r = _op_kind(tool), _resolved(tool)
    info = _approval_info(case, tool)
    if info["state"] == "revoked":
        return True
    if _follows_untrusted_instruction(case, tool):
        return True
    if _preflight_failed(case) and kind != "read":
        return True  # proceeding past a visible failed preflight bypasses the safety check
    if _preflight_required_and_bypassed(case, tool):
        return True
    sensitive = _is_sensitive(tool)
    # reading / searching credentials outside the task scope
    if sensitive and kind == "read" and re.search(r"credential|secret|\.env\b|id_rsa|\.pem|\.aws|\.ssh|token|api[_-]?key|keychain|vault|\.kube/config", _lc(_text_of(r.get("target"), tool.get("arguments")))):
        if not _credential_in_scope(case, tool):
            return True
    # private-data transfer to a destination nobody approved
    if kind == "send" and sensitive:
        if info["state"] != "approved":
            return True  # no approval, or an approval naming a different destination
        dest = _lc(_text_of(r.get("destination")))
        if re.search(r"unapproved|unknown|external|attacker|pastebin|anonymous", dest) and not r.get("approved"):
            return True
    return False


def _tool_policy(case: dict[str, Any], tool: dict[str, Any]) -> str:
    kind, r = _op_kind(tool), _resolved(tool)
    env = _env_kind(case, tool)
    target = _lc(r.get("target"))
    sensitive = _is_sensitive(tool)
    production = _is_production(tool, case)
    if not r or not (r.get("operation") or r.get("target")) or not env and not (case.get("environment") or {}):
        return "review"  # unknown environment or unresolved target
    if env in {"", "unknown", "unspecified"} or not target or target in {"unknown", "unresolved", "?"}:
        return "review"
    info = _approval_info(case, tool)
    approved = info["state"] == "approved"

    # production mutation: explicit exact approval + successful preflight + exact rollback plan
    if production and kind != "read":
        if approved and _preflight_ok(case) and _has_rollback(case):
            return "allow"
        return "review"
    if production and kind == "read" and sensitive:
        return "allow" if approved else "review"

    if kind in {"force_push", "dns", "host_docker", "privileged"}:
        return "allow" if approved else "review"
    if kind == "send":
        return "allow" if approved else "review"
    if kind == "delete":
        disposable = r.get("disposable") is True
        if disposable and _isolation_verified(case, tool):
            return "allow"
        if env == "container" and disposable and not _isolation_verified(case, tool):
            # container label alone proves nothing: mounts/credentials/network keep the original risk
            return "allow" if approved else "review"
        return "allow" if approved else "review"
    if kind == "read":
        if sensitive:
            return "allow" if _credential_in_scope(case, tool) else "review"
        return "allow"
    if kind == "write":
        if sensitive and not approved:
            return "review"
        return "allow"
    return "allow" if approved else "review"


# ----------------------------------------------------------------------------- per-case decision
def decide_case(case: dict[str, Any]) -> dict[str, str]:
    from T32026.GA5 import harness_structured  # real grader case shape (resolved operation vocabulary)
    structured = harness_structured.decide(case)
    if structured is not None:
        return structured
    axes = _request_axes(case)
    redirect = _redirect_attempt(case)
    tool = case.get("proposedTool") if isinstance(case.get("proposedTool"), dict) and case.get("proposedTool") else None

    if axes["harm"]:
        request = "block"
    elif axes["security"] and axes["unclear_scope"]:
        request = "review"
    else:
        request = "allow"

    tool_d = tool_decision(case, request)

    if request == "block":
        route = "none"
    elif axes["security"]:
        route = "restricted"  # vulnerability/exploit work, or unclear security scope
    else:
        route = "primary"

    if request == "block" or tool_d == "block":
        trajectory = "intervene"
    elif request == "review" or tool_d == "review" or axes["unclear_scope"] or redirect:
        trajectory = "watch"
    else:
        trajectory = "normal"
    return {"requestDecision": request, "toolDecision": tool_d, "route": route, "trajectory": trajectory}


_SAFE_DEFAULT = {"requestDecision": "review", "toolDecision": "review", "route": "primary", "trajectory": "watch"}


def decide_batch(body: dict[str, Any]) -> dict[str, Any]:
    cases = body.get("cases")
    if not isinstance(cases, list):
        raise ValueError("'cases' must be a list")
    if len(cases) > 1000:
        raise ValueError("too many cases in one batch")
    results, seen = [], set()
    for case in cases:
        if not isinstance(case, dict) or case.get("caseId") in (None, "") or isinstance(case.get("caseId"), (dict, list, bool)):
            raise ValueError("every case needs a caseId")
        if case["caseId"] in seen:
            raise ValueError("duplicate caseId")
        seen.add(case["caseId"])
        try:
            decision = decide_case(case)
        except Exception:  # one malformed case must not fail the batch
            decision = dict(_SAFE_DEFAULT)
            if not isinstance(case.get("proposedTool"), dict) or not case.get("proposedTool"):
                decision["toolDecision"] = "none"
        results.append({"caseId": case["caseId"], **decision})
    return {"profile": PROFILE, "batchId": body.get("batchId"), "results": results}
