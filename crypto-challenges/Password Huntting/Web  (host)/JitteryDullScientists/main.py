from flask import Flask, request, render_template_string, send_file
import hashlib
import os

app = Flask(__name__)

# Default targets: auto-generated into hashes.txt if absent
DEFAULT_HASHES = {
    'Fateh':       'd4d9704b764bc09fc8247a70221df7d3',  # MD5(LapirozIsGoat)
    'Abderahim':   'a862b67ab77396ffc37550acbf9165c0',  # MD5(FatehIsGoat)
    'Tarek':       'a02930df0f5d9bbe1be12b7677f135e3'   # MD5(132558542)
}
HASH_FILE = 'hashes.txt'


def load_hashes():
    # Create hashes.txt with defaults if not exists
    if not os.path.isfile(HASH_FILE):
        with open(HASH_FILE, 'w') as f:
            for user, h in DEFAULT_HASHES.items():
                f.write(f"{user}:{h}\n")
        print(f"{HASH_FILE} created with default targets.")

    # Parse user:hash entries
    entries = {}
    with open(HASH_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or ':' not in line:
                continue
            user, hsh = line.split(':', 1)
            entries[user.strip()] = hsh.strip()
    return entries


users = load_hashes()

# Cyber‑themed HTML with animations & cryptography visuals
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>🔐 Rainbow‑Table Hunt</title>
  <style>
    /* Neon grid background */
    body {
      margin:0;
      height:100vh;
      background: #000;
      background-image: radial-gradient(circle at center, rgba(57,255,20,0.1), transparent 70%),
                         linear-gradient(#222 1px, transparent 1px),
                         linear-gradient(90deg, #222 1px, transparent 1px);
      background-size: 50px 50px, 50px 50px;
      color: #39ff14;
      font-family: 'Courier New', monospace;
      overflow-x:hidden;
    }
    /* Flicker and glitch effect on header */
    h1 {
      position:relative;
      font-size:3rem;
      text-transform:uppercase;
      letter-spacing:2px;
      animation: flicker 3s infinite;
      text-align:center;
      margin:1rem 0;
    }
    @keyframes flicker {
      0%,19%,21%,23%,25%,54%,56%,100% {opacity:1;}
      20%,24%,55% {opacity:0.3;}
    }
    .container {
      width:90%; max-width:900px;
      margin: auto;
      backdrop-filter: blur(4px) brightness(0.2);
      padding:20px;
      border:1px solid #39ff14;
      box-shadow:0 0 20px #39ff14;
      animation: fadeIn 1.5s ease-in-out;
    }
    @keyframes fadeIn { from {opacity:0;} to {opacity:1;} }
    .hash-list, .story, .hashing {
      margin-bottom:1.5rem;
    }
    .hash-list {padding:1rem; border:1px dashed #39ff14;}
    .hash-item { display:flex; justify-content:space-between; padding:0.3rem 0;
      border-bottom:1px solid rgba(57,255,20,0.2);
    }
    input, button {
      font-family:inherit;
      font-size:1rem;
      padding:0.5rem;
      margin-top:0.5rem;
    }
    input {
      width:100%;
      background:#111;
      border:1px solid #39ff14;
      color:#fff;
      transition:0.3s;
    }
    input:focus { outline:none; border-color:#00ffee; }
    button {
      background:#39ff14;
      border:none;
      color:#000;
      cursor:pointer;
      width:100%;
      margin-top:1rem;
      animation: glow 2s infinite;
    }
    @keyframes glow {
      0%,100% { box-shadow:0 0 5px #39ff14; }
      50% { box-shadow:0 0 20px #39ff14; }
    }
    .msg {
      margin-top:1rem;
      padding:1rem;
      background:rgba(0,0,0,0.7);
      border-left:4px solid #39ff14;
      animation: shake 0.4s;
    }
    @keyframes shake {
      0%,100%{transform:translateX(0);} 20%,80%{transform:translateX(-5px);} 40%,60%{transform:translateX(5px);} 50%{transform:rotate(1deg);} 30%,70%{transform:rotate(-1deg);} }
    a { color:#39ff14; text-decoration:none; }
    a:hover { text-decoration:underline; }
  </style>
</head>
<body>
  <h1>🔐 Rainbow‑Table Hunt 🔐</h1>
  <div class="container">
    <div class="story">
      <p>In the techy buzz of <strong>B3</strong>, <em>Moussa</em> cornered Dr. Berghout with a classic cryptographer’s challenge: “Talk to me about hashing.” What followed was a rapid-fire breakdown of the digital dark arts:</p>
      <ul>
        <li>Hashing = one-way cryptographic street with no U-turns</li>
        <li>MD5? Blazing fast, yes—but without salt, it's like a lock with the key taped beside it</li>
        <li>Rainbow tables? Think hacker cheat-sheets—ready-made hash→password blueprints</li>
      </ul>
      <p>By the end, Moussa was grinning. Knowledge unlocked. Security vibes activated.</p>
    </div>

    <div class="hash-list">
      <p><strong>Target Hashes:</strong></p>
      {% for user, hsh in users.items() %}
        <div class="hash-item"><span>{{ user }}</span><code>{{ hsh }}</code></div>
      {% endfor %}
    </div>
    <p><a href="/wordlist">Download <code>moussa.txt</code> (500 passwords)</a></p>

    <form method="post">
      {% for user in users.keys() %}
        <label>{{ user }}:</label>
        <input type="text" name="{{ user }}" placeholder="Enter plaintext" required />
      {% endfor %}
      <button type="submit">Decrypt & Reveal Flag</button>
    </form>
    {% if msg %}<div class="msg">{{ msg }}</div>{% endif %}
  </div>
</body>
</html>
'''

@app.route('/', methods=['GET','POST'])
def index():
    msg = ''
    if request.method == 'POST':
        for user, hsh in users.items():
            val = request.form.get(user,'').strip()
            if hashlib.md5(val.encode()).hexdigest() != hsh:
                msg = f'❌ Incorrect for {user}. Try again.'
                break
        else:
            msg = '✅ Flag: CIC{BerghoutYasserIsTheGoat}'
    return render_template_string(HTML, users=users, msg=msg)

@app.route('/wordlist')
def wordlist():
    return send_file(os.path.join(os.getcwd(), 'moussa.txt'), as_attachment=True)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
