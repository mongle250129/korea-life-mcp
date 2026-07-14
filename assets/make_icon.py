"""korea-life-mcp 대표 이미지(600x600) 생성 스크립트."""
from PIL import Image, ImageDraw, ImageFont

W = H = 600
BOLD = "C:/Windows/Fonts/malgunbd.ttf"
REG = "C:/Windows/Fonts/malgun.ttf"

# 배경: 세로 그라데이션 (딥 네이비 -> 블루)
top = (14, 32, 78)      # #0E204E
bottom = (37, 74, 168)  # #254AA8
img = Image.new("RGB", (W, H), top)
px = img.load()
for y in range(H):
    t = y / (H - 1)
    r = int(top[0] + (bottom[0] - top[0]) * t)
    g = int(top[1] + (bottom[1] - top[1]) * t)
    b = int(top[2] + (bottom[2] - top[2]) * t)
    for x in range(W):
        px[x, y] = (r, g, b)

d = ImageDraw.Draw(img)

# 중앙 흰 원(카드 느낌)
cx, cy, rad = 300, 250, 150
d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(255, 255, 255))

# 큰 '한' 글자 (네이비)
f_han = ImageFont.truetype(BOLD, 210)
tb = d.textbbox((0, 0), "한", font=f_han)
tw, th = tb[2] - tb[0], tb[3] - tb[1]
d.text((cx - tw / 2 - tb[0], cy - th / 2 - tb[1]), "한", font=f_han, fill=(16, 38, 92))

# 태극 색 악센트 바 (원 아래)
bar_w, bar_h, bar_y = 150, 10, cy + rad + 26
d.rounded_rectangle([cx - bar_w, bar_y, cx, bar_y + bar_h], radius=5, fill=(205, 46, 58))   # 빨강
d.rounded_rectangle([cx, bar_y, cx + bar_w, bar_y + bar_h], radius=5, fill=(0, 71, 160))    # 파랑

# 메인 타이틀
f_title = ImageFont.truetype(BOLD, 54)
title = "한국생활 도우미"
tb = d.textbbox((0, 0), title, font=f_title)
d.text((cx - (tb[2] - tb[0]) / 2 - tb[0], bar_y + 34), title, font=f_title, fill=(255, 255, 255))

# 서브 타이틀
f_sub = ImageFont.truetype(REG, 26)
sub = "KOREA LIFE · MCP"
tb = d.textbbox((0, 0), sub, font=f_sub)
d.text((cx - (tb[2] - tb[0]) / 2 - tb[0], bar_y + 104), sub, font=f_sub, fill=(180, 200, 240))

out = "C:/Users/usoab/.local/bin/korea-life-mcp/assets/icon-600.png"
img.save(out, "PNG")
print("saved:", out, img.size)
