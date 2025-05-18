import string

LOWERCASE_OFFSET = ord("a")
ALPHABET = string.ascii_lowercase[:16] 
def b16_encode(s: str) -> str:
   
    enc = []
    for c in s:
        byte = ord(c)
               if not 0 <= byte < 256:
            raise ValueError(f"Character {c!r} out of byte range")
        bits = format(byte, "08b")
        high, low = bits[:4], bits[4:]
        enc.append(ALPHABET[int(high, 2)])
        enc.append(ALPHABET[int(low, 2)])
    return "".join(enc)

def shift(c: str, k: str) -> str:
      i = ALPHABET.index(c)
    j = ALPHABET.index(k)
    return ALPHABET[(i + j) % len(ALPHABET)]

def encrypt(plain: str, key: str) -> str:
    
    b16_plain = b16_encode(plain)
    b16_key   = b16_encode(key)
    out = []
    key_len = len(b16_key)
    for idx, pc in enumerate(b16_plain):
        kc = b16_key[idx % key_len]
        out.append(shift(pc, kc))
    return "".join(out)

if __name__ == "__main__":
    plaintext  = " "
    key        = " "
    ciphertext = encrypt(plaintext, key)
    print("Ciphertext:", ciphertext)

