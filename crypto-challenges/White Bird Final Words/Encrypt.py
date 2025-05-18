def bird_encrypt(text: str) -> str:
    vowels = "aeiouAEIOU"
    result = []
    for ch in text:
        if ch in vowels:
            result.append(ch + '@' + ch)
        else:
            result.append(ch)
    return ''.join(result)


if __name__ == "__main__":
    plaintext = " "
    
    ciphertext = bird_encrypt(plaintext)
    print(ciphertext)
