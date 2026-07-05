from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>TeleSpotter PY</title>
<style>
body { background:#000; color:#0f0; font-family:monospace; padding:40px; text-align:center; }
.phone { border:10px solid #0f0; border-radius:30px; padding:40px; max-width:420px; margin:auto; background:#111; }
input, button { padding:18px; font-size:18px; margin:15px; width:85%; }
button { background:#0f0; color:#000; border:none; cursor:pointer; }
button:hover { background:#ff00ff; color:white; }
</style>
</head>
<body>
<div class="phone">
<h1>📱 TELESPOTTER PY</h1>
<form method="post" action="/search">
<input name="phone" placeholder="5555551212" required><br>
<button type="submit">🚀 SCAN NUMBER</button>
</form>
<div id="results"></div>
</div>
<script>
document.querySelector('form').onsubmit = async function(e) {
  e.preventDefault();
  const formData = new FormData(this);
  const response = await fetch('/search', { method: 'POST', body: formData });
  const data = await response.json();
  let html = '<h2>Results for ' + data.phone + '</h2>';
  data.results.forEach(r => {
    html += '<p>🔍 ' + r.title + '</p>';
  });
  document.getElementById('results').innerHTML = html;
};
</script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return HTML

@app.route("/search", methods=["POST"])
def search():
    phone = request.form.get("phone", "").strip()
    results = []
    try:
        for q in [phone, re.sub(r'\D', '', phone)]:
            resp = requests.get(
                f"https://www.google.com/search?q={q}",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                timeout=12
            )
            matches = re.findall(r'<h3[^>]*>([^<]+)</h3>', resp.text, re.I)
            for m in matches[:10]:
                results.append({"title": m.strip()})
    except Exception as e:
        results.append({"title": "Error: " + str(e)[:50]})
    
    return jsonify({"phone": phone, "results": results[:15]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
