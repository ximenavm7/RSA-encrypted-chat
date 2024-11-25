import socket
import threading
import sys
import time
import json

# RSA Key Components
p = 61
q = 53
n = p * q
phi = (p - 1) * (q - 1)
e = 17
d = 2753  

# Global variables
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

choice = input("Host (1) or connect (2)?: ")

# Standard RSA Encryption
def encriptacion_RSA(plain, e, n):
    r = []
    for p in plain:
        result = pow(p, e, n)
        #print(f"{p}^{e} mod {n}: {result}")
        r.append(result)
    return r    

# Compare Decryption Times
def compare_decryption_methods(cipher, d, n, p, q):
    # RSA Decryption
    start_time_rsa = time.time()
    rsa_decrypted = decriptacion_RSA(cipher, d, n)
    rsa_time = time.time() - start_time_rsa

    # RSA-CRT Decryption
    start_time_crt = time.time()
    crt_decrypted = decriptacion_RSA_CRT(cipher, d, p, q)
    crt_time = time.time() - start_time_crt

    return rsa_time, crt_time, rsa_decrypted, crt_decrypted

# RSA Decryption
def decriptacion_RSA(cipher, d, n):
    r = []
    for c in cipher:
        result = pow(c, d, n)
        #print(f"{c}^{d} mod {n}: {result}")
        r.append(result)
    return r

# RSA-CRT Decryption
def decriptacion_RSA_CRT(cipher, d, p, q):
    dp = d % (p - 1)
    dq = d % (q - 1)
    q_inv = pow(q, -1, p)
    r = []

    for c in cipher: 
        m1 = pow(c % p, dp, p)
        m2 = pow(c % q, dq, q)
        h = (q_inv * (m1 - m2)) % p
        result = m2 + h * q
        #print(f"CRT result for {c}: {result}")
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

            # Encryption using RSA
            rsa_encrypted = encriptacion_RSA(message_ints, e, n)


            # Serialize and send the RSA-encrypted message
            serialized_message = json.dumps(rsa_encrypted)
            c.send(serialized_message.encode())
            #print(f"You (encrypted): {serialized_message}")
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
                print("------ Partner has disconnected.------")
                c.close()
                break

            # Deserialize and decrypt the received message
            encrypted_message = json.loads(data)
            # Compare RSA and RSA-CRT decryption times
            rsa_time, crt_time, rsa_decrypted, crt_decrypted = compare_decryption_methods(encrypted_message, d, n, p, q)

            print(f"RSA Decryption Time: {rsa_time:.6f} seconds")
            print(f"RSA-CRT Decryption Time: {crt_time:.6f} seconds")

            # Convert decrypted integers back to characters
            plain_message = ''.join(chr(i) for i in rsa_decrypted)
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