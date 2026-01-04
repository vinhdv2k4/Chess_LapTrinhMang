"""
Profile View Modal for Chess Client
Shows detailed player information including ELO, stats, and match history
"""

import pygame
from config import *
from ui_components import Card, Badge, Button


class ProfileModal:
    """Modal window to display player profile information"""
    
    def __init__(self, screen, network_client, async_handler=None):
        self.screen = screen
        self.network = network_client
        self.async_handler = async_handler
        
        # Fonts
        self.font_title = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        
        # Modal state
        self.is_visible = False
        self.profile_data = None
        self.username = ""
        self.loading = False
        self.error_message = None
        
        # Modal dimensions
        self.modal_width = 600
        self.modal_height = 500
        self.modal_x = (SCREEN_WIDTH - self.modal_width) // 2
        self.modal_y = (SCREEN_HEIGHT - self.modal_height) // 2
        
        # Close button
        self.close_button = Button(
            self.modal_x + self.modal_width - 120,
            self.modal_y + self.modal_height - 70,
            100, 50,
            "Close",
            color=COLOR_SURFACE,
            hover_color=COLOR_SURFACE_LIGHT,
            font_size=FONT_SIZE_SMALL
        )
    
    def show(self, username, session_id):
        """Show profile for a specific user"""
        self.username = username
        self.is_visible = True
        self.profile_data = None
        self.error_message = None
        self.loading = True
        
        try:
            # Request profile from server
            self.network.send_message("GET_PROFILE", {
                "username": username,
                "sessionId": session_id
            })
            print(f"[ProfileModal] Requested profile for {username}")
            
        except Exception as e:
            self.error_message = f"Error: {str(e)}"
            self.loading = False
            print(f"[ProfileModal] Error sending request: {e}")
    
    def hide(self):
        """Hide the modal"""
        self.is_visible = False
        self.profile_data = None
        self.error_message = None
        self.loading = False
    
    def handle_event(self, event):
        """Handle events"""
        if not self.is_visible:
            return False
        
        # Handle close button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button.is_clicked(event.pos):
                self.hide()
                return True
        
        self.close_button.handle_event(event)
        # Consume clicks inside modal to prevent clicking through
        if event.type == pygame.MOUSEBUTTONDOWN:
            modal_rect = pygame.Rect(self.modal_x, self.modal_y, self.modal_width, self.modal_height)
            if modal_rect.collidepoint(event.pos):
                return True
                
        return False
    
    def update(self, dt=0.016):
        """Update animations and check for async responses"""
        if not self.is_visible:
            return
            
        self.close_button.update(dt)
        
        # Check for profile data if loading
        if self.loading and self.async_handler:
            update = self.async_handler.get_profile_update()
            if update:
                action = update.get("action")
                data = update.get("data", {})
                
                if action == "PROFILE_INFO":
                    # Check if this update matches the requested username
                    if data.get("username") == self.username:
                        self.profile_data = data
                        self.loading = False
                        print(f"[ProfileModal] Loaded profile for {self.username}")
                elif action == "PROFILE_ERROR":
                    self.error_message = data.get("reason", "Unknown error")
                    self.loading = False
                    print(f"[ProfileModal] Error loading profile: {self.error_message}")
        
    def draw(self):
        """Draw the profile modal"""
        if not self.is_visible:
            return
        
        # Update first (check for async data)
        self.update()
        
        # Draw overlay (semi-transparent background)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw modal background
        modal_rect = pygame.Rect(self.modal_x, self.modal_y, self.modal_width, self.modal_height)
        pygame.draw.rect(self.screen, COLOR_SURFACE, modal_rect, border_radius=BORDER_RADIUS_LARGE)
        
        # Draw border
        pygame.draw.rect(self.screen, COLOR_ACCENT_PRIMARY, modal_rect, 3, border_radius=BORDER_RADIUS_LARGE)
        
        if self.profile_data:
            self._draw_profile_content()
        elif self.error_message:
            self._draw_error()
        else:
            self._draw_loading()
        
        # Draw close button
        self.close_button.draw(self.screen)
    
    def _draw_profile_content(self):
        """Draw the actual profile content"""
        y_offset = self.modal_y + SPACING_LARGE
        
        # Title - Username
        username = self.profile_data.get("username", "Unknown")
        title_surface = self.font_title.render(username, True, COLOR_TEXT)
        title_rect = title_surface.get_rect(centerx=self.modal_x + self.modal_width // 2, y=y_offset)
        self.screen.blit(title_surface, title_rect)
        y_offset += 60
        
        # ELO Badge
        elo = self.profile_data.get("elo", 1200)
        elo_color = self._get_elo_color(elo)
        
        elo_text = f"ELO: {elo}"
        elo_surface = self.font_medium.render(elo_text, True, COLOR_TEXT)
        elo_rect = elo_surface.get_rect(centerx=self.modal_x + self.modal_width // 2, y=y_offset)
        
        # Draw ELO badge background
        badge_rect = pygame.Rect(
            elo_rect.x - SPACING_MEDIUM,
            elo_rect.y - SPACING_SMALL,
            elo_rect.width + SPACING_MEDIUM * 2,
            elo_rect.height + SPACING_SMALL * 2
        )
        pygame.draw.rect(self.screen, elo_color, badge_rect, border_radius=BORDER_RADIUS_MEDIUM)
        self.screen.blit(elo_surface, elo_rect)
        y_offset += 80
        
        # Stats section
        wins = self.profile_data.get("wins", 0)
        losses = self.profile_data.get("losses", 0)
        draws = self.profile_data.get("draws", 0)
        total_games = wins + losses + draws
        
        # Draw stats title
        stats_title = self.font_medium.render("Statistics", True, COLOR_TEXT_SECONDARY)
        stats_title_rect = stats_title.get_rect(centerx=self.modal_x + self.modal_width // 2, y=y_offset)
        self.screen.blit(stats_title, stats_title_rect)
        y_offset += 50
        
        # Draw stats in a grid
        stats_data = [
            ("Total Games", total_games, COLOR_INFO),
            ("Wins", wins, COLOR_SUCCESS),
            ("Losses", losses, COLOR_ERROR),
            ("Draws", draws, COLOR_WARNING)
        ]
        
        # Calculate win rate
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        
        # Draw stats cards
        card_width = 120
        card_height = 80
        spacing = 20
        total_width = card_width * 4 + spacing * 3
        start_x = self.modal_x + (self.modal_width - total_width) // 2
        
        for i, (label, value, color) in enumerate(stats_data):
            card_x = start_x + i * (card_width + spacing)
            card_rect = pygame.Rect(card_x, y_offset, card_width, card_height)
            
            # Draw card background
            pygame.draw.rect(self.screen, COLOR_BACKGROUND_SECONDARY, card_rect, border_radius=BORDER_RADIUS_MEDIUM)
            pygame.draw.rect(self.screen, color, card_rect, 2, border_radius=BORDER_RADIUS_MEDIUM)
            
            # Draw value
            value_surface = self.font_medium.render(str(value), True, color)
            value_rect = value_surface.get_rect(centerx=card_x + card_width // 2, y=y_offset + 15)
            self.screen.blit(value_surface, value_rect)
            
            # Draw label
            label_surface = self.font_small.render(label, True, COLOR_TEXT_SECONDARY)
            label_rect = label_surface.get_rect(centerx=card_x + card_width // 2, y=y_offset + 50)
            self.screen.blit(label_surface, label_rect)
        
        y_offset += 110
        
        # Win rate
        win_rate_text = f"Win Rate: {win_rate:.1f}%"
        win_rate_surface = self.font_small.render(win_rate_text, True, COLOR_TEXT_SECONDARY)
        win_rate_rect = win_rate_surface.get_rect(centerx=self.modal_x + self.modal_width // 2, y=y_offset)
        self.screen.blit(win_rate_surface, win_rate_rect)
        
        # Online status
        is_online = self.profile_data.get("online", False)
        status_text = "● Online" if is_online else "○ Offline"
        status_color = COLOR_SUCCESS if is_online else COLOR_TEXT_MUTED
        status_surface = self.font_small.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(centerx=self.modal_x + self.modal_width // 2, y=y_offset + 30)
        self.screen.blit(status_surface, status_rect)
    
    def _draw_loading(self):
        """Draw loading state"""
        loading_text = "Loading profile..."
        loading_surface = self.font_medium.render(loading_text, True, COLOR_TEXT_SECONDARY)
        loading_rect = loading_surface.get_rect(center=(self.modal_x + self.modal_width // 2, 
                                                         self.modal_y + self.modal_height // 2))
        self.screen.blit(loading_surface, loading_rect)
    
    def _draw_error(self):
        """Draw error state"""
        error_text = self.error_message or "Error loading profile"
        error_surface = self.font_medium.render(error_text, True, COLOR_ERROR)
        error_rect = error_surface.get_rect(center=(self.modal_x + self.modal_width // 2, 
                                                     self.modal_y + self.modal_height // 2))
        self.screen.blit(error_surface, error_rect)
        
        # Show hint
        hint_text = "Server may have returned invalid data"
        hint_surface = self.font_small.render(hint_text, True, COLOR_TEXT_MUTED)
        hint_rect = hint_surface.get_rect(center=(self.modal_x + self.modal_width // 2, 
                                                   self.modal_y + self.modal_height // 2 + 40))
        self.screen.blit(hint_surface, hint_rect)
    
    def _get_elo_color(self, elo):
        """Get color based on ELO rating"""
        if elo < 1000:
            return COLOR_ELO_BRONZE
        elif elo < 1200:
            return COLOR_ELO_SILVER
        elif elo < 1400:
            return COLOR_ELO_GOLD
        else:
            return COLOR_ELO_DIAMOND
