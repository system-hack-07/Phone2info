from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import httpx
import re
try:
    from bs4 import BeautifulSoup
except:
    BeautifulSoup = None

app = FastAPI()

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>TeleSpotter</title>
<style>
body{background:#000;color:#0f0;font-family:monospace;padding:20px;}
.phone{border:8px solid #0f0;border-radius:20px;padding:20px;max-width:400px;margin:auto;}
input,button{width:100%;padding:15px;margin:10px 0;font-size:18px;}
button{background:#0f0;color:#000;}
.result{margin-top:20px;}
</style>
</head>
<body>
<div class="phone">
<h1>📱 TELESPOTTER</h1>
<form action="/search" method="post">
<input name="phone" placeholder="5555551212" required>
<button type="submit">SCAN</button>
</form>
<div id="out"></div>
</div>
<script>
document.querySelector('form').onsubmit = async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const r = await fetch('/search', {method:'POST', body:form});
  const data = await r.json();
  let html = '<div class="result"><h2>Results for '+data.phone+'</h2>';
  data.results.forEach(item => {
    html += '<p><strong>'+item.title+'</strong><br>'+item.snippet+'</p>';
  });
  html += '</div>';
  document.getElementById('out').innerHTML = html;
};
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return INDEX_HTML

@app.post("/search")
async def search(phone: str = Form(...)):
    results = []
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            for q in [phone, phone.replace("-","")]:
                for url in ["https://www.google.com/search?q=", "https://www.bing.com/search?q="]:
                    try:
                        r = await client.get(url + q, headers={"User-Agent": "Mozilla/5.0"})
                        if BeautifulSoup:
                            soup = BeautifulSoup(r.text, "html.parser")
                            for item in soup.select(".g, .b_algo")[:6]:
                                t = item.find("h3") or item.find("a")
                                s = item.find("span") or item.find("p")
                                if t and s:
                                    results.append({"title": t.get_text()[:100], "snippet": s.get_text()[:200]})
                    except:
                        pass
    except:
        pass

    return JSONResponse({
        "phone": phone,
        "results": results[:15],
        "analysis": {"names": [], "locations": []}
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
