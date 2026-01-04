"""
Challenge Notification View
Displays incoming challenge and allows accept/decline
"""

import pygame
from config import *


class ChallengeNotification:
    """Popup notification for incoming challenges"""
    
    def __init__(self, screen, network_client):
        self.screen = screen
        self.network = network_client
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        
        # Session data
        self.my_username = ""
        
        # Challenge data
        self.challenger_name = ""
        self.is_visible = False
        
        # UI state
        self._should_accept = False
        self._should_decline = False
        
        # UI rectangles
        self.popup_rect = pygame.Rect(250, 300, 500, 300)
        self.button_accept = pygame.Rect(300, 500, 180, 50)
        self.button_decline = pygame.Rect(520, 500, 180, 50)
    
    def set_session_data(self, session_data):
        """Set session data"""
        self.my_username = session_data.get("username", "")
    
    def show_challenge(self, challenger_name):
        """Show challenge notification"""
        self.challenger_name = challenger_name
        self.is_visible = True
        self._should_accept = False
        self._should_decline = False
        print(f"[Challenge] Showing challenge from {challenger_name}")
    
    def handle_event(self, event):
        """Handle pygame events"""
        if not self.is_visible:
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            if self.button_accept.collidepoint(mouse_pos):
                self.accept_challenge()
            elif self.button_decline.collidepoint(mouse_pos):
                self.decline_challenge()
    
    def accept_challenge(self):
        """Accept the challenge"""
        try:
            success = self.network.send_message("ACCEPT", {
                "from": self.my_username,
                "to": self.challenger_name
            })
            
            if success:
                print(f"[Challenge] Accepted challenge from {self.challenger_name}")
                self._should_accept = True
            else:
                print("[Challenge] Failed to send ACCEPT")
                
        except Exception as e:
            print(f"[Challenge] Error accepting: {e}")
        
        # DON'T hide popup here - let main.py hide it after checking should_accept()
        # This prevents menu events from being processed in the same frame
        # self.is_visible = False
    
    def decline_challenge(self):
        """Decline the challenge"""
        try:
            success = self.network.send_message("DECLINE", {
                "from": self.my_username,
                "to": self.challenger_name
            })
            
            if success:
                print(f"[Challenge] Declined challenge from {self.challenger_name}")
                self._should_decline = True
            else:
                print("[Challenge] Failed to send DECLINE")
                
        except Exception as e:
            print(f"[Challenge] Error declining: {e}")
        
        # DON'T hide popup here - let main.py hide it after checking should_decline()
        # self.is_visible = False
    
    def draw(self):
        """Draw the challenge notification"""
        if not self.is_visible:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Popup background
        pygame.draw.rect(self.screen, (40, 40, 40), self.popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLOR_SUCCESS, self.popup_rect, 3, border_radius=15)
        
        # Title
        title_text = "Challenge Received!"
        title_surface = self.font_large.render(title_text, True, COLOR_SUCCESS)
        title_rect = title_surface.get_rect(center=(self.popup_rect.centerx, self.popup_rect.y + 60))
        self.screen.blit(title_surface, title_rect)
        
        # Challenger name
        challenger_text = f"{self.challenger_name} wants to play!"
        challenger_surface = self.font_medium.render(challenger_text, True, COLOR_TEXT)
        challenger_rect = challenger_surface.get_rect(center=(self.popup_rect.centerx, self.popup_rect.y + 130))
        self.screen.blit(challenger_surface, challenger_rect)
        
        # Question
        question_text = "Do you accept?"
        question_surface = self.font_small.render(question_text, True, COLOR_TEXT_SECONDARY)
        question_rect = question_surface.get_rect(center=(self.popup_rect.centerx, self.popup_rect.y + 180))
        self.screen.blit(question_surface, question_rect)
        
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(self.button_accept, "Accept", COLOR_SUCCESS, mouse_pos)
        self._draw_button(self.button_decline, "Decline", COLOR_ERROR, mouse_pos)
    
    def _draw_button(self, rect, text, base_color, mouse_pos):
        """Helper to draw a button with hover effect"""
        hover_color = tuple(min(c + 30, 255) for c in base_color)
        color = hover_color if rect.collidepoint(mouse_pos) else base_color
        
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        
        text_surface = self.font_medium.render(text, True, COLOR_BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def should_accept(self):
        """Check if challenge was accepted"""
        return self._should_accept
    
    def should_decline(self):
        """Check if challenge was declined"""
        return self._should_decline
    
    def reset(self):
        """Reset notification state"""
        self.is_visible = False
        self.challenger_name = ""
        self._should_accept = False
        self._should_decline = False
