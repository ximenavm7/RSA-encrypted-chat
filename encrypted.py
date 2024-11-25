import socket
import threading
import sys
import json

# RSA key generation utility
def generate_rsa_keys():
    # Use small primes for simplicity; replace with larger primes for production.
    p = 61
    q = 53
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17  # Small prime coprime to phi
    d = pow(e, -1, phi)
    return e, d, n, p, q

# RSA Encryption
def encriptacion_RSA(plain, e, n):
    try:
        r = []
        for p in plain:
            result = pow(p, e, n)
            r.append(result)
        return r
    except Exception as error:
        raise ValueError(f"Encryption error: {error}")

# RSA Decryption
def decriptacion_RSA(cipher, d, n):
    try:
        r = []
        for c in cipher:
            result = pow(c, d, n)
            r.append(result)
        return r
    except Exception as error:
        raise ValueError(f"Decryption error: {error}")

# RSA-CRT Decryption
def decriptacion_RSA_CRT(cipher, d, p, q):
    try:
        dp = d % (p - 1)
        dq = d % (q - 1)
        q_inv = pow(q, -1, p)
        r = []

        for c in cipher:
            m1 = pow(c % p, dp, p)
            m2 = pow(c % q, dq, q)
            h = (q_inv * (m1 - m2)) % p
            result = m2 + h * q
            r.append(result)
        return r
    except Exception as error:
        raise ValueError(f"CRT Decryption error: {error}")

# Initialize RSA Keys
e, d, n, p, q = generate_rsa_keys()

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

choice = input("Host (1) or connect (2)?: ")

# Sending Messages
def sending_messages(c):
    try:
        while True:
            message = input("")
            if message.lower() == "exit":
                c.send("DISCONNECT".encode())
                print("You disconnected.")
                c.close()
                break

            # Encrypt the message
            message_ints = [ord(char) for char in message]
            encrypted_message = encriptacion_RSA(message_ints, e, n)
            serialized_message = json.dumps(encrypted_message)
            c.send(serialized_message.encode())
            print("You (encrypted): " + serialized_message)
    except Exception as error:
        print(f"Error sending message: {error}")
        c.close()

# Receiving Messages
def receiving_messages(c):
    try:
        while True:
            data = c.recv(4096).decode()
            if not data:
                break
            if data == "DISCONNECT":
                print("Partner has disconnected.")
                c.close()
                break

            # Decrypt the received message
            encrypted_message = json.loads(data)
            decrypted_rsa = decriptacion_RSA(encrypted_message, d, n)
            decrypted_crt = decriptacion_RSA_CRT(encrypted_message, d, p, q)

            plaintext_rsa = ''.join(chr(x) for x in decrypted_rsa)
            plaintext_crt = ''.join(chr(x) for x in decrypted_crt)

            print("Partner (RSA): " + plaintext_rsa)
            print("Partner (RSA-CRT): " + plaintext_crt)
    except Exception as error:
        print(f"Error receiving message: {error}")
        c.close()

try:
    if choice == "1":
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((SERVER_IP, SERVER_PORT))
        server.listen(1)
        print(f"Server listening on {SERVER_IP}:{SERVER_PORT}...")

        client, addr = server.accept()
        print(f"Connection established with {addr}")
        print("Type 'exit' to leave the conversation.")

        threading.Thread(target=sending_messages, args=(client,)).start()
        threading.Thread(target=receiving_messages, args=(client,)).start()

    elif choice == "2":
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((SERVER_IP, SERVER_PORT))
            print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
            print("Type 'exit' to leave the conversation.")

            threading.Thread(target=sending_messages, args=(client,)).start()
            threading.Thread(target=receiving_messages, args=(client,)).start()
        except Exception as error:
            print(f"Failed to connect to server: {error}")
            sys.exit()

    else:
        print("Invalid choice.")
        sys.exit()

except KeyboardInterrupt:
    print("\nExiting chat.")
    sys.exit()