from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import httpx
import re

app = FastAPI(title="TeleSpotter")

HTML = """
<!DOCTYPE html>
<html>
<head><title>TeleSpotter</title>
<style>body{background:#111;color:#0f0;font-family:monospace;padding:40px;text-align:center;}
input,button{padding:15px;font-size:18px;margin:10px;width:300px;}</style>
</head>
<body>
<h1>📱 TELESPOTTER PY</h1>
<form action="/search" method="post">
<input name="phone" placeholder="5555551212" required><br>
<button type="submit">SCAN</button>
</form>
<div id="r"></div>
<script>
document.querySelector('form').onsubmit=async(e)=>{e.preventDefault();
const f=new FormData(e.target);
const res=await fetch('/search',{method:'POST',body:f});
const d=await res.json();
document.getElementById('r').innerHTML='<h2>Results:</h2>'+JSON.stringify(d.results);
};
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML

@app.post("/search")
async def search(phone: str = Form(...)):
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(f"https://www.google.com/search?q={phone}", headers={"User-Agent":"Mozilla/5.0"})
            text = r.text
            titles = re.findall(r'<h3[^>]*>(.*?)</h3>', text, re.I)[:10]
            return {"phone": phone, "results": [{"title": t} for t in titles], "status": "ok"}
    except Exception as e:
        return {"phone": phone, "results": [], "error": str(e)[:100]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
