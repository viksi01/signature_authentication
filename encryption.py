# Функції для шифрування та дешифрування

#Шифрує текст за допомогою публічного ключа
def encrypt(message):
    e = 5  # Встановлене значення e
    n = 323  # Встановлене значення n
    encrypted_message = []
    for char in message:
        T_i = ord(char)  # Перетворення символу в код Юнікоду
        C_i = pow(T_i, e, n)  # Шифрування
        encrypted_message.append(C_i)
    return encrypted_message

#Дешифрує текст за допомогою приватного ключа.
def decrypt(encrypted_message):
    d = 173  # Встановлене значення d
    n = 323  # Встановлене значення n
    decrypted_message = []
    for C_i in encrypted_message:
        T_i = pow(C_i, d, n)  # Дешифрування
        char = chr(T_i)  # Перетворення коду Юнікоду в символ
        decrypted_message.append(char)
    return ''.join(decrypted_message)
