# korea-life-mcp 🇰🇷

**한국 생활 특화 유틸리티 MCP 서버** — 카카오 **PlayMCP** 공모전(MCP Player 10) 제출용.

외부 API 키·네트워크·개인정보 조회 없이 **완전히 자기완결형**으로 동작하므로, MCP Inspector 검증과 심사가 간단하고 안정적입니다.

---

## 제공 도구 (15종)

| 도구 | 설명 | 예시 |
|------|------|------|
| `decompose_hangul` | 한글을 초/중/종성으로 분해 | `값` → ㄱ, ㅏ, ㅄ |
| `chosung` | 초성 검색용 문자열 생성 | `한국어` → `ㅎㄱㅇ` |
| `compose_hangul` | 자모를 완성형 한글로 조합 | ㅎ,ㅏ,ㄴ → `한` |
| `romanize` | 로마자 표기(자음동화 반영) | `종로` → `jongno` |
| `number_to_korean` | 숫자 → 한글 (읽기/금액 정자체) | `12345` → `일만이천삼백사십오` |
| `korean_to_number` | 한글 금액 → 숫자 | `일만이천삼백사십오` → `12345` |
| `validate_business_number` | 사업자등록번호 체크섬 검증 | `220-81-62517` → valid |
| `validate_rrn` | 주민등록번호 형식/체크섬 + 생년월일·성별 추출 | 형식 검증만 (조회 X) |
| `korean_holidays` | 연도별 공휴일 목록 | `2026` → 신정, 설날 … |
| `business_days_between` | 두 날짜 사이 영업일(주말·공휴일 제외) 수 | |
| `d_day` | 기준일→목표일 D-day 계산 | `D-6` |
| `format_phone_number` | 전화번호 포맷 + 종류/지역 판별 | `0212345678` → 서울, `02-1234-5678` |
| `area_convert` | 면적 평↔㎡ 변환 | `34평` → `112.4㎡` |
| `korean_age` | 만 나이·연 나이·세는나이 계산 | 생년월일+기준일 |
| `won_format` | 원화 천 단위 포맷 | `1234567` → `₩1,234,567` |

> ⚠️ **개인정보 안전**: `validate_rrn`은 어떤 외부 조회도 하지 않으며, 입력된 번호의 **형식·체크섬만** 계산합니다.

---

## 1. 설치 & 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt        # 또는: pip install mcp

# (a) 로컬 개발용 stdio 모드 — Claude Desktop 등에서 직접 실행
python server.py

# (b) 원격(Streamable HTTP) 모드 — PlayMCP 배포와 동일한 형태
#     엔드포인트: http://0.0.0.0:8000/mcp
MCP_TRANSPORT=http python server.py
```

Windows PowerShell에서 HTTP 모드로 띄우려면:

```powershell
$env:MCP_TRANSPORT="http"; python server.py
```

### 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `MCP_TRANSPORT` | `stdio` | `stdio` / `http`(streamable) / `sse` |
| `HOST` | `0.0.0.0` | HTTP 바인드 주소 |
| `PORT` | `8000` | HTTP 포트 |

---

## 2. 자체 테스트

```bash
python test_tools.py       # 순수 로직 21개 케이스 검증 (21/21 PASS)
```

---

## 3. MCP Inspector로 검증 (PlayMCP 등록 전 필수)

Inspector는 별도 설치 없이 `npx`로 실행됩니다.

**HTTP(원격) 모드 검증** — PlayMCP 등록 형태와 동일하므로 권장:

```bash
# 터미널 1: 서버 실행
MCP_TRANSPORT=http python server.py

# 터미널 2: Inspector 실행 후 브라우저에서 접속
npx @modelcontextprotocol/inspector
#  → Transport: "Streamable HTTP"
#  → URL: http://localhost:8000/mcp
#  → Connect → Tools 탭에서 11개 도구 호출 테스트
```

**stdio 모드 검증**:

```bash
npx @modelcontextprotocol/inspector python server.py
```

---

## 4. 카카오 클라우드 배포 (원격 엔드포인트 만들기)

PlayMCP는 **공개 URL을 가진 원격 MCP 서버**를 등록합니다. 포함된 `Dockerfile`로 컨테이너 이미지를 만들어 카카오 클라우드에 배포하세요.

```bash
# 이미지 빌드
docker build -t korea-life-mcp .

# 로컬에서 컨테이너 동작 확인 (http://localhost:8000/mcp)
docker run -p 8000:8000 korea-life-mcp
```

카카오 클라우드에 배포하면 `https://<발급받은-도메인>/mcp` 형태의 **공개 엔드포인트**가 생성됩니다. 이 URL을 다음 단계에서 등록합니다.

> 📄 **가장 쉬운 배포(VM + Docker + 자동 HTTPS) 단계별 가이드**: [`deploy/DEPLOY.md`](deploy/DEPLOY.md)
>
> 공모전 규정상 제출물은 **카카오 클라우드 MCP 서버 엔드포인트**여야 참가 자격이 인정됩니다.

---

## 5. PlayMCP 등록 절차

1. [playmcp.kakao.com](https://playmcp.kakao.com/) 에 카카오 계정으로 로그인
2. 개발자 콘솔 → **새 MCP 서버 등록**
3. 위 4단계에서 만든 **카카오 클라우드 엔드포인트 URL**(`.../mcp`) 입력
4. 제공된 템플릿에 맞춰 서버 정보(이름·설명·도구 목록) 작성
5. Inspector 검증 완료 후 **공개(Public) 전환**
6. 공모전 페이지에서 제출 → 심사 대기

---

## 알려진 한계

- `romanize`: 자모 매핑 + 연음 + **자음동화(유음화·비음화) 주요 규칙**을 반영합니다(`종로`→`jongno`, `신라`→`silla`, `협력`→`hyeomnyeok`). 다만 **겹받침 연음·구개음화·ㅎ축약** 등 일부 음운 변동은 단순화되어 있습니다.
- `korean_holidays` / `business_days_between`: **양력 고정 공휴일**은 모든 연도 계산 가능하지만, **음력 기반(설날·추석·부처님오신날) 및 대체공휴일**은 `korea_tools.py`의 `_LUNAR_TABLE`에 등록된 연도(현재 2025·2026)만 정확합니다. 다른 연도는 결과의 `note` 필드로 안내되며, 표를 갱신하면 확장됩니다.

---

## 프로젝트 구조

```
korea-life-mcp/
├── server.py          # FastMCP 서버 (도구 11종 노출, stdio/http 전환)
├── korea_tools.py     # 순수 로직 함수 (테스트 가능, 네트워크 미사용)
├── test_tools.py      # 자체 검증 스크립트
├── requirements.txt   # 의존성 (mcp)
├── pyproject.toml     # 패키지 메타데이터
├── Dockerfile         # 카카오 클라우드 배포용 컨테이너
└── README.md
```
