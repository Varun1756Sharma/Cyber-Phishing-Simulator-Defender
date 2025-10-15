#!/usr/bin/env python3
from flask import Flask, request
import os, time

app = Flask(__name__)
ART = os.path.join(os.path.dirname(__file__), 'artifacts')
os.makedirs(ART, exist_ok=True)

HTML = """
<h2>Lab Login (Training)</h2>
<form method="post">
  <input name="user" placeholder="username">
  <button>Submit</button>
</form>
"""

@app.route('/phish', methods=['GET','POST'])
def phish():
    if request.method == 'POST':
        with open(os.path.join(ART, 'submissions.csv'), 'a') as f:
            f.write(f"{time.time()},{request.form.get('user')},{request.remote_addr}\n")
        return "<h3>This was a simulated phishing exercise — no real credentials stored.</h3>"
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
