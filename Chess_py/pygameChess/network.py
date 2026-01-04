import ctypes
import json
import threading
import time
import os
from config import SERVER_HOST, SERVER_PORT

# Session file path
SESSION_FILE = os.path.expanduser("~/.chess_session.json")

# Load C library
try:
    # Assuming library is in ../network_lib/client_network.so relative to this file
    _lib_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "network_lib", "client_network.so")
    _clib = ctypes.CDLL(_lib_path)
    
    # Define argument/return types
    _clib.connect_to_server.argtypes = [ctypes.c_char_p, ctypes.c_int]
    _clib.connect_to_server.restype = ctypes.c_int
    
    _clib.disconnect_server.argtypes = [ctypes.c_int]
    
    _clib.send_message.argtypes = [ctypes.c_int, ctypes.c_char_p]
    _clib.send_message.restype = ctypes.c_int
    
    _clib.receive_message.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
    _clib.receive_message.restype = ctypes.c_int
    
    _clib.check_connection.argtypes = [ctypes.c_int]
    _clib.check_connection.restype = ctypes.c_int
    
except OSError:
    print(f"Error: Could not load C library at {_lib_path}")
    _clib = None


class NetworkClient:
    """Client for communicating with C Server using C shared library"""
    
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.socket_fd = 0
        self.connected = False
        self.lock = threading.Lock()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        # Session tracking for reconnect
        self.last_session_id = None
        self.last_username = None
        
        # Load persisted session from file
        self._load_session_from_file()
        
        if not _clib:
            print("[Network] FATAL: C library not loaded")
    
    def _load_session_from_file(self):
        """Load saved session from file for reconnect after restart"""
        try:
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, 'r') as f:
                    data = json.load(f)
                    self.last_session_id = data.get('session_id')
                    self.last_username = data.get('username')
                    print(f"[Network] Loaded saved session: {self.last_username}")
        except Exception as e:
            print(f"[Network] Could not load session: {e}")
    
    def _save_session_to_file(self):
        """Save session to file for reconnect after restart"""
        try:
            with open(SESSION_FILE, 'w') as f:
                json.dump({
                    'session_id': self.last_session_id,
                    'username': self.last_username
                }, f)
            print(f"[Network] Session saved to file")
        except Exception as e:
            print(f"[Network] Could not save session: {e}")
    
    def _clear_session_file(self):
        """Clear session file on logout"""
        try:
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
                print("[Network] Session file cleared")
        except:
            pass
    
    def has_saved_session(self):
        """Check if there's a saved session to try reconnecting"""
        return self.last_session_id is not None and self.last_username is not None
        
    def connect(self):
        """Establish connection to the server via C library"""
        if not _clib: return False
        
        try:
            host_bytes = self.host.encode('utf-8')
            fd = _clib.connect_to_server(host_bytes, self.port)
            
            if fd > 0:
                self.socket_fd = fd
                self.connected = True
                self.reconnect_attempts = 0
                print(f"[Network] Connected to server at {self.host}:{self.port} (FD: {fd})")
                return True
            else:
                print(f"[Network] Connection failed with code: {fd}")
                self.connected = False
                return False
                
        except Exception as e:
            print(f"[Network] Connection exception: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Close connection via C library"""
        with self.lock:
            if self.socket_fd > 0:
                try:
                    _clib.disconnect_server(self.socket_fd)
                except Exception as e:
                    print(f"[Network] Error during disconnect: {e}")
                self.socket_fd = 0
            self.connected = False
            self.reconnect_attempts = 0
            print("[Network] Disconnected from server")
    
    def reconnect(self):
        """Attempt to reconnect to the server"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print("[Network] Max reconnection attempts reached")
            return False
        
        print(f"[Network] Reconnecting... (attempt {self.reconnect_attempts + 1})")
        
        # Ensure old socket is fully closed
        if self.socket_fd > 0:
            try:
                _clib.disconnect_server(self.socket_fd)
            except:
                pass
            self.socket_fd = 0
        
        self.connected = False
        time.sleep(1)  # Wait before reconnecting
        self.reconnect_attempts += 1
        return self.connect()
    
    def reconnect_with_session(self):
        """Reconnect và restore session bằng sessionId đã lưu"""
        if not self.last_session_id or not self.last_username:
            print("[Network] No saved session to restore")
            return False
        
        if not self.reconnect():
            return False
        
        # Gửi RECONNECT request thay vì LOGIN
        print(f"[Network] Attempting to restore session for {self.last_username}")
        return self.send_message("RECONNECT", {
            "sessionId": self.last_session_id,
            "username": self.last_username
        })
    
    def save_session(self, session_id, username):
        """Lưu session để có thể reconnect sau này"""
        self.last_session_id = session_id
        self.last_username = username
        self._save_session_to_file()  # Persist to file
        print(f"[Network] Session saved: {username} ({session_id[:8]}...)")
    
    def clear_session(self):
        """Clear session on logout"""
        self.last_session_id = None
        self.last_username = None
        self._clear_session_file()
    
    def check_alive(self):
        """Kiểm tra connection còn sống không"""
        if not _clib or self.socket_fd <= 0:
            return False
        try:
            result = _clib.check_connection(self.socket_fd)
            return result == 1
        except:
            return False
    
    def send_message(self, action, data):
        """Send JSON message via C library"""
        message = {
            "action": action,
            "data": data
        }
        
        try:
            json_str = json.dumps(message)
            msg_bytes = json_str.encode('utf-8')
            
            with self.lock:
                if not self.connected or self.socket_fd <= 0:
                    print("[Network] Not connected, attempting to reconnect...")
                    if not self.reconnect():
                        return False
                
                result = _clib.send_message(self.socket_fd, msg_bytes)
                if result == 0:
                    print(f"[Network] Sent: {json_str}")
                    return True
                else:
                    print("[Network] Send failed")
                    self.connected = False
                    return False
                
        except Exception as e:
            print(f"[Network] Send error: {e}")
            self.connected = False
            return False
    
    def receive_message(self, timeout=10.0):
        """Receive JSON message via C library"""
        # Note: timeout logic is handled in C library socket options
        
        try:
            with self.lock:
                if not self.connected or self.socket_fd <= 0:
                    return None
                
                # Create buffer
                buffer = ctypes.create_string_buffer(4096)
                
                # Call C receive (blocking with timeout set in connect)
                bytes_read = _clib.receive_message(self.socket_fd, buffer, 4096)
                
                if bytes_read > 0:
                    json_str = buffer.value.decode('utf-8').strip()
                    if json_str:
                        try:
                            message = json.loads(json_str)
                            print(f"[Network] Received: {json_str}")
                            return message
                        except json.JSONDecodeError:
                            print(f"[Network] JSON parse error: {json_str}")
                            return None
                    return None
                elif bytes_read == -1:
                    return None
                else:
                    return None
                
        except Exception as e:
            print(f"[Network] Receive error: {e}")
            # Only mark disconnected on actual exceptions, not timeouts
            self.connected = False
            return None
    
    def is_connected(self):
        """Check if connected to server"""
        return self.connected
    
    def __del__(self):
        """Cleanup on deletion"""
        self.disconnect()
