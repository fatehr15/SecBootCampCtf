from flask import Flask, render_template, request
import base64
import codecs
import hashlib

app = Flask(__name__)

# Encryption functions
def encrypt_reversed(text):
    return text[::-1]

def encrypt_base64(text):
    return base64.b64encode(text.encode()).decode()

def encrypt_caesar(text, shift=3):
    result = ""
    for char in text:
        if char.isalpha():
            offset = 65 if char.isupper() else 97
            result += chr((ord(char) - offset + shift) % 26 + offset)
        else:
            result += char
    return result

def encrypt_hex(text):
    return text.encode().hex()

def encrypt_rot13(text):
    return codecs.encode(text, "rot_13")

@app.route("/", methods=["GET", "POST"])
def index():
    flag = None
    message = ""
    submitted = False

    if request.method == "POST":
        submitted = True
        town_input = request.form.get("town", "").strip().lower()
        town_hash = hashlib.sha256(town_input.encode()).hexdigest()

        with open("expected_town_hash.txt", "r") as f:
            expected_hash = f.read().strip()

        if town_hash == expected_hash:
            with open("flag.txt", "r") as f:
                flag = f.read().strip()
        else:
            message = "Nope. Try harder."

    # Story and encrypted keys
    story = (
        "Welcome to the Medical Data Security Lab investigation.\n"
        "In our secure system, we have stored five critical keys whose origins remain mysterious.\n"
        "Each key is shielded by a different layer of encryption. Your mission is to analyze the methods,\n"
        "unlock each key, and piece together the clues hidden within their secure envelopes.\n\n"
        "Remember: sometimes what truly matters is not just the content of the key, but where it comes from.\n"
        "Investigate carefully—the provenance of one identity may reveal more than its mere letters.\n"
        "Hint: The origin of the identity, when considered from an ancient perspective, might hold the answer."
    )

    keys = [
        ("Berghout Yasser", encrypt_reversed),
        ("Soualmi Abdallah", encrypt_base64),
        ("Sahraoui Walid", encrypt_caesar),
        ("Bentrad Sassi", encrypt_hex),
        ("Djeghlouf Asma", encrypt_rot13)
    ]

    encrypted_keys = [method(name) for name, method in keys]

    return render_template("index.html", story=story, encrypted_keys=encrypted_keys, flag=flag, message=message, submitted=submitted)

if __name__ == "__main__":
    app.run(debug=True)
