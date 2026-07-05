from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import httpx
import re
from bs4 import BeautifulSoup

app = FastAPI(title="TeleSpotter PY")

# Pro Cool Phone UI
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 TeleSpotter PY</title>
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
        .phone {
            background: #111;
            border: 12px solid #00ff41;
            border-radius: 40px;
            padding: 30px 20px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 0 50px rgba(0, 255, 65, 0.7);
        }
        h1 { text-align: center; margin: 10px 0 25px; text-shadow: 0 0 15px #00ff41; }
        input {
            width: 100%;
            padding: 18px;
            font-size: 17px;
            background: #000;
            color: #00ff41;
            border: 4px solid #00ff41;
            border-radius: 12px;
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
            border-radius: 12px;
            cursor: pointer;
            transition: 0.3s;
        }
        button:hover { background: #ff00ff; color: white; transform: scale(1.05); }
        .result { margin-top: 25px; background: #000; padding: 15px; border-radius: 12px; border: 3px solid #ff00ff; }
        .emoji { font-size: 30px; animation: pop 0.8s ease; }
        @keyframes pop { from {transform: scale(0);} to {transform: scale(1);} }
        .card { background: #1a001a; margin: 12px 0; padding: 12px; border-left: 6px solid #ff00ff; }
    </style>
</head>
<body>
    <div class="phone">
        <h1>📱 TELESPOTTER PY 🔥</h1>
        <form action="/search" method="post">
            <input name="phone" placeholder="5555551212" required>
            <button type="submit">🚀 SCAN PHONE</button>
        </form>
        <div id="results"></div>
    </div>

    <script>
        document.querySelector('form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const res = await fetch('/search', { method: 'POST', body: formData });
            const data = await res.json();
            
            let html = `<div class="result"><h2>🔍 ${data.phone} RESULTS 🎯</h2>`;
            data.results.forEach(r => {
                html += `<div class="card">
                    <span class="emoji">📞</span> <strong>${r.title}</strong><br>
                    <small>${r.snippet}</small><br>
                    <small><em>Source: ${r.source}</em></small>
                </div>`;
            });
            html += `<p><strong>📛 Names:</strong> ${data.analysis.top_names.join(', ') || 'None detected'}</p>`;
            html += `<p><strong>📍 Locations:</strong> ${data.analysis.locations.join(', ') || 'None detected'}</p>`;
            document.getElementById('results').innerHTML = html;
        });
    </script>
</body>
</html>
"""

async def quick_search(phone: str):
    results = []
    formats = [phone.replace("-", ""), re.sub(r'(\d{3})(\d{3})(\d{4})', r'\1-\2-\3', phone)]
    
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for fmt in formats:
            for engine in ["https://www.google.com/search?q=", "https://www.bing.com/search?q="]:
                try:
                    resp = await client.get(engine + fmt, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for item in soup.select(".g, .b_algo, .result")[:10]:
                        title_tag = item.find(["h3", "a"])
                        snippet_tag = item.find(["span", "p", ".b_caption", ".st"])
                        if title_tag and snippet_tag:
                            results.append({
                                "title": title_tag.get_text()[:130],
                                "snippet": snippet_tag.get_text()[:280],
                                "source": "Google" if "google" in engine else "Bing"
                            })
                except:
                    continue

    analysis = {
        "top_names": list(dict.fromkeys(re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', ' '.join([r["snippet"] for r in results]))))[:6],
        "locations": list(dict.fromkeys(re.findall(r'\b[A-Z][a-z]+(?:,\s*[A-Z]{2})?\b', ' '.join([r["snippet"] for r in results]))))[:6]
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
