from flask import Flask, request, session, redirect, url_for, render_template_string
from Crypto.Util.number import getPrime, inverse, bytes_to_long, long_to_bytes

app = Flask(__name__)
app.secret_key = "ReplaceWithASecureSecretKey"  # Replace with a real secret!

zedk_songs = ["Sa7en", "Noises", "FiLaman", "Window", "Okey"]

def generate_rsa_challenge(song):
    m = bytes_to_long(song.encode())
    # Ensure n > m by generating sufficiently large primes (32-bit in this example)
    while True:
        p = getPrime(32)
        q = getPrime(32)
        n = p * q
        if m < n:
            break
    phi = (p - 1) * (q - 1)
    e = 65537
    while phi % e == 0:
        e = getPrime(32)
    c = pow(m, e, n)
    return {"song": song, "c": c, "e": e, "n": n, "phi": phi}

@app.route('/')
def index():
    # Initialize the session challenge data
    session.clear()
    session['index'] = 0
    session['success'] = 0
    session['challenges'] = [generate_rsa_challenge(song) for song in zedk_songs]
    return redirect(url_for('challenge'))

@app.route('/challenge', methods=['GET', 'POST'])
def challenge():
    idx = session.get('index', 0)
    challenges = session.get('challenges', [])

    if idx >= len(challenges):
        # All challenges solved, display flag if successes equal total challenges
        flag = "CIC{Fina_Tarkiba_Unique}" if session.get('success', 0) == len(challenges) else \
               "Challenge not solved. ZEDK says: Try again, operator!"
        return render_template_string('''
<!doctype html>
<html>
  <head>
    <title>Challenge Completed</title>
    <style>
      body { background-color: #000; color: #00FF00; font-family: monospace; }
      .container { width: 80%; margin: 50px auto; text-align: center; }
      a { color: #00FF00; text-decoration: none; border: 1px solid #00FF00; padding: 5px 10px; }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>[MISSION COMPLETED]</h1>
      <p>{{ flag }}</p>
      <a href="{{ url_for('index') }}">Restart Challenge</a>
    </div>
  </body>
</html>
''', flag=flag)

    current = challenges[idx]

    if request.method == 'POST':
        answer = request.form.get('answer', '').strip()
        try:
            # Decrypt the RSA ciphertext
            d = inverse(current['e'], current['phi'])
            decrypted = pow(current['c'], d, current['n'])
            decoded = long_to_bytes(decrypted).decode()

            # Compare the user's answer with the decrypted result.
            if answer == decoded:
                session['success'] = session.get('success', 0) + 1
                session['index'] = idx + 1
                return redirect(url_for('challenge'))
            else:
                # Wrong answer: reset the session and start over.
                session.clear()
                return redirect(url_for('index'))
        except Exception:
            # On any error, reset the session.
            session.clear()
            return redirect(url_for('index'))

    total = len(challenges)
    progress = int((idx / total) * 100)

    return render_template_string('''
<!doctype html>
<html>
  <head>
    <title>SecBoot Challenge</title>
    <style>
      body { background-color: #000; color: #00FF00; font-family: "Courier New", monospace; margin:0; }
      .container { width: 80%; margin: 20px auto; padding: 20px; }
      .banner { text-align: center; animation: blink 2s infinite; }
      pre { font-size: 16px; }
      input { background: #000; color: #00FF00; border: 1px solid #00FF00; padding: 5px; font-family: monospace; }
      button { background: #000; color: #00FF00; border: 1px solid #00FF00; padding: 5px 10px; cursor: pointer; }
      .progress-container { width: 100%; background: #333; border: 1px solid #00FF00; height: 20px; margin-bottom: 20px; }
      .progress-bar { height: 100%; background: #00FF00; width: {{ progress }}%; transition: width 0.5s; }
      @keyframes blink { 50% {opacity: 0.5;} }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="banner">
         <pre>
   _____              _                      _   
  / ____|            | |                    | |  
 | (___   ___  _ __  | |__   _____   ____   | |_ 
  \___ \ / _ \|  __\ | '_ \ /  _  \ /  __ \ | __|
  ____) | (__ | |___ | |_) |  (_) | | (__) || |_ 
 |_____/ \___/|_____||_.__/ \_____| \______||\__|
         </pre>
         <p>SecBoot RSA Challenge: ZEDK</p>
         <p>[Challenge {{ idx + 1 }} of {{ total }}]</p>
      </div>

      <div class="progress-container">
        <div class="progress-bar"></div>
      </div>

      <div class="challenge">
        <p>[SECURITY NOTICE] Encrypted payload: {{ current.c }}</p>
        <p>[SECURITY NOTICE] Public Exponent (e): {{ current.e }}</p>
        <p>[SECURITY NOTICE] Modulus (n): {{ current.n }}</p>
      </div>

      <form method="post">
        <p>[ENTER DECRYPTED MESSAGE] > 
           <input type="text" name="answer" autofocus>
        </p>
        <button type="submit">Submit</button>
      </form>
    </div>
  </body>
</html>
''', current=current, idx=idx, total=total, progress=progress)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

