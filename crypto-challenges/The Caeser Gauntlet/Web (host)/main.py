from flask import Flask, render_template_string, send_from_directory, abort
from werkzeug.utils import secure_filename
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
import os, random

# === Configuration ===
FLAG = os.environ.get('CHAL_FLAG', 'CIC{Hastads_broadcast}')  # Pull flag from env
E = 3
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CHAL_DIR = os.path.join(BASE_DIR, 'static', 'challenge')

# === Flask App Setup ===
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32))

# Enforce HTTPS, secure headers
Talisman(app,
         content_security_policy={
             'default-src': ["'self'"],
             'script-src': ["'self'", 'https://www.youtube.com', 'https://s.ytimg.com'],
             'style-src': ["'self'", "'unsafe-inline'"],
             'frame-src': ['https://www.youtube.com'],
             'media-src': ['https://www.youtube.com']
         },
         force_https=True,
         strict_transport_security=True)
# CSRF protection
csrf = SeaSurf(app)

# === Prime Generation ===
small_primes = [2,3,5,7,11,13,17,19,23,29]

def is_prime(n, k=8):
    if n < 2:
        return False
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False
    # Miller-Rabin
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2; s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

class number:
    @staticmethod
    def getPrime(bits=1024):
        while True:
            p = random.getrandbits(bits - 2) | (1 << (bits - 1)) | 1
            if is_prime(p):
                return p

# === Challenge Generation ===
def generate_challenge():
    os.makedirs(CHAL_DIR, exist_ok=True)
    m_int = int.from_bytes(FLAG.encode(), 'big')
    for i in range(1, 4):
        p, q = number.getPrime(), number.getPrime()
        N = p * q
        c = pow(m_int, E, N)
        # Write public key
        with open(os.path.join(CHAL_DIR, f'N{i}.pub'), 'w') as f:
            f.write(f"{N}\n{E}\n")
        # Write ciphertext
        with open(os.path.join(CHAL_DIR, f'c{i}.bin'), 'wb') as f:
            f.write(c.to_bytes((c.bit_length() + 7) // 8, 'big'))

# Initialize challenge
os.makedirs(CHAL_DIR, exist_ok=True)
if not os.path.exists(os.path.join(CHAL_DIR, 'N1.pub')):
    generate_challenge()

# === Routes ===
@app.route('/')
def index():
    # Embed YouTube audio-only background
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🏯 Cipher Wall Challenge</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;}
    body{font-family:'Segoe UI',sans-serif;background:#0d0d0d;color:#eee;overflow:hidden;}
    .calligraphy{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) rotate(-22deg);pointer-events:none;
      font-size:12vw;color:rgba(255,255,255,0.02);z-index:-4;white-space:nowrap;}
    canvas{position:fixed;top:0;left:0;width:100%;height:100%;}
    #nebula{z-index:-3;opacity:0.6;background:radial-gradient(circle at 25% 30%,#f06c9b,transparent 50%),
      radial-gradient(circle at 75% 70%,#2693ff,transparent 60%);animation:rotate 80s linear infinite;}
    @keyframes rotate{from{transform:rotate(0)}to{transform:rotate(360deg)}}
    .container{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
      background:rgba(20,20,20,0.9);border:2px solid #ff9f1c;border-radius:12px;
      padding:2rem;max-width:680px;width:90%;box-shadow:0 0 25px rgba(255,159,28,0.6);
      backdrop-filter:blur(8px);}
    .title{text-align:center;font-size:2.8rem;color:#ff9f1c;margin-bottom:1rem;}
    .story{font-size:1rem;line-height:1.7;color:#ccc;margin-bottom:1.5rem;}
    .hint{background:#1a1a1a;padding:1rem;border-left:4px solid #ff9f1c;font-size:0.95rem;margin-bottom:1.5rem;}
    .downloads{text-align:center;margin-bottom:1.5rem;}
    .btn{display:inline-block;margin:0.4rem;padding:0.6rem 1.2rem;
      background:linear-gradient(45deg,#ff9f1c,#ff5454);color:#111;font-weight:bold;border:none;
      border-radius:6px;text-decoration:none;transition:0.3s;}
    .btn:hover{transform:translateY(-3px);box-shadow:0 5px 15px rgba(255,84,84,0.5);}
    .resources{font-size:0.9rem;color:#aaa;margin-top:1rem;}
    .resources a{color:#67d7ff;text-decoration:none;}
    .resources a:hover{text-decoration:underline;}
  </style>
</head>
<body>
  <div class="calligraphy">长城·水滴·镜</div>
  <!-- Background Audio -->
  <iframe width="0" height="0"
        src="https://www.youtube.com/embed/OjNpRbNdR7E?autoplay=1&loop=1&playlist=OjNpRbNdR7E&controls=0"
        frameborder="0" allow="autoplay; encrypted-media" hidden></iframe>


  <canvas id="stars"></canvas>
  <div id="nebula"></div>
  <canvas id="matrix"></canvas>
  <div class="container">
    <div class="title">🏯 The Great Cipher Wall</div>
    <div class="story">For millennia, the Great Wall stood sentinel against unseen threats,
      stones guarding secrets. Today, digital ramparts protect our messages.
      Will you breach the Cipher Wall and unveil the hidden relic?</div>
    <div class="hint">Hint: Three gates (moduli) share one secret, with exponent <code>e=3</code>.
      Use CRT to unify the fragments, then extract the cube root to uncover the message.
    </div>
    <div class="downloads">
      {% for i in range(1,4) %}
        <a class="btn" href="/download/N{{i}}.pub">N{{i}}.pub</a>
        <a class="btn" href="/download/c{{i}}.bin">c{{i}}.bin</a>
      {% endfor %}
    </div>
    <div class="resources"><strong>Readings:</strong>
      <a href="https://math.stackexchange.com/questions/4660690" target="_blank">Math.SE Cube Root Euclid</a> |
      <a href="https://crypto.stackexchange.com/questions/52504" target="_blank">Crypto.SE Three Keys</a>
    </div>
  </div>

  <script>
    // Stars background
    const sc = document.getElementById('stars'), sC = sc.getContext('2d');
    function startStars(){ sc.width=innerWidth; sc.height=innerHeight;
      return Array(400).fill().map(_=>({x:Math.random()*sc.width,y:Math.random()*sc.height,z:Math.random()*sc.width})); }
    let stars = startStars();
    function drawStars(){ sC.fillStyle='rgba(0,0,0,0.8)'; sC.fillRect(0,0,sc.width,sc.height);
      stars.forEach(s=>{ s.z-=0.5; if(s.z<1) s.z=sc.width;
        const k = 128/s.z, x = s.x*k + sc.width/2, y = s.y*k + sc.height/2;
        sC.fillStyle='white'; sC.fillRect(x, y, (1-s.z/sc.width)*2, (1-s.z/sc.width)*2);
      }); requestAnimationFrame(drawStars); }
    drawStars(); window.onresize = ()=>{ stars = startStars(); };

    // Matrix rain
    const mc = document.getElementById('matrix'), mC = mc.getContext('2d');
    function startMatrix(){ mc.width=innerWidth; mc.height=innerHeight; return Array(Math.floor(mc.width/20)).fill(1); }
    let rain = startMatrix();
    const chars = '长城守护安全秘密代码解密防御力量智慧力量'.split('');
    function drawMatrix(){ mC.fillStyle='rgba(0,0,0,0.05)'; mC.fillRect(0,0,mc.width,mc.height);
      mC.fillStyle='#0f0'; mC.font='16px monospace';
      rain.forEach((r,i)=>{ const t = chars[Math.floor(Math.random()*chars.length)];
        mC.fillText(t, i*20, r*20);
        rain[i] = (r*20 > mc.height || Math.random()>0.975) ? 0 : r + 1;
      }); requestAnimationFrame(drawMatrix); }
    drawMatrix(); window.onresize = ()=>{ rain = startMatrix(); };
  </script>
</body>
</html>''')
@app.route('/download/<path:filename>')
def download(filename):
    # Secure filename and check existence
    safe_name = secure_filename(filename)
    file_path = os.path.join(CHAL_DIR, safe_name)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(CHAL_DIR, safe_name, as_attachment=True)

if __name__ == '__main__':
    # Production: disable debug, enforce HTTPS
    app.run(host='0.0.0.0', port=5000, debug=False)
