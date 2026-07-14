"""korea-life-mcp: 한국 생활 특화 유틸리티 순수 함수 모음.

외부 API/네트워크에 의존하지 않는 자기완결형(self-contained) 함수들입니다.
server.py 가 이 함수들을 MCP 도구로 노출합니다. 테스트는 test_tools.py 참고.
"""

from __future__ import annotations

import datetime as _dt
import re

# ---------------------------------------------------------------------------
# 한글 자모 상수 (유니코드 한글 음절 U+AC00 ~ U+D7A3)
# ---------------------------------------------------------------------------
HANGUL_BASE = 0xAC00
HANGUL_LAST = 0xD7A3

CHO = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")  # 초성 19
JUNG = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")  # 중성 21
JONG = [""] + list("ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ")  # 종성 28(빈 것 포함)


def is_hangul_syllable(ch: str) -> bool:
    return len(ch) == 1 and HANGUL_BASE <= ord(ch) <= HANGUL_LAST


def _split_syllable(ch: str) -> tuple[int, int, int]:
    """완성형 한글 한 글자를 (초성, 중성, 종성) 인덱스로 분해."""
    code = ord(ch) - HANGUL_BASE
    jong = code % 28
    jung = (code // 28) % 21
    cho = code // (28 * 21)
    return cho, jung, jong


# ---------------------------------------------------------------------------
# 1) 한글 자모 분해 / 조합 / 초성 추출
# ---------------------------------------------------------------------------
def decompose_hangul(text: str) -> dict:
    """문자열의 각 글자를 초성/중성/종성으로 분해한다."""
    result = []
    for ch in text:
        if is_hangul_syllable(ch):
            cho, jung, jong = _split_syllable(ch)
            result.append(
                {
                    "char": ch,
                    "cho": CHO[cho],
                    "jung": JUNG[jung],
                    "jong": JONG[jong] if jong else None,
                }
            )
        else:
            result.append({"char": ch, "cho": None, "jung": None, "jong": None})
    flat = "".join(
        (r["cho"] or "") + (r["jung"] or "") + (r["jong"] or "")
        if is_hangul_syllable(r["char"])
        else r["char"]
        for r in result
    )
    return {"input": text, "syllables": result, "jamo": flat}


def chosung(text: str) -> str:
    """초성 검색용: 각 글자의 초성만 뽑는다. (예: '한국어' -> 'ㅎㄱㅇ')"""
    out = []
    for ch in text:
        if is_hangul_syllable(ch):
            cho, _, _ = _split_syllable(ch)
            out.append(CHO[cho])
        else:
            out.append(ch)
    return "".join(out)


def compose_hangul(cho: str, jung: str, jong: str = "") -> dict:
    """초/중/종성을 완성형 한글 한 글자로 조합한다."""
    if cho not in CHO:
        raise ValueError(f"초성이 올바르지 않습니다: {cho!r}")
    if jung not in JUNG:
        raise ValueError(f"중성이 올바르지 않습니다: {jung!r}")
    if jong and jong not in JONG:
        raise ValueError(f"종성이 올바르지 않습니다: {jong!r}")
    ci = CHO.index(cho)
    ji = JUNG.index(jung)
    ki = JONG.index(jong) if jong else 0
    code = HANGUL_BASE + (ci * 21 + ji) * 28 + ki
    return {"char": chr(code), "code": f"U+{code:04X}"}


# ---------------------------------------------------------------------------
# 2) 로마자 표기 (국어의 로마자 표기법 기반, 기본 연음 처리)
#    ※ 완전한 자음동화(예: 종로->Jongno)는 단순화됨. README 한계 참고.
# ---------------------------------------------------------------------------
_ROM_CHO = {
    "ㄱ": "g", "ㄲ": "kk", "ㄴ": "n", "ㄷ": "d", "ㄸ": "tt", "ㄹ": "r",
    "ㅁ": "m", "ㅂ": "b", "ㅃ": "pp", "ㅅ": "s", "ㅆ": "ss", "ㅇ": "",
    "ㅈ": "j", "ㅉ": "jj", "ㅊ": "ch", "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h",
}
_ROM_JUNG = {
    "ㅏ": "a", "ㅐ": "ae", "ㅑ": "ya", "ㅒ": "yae", "ㅓ": "eo", "ㅔ": "e",
    "ㅕ": "yeo", "ㅖ": "ye", "ㅗ": "o", "ㅘ": "wa", "ㅙ": "wae", "ㅚ": "oe",
    "ㅛ": "yo", "ㅜ": "u", "ㅝ": "wo", "ㅞ": "we", "ㅟ": "wi", "ㅠ": "yu",
    "ㅡ": "eu", "ㅢ": "ui", "ㅣ": "i",
}
_ROM_JONG = {
    "": "", "ㄱ": "k", "ㄲ": "k", "ㄳ": "k", "ㄴ": "n", "ㄵ": "n", "ㄶ": "n",
    "ㄷ": "t", "ㄹ": "l", "ㄺ": "k", "ㄻ": "m", "ㄼ": "l", "ㄽ": "l", "ㄾ": "l",
    "ㄿ": "p", "ㅀ": "l", "ㅁ": "m", "ㅂ": "p", "ㅄ": "p", "ㅅ": "t", "ㅆ": "t",
    "ㅇ": "ng", "ㅈ": "t", "ㅊ": "t", "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "t",
}
# 종성이 뒤 음절 초성 ㅇ 으로 연음될 때, 초성으로 발음되는 자모(단일 받침)
_LIAISON = {
    "ㄱ": "ㄱ", "ㄲ": "ㄲ", "ㄴ": "ㄴ", "ㄷ": "ㄷ", "ㄹ": "ㄹ", "ㅁ": "ㅁ",
    "ㅂ": "ㅂ", "ㅅ": "ㅅ", "ㅆ": "ㅆ", "ㅈ": "ㅈ", "ㅊ": "ㅊ", "ㅋ": "ㅋ",
    "ㅌ": "ㅌ", "ㅍ": "ㅍ",
}

# 받침 소리 분류(대표음 기준) — 자음동화 규칙에 사용
_CODA_G = {"ㄱ", "ㄲ", "ㄳ", "ㄺ", "ㅋ"}   # 대표음 ㄱ
_CODA_D = {"ㄷ", "ㅅ", "ㅆ", "ㅈ", "ㅊ", "ㅌ", "ㅎ"}  # 대표음 ㄷ
_CODA_B = {"ㅂ", "ㅄ", "ㅍ", "ㄼ", "ㄿ"}   # 대표음 ㅂ
_CODA_LIQ = {"ㄹ", "ㄾ", "ㄽ", "ㅀ"}       # 대표음 ㄹ


def _assimilate(coda: str, onset: str):
    """앞 음절 받침(coda)과 뒤 음절 초성(onset)의 자음동화를 계산.

    반환: (새 받침 자모 또는 None, 새 초성 자모 또는 None). None 은 '변화 없음'.
    표준 발음법의 유음화·비음화 주요 규칙만 반영(구개음화·ㅎ축약 등은 제외).
    """
    # 유음화(ㄹㄹ)
    if coda == "ㄴ" and onset == "ㄹ":
        return "ㄹ", "ㄹ"
    if coda in _CODA_LIQ and onset == "ㄴ":
        return "ㄹ", "ㄹ"
    # ㄹ 앞에서의 비음화
    if onset == "ㄹ":
        if coda in ("ㅁ", "ㅇ"):
            return None, "ㄴ"
        if coda in _CODA_G:
            return "ㅇ", "ㄴ"
        if coda in _CODA_D:
            return "ㄴ", "ㄴ"
        if coda in _CODA_B:
            return "ㅁ", "ㄴ"
    # ㄴ/ㅁ 앞에서의 비음화
    if onset in ("ㄴ", "ㅁ"):
        if coda in _CODA_G:
            return "ㅇ", None
        if coda in _CODA_D:
            return "ㄴ", None
        if coda in _CODA_B:
            return "ㅁ", None
    return None, None


def romanize(text: str) -> dict:
    """한글 문자열을 로마자로 변환한다(국어의 로마자 표기법 기반).

    - 자모 단위 매핑 + 받침 무성음화 + 연음(liaison)
    - 자음동화(유음화·비음화) 주요 규칙 반영: 종로→jongno, 신라→silla 등
    - 겹받침 연음, 구개음화, ㅎ축약 등 일부 음운 변동은 단순화됨.
    """
    # 1) 음절 리스트로 분해
    sylls: list = []  # [cho, jung, jong] 또는 원본 문자열
    for ch in text:
        if is_hangul_syllable(ch):
            sylls.append(list(_split_syllable(ch)))
        else:
            sylls.append(ch)

    # 2) 경계 처리: 연음 또는 자음동화
    for i in range(len(sylls) - 1):
        cur, nxt = sylls[i], sylls[i + 1]
        if not isinstance(cur, list) or not isinstance(nxt, list):
            continue
        coda = JONG[cur[2]]
        onset = CHO[nxt[0]]
        if not coda:
            continue
        if onset == "ㅇ":
            # 연음: 뒤 음절 초성이 ㅇ 이면 단일 받침을 이동(ㅇ 받침 제외)
            if coda != "ㅇ" and coda in _LIAISON:
                cur[2] = 0
                nxt[0] = CHO.index(_LIAISON[coda])
            continue
        new_coda, new_onset = _assimilate(coda, onset)
        if new_coda is not None:
            cur[2] = JONG.index(new_coda)
        if new_onset is not None:
            nxt[0] = CHO.index(new_onset)

    # 3) 음절별 로마자 조합 (ㄹㄹ → ll 처리 포함)
    out = []
    for i, s in enumerate(sylls):
        if isinstance(s, list):
            cho, jung, jong = s
            cho_rom = _ROM_CHO[CHO[cho]]
            if (
                CHO[cho] == "ㄹ"
                and i > 0
                and isinstance(sylls[i - 1], list)
                and JONG[sylls[i - 1][2]] == "ㄹ"
            ):
                cho_rom = "l"  # ㄹㄹ 은 'll'
            out.append(cho_rom + _ROM_JUNG[JUNG[jung]] + _ROM_JONG[JONG[jong]])
        else:
            out.append(s)
    romanized = "".join(out)
    return {"input": text, "romanized": romanized}


# ---------------------------------------------------------------------------
# 3) 숫자 <-> 한글 (금액 표기)
# ---------------------------------------------------------------------------
_NUM_DIGITS = "영일이삼사오육칠팔구"
_SMALL_UNITS = ["", "십", "백", "천"]
_BIG_UNITS = ["", "만", "억", "조", "경"]


def _group_to_korean(group: int, formal: bool) -> str:
    """0~9999 사이의 4자리 묶음을 한글로."""
    s = str(group).zfill(4)
    parts = []
    for i, ch in enumerate(s):
        d = int(ch)
        pos = 3 - i  # 3=천, 2=백, 1=십, 0=일
        if d == 0:
            continue
        if d == 1 and pos != 0 and not formal:
            parts.append(_SMALL_UNITS[pos])  # '일십' -> '십'
        else:
            parts.append(_NUM_DIGITS[d] + _SMALL_UNITS[pos])
    return "".join(parts)


def number_to_korean(amount: int, style: str = "read") -> dict:
    """정수를 한글로 표기한다.

    style="read"   : 자연스러운 읽기 (예: 12345 -> '일만이천삼백사십오')
    style="formal" : 금액 정자체 (예: 12345 -> '금 일만이천삼백사십오원정', 일십/일백 유지)
    """
    if not isinstance(amount, int):
        raise ValueError("amount 는 정수여야 합니다.")
    formal = style == "formal"
    negative = amount < 0
    n = abs(amount)

    if n == 0:
        body = "영"
    else:
        groups = []
        while n > 0:
            groups.append(n % 10000)
            n //= 10000
        if len(groups) > len(_BIG_UNITS):
            raise ValueError("지원 범위(경 미만)를 초과했습니다.")
        chunks = []
        for idx in range(len(groups) - 1, -1, -1):
            g = groups[idx]
            if g == 0:
                continue
            chunks.append(_group_to_korean(g, formal) + _BIG_UNITS[idx])
        body = "".join(chunks)

    if negative:
        body = "마이너스" + body

    if formal:
        text = f"금 {body}원정"
    else:
        text = body
    return {"amount": amount, "style": style, "korean": text}


_KOR_DIGIT = {"영": 0, "공": 0, **{c: i for i, c in enumerate(_NUM_DIGITS)}}
_KOR_SMALL = {"십": 10, "백": 100, "천": 1000}
_KOR_BIG = {"만": 10**4, "억": 10**8, "조": 10**12, "경": 10**16}


def korean_to_number(text: str) -> dict:
    """한글 금액/숫자 표기를 정수로 변환한다. (예: '일만이천삼백사십오' -> 12345)"""
    cleaned = re.sub(r"[\s,원정금]", "", text)
    negative = cleaned.startswith("마이너스")
    if negative:
        cleaned = cleaned[len("마이너스"):]

    result = 0
    group = 0
    num = 0
    for ch in cleaned:
        if ch in _KOR_DIGIT:
            num = _KOR_DIGIT[ch]
        elif ch in _KOR_SMALL:
            group += (num if num else 1) * _KOR_SMALL[ch]
            num = 0
        elif ch in _KOR_BIG:
            group += num
            result += group * _KOR_BIG[ch]
            group = 0
            num = 0
        else:
            raise ValueError(f"해석할 수 없는 문자: {ch!r}")
    value = result + group + num
    if negative:
        value = -value
    return {"input": text, "number": value}


# ---------------------------------------------------------------------------
# 4) 사업자등록번호 검증 (체크섬)
# ---------------------------------------------------------------------------
def validate_business_number(number: str) -> dict:
    """대한민국 사업자등록번호(10자리) 형식/체크섬 검증."""
    digits = re.sub(r"\D", "", number)
    if len(digits) != 10:
        return {"input": number, "valid": False, "reason": "10자리 숫자가 아닙니다."}
    d = [int(c) for c in digits]
    weights = [1, 3, 7, 1, 3, 7, 1, 3, 5]
    total = sum(d[i] * weights[i] for i in range(9))
    total += (d[8] * 5) // 10
    check = (10 - (total % 10)) % 10
    valid = check == d[9]
    return {
        "input": number,
        "normalized": f"{digits[:3]}-{digits[3:5]}-{digits[5:]}",
        "valid": valid,
        "reason": "정상" if valid else "체크섬 불일치",
    }


# ---------------------------------------------------------------------------
# 5) 주민등록번호 검증 (형식/체크섬 + 생년월일·성별 추출)
#    ※ 개인정보를 조회하지 않으며, 순수 형식 검증만 수행합니다.
#    ※ 2020.10 이후 발급 번호는 체크섬이 없을 수 있습니다.
# ---------------------------------------------------------------------------
_RRN_CENTURY = {
    "1": (1900, "남"), "2": (1900, "여"),
    "3": (2000, "남"), "4": (2000, "여"),
    "5": (1900, "남(외국인)"), "6": (1900, "여(외국인)"),
    "7": (2000, "남(외국인)"), "8": (2000, "여(외국인)"),
    "9": (1800, "남"), "0": (1800, "여"),
}


def validate_rrn(number: str) -> dict:
    """주민등록번호(13자리) 형식/체크섬 검증 및 생년월일·성별 추출."""
    digits = re.sub(r"\D", "", number)
    if len(digits) != 13:
        return {"input": number, "valid": False, "reason": "13자리 숫자가 아닙니다."}

    yy, mm, dd = digits[0:2], digits[2:4], digits[4:6]
    gender_code = digits[6]
    info = {"input": number}

    if gender_code in _RRN_CENTURY:
        base, gender = _RRN_CENTURY[gender_code]
        year = base + int(yy)
        try:
            birth = _dt.date(year, int(mm), int(dd))
            info["birth_date"] = birth.isoformat()
            info["gender"] = gender
        except ValueError:
            info["birth_date"] = None
            info["gender"] = gender
            info["date_valid"] = False
    else:
        info["gender"] = None

    d = [int(c) for c in digits]
    weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]
    total = sum(d[i] * weights[i] for i in range(12))
    check = (11 - (total % 11)) % 10
    checksum_ok = check == d[12]
    info["checksum_valid"] = checksum_ok
    info["valid"] = checksum_ok
    info["note"] = (
        "정상" if checksum_ok
        else "체크섬 불일치(2020.10 이후 발급 번호는 검증식이 적용되지 않을 수 있음)"
    )
    return info


# ---------------------------------------------------------------------------
# 6) 공휴일 / 영업일(근무일) 계산
#    - 양력 고정 공휴일은 어떤 연도든 계산 가능.
#    - 음력 기반(설날·추석·부처님오신날) 및 대체공휴일은 표(_LUNAR_TABLE)에 의존.
#      해당 표는 연도별로 검증/갱신이 필요합니다(README 참고).
# ---------------------------------------------------------------------------
_FIXED_HOLIDAYS = {
    (1, 1): "신정",
    (3, 1): "삼일절",
    (5, 5): "어린이날",
    (6, 6): "현충일",
    (8, 15): "광복절",
    (10, 3): "개천절",
    (10, 9): "한글날",
    (12, 25): "성탄절",
}

# 음력 기반 및 대체공휴일 (연도별 확정 데이터). 필요 시 최신 관보 기준으로 갱신하세요.
_LUNAR_TABLE = {
    2025: {
        "2025-01-28": "설날 연휴", "2025-01-29": "설날", "2025-01-30": "설날 연휴",
        "2025-05-05": "부처님오신날/어린이날", "2025-05-06": "대체공휴일",
        "2025-10-05": "추석 연휴", "2025-10-06": "추석", "2025-10-07": "추석 연휴",
        "2025-10-08": "대체공휴일(추석)",
    },
    2026: {
        "2026-02-16": "설날 연휴", "2026-02-17": "설날", "2026-02-18": "설날 연휴",
        "2026-03-02": "대체공휴일(삼일절)",
        "2026-05-24": "부처님오신날", "2026-05-25": "대체공휴일(부처님오신날)",
        "2026-09-24": "추석 연휴", "2026-09-25": "추석", "2026-09-26": "추석 연휴",
    },
}


def korean_holidays(year: int) -> dict:
    """해당 연도의 대한민국 공휴일 목록을 반환한다."""
    holidays: dict[str, str] = {}
    for (mm, dd), name in _FIXED_HOLIDAYS.items():
        holidays[_dt.date(year, mm, dd).isoformat()] = name
    lunar = _LUNAR_TABLE.get(year, {})
    holidays.update(lunar)
    complete = year in _LUNAR_TABLE
    items = [{"date": d, "name": n} for d, n in sorted(holidays.items())]
    return {
        "year": year,
        "count": len(items),
        "holidays": items,
        "lunar_data_available": complete,
        "note": None if complete
        else f"{year}년 음력/대체공휴일 데이터가 없어 양력 고정 공휴일만 포함되었습니다.",
    }


def _holiday_dates_for_range(start: _dt.date, end: _dt.date) -> set[_dt.date]:
    dates: set[_dt.date] = set()
    for year in range(start.year, end.year + 1):
        for item in korean_holidays(year)["holidays"]:
            dates.add(_dt.date.fromisoformat(item["date"]))
    return dates


def business_days_between(start_date: str, end_date: str) -> dict:
    """두 날짜(포함) 사이의 영업일(주말·공휴일 제외) 수를 계산한다.

    날짜 형식: 'YYYY-MM-DD'
    """
    start = _dt.date.fromisoformat(start_date)
    end = _dt.date.fromisoformat(end_date)
    if end < start:
        start, end = end, start
    holidays = _holiday_dates_for_range(start, end)

    total = (end - start).days + 1
    business = 0
    weekend = 0
    holiday_hit = 0
    cur = start
    incomplete_years = set()
    while cur <= end:
        if cur.year not in _LUNAR_TABLE:
            incomplete_years.add(cur.year)
        if cur.weekday() >= 5:  # 토(5), 일(6)
            weekend += 1
        elif cur in holidays:
            holiday_hit += 1
        else:
            business += 1
        cur += _dt.timedelta(days=1)

    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "total_days": total,
        "business_days": business,
        "weekend_days": weekend,
        "holiday_days": holiday_hit,
        "note": None if not incomplete_years
        else f"음력/대체공휴일 데이터가 없는 연도 포함: {sorted(incomplete_years)} (영업일이 실제보다 많게 계산될 수 있음)",
    }


# ---------------------------------------------------------------------------
# 7) 전화번호 포맷 / 지역 판별
# ---------------------------------------------------------------------------
_AREA_CODES = {
    "02": "서울", "031": "경기", "032": "인천", "033": "강원",
    "041": "충남", "042": "대전", "043": "충북", "044": "세종",
    "051": "부산", "052": "울산", "053": "대구", "054": "경북", "055": "경남",
    "061": "전남", "062": "광주", "063": "전북", "064": "제주",
}
_MOBILE_PREFIX = {"010", "011", "016", "017", "018", "019"}


def format_phone_number(number: str) -> dict:
    """대한민국 전화번호를 표준 형태로 포맷하고 종류/지역을 판별한다."""
    d = re.sub(r"\D", "", number)
    kind = "알 수 없음"
    region = None

    def _split_local(rest: str) -> str:
        # 국번(3~4자리) + 4자리
        if len(rest) == 8:
            return f"{rest[:4]}-{rest[4:]}"
        if len(rest) == 7:
            return f"{rest[:3]}-{rest[3:]}"
        return rest

    if d[:3] in _MOBILE_PREFIX:
        kind = "휴대전화"
        rest = d[3:]
        formatted = f"{d[:3]}-{_split_local(rest)}" if rest else d
    elif d.startswith("070"):
        kind = "인터넷전화"
        formatted = f"070-{_split_local(d[3:])}"
    elif d.startswith("050"):
        kind = "평생번호"
        formatted = f"{d[:4]}-{_split_local(d[4:])}"
    elif d[:4] in {"1588", "1577", "1544", "1566", "1600", "1666", "1670", "1899", "1811", "1522"} or (
        len(d) == 8 and d[0] == "1"
    ):
        kind = "전국대표번호"
        formatted = f"{d[:4]}-{d[4:]}"
    elif d.startswith("02"):
        kind = "지역번호(유선)"
        region = "서울"
        formatted = f"02-{_split_local(d[2:])}"
    elif d[:3] in _AREA_CODES:
        kind = "지역번호(유선)"
        region = _AREA_CODES[d[:3]]
        formatted = f"{d[:3]}-{_split_local(d[3:])}"
    else:
        formatted = d

    return {
        "input": number,
        "digits": d,
        "formatted": formatted,
        "kind": kind,
        "region": region,
    }


# ---------------------------------------------------------------------------
# 8) 면적 단위 변환 (평 <-> ㎡)
# ---------------------------------------------------------------------------
_PYEONG_TO_M2 = 400 / 121  # 1평 = 400/121 ≈ 3.305785 ㎡


def area_convert(value: float, unit: str) -> dict:
    """면적을 평↔㎡ 로 변환한다. unit='pyeong' 또는 'm2'."""
    unit = unit.lower()
    if unit in ("pyeong", "평"):
        m2 = value * _PYEONG_TO_M2
        return {"input": value, "unit": "pyeong", "pyeong": round(value, 4),
                "m2": round(m2, 4)}
    if unit in ("m2", "㎡", "sqm"):
        pyeong = value / _PYEONG_TO_M2
        return {"input": value, "unit": "m2", "m2": round(value, 4),
                "pyeong": round(pyeong, 4)}
    raise ValueError("unit 은 'pyeong' 또는 'm2' 여야 합니다.")


# ---------------------------------------------------------------------------
# 9) 만 나이 계산 (2023.6 이후 '만 나이' 공식)
# ---------------------------------------------------------------------------
def korean_age(birth_date: str, base_date: str) -> dict:
    """생년월일과 기준일로 만 나이·연 나이·세는나이를 계산한다. 형식 'YYYY-MM-DD'."""
    birth = _dt.date.fromisoformat(birth_date)
    base = _dt.date.fromisoformat(base_date)
    if base < birth:
        raise ValueError("기준일이 생년월일보다 빠릅니다.")
    man_age = base.year - birth.year - (
        1 if (base.month, base.day) < (birth.month, birth.day) else 0
    )
    year_age = base.year - birth.year
    return {
        "birth_date": birth.isoformat(),
        "base_date": base.isoformat(),
        "manAge": man_age,        # 만 나이 (공식)
        "yearAge": year_age,      # 연 나이 (병역·청소년보호법 등)
        "koreanAge": year_age + 1,  # 세는 나이 (2023.6 폐지, 참고용)
        "note": "2023.6.28부터 법적으로 '만 나이'가 공식 기준입니다.",
    }


# ---------------------------------------------------------------------------
# 10) 원화 금액 포맷
# ---------------------------------------------------------------------------
def won_format(amount: int) -> dict:
    """정수 금액을 천 단위 구분 원화 형식으로 포맷한다."""
    if not isinstance(amount, int):
        raise ValueError("amount 는 정수여야 합니다.")
    grouped = f"{amount:,}"
    return {"amount": amount, "won": f"₩{grouped}", "text": f"{grouped}원"}


def d_day(target_date: str, base_date: str | None = None) -> dict:
    """목표일까지 남은 일수(D-day)를 계산한다. base_date 미지정 시 today 대신 명시 필요."""
    if base_date is None:
        raise ValueError("base_date('YYYY-MM-DD')를 지정하세요. (서버는 현재시각을 임의로 쓰지 않습니다)")
    target = _dt.date.fromisoformat(target_date)
    base = _dt.date.fromisoformat(base_date)
    diff = (target - base).days
    if diff > 0:
        label = f"D-{diff}"
    elif diff < 0:
        label = f"D+{abs(diff)}"
    else:
        label = "D-day"
    return {"base": base.isoformat(), "target": target.isoformat(), "days": diff, "label": label}
