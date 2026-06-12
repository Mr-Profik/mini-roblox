import os
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# База данных плейсов (создаем 1 плейс по умолчанию)
places = {
    "1": {
        "name": "Начальный мир",
        "creator": "Admin",
        "blocks": [
            {"x": 0, "y": 350, "w": 800, "h": 50},  # Земля
            {"x": 200, "y": 250, "w": 100, "h": 20}, # Платформа 1
            {"x": 400, "y": 150, "w": 100, "h": 20}  # Платформа 2
        ]
    }
}

# HTML движок игры
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini-Roblox Engine</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; background: #222; color: white; font-family: sans-serif; text-align: center; overflow: hidden; }
        canvas { background: #87CEEB; display: block; margin: 0 auto; border: 3px solid #444; touch-action: none; }
        .controls { position: fixed; bottom: 20px; width: 100%; display: flex; justify-content: center; gap: 20px; }
        .btn { width: 60px; height: 60px; background: rgba(255,255,255,0.3); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; user-select: none; }
    </style>
</head>
<body>
    <h3>Плейс: {{name}}</h3>
    <canvas id="g"></canvas>
    
    <div class="controls">
        <div class="btn" id="btnL">←</div>
        <div class="btn" id="btnJ">UP</div>
        <div class="btn" id="btnR">→</div>
        <div class="btn" id="btnB" style="background: #ff4757">B</div>
    </div>

    <script>
        const canvas = document.getElementById('g');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth > 800 ? 800 : window.innerWidth;
        canvas.height = 400;

        let player = { x: 50, y: 100, w: 30, h: 30, dy: 0, speed: 5, onG: false };
        let blocks = {{blocks}};
        let keys = {};

        // Управление (клавиатура + тач)
        window.onkeydown = (e) => keys[e.code] = true;
        window.onkeyup = (e) => keys[e.code] = false;
        
        const bindBtn = (id, code) => {
            const el = document.getElementById(id);
            el.ontouchstart = (e) => { e.preventDefault(); keys[code] = true; };
            el.ontouchend = (e) => { e.preventDefault(); keys[code] = false; };
        };
        bindBtn('btnL', 'ArrowLeft');
        bindBtn('btnR', 'ArrowRight');
        bindBtn('btnJ', 'Space');
        document.getElementById('btnB').onclick = () => {
            blocks.push({x: player.x, y: player.y, w: 40, h: 10});
        };

        function update() {
            player.dy += 0.6; // Гравитация
            player.y += player.dy;

            if (keys['ArrowLeft'] || keys['KeyA']) player.x -= player.speed;
            if (keys['ArrowRight'] || keys['KeyD']) player.x += player.speed;
            if ((keys['Space'] || keys['ArrowUp'] || keys['KeyW']) && player.onG) {
                player.dy = -12;
                player.onG = false;
            }

            player.onG = false;
            blocks.forEach(b => {
                if (player.x < b.x + b.w && player.x + player.w > b.x &&
                    player.y + player.h > b.y && player.y < b.y + b.h) {
                    if (player.dy > 0) {
                        player.y = b.y - player.h;
                        player.dy = 0;
                        player.onG = true;
                    }
                }
            });

            if (player.y > canvas.height) { player.y = 0; player.dy = 0; }
            if (player.x < 0) player.x = canvas.width;
            if (player.x > canvas.width) player.x = 0;
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ff4757';
            ctx.fillRect(player.x, player.y, player.w, player.h);
            ctx.fillStyle = '#2ed573';
            blocks.forEach(b => ctx.fillRect(b.x, b.y, b.w, b.h));
            update();
            requestAnimationFrame(draw);
        }
        draw();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    html = "<h1>Список плейсов</h1><ul>"
    if not places:
        html += "<li>Плейсов пока нет</li>"
    for pid, data in places.items():
        html += f'<li><a href="/join/{pid}" style="color:cyan; font-size: 24px;">{data["name"]} (войти)</a></li>'
    html += "</ul>"
    return html

@app.get("/join/{pid}", response_class=HTMLResponse)
async def join(pid: str):
    if pid in places:
        p = places[pid]
        page = HTML_TEMPLATE.replace("{{name}}", p["name"])
        page = page.replace("{{blocks}}", json.dumps(p["blocks"]))
        return page
    return "Плейс не найден"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
