# 카카오 클라우드 배포 가이드 (VM + Docker — 가장 쉬운 방식)

쿠버네티스 없이 **가상머신 1대에 컨테이너 하나**만 띄우는 방법입니다.
결과물: PlayMCP에 등록할 **공개 엔드포인트 URL** (`.../mcp`).

---

## 0. 사전 준비
- 카카오 클라우드 계정
- (HTTPS용) 도메인 1개 — 없으면 우선 HTTP로 테스트 후 나중에 붙여도 됩니다.

---

## 1. 가상머신(VM) 생성
카카오 클라우드 콘솔 → **Virtual Machine** 인스턴스 생성
- OS: Ubuntu 22.04 LTS
- 사양: 최소(1~2 vCPU / 2GB) 로 충분
- **공인 IP 할당** 체크
- 방화벽(보안 그룹) 인바운드 허용:
  - `22` (SSH)
  - `8000` (HTTP 테스트용)
  - `80`, `443` (HTTPS 운영용)

## 2. VM 접속 & Docker 설치
```bash
ssh ubuntu@<VM_공인IP>

sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER   # 재로그인 후 sudo 없이 docker 사용
# (재접속) exit 후 다시 ssh
```

## 3. 소스 내려받기
```bash
git clone https://github.com/mongle250129/korea-life-mcp.git
cd korea-life-mcp
```

## 4-A. 빠른 확인 (HTTP)
```bash
docker compose -f deploy/docker-compose.yml up -d --build mcp
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}'
```
→ 외부에서 접근 주소: `http://<VM_공인IP>:8000/mcp`

## 4-B. 운영 배포 (HTTPS · 자동 인증서)
1. 도메인 DNS의 **A 레코드**를 VM 공인 IP로 연결 (예: `mcp.mydomain.com` → `1.2.3.4`)
2. 실행:
```bash
MCP_DOMAIN=mcp.mydomain.com docker compose -f deploy/docker-compose.yml --profile tls up -d --build
```
→ 몇 초 뒤 자동으로 Let's Encrypt 인증서 발급. 최종 엔드포인트: `https://mcp.mydomain.com/mcp`

## 5. Inspector로 최종 검증
로컬 PC에서:
```bash
npx @modelcontextprotocol/inspector
```
→ Transport: `Streamable HTTP`, URL: 위에서 만든 `.../mcp` → Connect → 도구 15개 확인

## 6. PlayMCP 등록
1. https://playmcp.kakao.com 카카오 로그인 → 개발자 콘솔 → **새 MCP 서버 등록**
2. **엔드포인트 URL**: `https://<도메인>/mcp` (운영) 입력
3. 이름/설명 입력 후 임시 등록 → 테스트 → **공개 전환** → 심사 요청

---

## 운영 팁
- 로그 확인: `docker compose -f deploy/docker-compose.yml logs -f`
- 업데이트: `git pull && docker compose -f deploy/docker-compose.yml up -d --build`
- 재시작 정책이 `unless-stopped` 라 VM 재부팅 후 자동 기동됩니다.
