from flask import Flask, render_template_string, request, session, redirect
import hashlib
import secrets
import string

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Utility functions

def rand_str(length=8):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def count_leading_zeros(hex_str):
    count = 0
    for c in hex_str:
        if c == '0': count += 1
        else: break
    return count

# Fancy HTML template with animations, starfield, progress dots, and YouTube music
TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Beautiful Life Challenge</title>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
  <style>
    :root { --bg-dark: #101018; --card-dark: #1F1F2B; --accent: #00FFE7; --text: #EAEAEA; --fade: 0.6s; }
    * { box-sizing: border-box; }
    body {
      margin:0; height:100vh; display:flex; align-items:center; justify-content:center;
      font-family:'Montserrat',sans-serif; color:var(--text); overflow:hidden;
      background: radial-gradient(circle at center, #1a1a1a,#000); animation:hue 60s infinite;
    }
    @keyframes hue {0%{filter:hue-rotate(0deg);}50%{filter:hue-rotate(30deg);}100%{filter:hue-rotate(0deg);}}
    #bg-canvas{position:fixed;inset:0;z-index:-1;}
    #bg-music{position:absolute;top:-9999px;left:-9999px;}
    .wrapper{width:480px;text-align:center;}
    .progress{display:flex;justify-content:center;gap:12px;margin-bottom:20px;}
    .dot{width:14px;height:14px;border-radius:50%;background:#555;transition:0.3s;}
    .dot.active{background:var(--accent);box-shadow:0 0 8px var(--accent);}
    .card{background:var(--card-dark);padding:30px;border-radius:16px;
      box-shadow:0 8px 24px rgba(0,255,231,0.2);
      opacity:0;transform:translateY(30px);animation:slide var(--fade) forwards;
    }
    @keyframes slide{to{opacity:1;transform:translateY(0);}}
    h3{margin:0 0 15px;font-weight:700;}
    p{margin:8px 0;}
    input,button{width:100%;padding:12px;margin-top:12px;border:none;border-radius:8px;font-size:1rem;}
    input{background:#2A2A38;color:var(--text);}
    button{background:var(--accent);color:#000;font-weight:700;cursor:pointer;transition:transform 0.2s;}
    button:hover{transform:scale(1.04);}
    .message{color:#F55;margin-top:10px;font-style:italic;}
    .flag-image img{display:block;margin:24px auto 0;max-width:100%;border-radius:12px;
      box-shadow:0 0 20px var(--accent);
    }
  </style>
</head>
<body>
  <iframe id="bg-music" src="https://www.youtube.com/embed/75P0QGi3RO0?autoplay=1&loop=1&playlist=75P0QGi3RO0&controls=0&mute=0" frameborder="0" allow="autoplay; encrypted-media"></iframe>
  <canvas id="bg-canvas"></canvas>
  <div class="wrapper">
    <div class="progress">
      <div class="dot {% if step==1 %}active{% endif %}"></div>
      <div class="dot {% if step==2 %}active{% endif %}"></div>
      <div class="dot {% if step==3 %}active{% endif %}"></div>
      <div class="dot {% if step==4 %}active{% endif %}"></div>
    </div>
    <div class="card">
      {% if step==1 %}
        <h3>Step 1</h3>
        <p><strong>PREFIX:</strong> {{ prefix }}</p>
        <p><strong>DIFFICULTY:</strong> {{ difficulty }}</p>
        <form method="post"><input name="suffix" placeholder="Suffix" required/><button>Submit</button></form>
        {% if message %}<div class="message">{{ message }}</div>{% endif %}
      {% elif step==2 %}
        <h3>Step 2</h3>
        <p><strong>PREFIX:</strong> {{ prefix2 }}</p>
        <p><strong>SUFFIX:</strong> {{ suffix2 }}</p>
        <p>Enter difficulty:</p>
        <form method="post"><input name="ans" placeholder="Difficulty" required/><button>Submit</button></form>
        {% if message %}<div class="message">{{ message }}</div>{% endif %}
      {% elif step==3 %}
        <h3>Step 3</h3>
        <p><strong>SUFFIX:</strong> {{ suffix3 }}</p>
        <p><strong>DIFFICULTY:</strong> {{ difficulty3 }}</p>
        <p>Enter prefix:</p>
        <form method="post"><input name="pre" placeholder="Prefix" required/><button>Submit</button></form>
        {% if message %}<div class="message">{{ message }}</div>{% endif %}
      {% else %}
        <h3>🎉 You Passed All Steps!</h3>
        <p>Flag: <strong>CIC{You_had_a_beautiful_skill}</strong></p>
        <div class="flag-image"><img src="https://i.ibb.co/G3crdXJG/5c7d91f4847912c0d73f3fb9495a2379.jpg" alt="Celebration"/></div>
      {% endif %}
    </div>
  </div>
  <script>
    const canvas=document.getElementById('bg-canvas'),ctx=canvas.getContext('2d');let stars=[];
    function init(){canvas.width=innerWidth;canvas.height=innerHeight;stars=[];for(let i=0;i<220;i++)stars.push({x:Math.random()*canvas.width,y:Math.random()*canvas.height,r:Math.random()*1.5+0.2,d:Math.random()*200});}
    let angle=0;function update(){angle+=0.01;stars.forEach(s=>{s.y+=Math.cos(angle+s.d)+0.6;s.x+=Math.sin(angle)*0.4;if(s.x>canvas.width)s.x=0;if(s.x<0)s.x=canvas.width;if(s.y>canvas.height)s.y=0;});}
    function draw(){ctx.clearRect(0,0,canvas.width,canvas.height);ctx.fillStyle='rgba(255,255,255,0.7)';stars.forEach(s=>{ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,2*Math.PI);ctx.fill();});update();requestAnimationFrame(draw);}
    window.addEventListener('load',()=>{init();draw();});window.addEventListener('resize',init);
  </script>
</body>
</html>
'''

@app.route('/', methods=['GET','POST'])
def index():
    # Initialize on GET or missing step
    if 'step' not in session or request.method=='GET':
        session.clear()
        session['step']=1
        session['prefix']=rand_str(8)
        session['difficulty']=secrets.choice(range(3,6))
        return render_template_string(TEMPLATE, step=1, prefix=session['prefix'], difficulty=session['difficulty'], message=None)

    step=session['step']
    # Step 1
    if step==1:
        suf=request.form.get('suffix','')
        h=hashlib.sha256((session['prefix']+suf).encode()).hexdigest()
        if count_leading_zeros(h)>=session['difficulty']:
            session['step']=2
            session['prefix2']=rand_str(6)
            session['suffix2']=rand_str(6)
            h2=hashlib.sha256((session['prefix2']+session['suffix2']).encode()).hexdigest()
            session['difficulty2']=count_leading_zeros(h2)
            return render_template_string(TEMPLATE, step=2, prefix2=session['prefix2'], suffix2=session['suffix2'], message=None)
        return render_template_string(TEMPLATE, step=1, prefix=session['prefix'], difficulty=session['difficulty'], message='Incorrect PoW')
    # Step 2
    if step==2:
        ans=request.form.get('ans','')
        if ans.isdigit() and int(ans)==session['difficulty2']:
            session['step']=3
            session['suffix3']=rand_str(6)
            session['difficulty3']=secrets.choice(range(2,5))
            return render_template_string(TEMPLATE, step=3, suffix3=session['suffix3'], difficulty3=session['difficulty3'], message=None)
        return render_template_string(TEMPLATE, step=2, prefix2=session['prefix2'], suffix2=session['suffix2'], message='Wrong difficulty')
    # Step 3
    if step==3:
        pre=request.form.get('pre','')
        h3=hashlib.sha256((pre+session['suffix3']).encode()).hexdigest()
        if count_leading_zeros(h3)>=session['difficulty3']:
            session['step']=4
            return render_template_string(TEMPLATE, step=4)
        return render_template_string(TEMPLATE, step=3, suffix3=session['suffix3'], difficulty3=session['difficulty3'], message='Prefix does not meet difficulty')
    # Else restart
    session.clear()
    return redirect('/')

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)
