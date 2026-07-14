"""korea-life-mcp : 한국 생활 특화 MCP 서버 (PlayMCP 공모전 제출용).

외부 API 키 없이 동작하는 자기완결형 원격 MCP 서버입니다.

실행 방법
---------
  # 1) 로컬 개발 (stdio) — Claude Desktop 등에서 직접 연결
  python server.py

  # 2) 원격(Streamable HTTP) — PlayMCP/카카오 클라우드 배포 형태
  MCP_TRANSPORT=http python server.py        # -> http://0.0.0.0:8000/mcp

환경변수
  MCP_TRANSPORT : "stdio"(기본) 또는 "http"
  HOST          : HTTP 바인드 주소 (기본 0.0.0.0)
  PORT          : HTTP 포트 (기본 8000)
"""

import os

from mcp.server.fastmcp import FastMCP

import korea_tools as kt

mcp = FastMCP(
    "korea-life-mcp",
    host=os.environ.get("HOST", "0.0.0.0"),
    port=int(os.environ.get("PORT", "8000")),
    instructions=(
        "대한민국 생활 특화 유틸리티 서버입니다. 한글 자모 분해/조합/초성 검색, "
        "로마자 표기, 숫자↔한글 금액 변환, 사업자등록번호·주민등록번호 형식 검증, "
        "공휴일·영업일 계산, D-day 계산 도구를 제공합니다. "
        "모든 도구는 외부 네트워크에 접속하지 않으며 개인정보를 조회하지 않습니다."
    ),
)


# --- 한글 자모 --------------------------------------------------------------
@mcp.tool()
def decompose_hangul(text: str) -> dict:
    """한글 문자열을 초성/중성/종성으로 분해합니다. (예: '값' → ㄱ,ㅏ,ㅄ)"""
    return kt.decompose_hangul(text)


@mcp.tool()
def chosung(text: str) -> dict:
    """초성 검색용 문자열을 만듭니다. (예: '한국어' → 'ㅎㄱㅇ')"""
    return {"input": text, "chosung": kt.chosung(text)}


@mcp.tool()
def compose_hangul(cho: str, jung: str, jong: str = "") -> dict:
    """초/중/종성 자모를 완성형 한글 한 글자로 조합합니다. (예: ㅎ,ㅏ,ㄴ → '한')"""
    return kt.compose_hangul(cho, jung, jong)


# --- 로마자 -----------------------------------------------------------------
@mcp.tool()
def romanize(text: str) -> dict:
    """한글을 로마자로 표기합니다(국어의 로마자 표기법 기반, 기본 연음 처리)."""
    return kt.romanize(text)


# --- 숫자/한글 금액 ---------------------------------------------------------
@mcp.tool()
def number_to_korean(amount: int, style: str = "read") -> dict:
    """정수를 한글로 표기합니다. style='read'(읽기) 또는 'formal'(금액 정자체, 예: '금 …원정')."""
    return kt.number_to_korean(amount, style)


@mcp.tool()
def korean_to_number(text: str) -> dict:
    """한글 금액/숫자 표기를 정수로 변환합니다. (예: '일만이천삼백사십오' → 12345)"""
    return kt.korean_to_number(text)


# --- 번호 검증 --------------------------------------------------------------
@mcp.tool()
def validate_business_number(number: str) -> dict:
    """대한민국 사업자등록번호(10자리)의 형식과 체크섬을 검증합니다."""
    return kt.validate_business_number(number)


@mcp.tool()
def validate_rrn(number: str) -> dict:
    """주민등록번호(13자리)의 형식/체크섬을 검증하고 생년월일·성별을 추출합니다.
    개인정보를 조회하지 않으며 순수 형식 검증만 수행합니다."""
    return kt.validate_rrn(number)


# --- 날짜/공휴일 ------------------------------------------------------------
@mcp.tool()
def korean_holidays(year: int) -> dict:
    """해당 연도의 대한민국 공휴일 목록을 반환합니다."""
    return kt.korean_holidays(year)


@mcp.tool()
def business_days_between(start_date: str, end_date: str) -> dict:
    """두 날짜(포함, 'YYYY-MM-DD') 사이의 영업일 수를 계산합니다(주말·공휴일 제외)."""
    return kt.business_days_between(start_date, end_date)


@mcp.tool()
def d_day(target_date: str, base_date: str) -> dict:
    """기준일(base_date)로부터 목표일(target_date)까지의 D-day를 계산합니다. 형식 'YYYY-MM-DD'."""
    return kt.d_day(target_date, base_date)


# --- 생활 편의 -------------------------------------------------------------
@mcp.tool()
def format_phone_number(number: str) -> dict:
    """대한민국 전화번호를 표준 형태로 포맷하고 종류(휴대전화/유선 등)와 지역을 판별합니다."""
    return kt.format_phone_number(number)


@mcp.tool()
def area_convert(value: float, unit: str) -> dict:
    """면적을 평↔㎡ 로 변환합니다. unit='pyeong' 또는 'm2'."""
    return kt.area_convert(value, unit)


@mcp.tool()
def korean_age(birth_date: str, base_date: str) -> dict:
    """생년월일과 기준일로 만 나이·연 나이·세는나이를 계산합니다. 형식 'YYYY-MM-DD'."""
    return kt.korean_age(birth_date, base_date)


@mcp.tool()
def won_format(amount: int) -> dict:
    """정수 금액을 천 단위 구분 원화 형식(₩1,234,567 / 1,234,567원)으로 포맷합니다."""
    return kt.won_format(amount)


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()
    if transport in ("http", "streamable-http", "streamable_http"):
        mcp.run(transport="streamable-http")
    elif transport == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
