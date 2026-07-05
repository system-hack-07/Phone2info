from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
import httpx, re
from bs4 import BeautifulSoup

app = FastAPI(title="TeleSpotter PY")

# 🔥 Pro Dark Phone Theme HTML
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>☎️ TeleSpotter PY</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
        body {
            font-family: 'Press Start 2P', cursive;
            background: linear-gradient(135deg, #0a0a0a, #1a0033);
            color: #00ff41;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .phone-container {
            background: #111;
            border: 8px solid #00ff41;
            border-radius: 30px;
            padding: 25px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 0 40px rgba(0, 255, 65, 0.6);
            position: relative;
        }
        h1 {
            text-align: center;
            font-size: 22px;
            margin: 10px 0 20px;
            text-shadow: 0 0 10px #00ff41;
        }
        input {
            width: 100%;
            padding: 18px;
            font-size: 18px;
            background: #000;
            color: #00ff41;
            border: 3px solid #00ff41;
            border-radius: 10px;
            margin-bottom: 15px;
            text-align: center;
        }
        button {
            width: 100%;
            padding: 18px;
            font-size: 18px;
            background: #00ff41;
            color: #000;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover {
            background: #ff00ff;
            color: white;
            transform: scale(1.05);
        }
        .result {
            margin-top: 25px;
            background: #000;
            padding: 15px;
            border-radius: 10px;
            border: 2px solid #00ff41;
            max-height: 500px;
            overflow-y: auto;
        }
        .emoji { font-size: 28px; animation: pop 0.6s; }
        @keyframes pop { 0% { transform: scale(0.2); } 100% { transform: scale(1); } }
        .card {
            background: #1a001a;
            margin: 10px 0;
            padding: 12px;
            border-left: 5px solid #ff00ff;
        }
    </style>
</head>
<body>
    <div class="phone-container">
        <h1>📱 TELESPOTTER PY 🔥</h1>
        <form action="/search" method="post">
            <input name="phone" placeholder="555-555-1212" required>
            <button type="submit">🚀 SCAN NUMBER</button>
        </form>
        <div id="results"></div>
    </div>

    <script>
        document.querySelector('form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const phone = document.querySelector('input').value;
            const res = await fetch('/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `phone=${encodeURIComponent(phone)}`
            });
            const data = await res.json();
            
            let html = `<div class="result"><h2>🔍 RESULTS FOR ${data.phone} 🎯</h2>`;
            data.results.forEach(r => {
                html += `<div class="card">
                    <span class="emoji">📞</span> <strong>${r.title}</strong><br>
                    <small>${r.snippet}</small><br>
                    <small>Source: ${r.source}</small>
                </div>`;
            });
            html += `<h3>📛 Top Names: ${data.analysis.top_names.join(', ') || 'None'}</h3>`;
            html += `<h3>📍 Locations: ${data.analysis.locations.join(', ') || 'None'}</h3></div>`;
            document.getElementById('results').innerHTML = html;
        });
    </script>
</body>
</html>
"""

async def quick_search(phone: str):
    results = []
    formats = [phone, re.sub(r'(\d{3})(\d{3})(\d{4})', r'\1-\2-\3', phone)]
    
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        for fmt in formats:
            for base_url in ["https://www.google.com/search?q=", "https://www.bing.com/search?q="]:
                try:
                    r = await client.get(base_url + fmt, headers={"User-Agent": "Mozilla/5.0"})
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for item in soup.select('.g, .b_algo, .result')[:10]:
                        title = item.find(['h3', 'a'])
                        snippet = item.find(['span', 'p', '.b_caption'])
                        if title and snippet:
                            results.append({
                                "title": str(title.get_text())[:120],
                                "snippet": str(snippet.get_text())[:250],
                                "source": "Google" if "google" in base_url else "Bing"
                            })
                except:
                    continue
    
    analysis = {
        "top_names": list(set(re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', ' '.join(r['snippet'] for r in results))))[:5],
        "locations": list(set(re.findall(r'\b[A-Z][a-z]+(?:,\s*[A-Z]{2})?\b', ' '.join(r['snippet'] for r in results))))[:5]
    }
    
    return {"phone": phone, "results": results[:25], "analysis": analysis}

@app.get("/", response_class=HTMLResponse)
async def home():
    return INDEX_HTML

@app.post("/search")
async def search(phone: str = Form(...)):
    data = await quick_search(phone)
    return JSONResponse(data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
