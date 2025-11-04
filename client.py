import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import socket
import threading
import json
import time
from datetime import datetime, timedelta

class WhatsAppClient:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Clone - Client")
        self.root.geometry("450x700")
        self.root.configure(bg="#075E54")
        
        # Client state
        self.client_socket = None
        self.connected = False
        self.username = None
        self.server_time_offset = 0  # For clock synchronization
        self.last_sync_time = 0
        
        # WhatsApp colors
        self.colors = {
            'dark_green': '#075E54',
            'light_green': "#006D0F", 
            'teal': '#25D366',
            'white': '#FFFFFF',
            'light_gray': '#ECE5DD',
            'dark_gray': '#454545',
            'message_sent': '#DCF8C6',
            'message_received': '#FFFFFF',
            'system_message': '#E1F5FE'
        }
        
        self.setup_ui()
        self.start_clock_sync_timer()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.create_header()
        self.create_chat_area()
        self.create_input_area()
        self.create_connection_controls()
        
    def create_header(self):
        """Create header with title and status"""
        header_frame = tk.Frame(self.root, bg=self.colors['dark_green'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="WhatsApp Clone",
            font=("Helvetica", 18, "bold"),
            bg=self.colors['dark_green'],
            fg=self.colors['white']
        )
        title_label.pack(side='left', padx=20, pady=10)
        
        # Status and time frame
        status_frame = tk.Frame(header_frame, bg=self.colors['dark_green'])
        status_frame.pack(side='right', padx=20, pady=10)
        
        # Connection status
        self.status_label = tk.Label(
            status_frame,
            text="Disconnected",
            font=("Helvetica", 10),
            bg=self.colors['dark_green'],
            fg="#FF6B6B"
        )
        self.status_label.pack()
        
        # Synchronized time display
        self.time_label = tk.Label(
            status_frame,
            text="--:--:--",
            font=("Helvetica", 9),
            bg=self.colors['dark_green'],
            fg=self.colors['white']
        )
        self.time_label.pack()
        
        # Start time update
        self.update_time_display()
        
    def create_chat_area(self):
        """Create scrollable chat area"""
        chat_container = tk.Frame(self.root, bg=self.colors['light_gray'])
        chat_container.pack(fill='both', expand=True)
        
        # Canvas and scrollbar for chat
        self.chat_canvas = tk.Canvas(chat_container, bg=self.colors['light_gray'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.chat_canvas.yview)
        self.chat_frame = tk.Frame(self.chat_canvas, bg=self.colors['light_gray'])
        
        self.chat_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        
        self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.chat_canvas.bind("<MouseWheel>", self._on_mousewheel)
        
    def create_input_area(self):
        """Create message input area"""
        input_frame = tk.Frame(self.root, bg=self.colors['white'], height=70)
        input_frame.pack(fill='x')
        input_frame.pack_propagate(False)
        
        # Message entry
        self.message_entry = tk.Entry(
            input_frame,
            font=("Helvetica", 12),
            bg=self.colors['white'],
            fg=self.colors['dark_gray'],
            relief='flat',
            bd=5
        )
        self.message_entry.pack(side='left', fill='x', expand=True, padx=15, pady=20)
        self.message_entry.bind('<Return>', self.send_message)
        
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            font=("Helvetica", 11, "bold"),
            bg=self.colors['light_green'],
            fg=self.colors['teal'],
            relief='flat',
            bd=0,
            padx=25,
            command=self.send_message,
            cursor="hand2",
            activebackground=self.colors['light_green'],
            activeforeground=self.colors['teal']
        )
        self.send_button.pack(side='right', padx=15, pady=20)
        
    def create_connection_controls(self):
        """Create connection controls"""
        control_frame = tk.Frame(self.root, bg=self.colors['dark_green'], height=60)
        control_frame.pack(fill='x')
        control_frame.pack_propagate(False)
        
        # Connect button
        self.connect_button = tk.Button(
            control_frame,
            text="Connect",
            font=("Helvetica", 11, "bold"),
            bg=self.colors['light_green'],
            fg=self.colors['teal'],
            relief='flat',
            bd=0,
            padx=25,
            command=self.toggle_connection,
            cursor="hand2",
            activebackground=self.colors['light_green'],
            activeforeground=self.colors['teal']
        )
        self.connect_button.pack(side='left', padx=20, pady=15)
        
        # Sync clock button
        self.sync_button = tk.Button(
            control_frame,
            text="Sync Clock",
            font=("Helvetica", 10),
            bg=self.colors['light_green'],
            fg=self.colors['white'],
            relief='flat',
            bd=0,
            padx=20,
            command=self.sync_clock,
            cursor="hand2",
            activebackground=self.colors['teal'],
            activeforeground=self.colors['white']
        )
        self.sync_button.pack(side='left', padx=10, pady=15)
        
        # Server info
        server_info = tk.Label(
            control_frame,
            text="Server: 127.0.0.1:50001",
            font=("Helvetica", 10),
            bg=self.colors['dark_green'],
            fg=self.colors['white']
        )
        server_info.pack(side='right', padx=20, pady=15)
        
    def add_message(self, message, msg_type='sent', username=None, timestamp=None):
        """Add message to chat area"""
        # Message container
        msg_container = tk.Frame(self.chat_frame, bg=self.colors['light_gray'])
        msg_container.pack(fill='x', padx=15, pady=5)
        
        # Determine colors and alignment
        if msg_type == 'sent':
            bubble_color = self.colors['message_sent']
            align = 'right'
            anchor = 'e'
        elif msg_type == 'received':
            bubble_color = self.colors['message_received']
            align = 'left'
            anchor = 'w'
        else:  # system message
            bubble_color = self.colors['system_message']
            align = 'center'
            anchor = 'center'
        
        # Message bubble
        msg_frame = tk.Frame(msg_container, bg=bubble_color, relief='solid', bd=1)
        
        if align == 'center':
            msg_frame.pack(anchor='center', padx=50)
        elif align == 'right':
            msg_frame.pack(side='right', anchor=anchor, padx=30)
        else:
            msg_frame.pack(side='left', anchor=anchor, padx=30)
        
        # Username for received messages
        if msg_type == 'received' and username:
            username_label = tk.Label(
                msg_frame,
                text=f"@{username}",
                font=("Helvetica", 9, "bold"),
                bg=bubble_color,
                fg=self.colors['teal'],
                padx=15,
                pady=5
            )
            username_label.pack(anchor='w')
        
        # Message text
        msg_label = tk.Label(
            msg_frame,
            text=message,
            font=("Helvetica", 11),
            bg=bubble_color,
            fg=self.colors['dark_gray'],
            wraplength=280,
            justify='left',
            padx=15,
            pady=8
        )
        msg_label.pack()
        
        # Timestamp
        if timestamp:
            time_str = self.format_timestamp(timestamp)
        else:
            time_str = self.get_synchronized_time().strftime("%H:%M")
            
        time_label = tk.Label(
            msg_frame,
            text=time_str,
            font=("Helvetica", 8),
            bg=bubble_color,
            fg='#666666',
            padx=15,
            pady=3
        )
        time_label.pack(anchor='e')
        
        # Auto-scroll to bottom
        self.root.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)
        
    def toggle_connection(self):
        """Toggle connection to server"""
        if not self.connected:
            self.connect_to_server()
        else:
            self.disconnect_from_server()
            
    def connect_to_server(self):
        """Connect to the chat server"""
        # Get username
        username = simpledialog.askstring(
            "Username",
            "Enter your username:",
            initialvalue=f"User_{int(time.time() % 10000)}"
        )
        
        if not username:
            return
            
        self.username = username
        
        try:
            # Create socket connection
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('127.0.0.1', 50001))
            self.connected = True
            self.connection_time = time.time()  # Track connection time
            
            # Send join message
            join_message = {
                'type': 'join',
                'username': self.username,
                'timestamp': time.time()
            }
            self.send_to_server(join_message)
            
            # Update UI
            self.status_label.config(text=f"Connected as {self.username}", fg=self.colors['teal'])
            self.connect_button.config(text="Disconnect", bg="#D32F2F", fg=self.colors['white'])
            self.root.title(f"WhatsApp Clone - {self.username}")
            
            # Start listening thread
            self.listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
            self.listen_thread.start()
            
            # Initial clock sync
            self.sync_clock()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {str(e)}")
            self.connected = False
            
    def disconnect_from_server(self):
        """Disconnect from server"""
        if self.connected and self.client_socket:
            # Send leave message
            leave_message = {
                'type': 'leave',
                'username': self.username,
                'timestamp': time.time()
            }
            self.send_to_server(leave_message)
            
            self.client_socket.close()
            
        self.connected = False
        self.username = None
        
        # Update UI
        self.status_label.config(text="Disconnected", fg="#FF6B6B")
        self.connect_button.config(text="Connect", bg=self.colors['light_green'], fg=self.colors['white'])
        self.root.title("WhatsApp Clone - Client")
        
        # Add disconnect message
        self.add_message("Disconnected from server", 'system')
        
    def send_message(self, event=None):
        """Send chat message"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the server first.")
            return
            
        message_text = self.message_entry.get().strip()
        if not message_text:
            return
            
        try:
            # Send to server
            chat_message = {
                'type': 'chat',
                'message': message_text,
                'username': self.username,
                'timestamp': time.time()
            }
            self.send_to_server(chat_message)
            
            # Add to local chat (will be confirmed by server)
            self.add_message(message_text, 'sent')
            
            # Clear input
            self.message_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Send Error", f"Could not send message: {str(e)}")
            
    def send_to_server(self, message):
        """Send JSON message to server"""
        if self.client_socket:
            json_message = json.dumps(message)
            self.client_socket.send(json_message.encode('utf-8'))
            
    def listen_for_messages(self):
        """Listen for messages from server"""
        while self.connected:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if data:
                    message = json.loads(data)
                    self.root.after(0, lambda: self.handle_server_message(message))
                else:
                    break
            except:
                break
                
    def handle_server_message(self, message):
        """Handle different types of messages from server"""
        msg_type = message.get('type')
        
        if msg_type == 'join_success':
            self.add_message(message.get('message', 'Connected!'), 'system')
            
        elif msg_type == 'chat_message':
            username = message.get('username')
            text = message.get('message')
            timestamp = message.get('timestamp')
            self.add_message(text, 'received', username, timestamp)
            
        elif msg_type == 'user_joined':
            username = message.get('username')
            self.add_message(f"{username} joined the chat", 'system')
            
        elif msg_type == 'user_left':
            username = message.get('username')
            self.add_message(f"{username} left the chat", 'system')
            
        elif msg_type == 'clock_sync_response':
            self.handle_clock_sync_response(message)
            
        elif msg_type == 'message_delivered':
            # Message delivery confirmation - could add checkmarks here
            pass
            
    def sync_clock(self):
        """Perform Cristian's clock synchronization"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect to server first to sync clock.")
            return
            
        client_send_time = time.time()
        
        sync_message = {
            'type': 'clock_sync',
            'client_time': client_send_time
        }
        self.send_to_server(sync_message)
        
    def handle_clock_sync_response(self, message):
        """Handle clock synchronization response using Cristian's algorithm"""
        client_receive_time = time.time()
        server_time = message.get('server_time')
        client_send_time = message.get('client_request_time')
        estimated_rtt = message.get('estimated_rtt', 0.001)
        
        # Cristian's algorithm: adjust for network delay
        # Server time + half of round trip time
        network_delay = (client_receive_time - client_send_time) / 2
        synchronized_time = server_time + network_delay
        
        # Calculate offset
        self.server_time_offset = synchronized_time - time.time()
        self.last_sync_time = time.time()
        
        print(f"Clock synced: offset = {self.server_time_offset:.3f}s")
        # Only show sync message on initial connection, not regular auto-sync
        if time.time() - getattr(self, 'connection_time', 0) < 5:
            self.add_message(f"Clock synchronized (offset: {self.server_time_offset:.3f}s)", 'system')
        
    def get_synchronized_time(self):
        """Get current time synchronized with server"""
        return datetime.fromtimestamp(time.time() + self.server_time_offset)
        
    def format_timestamp(self, timestamp):
        """Format timestamp for display"""
        return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
        
    def start_clock_sync_timer(self):
        """Start automatic clock synchronization every 30 seconds"""
        def auto_sync():
            if self.connected and time.time() - self.last_sync_time > 30:
                self.sync_clock()
            self.root.after(30000, auto_sync)  # 30 seconds
            
        self.root.after(30000, auto_sync)
        
    def update_time_display(self):
        """Update time display in header"""
        current_time = self.get_synchronized_time()
        self.time_label.config(text=current_time.strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time_display)  # Update every second
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def on_closing(self):
        """Handle window closing"""
        if self.connected:
            self.disconnect_from_server()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppClient(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()