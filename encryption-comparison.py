import socket
import threading
import sys
import time
import json

# RSA Key Components
p = 61  # Example prime
q = 53  # Example prime
n = p * q
phi = (p - 1) * (q - 1)
e = 17  # Public key exponent (must be coprime to phi and less than phi)
d = 2753  # Private key exponent (modular inverse of e modulo phi)

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

choice = input("Host (1) or connect (2)?: ")

# Standard RSA Encryption
def encriptacion_RSA(plain, e, n):
    r = []
    for p in plain:
        result = pow(p, e, n)
        r.append(result)
    return r

# RSA-CRT Encryption
def encriptacion_RSA_CRT(plain, e, p, q):
    n = p * q
    r = []
    for pt in plain:
        ep = e % (p - 1)
        eq = e % (q - 1)
        q_inv = pow(q, -1, p)

        # Encrypt using CRT-like logic
        c1 = pow(pt % p, ep, p)
        c2 = pow(pt % q, eq, q)
        h = (q_inv * (c1 - c2)) % p
        crt_result = c2 + h * q

        #print(f"CRT encryption for {pt}: {crt_result}")
        r.append(crt_result)
    return r

# Compare RSA and RSA-CRT Encryption Times
def compare_encryption_methods(plain, e, n, p, q):
    # RSA Encryption
    start_time_rsa = time.time()
    rsa_encrypted = encriptacion_RSA(plain, e, n)
    rsa_time = time.time() - start_time_rsa

    # RSA-CRT Encryption
    start_time_crt = time.time()
    crt_encrypted = encriptacion_RSA_CRT(plain, e, p, q)
    crt_time = time.time() - start_time_crt

    return rsa_time, crt_time, rsa_encrypted, crt_encrypted

# RSA Decryption
def decriptacion_RSA(cipher, d, n):
    r = []
    for c in cipher:
        result = pow(c, d, n)
        r.append(result)
    return r

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

            # Convert message to integers for encryption
            message_ints = [ord(char) for char in message]

            # Compare encryption times
            rsa_time, crt_time, rsa_encrypted, crt_encrypted = compare_encryption_methods(message_ints, e, n, p, q)

            # Serialize and send the RSA-encrypted message
            serialized_message = json.dumps(rsa_encrypted)
            c.send(serialized_message.encode())
            print(f"RSA Encryption Time: {rsa_time:.6f} seconds")
            print(f"RSA-CRT Encryption Time: {crt_time:.6f} seconds")
    except Exception as error:
        print(f"Error sending message: {error}")
        c.close()

# Receiving Messages
def receiving_messages(c):
    try:
        while True:
            data = c.recv(1024).decode()
            if not data:
                break
            if data == "DISCONNECT":
                print("------ Partner has disconnected. ------")
                c.close()
                break

            # Deserialize and decrypt the received message
            cipher = json.loads(data)
            decrypted_message = decriptacion_RSA(cipher, d, n)  # Decrypt with RSA
            plain_message = ''.join(chr(i) for i in decrypted_message)
            print(f"Partner: {plain_message}")
    except Exception as error:
        print(f"Error receiving message: {error}")
        c.close()

def main():
    try:
        if choice == "1":
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((SERVER_IP, SERVER_PORT))
            server.listen(1)
            print(f"Server listening on {SERVER_IP}:{SERVER_PORT}...")
            
            client, addr = server.accept()
            print(f"Connection established with {addr}")
            print("\nType 'exit' to leave the conversation.")
            
            threading.Thread(target=sending_messages, args=(client,)).start()
            threading.Thread(target=receiving_messages, args=(client,)).start()

        elif choice == "2":
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client.connect((SERVER_IP, SERVER_PORT))
                print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
                print("\nType 'exit' to leave the conversation.")
                
                threading.Thread(target=sending_messages, args=(client,)).start()
                threading.Thread(target=receiving_messages, args=(client,)).start()
            except Exception as e:
                print(f"Failed to connect to server: {e}")
                exit()

        else:
            print("Invalid choice.")
            exit()

    except KeyboardInterrupt:
        print("\nExiting chat.")
        sys.exit()

if __name__ == "__main__":
    main()