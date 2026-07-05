from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>TeleSpotter PY</title>
<style>
body{background:#000;color:#0f0;font-family:monospace;padding:30px;text-align:center;}
.phone{border:10px solid #0f0;border-radius:25px;padding:30px;max-width:400px;margin:40px auto;}
input,button{padding:15px;font-size:18px;width:90%;margin:10px;}
button{background:#0f0;color:#000;}
</style>
</head>
<body>
<div class="phone">
<h1>📱 TELESPOTTER</h1>
<form method="post">
<input name="phone" placeholder="5555551212" required>
<button type="submit">SCAN</button>
</form>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return HTML

@app.route("/search", methods=["POST"])
def search():
    phone = request.form.get("phone", "")
    results = []
    try:
        for q in [phone, re.sub(r'\D', '', phone)]:
            r = requests.get(f"https://www.google.com/search?q={q}", 
                           headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', r.text)[:8]
            for t in titles:
                results.append({"title": t.strip()})
    except:
        pass
    return jsonify({"phone": phone, "results": results[:12]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
