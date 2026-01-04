"""
Async Message Handler
Polls for async messages from server (challenges, game updates, etc.)
"""

import threading
import time


class AsyncMessageHandler:
    """Background thread to poll for async messages"""
    
    def __init__(self, network_client):
        self.network = network_client
        self.running = False
        self.thread = None
        
        # Message queues
        self.incoming_challenges = []
        self.game_starts = []
        self.player_lists = []
        self.move_made = []  # Queue for MOVE_MADE messages
        self.game_over = []  # Queue for GAME_OVER messages
        self.move_ok = []  # Queue for MOVE_OK messages
        self.move_invalid = []  # Queue for MOVE_INVALID messages
        self.valid_moves_response = []  # Queue for VALID_MOVES
        self.draw_offered = []
        self.draw_declined = []
        self.abort_offered = []
        self.abort_declined = []
        self.rematch_offered = []
        self.rematch_declined = []
        self.matchmaking_status = []
        self.match_replay = [] # Queue for MATCH_REPLAY messages
        self.reconnect_success = []  # Queue for RECONNECT_SUCCESS
        self.reconnect_fail = []  # Queue for RECONNECT_FAIL
        self.other_messages = []
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Reconnect state
        self.is_disconnected = False
        self.reconnect_in_progress = False
        self.reconnect_needed = False
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
    
    def start(self):
        """Start the async message polling thread"""
        if self.running:
            return
        
        self.running = True
        self.is_disconnected = False
        self.reconnect_needed = False
        self.consecutive_failures = 0
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        print("[AsyncHandler] Started polling for async messages")
    
    def stop(self):
        """Stop the polling thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print("[AsyncHandler] Stopped polling")
    
    def _poll_loop(self):
        """Main polling loop (runs in background thread)"""
        while self.running:
            try:
                # Check if we need to reconnect
                if self.reconnect_needed and not self.reconnect_in_progress:
                    self._attempt_reconnect()
                    continue
                
                # Try to receive message with short timeout
                message = self.network.receive_message(timeout=0.5)
                
                if message:
                    self._handle_async_message(message)
                    self.consecutive_failures = 0  # Reset on success
                else:
                    # Check if connection is still alive
                    if not self.network.check_alive() and self.network.last_session_id:
                        self.consecutive_failures += 1
                        if self.consecutive_failures >= self.max_consecutive_failures:
                            print("[AsyncHandler] Connection lost, triggering reconnect...")
                            self.is_disconnected = True
                            self.reconnect_needed = True
                    
            except Exception as e:
                print(f"[AsyncHandler] Error in poll loop: {e}")
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.max_consecutive_failures:
                    self.is_disconnected = True
                    self.reconnect_needed = True
            
            # Small delay to avoid busy waiting
            time.sleep(0.1)
    
    def _attempt_reconnect(self):
        """Attempt to reconnect to server"""
        if self.reconnect_in_progress:
            return
        
        self.reconnect_in_progress = True
        print("[AsyncHandler] Attempting to reconnect...")
        
        try:
            if self.network.reconnect_with_session():
                print("[AsyncHandler] Reconnect request sent, waiting for response...")
                # Wait for response
                time.sleep(1)
                response = self.network.receive_message(timeout=5.0)
                if response:
                    self._handle_async_message(response)
                    if response.get("action") == "RECONNECT_SUCCESS":
                        print("[AsyncHandler] Reconnect successful!")
                        self.is_disconnected = False
                        self.reconnect_needed = False
                        self.consecutive_failures = 0
                    else:
                        print(f"[AsyncHandler] Reconnect failed: {response}")
                        self.reconnect_needed = False  # Stop trying
            else:
                print("[AsyncHandler] Reconnect_with_session failed")
                time.sleep(2)  # Wait before retrying
        except Exception as e:
            print(f"[AsyncHandler] Reconnect error: {e}")
            time.sleep(2)
        finally:
            self.reconnect_in_progress = False
    
    def is_connection_lost(self):
        """Check if connection was lost and needs reconnect"""
        return self.is_disconnected
    
    def is_reconnecting(self):
        """Check if reconnection is in progress"""
        return self.reconnect_in_progress
    
    def _handle_async_message(self, message):
        """Handle an async message from server"""
        action = message.get("action", "")
        data = message.get("data", {})
        
        print(f"[AsyncHandler] Received async message: {action}")
        
        with self.lock:
            if action == "INCOMING_CHALLENGE":
                challenger = data.get("from", "Unknown")
                self.incoming_challenges.append(challenger)
                print(f"[AsyncHandler] Queued challenge from {challenger}")
                
            elif action == "START_GAME":
                self.game_starts.append(data)
                print(f"[AsyncHandler] Queued game start: {data.get('matchId')}")
                
            elif action == "PLAYER_LIST":
                self.player_lists.append(data)
                print(f"[AsyncHandler] Queued player list: {len(data.get('players', []))} players")
                
            elif action == "OPPONENT_MOVE":
                self.move_made.append(data)
                print(f"[AsyncHandler] Queued opponent move: {data.get('from')} -> {data.get('to')}")
                
            elif action == "GAME_OVER" or action == "GAME_RESULT":
                self.game_over.append(data)
                print(f"[AsyncHandler] Game over: {data.get('winner')} wins")
                
            elif action == "MOVE_OK":
                self.move_ok.append(data)
                print(f"[AsyncHandler] Move confirmed: {data.get('from')} -> {data.get('to')}")
                
            elif action == "MOVE_INVALID":
                self.move_invalid.append(data)
                print(f"[AsyncHandler] Move rejected: {data.get('reason')}")
                
            elif action == "VALID_MOVES":
                self.valid_moves_response.append(data)
                print(f"[AsyncHandler] Received valid moves for {data.get('position')}")
                
            elif action == "DRAW_OFFERED":
                self.draw_offered.append(data)
                print(f"[AsyncHandler] Draw offered by {data.get('from')}")

            elif action == "DRAW_DECLINED":
                self.draw_declined.append(data)
                print(f"[AsyncHandler] Draw declined")

            elif action == "ABORT_OFFERED":
                self.abort_offered.append(data)
                print(f"[AsyncHandler] Abort offered by {data.get('from')}")

            elif action == "ABORT_DECLINED":
                self.abort_declined.append(data)
                print(f"[AsyncHandler] Abort declined")

            elif action == "REMATCH_OFFERED":
                self.rematch_offered.append(data)
                print(f"[AsyncHandler] Rematch offered by {data.get('from')}")

            elif action == "REMATCH_DECLINED":
                self.rematch_declined.append(data)
                print(f"[AsyncHandler] Rematch declined")

            elif action == "MATCH_REPLAY":
                self.match_replay.append(data)
                print(f"[AsyncHandler] Received match replay")

            elif action == "MATCHMAKING_STATUS":
                self.matchmaking_status.append(data)
                print(f"[AsyncHandler] Received matchmaking status: {data.get('status')}")
            
            elif action == "RECONNECT_SUCCESS":
                self.reconnect_success.append(data)
                print(f"[AsyncHandler] Reconnect successful: {data.get('username')}")
            
            elif action == "RECONNECT_FAIL":
                self.reconnect_fail.append(data)
                print(f"[AsyncHandler] Reconnect failed: {data.get('reason')}")
                
            else:
                # Store other messages
                self.other_messages.append(message)
    
    def get_incoming_challenge(self):
        """Get next incoming challenge (if any)"""
        with self.lock:
            if self.incoming_challenges:
                return self.incoming_challenges.pop(0)
        return None
    
    def get_game_start(self):
        """Get next game start message (if any)"""
        with self.lock:
            if self.game_starts:
                return self.game_starts.pop(0)
        return None
    
    def get_player_list(self):
        """Get next player list response (if any)"""
        with self.lock:
            if self.player_lists:
                return self.player_lists.pop(0)
        return None
    
    def get_move_made(self):
        """Get next move from opponent (if any)"""
        with self.lock:
            if self.move_made:
                return self.move_made.pop(0)
        return None
    
    def get_game_over(self):
        """Get game over message (if any)"""
        with self.lock:
            if self.game_over:
                return self.game_over.pop(0)
        return None
    
    def get_move_ok(self):
        """Get MOVE_OK confirmation (if any)"""
        with self.lock:
            if self.move_ok:
                return self.move_ok.pop(0)
        return None
    
    def get_move_invalid(self):
        """Get MOVE_INVALID rejection (if any)"""
        with self.lock:
            if self.move_invalid:
                return self.move_invalid.pop(0)
        return None
        
    def get_valid_moves(self):
        """Get VALID_MOVES response (if any)"""
        with self.lock:
            if self.valid_moves_response:
                return self.valid_moves_response.pop(0)
        return None

    def get_draw_offered(self):
        with self.lock:
            if self.draw_offered:
                return self.draw_offered.pop(0)
        return None

    def get_draw_declined(self):
        with self.lock:
            if self.draw_declined:
                return self.draw_declined.pop(0)
        return None

    def get_abort_offered(self):
        with self.lock:
            if self.abort_offered:
                return self.abort_offered.pop(0)
        return None

    def get_abort_declined(self):
        with self.lock:
            if self.abort_declined:
                return self.abort_declined.pop(0)
        return None
    
    def get_rematch_offered(self):
        with self.lock:
            if self.rematch_offered:
                return self.rematch_offered.pop(0)
        return None

    def get_rematch_declined(self):
        with self.lock:
            if self.rematch_declined:
                return self.rematch_declined.pop(0)
        return None
    
    def get_match_replay(self):
        with self.lock:
            if self.match_replay:
                return self.match_replay.pop(0)
        return None
    
    def get_matchmaking_status(self):
        with self.lock:
            if self.matchmaking_status:
                return self.matchmaking_status.pop(0)
        return None
    
    def get_reconnect_success(self):
        """Get RECONNECT_SUCCESS response (if any)"""
        with self.lock:
            if self.reconnect_success:
                return self.reconnect_success.pop(0)
        return None
    
    def get_reconnect_fail(self):
        """Get RECONNECT_FAIL response (if any)"""
        with self.lock:
            if self.reconnect_fail:
                return self.reconnect_fail.pop(0)
        return None
    
    def has_pending_messages(self):
        """Check if there are any pending messages"""
        with self.lock:
            return (len(self.incoming_challenges) > 0 or 
                    len(self.game_starts) > 0 or
                    len(self.player_lists) > 0 or
                    len(self.move_made) > 0 or
                    len(self.game_over) > 0 or
                    len(self.move_ok) > 0 or
                    len(self.move_invalid) > 0 or
                    len(self.valid_moves_response) > 0 or
                    len(self.draw_offered) > 0 or
                    len(self.abort_offered) > 0 or
                    len(self.rematch_offered) > 0 or
                    len(self.reconnect_success) > 0 or
                    len(self.reconnect_fail) > 0 or
                    len(self.other_messages) > 0)
    
    def clear_all(self):
        """Clear all message queues"""
        with self.lock:
            self.incoming_challenges.clear()
            self.game_starts.clear()
            self.player_lists.clear()
            self.move_made.clear()
            self.game_over.clear()
            self.move_ok.clear()
            self.move_invalid.clear()
            self.valid_moves_response.clear()
            self.draw_offered.clear()
            self.draw_declined.clear()
            self.abort_offered.clear()
            self.abort_declined.clear()
            self.rematch_offered.clear()
            self.rematch_declined.clear()
            self.matchmaking_status.clear()
            self.reconnect_success.clear()
            self.reconnect_fail.clear()
            self.other_messages.clear()
