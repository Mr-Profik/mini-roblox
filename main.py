import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# База данных "плейсов" (в памяти для бесплатного хостинга)
places = {
    1: {"name": "Начальный мир", "creator": "Admin", "blocks": [{"x": 100, "y": 300, "w": 200, "h": 20}]}
}

# Шаблон визуальной части (Frontend)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini-Roblox Engine</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        canvas { border: 2px solid #333; background: #87CEEB; display: block; margin: 0 auto; width: 100%; max-width: 600px; }
        body { font-family: sans-serif; text-align: center; background: #222; color: #fff; }
        .ui { margin: 20px; }
        button { padding: 10px 20px; font-weight: bold; background: #ff4757; color: white; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>PY-BLOX: PLACE #{{id}}</h1>
    <p>Создатель: {{creator}} | Название: {{name}}</p>
    <canvas id="gameCanvas" width="800" height="400"></canvas>
    <div class="ui">
        <button onclick="addBlock()">ПОСТРОИТЬ БЛОК (BUILD)</button>
        <p>Стрелки или WASD для движения</p>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        let player = { x: 50, y: 50, w: 30, h: 30, dy: 0, speed: 5 };
        let blocks = {{blocks|tojson}};
        let keys = {};

        window.onkeydown = (e) => keys[e.code] = true;
        window.onkeyup = (e) => keys[e.code] = false;

        function addBlock() {
            const newBlock = { x: player.x, y: player.y + 40, w: 50, h: 20 };
            blocks.push(newBlock);
            // Тут можно отправить fetch запрос на сервер, чтобы сохранить!
        }

        function update() {
            // Гравитация
            player.dy += 0.5;
            player.y += player.dy;

            // Управление
            if (keys['KeyA'] || keys['ArrowLeft']) player.x -= player.speed;
            if (keys['KeyD'] || keys['ArrowRight']) player.x += player.speed;
            if ((keys['KeyW'] || keys['Space'] || keys['ArrowUp']) && player.onGround) {
                player.dy = -10;
                player.onGround = false;
            }

            // Коллизии с блоками
            player.onGround = false;
            blocks.forEach(b => {
                if (player.x < b.x + b.w && player.x + player.w > b.x &&
                    player.y + player.h > b.y && player.y < b.y + b.h) {
                    player.y = b.y - player.h;
                    player.dy = 0;
                    player.onGround = true;
                }
            });

            // Пол
            if (player.y > canvas.height) { player.y = 50; player.dy = 0; }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            // Игрок
            ctx.fillStyle = '#ff4757';
            ctx.fillRect(player.x, player.y, player.w, player.h);
            // Блоки
            ctx.fillStyle = '#2ed573';
            blocks.forEach(b => ctx.fillRect(b.x, b.y, b.w, b.h));
            requestAnimationFrame(() => { update(); draw(); });
        }
        draw();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    html = "<h1>Список плейсов</h1><ul>"
    for pid, data in places.items():
        html += f'<li><a href="/join/{pid}" style="color:white">{data["name"]} (ID: {pid})</a></li>'
    html += "</ul>"
    return html

@app.get("/join/{pid}", response_class=HTMLResponse)
async def join(pid: int):
    if pid in places:
        p = places[pid]
        content = HTML_TEMPLATE.replace("{{id}}", str(pid))
        content = content.replace("{{creator}}", p["creator"])
        content = content.replace("{{name}}", p["name"])
        # Простая замена для JSON (в идеале использовать Jinja2)
        import json
        content = content.replace("{{blocks|tojson}}", json.dumps(p["blocks"]))
        return content
    return "Плейс не найден"

if __name__ == "__main__":
    # Порт для Render.com
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
