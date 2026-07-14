# korea-life-mcp — 카카오 클라우드 등 컨테이너 환경 배포용 이미지
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY korea_tools.py server.py ./

# 원격 MCP 서버(Streamable HTTP)로 구동 → http://0.0.0.0:8000/mcp
ENV MCP_TRANSPORT=http
ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000

CMD ["python", "server.py"]
