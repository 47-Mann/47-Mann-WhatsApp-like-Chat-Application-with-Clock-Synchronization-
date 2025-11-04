#!/usr/bin/env python3
"""
WhatsApp Clone - Multi-Client Chat Application
Simple launcher for testing the chat system
"""

import subprocess
import sys
import os
import time

def start_server():
    """Start the chat server"""
    print("🚀 Starting ChatGPT Server...")
    try:
        # Use the virtual environment Python
        venv_python = "/Users/aarushkumar/Desktop/College/Distributed Systems/Whatsapp Client Server Interaction/.venv/bin/python"
        
        if sys.platform == "darwin":  # macOS
            server_cmd = [
                'osascript', '-e',
                f'tell app "Terminal" to do script "cd \\"{os.getcwd()}\\" && \\"{venv_python}\\" server.py"'
            ]
            subprocess.run(server_cmd)
        else:  # Linux/Windows
            subprocess.Popen([venv_python, "server.py"])
        print("✅ ChatGPT Server started successfully")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Trying with regular python3...")
        try:
            if sys.platform == "darwin":  # macOS
                server_cmd = [
                    'osascript', '-e',
                    f'tell app "Terminal" to do script "cd \\"{os.getcwd()}\\" && python3 server.py"'
                ]
                subprocess.run(server_cmd)
            else:
                subprocess.Popen([sys.executable, "server.py"])
            print("✅ Server started with python3")
            return True
        except Exception as e2:
            print(f"❌ Error starting server with python3: {e2}")
            return False

def start_client():
    """Start a chat client"""
    print("🎨 Starting Chat Client...")
    try:
        subprocess.Popen([sys.executable, "client.py"])
        print("✅ Client started successfully")
        return True
    except Exception as e:
        print(f"❌ Error starting client: {e}")
        return False

def main():
    print("=" * 70)
    print("🤖 WhatsApp Clone - ChatGPT Multi-Client Chat Application")
    print("=" * 70)
    print("\nFeatures:")
    print("✅ Multiple clients can connect simultaneously")
    print("✅ Real-time chat messaging with ChatGPT AI")
    print("✅ Cristian's clock synchronization algorithm")
    print("✅ WhatsApp-like GUI interface")
    print("✅ Threading for concurrent connections")
    print("🤖 ChatGPT responds to all messages!")
    print("=" * 70)
    
    while True:
        choice = input("""
Choose an option:
1. Start Server only
2. Start Client only  
3. Start Server + 1 Client
4. Start Server + Multiple Clients
5. Exit

Enter your choice (1-5): """).strip()
        
        if choice == "1":
            start_server()
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            start_client()
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            if start_server():
                print("⏳ Waiting 2 seconds for server to initialize...")
                time.sleep(2)
                start_client()
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            if start_server():
                print("⏳ Waiting 2 seconds for server to initialize...")
                time.sleep(2)
                
                num_clients = input("How many clients to start? (2-5): ").strip()
                try:
                    num_clients = int(num_clients)
                    if 2 <= num_clients <= 5:
                        for i in range(num_clients):
                            start_client()
                            time.sleep(0.5)  # Small delay between clients
                        print(f"✅ Started {num_clients} clients")
                    else:
                        print("❌ Please enter a number between 2 and 5")
                except ValueError:
                    print("❌ Invalid number")
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()