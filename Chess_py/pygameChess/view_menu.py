"""
Main Menu View for Chess Client
Displays after successful authentication
"""

import pygame
from config import *


class MenuView:
    """Main menu screen with matchmaking and profile options"""
    
    def __init__(self, screen, network_client):
        self.screen = screen
        self.network = network_client
        self.font_title = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        
        # Session data
        self.username = ""
        self.session_id = ""
        
        # UI state
        self.state = "menu"  # "menu" or "waiting"
        self.message = ""
        self.message_color = COLOR_TEXT_SECONDARY
        self._should_start_game = False
        self._should_logout = False
        self._should_exit = False
        self._should_show_players = False
        self._should_show_history = False
        self._should_find_match = False
        
        # Button rectangles (centered layout)
        button_width = 300
        button_height = 70
        button_spacing = 85
        start_y = 280
        center_x = SCREEN_WIDTH // 2
        
        self.button_online_players = pygame.Rect(
            center_x - button_width // 2, start_y, button_width, button_height
        )
        self.button_match_history = pygame.Rect(
            center_x - button_width // 2, start_y + button_spacing, button_width, button_height
        )
        self.button_view_profile = pygame.Rect(
            center_x - button_width // 2, start_y + button_spacing * 2, button_width, button_height
        )
        self.button_logout = pygame.Rect(
            center_x - button_width // 2, start_y + button_spacing * 3, button_width, button_height
        )
        self.button_exit = pygame.Rect(
            center_x - button_width // 2, start_y + button_spacing * 4, button_width, button_height
        )
        
        # Waiting room button
        self.button_cancel = pygame.Rect(
            center_x - 150, 500, 300, 60
        )
        
        self.button_find_match = pygame.Rect(
            center_x - button_width // 2, start_y - button_spacing, button_width, button_height
        )
        
    def set_session_data(self, session_data):
        """Set session data from login"""
        self.username = session_data.get("username", "Player")
        self.session_id = session_data.get("sessionId", "")
        
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "menu":
                # Menu buttons
                if self.button_online_players.collidepoint(event.pos):
                    self.show_online_players()
                elif self.button_match_history.collidepoint(event.pos):
                    self.show_match_history()
                elif self.button_view_profile.collidepoint(event.pos):
                    self.view_profile()
                elif self.button_logout.collidepoint(event.pos):
                    self.logout()
                elif self.button_exit.collidepoint(event.pos):
                    self.exit_app()
                elif self.button_find_match.collidepoint(event.pos):
                    self.find_match()
            elif self.state == "waiting":
                # Waiting room buttons
                if self.button_cancel.collidepoint(event.pos):
                    self.cancel_matchmaking()
    
    def show_online_players(self):
        """Show online players list"""
        self._should_show_players = True
    
    def show_match_history(self):
        """Show match history"""
        self._should_show_history = True
    
    def cancel_matchmaking(self):
        """Cancel matchmaking and return to menu"""
        self.state = "menu"
        self.message = "Matchmaking cancelled"
        self.message_color = COLOR_TEXT_SECONDARY
        
        # TODO: Send CANCEL_MATCH request to server
        # self.network.send_message("CANCEL_MATCH", {"sessionId": self.session_id})
    
    def view_profile(self):
        """View user profile"""
        # For now, just show a message
        # In future, can create a separate profile view or popup
        self.message = f"Profile: {self.username} | Session: {self.session_id[:8]}..."
        self.message_color = COLOR_SUCCESS
    
    def logout(self):
        """Logout and return to auth screen"""
        # Send LOGOUT message to server first
        if self.network.is_connected() and self.session_id:
            try:
                self.network.send_message("LOGOUT", {"sessionId": self.session_id})
                print("[MenuView] Sent LOGOUT message")
            except Exception as e:
                print(f"[MenuView] Error sending LOGOUT: {e}")
        
        self.network.disconnect()
        self._should_logout = True
    
    def exit_app(self):
        """Exit the application"""
        # Logout before exit
        if self.network.is_connected() and self.session_id:
            try:
                self.network.send_message("LOGOUT", {"sessionId": self.session_id})
                print("[MenuView] Sent LOGOUT message before exit")
            except Exception as e:
                print(f"[MenuView] Error sending LOGOUT: {e}")
        
        self.network.disconnect()
        self._should_exit = True
    
    def draw(self):
        """Draw the menu screen"""
        self.screen.fill(COLOR_BACKGROUND_PRIMARY)
        
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "waiting":
            self._draw_waiting()
            
    def find_match(self):
        self._should_find_match = True
        
    def should_do_find_match(self):
        return self._should_find_match
    
    def _draw_menu(self):
        """Draw the main menu"""
        # Title
        title_text = f"Welcome, {self.username}!"
        title_surface = self.font_title.render(title_text, True, COLOR_TEXT)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Find Match Button
        self._draw_button(
            self.button_find_match,
            "Find Match",
            COLOR_BUTTON_PRIMARY,
            mouse_pos
        )
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Online Players button
        self._draw_button(
            self.button_online_players, 
            "Online Players", 
            COLOR_BUTTON_PRIMARY, 
            mouse_pos
        )
        
        # Match History button
        self._draw_button(
            self.button_match_history,
            "Match History",
            COLOR_ACCENT_SECONDARY,
            mouse_pos
        )
        
        # View Profile button
        self._draw_button(
            self.button_view_profile, 
            "View Profile", 
            COLOR_BUTTON_PRIMARY, 
            mouse_pos
        )
        
        # Logout button
        self._draw_button(
            self.button_logout, 
            "Logout", 
            (220, 100, 53),  # Orange
            mouse_pos
        )
        
        # Exit button
        self._draw_button(
            self.button_exit, 
            "Exit", 
            COLOR_ERROR,  # Red
            mouse_pos
        )
        
        # Message
        if self.message:
            message_surface = self.font_small.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, 700))
            self.screen.blit(message_surface, message_rect)
        
        # Footer instruction
        footer_text = "Click a button to continue"
        footer_surface = self.font_small.render(footer_text, True, COLOR_TEXT_SECONDARY)
        footer_rect = footer_surface.get_rect(center=(SCREEN_WIDTH // 2, 800))
        self.screen.blit(footer_surface, footer_rect)
    
    def _draw_waiting(self):
        """Draw the waiting room screen"""
        # Title
        title_text = "Matchmaking"
        title_surface = self.font_title.render(title_text, True, COLOR_TEXT)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Waiting message
        waiting_text = "Searching for opponent..."
        waiting_surface = self.font_large.render(waiting_text, True, COLOR_TEXT_SECONDARY)
        waiting_rect = waiting_surface.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(waiting_surface, waiting_rect)
        
        # Animated dots (simple animation)
        dots_count = (pygame.time.get_ticks() // 500) % 4
        dots_text = "." * dots_count
        dots_surface = self.font_large.render(dots_text, True, COLOR_TEXT_SECONDARY)
        dots_rect = dots_surface.get_rect(center=(SCREEN_WIDTH // 2, 370))
        self.screen.blit(dots_surface, dots_rect)
        
        # Cancel button
        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(
            self.button_cancel,
            "Cancel",
            COLOR_ERROR,
            mouse_pos
        )
        
        # Info text
        info_text = "You will be matched with another player soon"
        info_surface = self.font_small.render(info_text, True, COLOR_TEXT_SECONDARY)
        info_rect = info_surface.get_rect(center=(SCREEN_WIDTH // 2, 650))
        self.screen.blit(info_surface, info_rect)
    
    def _draw_button(self, rect, text, base_color, mouse_pos):
        """Helper to draw a button with hover effect"""
        hover_color = tuple(min(c + 30, 255) for c in base_color)
        color = hover_color if rect.collidepoint(mouse_pos) else base_color
        
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        
        text_surface = self.font_medium.render(text, True, COLOR_BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def should_start_game(self):
        """Check if should transition to game"""
        return self._should_start_game
    
    def should_do_logout(self):
        """Check if should logout"""
        return self._should_logout
    
    def should_do_exit(self):
        """Check if should exit"""
        return self._should_exit
    
    def should_show_players(self):
        """Check if should show online players"""
        return self._should_show_players
    
    def should_show_history(self):
        """Check if should show match history"""
        return self._should_show_history
    
    def reset(self):
        """Reset menu state"""
        self.state = "menu"
        self.message = ""
        self._should_start_game = False
        self._should_logout = False
        self._should_exit = False
        self._should_show_players = False
        self._should_show_players = False
        self._should_show_history = False
        self._should_find_match = False
