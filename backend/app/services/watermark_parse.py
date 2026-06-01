"""Parse CCTV OSD watermark / filename — content-based (no fixed line order).

Spec: docs/design/watermark-ocr-extraction.md
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal


WELL_HEAD = re.compile(r"(?i)([A-Z]{1,6}\d+)")
DIAMETER_LIKE_TOKEN = re.compile(r"(?i)^DN\d+$|^D\d+$")

DIAMETER_PATTERNS = [
    (re.compile(r"(?i)DN\s*(\d{2,4})"), 1.0),
    (re.compile(r"(?i)[φΦ]\s*(\d{2,4})"), 0.95),
    (re.compile(r"(?i)(\d{3,4})\s*mm"), 0.9),
    (re.compile(r"(?i)(?<![A-Z])D\s*(\d{2,4})(?!-)"), 0.85),
]

DATE_PATTERN = re.compile(
    r"(\d{4})[/\-年](\d{1,2})[/\-月](\d{1,2})"
)
TIME_HINT = re.compile(r"UTC|上午|下午|:\d{2}")

# 管材：词表正则 → 规范名（优先长匹配）
MATERIAL_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"玻璃钢夹砂管?"), "玻璃钢夹砂"),
    (re.compile(r"球墨铸铁管?"), "球墨铸铁"),
    (re.compile(r"HDPE管?"), "HDPE"),
    (re.compile(r"高密度聚乙烯管?"), "HDPE"),
    (re.compile(r"钢筋混凝土管?"), "钢筋混凝土"),
    (re.compile(r"混凝土管?"), "混凝土"),
    (re.compile(r"CIPP管?"), "CIPP"),
    (re.compile(r"塑料管?"), "塑料"),
    (re.compile(r"砼管?"), "混凝土"),
]

# 道路简称 + 井号：NH2W5 / NH2W-5
# 道路简称 2–3 字母 + 可选数字，不含末尾 W（避免 nh2w 整段被当成路名）
ROAD_WELL_END = re.compile(
    r"(?i)^([A-Z]\d+(?:-[A-Za-z0-9]+)*)-([A-Z]{2,3}\d?)W-?(\d+(?:-[A-Za-z0-9]+)?)$"
)
# OCR 变体：w11-2-nhw-5 → W11-2 + NH2W-5
ROAD_WELL_OCR_END = re.compile(
    r"(?i)^([A-Z]\d+(?:-[A-Za-z0-9]+)*)-([A-Za-z]{2,4})-?(\d+)$"
)

ROAD_HINTS = ("通道", "路", "弄", "大街", "公路")


ChainMode = Literal["well_pair", "descriptive_end", "single_well", "unparsed"]


@dataclass
class ChainParse:
    start: str | None
    end: str | None
    mode: ChainMode
    warnings: list[str] = field(default_factory=list)


@dataclass
class ParseResult:
    chain_start_label: str | None = None
    chain_end_label: str | None = None
    chain_parse_mode: ChainMode = "unparsed"
    chain_confidence: float = 0.0
    chain_source: str = "none"
    chain_warnings: list[str] = field(default_factory=list)
    diameter_mm: int | None = None
    diameter_raw: str | None = None
    pipe_material: str | None = None
    pipe_system: str | None = None
    inspection_date: str | None = None
    inspection_date_raw: str | None = None
    field_confidence: dict[str, float] = field(default_factory=dict)
    ocr_blocks_used: list[str] = field(default_factory=list)
    filename_stem: str | None = None


def normalize_well(token: str) -> str:
    return token.strip().upper()


def preprocess_text(text: str) -> str:
    t = text.strip().replace("－", "-").replace("—", "-").replace("–", "-")
    t = t.replace("〇", "0")
    return t


def _is_diameter_token(token: str) -> bool:
    return bool(DIAMETER_LIKE_TOKEN.match(token.strip()))


def tokenize_wells(text: str) -> list[str]:
    """Split hyphenated chain into well tokens (spec §3.1 table)."""
    text = preprocess_text(text)
    tokens: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        m = WELL_HEAD.match(text, i)
        if not m:
            i += 1
            continue
        tok = normalize_well(m.group(1))
        j = m.end()
        while j < n and text[j] == "-":
            rest = text[j + 1 :]
            nxt = WELL_HEAD.match(rest)
            if nxt:
                break
            seg = re.match(r"[A-Za-z0-9]+", rest)
            if not seg:
                break
            tok = f"{tok}-{seg.group(0)}"
            j += 1 + len(seg.group(0))
        if not _is_diameter_token(tok):
            tokens.append(tok)
        i = j if j > m.end() else m.end()
    return tokens


def _expand_road_code(road: str) -> str:
    """NH → NH2 等常见道路编号补全（OCR 易丢数字）。"""
    r = road.upper()
    if r == "NH":
        return "NH2"
    if len(r) == 2 and r.isalpha():
        return f"{r[0]}2{r[1:]}" if r[1] != "2" else r
    return r


def _end_label_from_road_well(road: str, well_part: str) -> str:
    road = _expand_road_code(road)
    wp = well_part.strip().upper()
    if wp.startswith("W"):
        return f"{road}{wp}"
    if re.match(r"^\d", wp):
        return f"{road}W-{wp}"
    return f"{road}W{wp}"


def _parse_chain_road_well_end(text: str) -> ChainParse | None:
    """起止井号：标准井号 + 道路简称+W 终点（如 W11-2-NH2W-5）。"""
    compact = preprocess_text(text).replace(" ", "")
    m = ROAD_WELL_END.match(compact)
    if m:
        start_tokens = tokenize_wells(m.group(1))
        start = start_tokens[-1] if start_tokens else normalize_well(m.group(1))
        end = _end_label_from_road_well(m.group(2), m.group(3))
        return ChainParse(start, end, "well_pair", ["ROAD_WELL_END"])

    m = ROAD_WELL_OCR_END.match(compact)
    if m:
        start_tokens = tokenize_wells(m.group(1))
        start = start_tokens[-1] if start_tokens else normalize_well(m.group(1))
        road_seg = m.group(2).upper()
        well_num = m.group(3)
        if road_seg.endswith("W") and len(road_seg) > 1:
            end = _end_label_from_road_well(road_seg[:-1], well_num)
        elif len(road_seg) == 3 and road_seg[2] in "Ww":
            end = _end_label_from_road_well(road_seg[:2], well_num)
        else:
            end = _end_label_from_road_well(road_seg, well_num)
        return ChainParse(start, end, "well_pair", ["ROAD_WELL_END_OCR"])

    return None


def infer_pipe_system(
    chain_start: str | None,
    chain_end: str | None,
    chain_text: str = "",
) -> str | None:
    """雨/污/合流：编号含 W→污水、含 Y→雨水、以 H 开头→合流。"""
    parts = [
        preprocess_text(chain_start or ""),
        preprocess_text(chain_end or ""),
        preprocess_text(chain_text),
    ]
    blob = "-".join(p for p in parts if p).upper()
    if not blob:
        return None
    if re.match(r"^H", blob) or any(
        preprocess_text(p).upper().startswith("H") for p in (chain_start, chain_end) if p
    ):
        return "合流"
    if re.search(r"(^|-)[Y]\d", blob) or re.search(r"(^|-)Y\d", blob):
        return "雨水"
    if re.search(r"(^|-)[W]\d", blob) or re.search(r"(^|-)W\d", blob):
        return "污水"
    return None


def parse_chain_from_text(text: str) -> ChainParse:
    text = preprocess_text(text)
    if not text:
        return ChainParse(None, None, "unparsed", ["CHAIN_EMPTY"])

    road_cp = _parse_chain_road_well_end(text)
    if road_cp:
        return road_cp

    tokens = tokenize_wells(text)
    if len(tokens) >= 2:
        warnings: list[str] = []
        if len(tokens) > 2:
            warnings.append("EXTRA_TOKENS_IGNORED")
        return ChainParse(tokens[0], tokens[-1], "well_pair", warnings)

    if len(tokens) == 1:
        start = tokens[0]
        suffix = _descriptive_suffix(text, start)
        if suffix:
            return ChainParse(start, suffix, "descriptive_end", ["END_LABEL_DESCRIPTIVE"])
        return ChainParse(start, None, "single_well", ["SINGLE_TOKEN_ONLY"])

    if "-" in text:
        return ChainParse(None, None, "unparsed", ["CHAIN_UNPARSED"])

    return ChainParse(None, None, "unparsed", ["CHAIN_UNPARSED"])


def _descriptive_suffix(text: str, start_token: str) -> str | None:
    """After first well head, remainder after hyphen is descriptive end (Chinese etc.)."""
    text = preprocess_text(text)
    m = WELL_HEAD.search(text)
    if not m:
        return None
    rest = text[m.end() :].strip()
    if rest.startswith("-"):
        rest = rest[1:].strip()
    if not rest:
        return None
    if WELL_HEAD.match(rest) or tokenize_wells(rest):
        return None
    return rest


def score_diameter(text: str) -> tuple[float, int | None, str | None]:
    t = preprocess_text(text).replace(" ", "")
    t = re.sub(r"(?i)DN([0-9O]+)", lambda m: "DN" + m.group(1).replace("O", "0").replace("o", "0"), t)
    best = 0.0
    val: int | None = None
    raw: str | None = None
    for pat, w in DIAMETER_PATTERNS:
        m = pat.search(t)
        if m:
            score = w
            if score > best:
                best = score
                val = int(m.group(1))
                raw = m.group(0)
    return best, val, raw


def score_chain(text: str) -> float:
    t = preprocess_text(text)
    if TIME_HINT.search(t):
        return 0.0
    if score_diameter(t)[0] >= 0.85:
        return 0.0
    if "-" not in t and not WELL_HEAD.search(t):
        return 0.0
    cp = parse_chain_from_text(t)
    if cp.mode == "well_pair":
        return 0.95
    if cp.mode == "descriptive_end":
        return 0.85
    if cp.mode == "single_well":
        return 0.5
    return 0.2 if "-" in t else 0.0


def _score_material_on_text(t: str) -> tuple[float, str | None]:
    if not t:
        return 0.0, None
    d_sc, _, _ = score_diameter(t)
    has_lex = any(p.search(t) for p, _ in MATERIAL_PATTERNS)
    if d_sc >= 0.85 and not t.endswith("管") and not has_lex:
        return 0.0, None
    if not has_lex and not t.endswith("管"):
        for hint in ROAD_HINTS:
            if hint in t:
                return 0.0, None
    for pat, canonical in MATERIAL_PATTERNS:
        if pat.search(t):
            return 0.95, canonical
    if t.endswith("管"):
        body = t[:-1].strip()
        if body and len(body) <= 32:
            for pat, canonical in MATERIAL_PATTERNS:
                if pat.search(body):
                    return 0.9, canonical
            return 0.85, body
    return 0.0, None


def score_material(text: str) -> tuple[float, str | None]:
    """管材：词表正则命中 **或** 文本以「管」结尾（满足其一即可）。"""
    t = preprocess_text(text).strip()
    if not t:
        return 0.0, None
    best = (0.0, None)
    for candidate in (t, re.sub(r"\s+", "", t)):
        sc, mat = _score_material_on_text(candidate)
        if sc > best[0]:
            best = (sc, mat)
    return best


def pick_best_material(texts: list[str]) -> tuple[float, str | None]:
    """Scan lines, compact text, and fragments ending with 管."""
    best = (0.0, None)
    for raw in texts:
        for piece in (raw, preprocess_text(raw), re.sub(r"\s+", "", preprocess_text(raw))):
            sc, mat = score_material(piece)
            if sc > best[0]:
                best = (sc, mat)
        if "管" in raw:
            for frag in re.split(r"[\s,，;；|]+", raw):
                if frag.endswith("管") or any(p.search(frag) for p, _ in MATERIAL_PATTERNS):
                    sc, mat = score_material(frag)
                    if sc > best[0]:
                        best = (sc, mat)
    return best


def score_date(text: str) -> tuple[float, str | None, str | None]:
    t = preprocess_text(text)
    if TIME_HINT.search(t) and not DATE_PATTERN.search(t):
        return 0.0, None, None
    m = DATE_PATTERN.search(t)
    if not m:
        return 0.0, None, None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        iso = date(y, mo, d).isoformat()
    except ValueError:
        return 0.0, None, None
    return 0.93, iso, m.group(0)


def classify_block(text: str) -> tuple[str, float]:
    scores = {
        "diameter": score_diameter(text)[0],
        "chain": score_chain(text),
        "material": score_material(text)[0],
        "date": score_date(text)[0],
    }
    best = max(scores, key=scores.get)
    if scores[best] < 0.5:
        return "unknown", scores[best]
    return best, scores[best]


def parse_from_text_blocks(blocks: list[str], filename_stem: str | "") -> ParseResult:
    """Content-based extraction from OCR lines (any order)."""
    result = ParseResult(filename_stem=filename_stem or None)
    blocks = [preprocess_text(b) for b in blocks if b and b.strip()]
    result.ocr_blocks_used = blocks

    meta_blob = " ".join(blocks)

    best_d = (0.0, None, None)
    best_m = (0.0, None)
    best_dt = (0.0, None, None)
    chain_candidates: list[tuple[float, ChainParse, str]] = []

    mat_sc, mat_val = pick_best_material(blocks + ([meta_blob] if meta_blob else []))
    if mat_val:
        best_m = (mat_sc, mat_val)

    for b in blocks:
        ms, mat = score_material(b)
        if ms > best_m[0]:
            best_m = (ms, mat)
        kind, sc = classify_block(b)
        if kind == "diameter":
            ds, v, raw = score_diameter(b)
            if ds > best_d[0]:
                best_d = (ds, v, raw)
        elif kind == "date":
            dts, iso, raw = score_date(b)
            if dts > best_dt[0]:
                best_dt = (dts, iso, raw)
        elif kind == "chain":
            cp = parse_chain_from_text(b)
            chain_candidates.append((sc, cp, "ocr_block"))

    if meta_blob:
        cp = parse_chain_from_text(meta_blob)
        meta_sc = 0.88 if cp.mode == "well_pair" else 0.7
        if any(_is_diameter_token(t) for t in tokenize_wells(meta_blob)):
            meta_sc *= 0.5
        chain_candidates.append((meta_sc, cp, "meta_blob"))

    if filename_stem:
        cp_fn = parse_chain_from_text(filename_stem)
        chain_candidates.append(
            (0.8 if cp_fn.mode == "well_pair" else 0.65, cp_fn, "filename")
        )

    if best_d[1] is not None:
        result.diameter_mm = best_d[1]
        result.diameter_raw = best_d[2]
        result.field_confidence["diameter"] = best_d[0]

    if best_m[1]:
        result.pipe_material = best_m[1]
        result.field_confidence["material"] = best_m[0]
    elif meta_blob:
        for pat, canonical in MATERIAL_PATTERNS:
            if pat.search(meta_blob) and score_diameter(meta_blob)[0] < 0.85:
                result.pipe_material = canonical
                result.field_confidence["material"] = 0.85
                break

    if best_dt[1]:
        result.inspection_date = best_dt[1]
        result.inspection_date_raw = best_dt[2]
        result.field_confidence["date"] = best_dt[0]

    if chain_candidates:
        _src_rank = {"ocr_block": 3, "filename": 2, "meta_blob": 1}
        chain_candidates.sort(
            key=lambda x: (
                x[0],
                x[1].mode == "well_pair",
                _src_rank.get(x[2], 0),
                -(len(x[1].warnings)),
            ),
            reverse=True,
        )
        best_sc, best_cp, src = chain_candidates[0]
        result.chain_start_label = best_cp.start
        result.chain_end_label = best_cp.end
        result.chain_parse_mode = best_cp.mode
        result.chain_source = src
        result.chain_confidence = best_sc
        result.chain_warnings = list(best_cp.warnings)
        result.field_confidence["chain"] = best_sc

        fn_cp = next((c for s, c, so in chain_candidates if so == "filename"), None)
        ocr_cp = next((c for s, c, so in chain_candidates if so in ("ocr_block", "meta_blob")), None)
        if fn_cp and ocr_cp and fn_cp.start and ocr_cp.start:
            if fn_cp.start != ocr_cp.start or fn_cp.end != ocr_cp.end:
                result.chain_warnings.append("OCR_FILENAME_MISMATCH")

    chain_blob = meta_blob or (filename_stem or "")
    result.pipe_system = infer_pipe_system(
        result.chain_start_label,
        result.chain_end_label,
        chain_blob,
    )

    _validate_date(result)
    _validate_diameter(result)
    return result


def _validate_date(result: ParseResult) -> None:
    if not result.inspection_date:
        return
    try:
        d = date.fromisoformat(result.inspection_date)
    except ValueError:
        return
    if d.year < 2000:
        result.chain_warnings.append("DATE_OUT_OF_RANGE")
    if d > date.today():
        result.chain_warnings.append("DATE_OUT_OF_RANGE")


def _validate_diameter(result: ParseResult) -> None:
    if result.diameter_mm is None:
        return
    if not (150 <= result.diameter_mm <= 3000):
        result.chain_warnings.append("DIAMETER_OUT_OF_RANGE")


def parse_filename_only(filename_stem: str) -> ParseResult:
    return parse_from_text_blocks([], filename_stem)


def ocr_lines_to_blocks(raw: str) -> list[str]:
    if not raw.strip():
        return []
    return [ln.strip() for ln in raw.splitlines() if ln.strip()]
