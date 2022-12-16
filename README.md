This is the Repo for CS514: Advanced computer networking Final project

Remote File system with particular focus on security.
This project will allow several users maintain their own remote file system using the server.

Some security components:
1) Stored salt-hashed password with iteration count using bcrypt

2) implemented a SCRAM-based client authentication protocol.

3) Encrypted communication: Client and server use Diffie-Hellman for shared key, then encrypt communication using AES EAX mode. The decryption is verified for tampering


Custom SCRAM-based authentication protocol
<img width="465" alt="image" src="https://user-images.githubusercontent.com/41854864/207993850-9bf08763-1f14-4b76-95f4-bfe8ecbcaa5d.png">

