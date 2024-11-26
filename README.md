# RSA / CRT comparison on a SMS App
This project compares both the encryption and decryption times of the RSA and RSA-CRT methods on SMS messages between two users to determine which algorithm is the most efficient for a simple SMS application using Python.

## How to run this project:
1. Open up two terminals (or a divided terminal)
2. Execute the file on your first terminal (`python SMS-cipherchat.py`)
3. Since it is the first file, select '1' as your option (host)
4. On your second terminal, run the same file the same way as before and select '2' as an option
5. you have now established a connection between your two clients, chat away!

*__note:__ The encryption and decryption times of every message sent and received will be logged into a csv file named `chat_log.csv`*

Once you're done chatting, type 'exit' on both terminals to finish the programs.