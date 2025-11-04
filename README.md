# WhatsApp-like Chat Application with Clock Synchronization

##  Overview
A WhatsApp-like chat application where multiple clients communicate through a central server.  
The clients display messages in a graphical chat window built with **Tkinter** and synchronize their clocks with the server using **Cristian’s Clock Synchronization Algorithm**.  
**Threading** is used to handle concurrency and manage multiple client connections efficiently.

---

##  Features
- Multi-client real-time chat through a central server  
- Clock synchronization using Cristian’s algorithm  
- Graphical user interface using Tkinter  
- Threading for concurrent message handling  
- Lightweight and easy to run locally  

---

##  Technologies Used
- **Python 3**
- **Socket Programming**
- **Threading**
- **Tkinter (GUI)**

---

##  Project Structure
ChatApp/
│
├── server-2.py # Central server handling multiple clients
├── client.py # Client-side code with Tkinter chat interface
├── multi_client_launcher-2.py # Utility to launch multiple clients for testing
├── README.md # Project documentation

##  How to Run

### 1️⃣ Start the Server
python3 server-2.py
2️⃣ Launch the Clients
python3 client.py


Or, to test multiple clients:

python3 multi_client_launcher-2.py
