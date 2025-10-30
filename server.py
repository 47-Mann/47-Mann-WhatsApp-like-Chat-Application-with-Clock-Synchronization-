import socket
import threading
import time
import json
from datetime import datetime
import openai
import os

class ChatServer:
    def __init__(self, host='127.0.0.1', port=50001):
        self.host = host
        self.port = port
        self.clients = {}  # {socket: {'username': str, 'address': tuple}}
        self.server_socket = None
        self.running = False
        
        # 🤖 CHATGPT API SETUP - USING ENVIRONMENT VARIABLE
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        print("🤖 WhatsApp Server with ChatGPT Integration")
        print("=" * 60)
        
    def start_server(self):
        """Start the chat server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.running = True
            
            print(f"🟢 WhatsApp Chat Server started on {self.host}:{self.port}")
            print(f"🤖 ChatGPT integration: READY")
            print(f"⏰ Server time: {datetime.now().strftime('%H:%M:%S')}")
            print("📱 Waiting for client connections...")
            print("-" * 60)
            
            while self.running:
                try:
                    conn, addr = self.server_socket.accept()
                    
                    # Start client handler thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        print("❌ Error accepting connection")
                    break
                    
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.cleanup()
            
    def handle_client(self, conn, addr):
        """Handle individual client connection"""
        try:
            while self.running:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                try:
                    message = json.loads(data)
                    self.process_message(conn, addr, message)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON from {addr}")
                    
        except ConnectionResetError:
            print(f"🔌 Client {addr} disconnected unexpectedly")
        except Exception as e:
            print(f"❌ Error handling client {addr}: {e}")
        finally:
            self.remove_client(conn, addr)
            
    def process_message(self, conn, addr, message):
        """Process different types of messages"""
        msg_type = message.get('type')
        
        if msg_type == 'join':
            self.handle_join(conn, addr, message)
        elif msg_type == 'chat':
            self.handle_chat_message(conn, addr, message)
        elif msg_type == 'clock_sync':
            self.handle_clock_sync(conn, addr, message)
        elif msg_type == 'leave':
            self.handle_leave(conn, addr, message)
        else:
            print(f"❓ Unknown message type from {addr}: {msg_type}")
            
    def handle_join(self, conn, addr, message):
        """Handle client joining the chat"""
        username = message.get('username', f'User_{addr[1]}')
        
        # Add client to our list
        self.clients[conn] = {
            'username': username,
            'address': addr,
            'joined_at': time.time()
        }
        
        print(f"✅ {username} joined from {addr}")
        print(f"📊 Active clients: {len(self.clients)}")
        
        # Send join confirmation to the client
        response = {
            'type': 'join_success',
            'message': f'Welcome to ChatGPT Chat, {username}! 🤖 Type anything to chat with AI!',
            'server_time': time.time(),
            'clients_count': len(self.clients)
        }
        self.send_to_client(conn, response)
        
        # Notify other clients about new user
        notification = {
            'type': 'user_joined',
            'username': username,
            'message': f'{username} joined the chat',
            'timestamp': time.time(),
            'clients_count': len(self.clients)
        }
        self.broadcast_message(notification, exclude=conn)
        
    def handle_chat_message(self, conn, addr, message):
        """Handle chat messages with ChatGPT and broadcast to all clients"""
        if conn not in self.clients:
            return
            
        username = self.clients[conn]['username']
        chat_text = message.get('message', '')
        server_timestamp = time.time()
        
        print(f"💬 [{datetime.fromtimestamp(server_timestamp).strftime('%H:%M:%S')}] {username}: {chat_text}")
        
        # First, broadcast the user's message to all other clients
        user_broadcast_msg = {
            'type': 'chat_message',
            'username': username,
            'message': chat_text,
            'timestamp': server_timestamp,
            'sender_address': addr
        }
        self.broadcast_message(user_broadcast_msg, exclude=conn)
        
        # Send delivery confirmation to sender
        confirmation = {
            'type': 'message_delivered',
            'timestamp': server_timestamp
        }
        self.send_to_client(conn, confirmation)
        
        # 🤖 Get ChatGPT response and broadcast to ALL clients (including sender)
        gpt_response = self.get_chatgpt_response(chat_text, username)
        
        chatgpt_broadcast_msg = {
            'type': 'chat_message',
            'username': 'ChatGPT 🤖',
            'message': gpt_response,
            'timestamp': time.time(),
            'sender_address': ('ChatGPT', 'AI')
        }
        self.broadcast_message(chatgpt_broadcast_msg)
        
        print(f"🤖 ChatGPT responded: {gpt_response[:50]}...")
        
    def get_chatgpt_response(self, user_message, username):
        """Get response from ChatGPT API"""
        try:
            print(f"🔄 Sending to ChatGPT: {user_message}")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a helpful and friendly assistant in a WhatsApp-like chat app. The user's name is {username}. Keep responses conversational, helpful, and under 100 words. Use some emojis to make it fun and engaging! Be natural and chat-like."
                    },
                    {
                        "role": "user", 
                        "content": user_message
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            gpt_reply = response.choices[0].message.content.strip()
            print(f"✅ ChatGPT response received: {len(gpt_reply)} characters")
            return gpt_reply
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ ChatGPT API Error: {error_msg}")
            
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return f"Sorry {username}, I need my API key to be configured! 🔑 Please check the server setup."
            elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                return f"Oops {username}, looks like we've hit our API limit! 💳 Time to add some credits."
            elif "model" in error_msg.lower():
                return f"Hey {username}, there's a model issue on my end! 🤖 The server admin should check this."
            else:
                return f"Sorry {username}, I'm having trouble connecting to my brain right now! 🤖💭 Try again in a moment."
        
    def handle_clock_sync(self, conn, addr, message):
        client_request_time = message.get('client_time', time.time())
        server_time = time.time()
        
        estimated_rtt = 0.001
        
        response = {
            'type': 'clock_sync_response',
            'server_time': server_time,
            'client_request_time': client_request_time,
            'estimated_rtt': estimated_rtt
        }
        
        self.send_to_client(conn, response)
        
        if conn in self.clients:
            username = self.clients[conn]['username']
            print(f"🕐 Clock sync request from {username} at {addr}")
            
    def handle_leave(self, conn, addr, message):
        if conn in self.clients:
            username = self.clients[conn]['username']
            print(f"👋 {username} left the chat")
            
            notification = {
                'type': 'user_left',
                'username': username,
                'message': f'{username} left the chat',
                'timestamp': time.time(),
                'clients_count': len(self.clients) - 1
            }
            self.broadcast_message(notification, exclude=conn)
            
        self.remove_client(conn, addr)
        
    def send_to_client(self, conn, message):
        try:
            json_message = json.dumps(message)
            conn.send(json_message.encode('utf-8'))
        except Exception as e:
            print(f"❌ Error sending to client: {e}")
            
    def broadcast_message(self, message, exclude=None):
        disconnected_clients = []
        
        for client_conn in self.clients:
            if client_conn != exclude:
                try:
                    self.send_to_client(client_conn, message)
                except:
                    disconnected_clients.append(client_conn)
                    
        for client_conn in disconnected_clients:
            if client_conn in self.clients:
                addr = self.clients[client_conn]['address']
                self.remove_client(client_conn, addr)
                
    def remove_client(self, conn, addr):
        try:
            if conn in self.clients:
                self.clients.pop(conn)
            conn.close()
            print(f"❌ Client {addr} removed")
            print(f"📊 Active clients: {len(self.clients)}")
        except Exception as e:
            print(f"❌ Error removing client {addr}: {e}")
            
    def cleanup(self):
        print("\n🔄 Shutting down server...")
        self.running = False
        
        for client_conn in list(self.clients.keys()):
            try:
                client_conn.close()
            except:
                pass
        self.clients.clear()
        
        if self.server_socket:
            self.server_socket.close()
            
        print("✅ Server shutdown complete")
        
    def get_server_stats(self):
        return {
            'active_clients': len(self.clients),
            'server_time': time.time(),
            'uptime': time.time() - getattr(self, 'start_time', time.time())
        }

if __name__ == "__main__":
    server = ChatServer()
    server.start_time = time.time()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n⚠️ Server interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        server.cleanup()
