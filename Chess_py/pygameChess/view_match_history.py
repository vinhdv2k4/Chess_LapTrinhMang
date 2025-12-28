"""
Match History View for Chess Client
Displays list of past matches with details
"""

import pygame
from config import *
from ui_components import Button, Card
import time


class MatchHistoryView:
    """View to display match history"""
    
    def __init__(self, screen, network_client):
        self.screen = screen
        self.network = network_client
        
        # Fonts
        self.font_title = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        
        # State
        self.session_data = None
        self.matches = []
        self._should_go_back = False
        
        # Back button
        self.back_button = Button(
            50, SCREEN_HEIGHT - 100,
            150, 60,
            "← Back",
            color=COLOR_SURFACE,
            hover_color=COLOR_SURFACE_LIGHT,
            font_size=FONT_SIZE_MEDIUM
        )
        
        # Scroll offset
        self.scroll_offset = 0
        self.max_scroll = 0
        self.card_rects = [] # Store (rect, match_id)
        self.selected_match_id = None
    
    def set_session_data(self, session_data):
        """Set session data"""
        self.session_data = session_data
    
    def load_match_history(self):
        """Load match history from server"""
        if not self.session_data:
            return
        
        username = self.session_data.get("username")
        session_id = self.session_data.get("sessionId")
        
        # Request match history
        self.network.send_message("GET_MATCH_HISTORY", {
            "username": username,
            "sessionId": session_id
        })
        
        # Receive response
        response = self.network.receive_message(timeout=2.0)
        if response and response.get("action") == "MATCH_HISTORY":
            data = response.get("data", {})
            self.matches = data.get("matches", [])
            print(f"[MatchHistory] Loaded {len(self.matches)} matches")
        else:
            self.matches = []
            print("[MatchHistory] Failed to load match history")
    
    def get_selected_match_id(self):
        """Get selected match ID and clear it"""
        mid = self.selected_match_id
        self.selected_match_id = None
        return mid

    def handle_event(self, event):
        """Handle events"""
        # Handle back button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.is_clicked(event.pos):
                self._should_go_back = True
            
            # Check match cards
            for rect, match_id in self.card_rects:
                if rect.collidepoint(event.pos):
                    print(f"[MatchHistory] Clicked match {match_id}")
                    self.selected_match_id = match_id
                    break
        
        # Handle scroll
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 30
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
        
        self.back_button.handle_event(event)

    def update(self, dt=0.016):
        """Update animations"""
        self.back_button.update(dt)
    
    def draw(self):
        """Draw the match history view"""
        self.update()
        
        # Background
        self.screen.fill(COLOR_BACKGROUND_PRIMARY)
        
        # Title
        title_text = "Match History"
        title_surface = self.font_title.render(title_text, True, COLOR_TEXT)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surface, title_rect)
        
        # Draw matches
        if len(self.matches) == 0:
            self._draw_empty_state()
        else:
            self._draw_matches()
        
        # Draw back button
        self.back_button.draw(self.screen)
    
    def _draw_empty_state(self):
        """Draw empty state when no matches"""
        empty_text = "No matches played yet"
        empty_surface = self.font_medium.render(empty_text, True, COLOR_TEXT_SECONDARY)
        empty_rect = empty_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(empty_surface, empty_rect)
        
        hint_text = "Play some games to see your match history!"
        hint_surface = self.font_small.render(hint_text, True, COLOR_TEXT_MUTED)
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(hint_surface, hint_rect)
    
    def _draw_matches(self):
        """Draw list of matches"""
        y_start = 150
        match_height = 120
        match_spacing = 20
        
        # Calculate max scroll
        total_height = len(self.matches) * (match_height + match_spacing)
        visible_height = SCREEN_HEIGHT - y_start - 120
        self.max_scroll = max(0, total_height - visible_height)
        
        # Create clipping rect for scrollable area
        clip_rect = pygame.Rect(0, y_start, SCREEN_WIDTH, visible_height)
        self.screen.set_clip(clip_rect)
        
        self.card_rects = [] # Clear previous rects

        # Draw each match
        for i, match in enumerate(self.matches):
            y_pos = y_start + i * (match_height + match_spacing) - self.scroll_offset
            
            # Skip if not visible
            if y_pos + match_height < y_start or y_pos > y_start + visible_height:
                continue
            
            self._draw_match_card(match, 100, y_pos, SCREEN_WIDTH - 200, match_height)
        
        # Remove clipping
        self.screen.set_clip(None)
        
        # Draw scroll indicator if needed
        if self.max_scroll > 0:
            self._draw_scroll_indicator()
    
    def _draw_match_card(self, match, x, y, width, height):
        """Draw a single match card"""
        # Card background
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLOR_SURFACE, card_rect, border_radius=BORDER_RADIUS_MEDIUM)

        # Store rect for click detection
        match_id = match.get("matchId")
        if match_id:
            self.card_rects.append((card_rect, match_id))
        
        # Get match data
        match_id = match.get("matchId", "Unknown")
        white_player = match.get("white", "?")
        black_player = match.get("black", "?")
        winner = match.get("winner", "DRAW")
        timestamp = match.get("timestamp", 0)
        move_count = match.get("moveCount", 0)
        
        # Determine if current user won
        my_username = self.session_data.get("username") if self.session_data else ""
        
        if winner == my_username:
            result_text = "Victory"
            result_color = COLOR_SUCCESS
            border_color = COLOR_SUCCESS
        elif winner == "DRAW":
            result_text = "Draw"
            result_color = COLOR_WARNING
            border_color = COLOR_WARNING
        elif winner == "ABORT":
            result_text = "Aborted"
            result_color = COLOR_TEXT_MUTED
            border_color = COLOR_TEXT_MUTED
        else:
            result_text = "Defeat"
            result_color = COLOR_ERROR
            border_color = COLOR_ERROR
        
        # Draw colored border
        pygame.draw.rect(self.screen, border_color, card_rect, 3, border_radius=BORDER_RADIUS_MEDIUM)
        
        # Draw content
        content_x = x + SPACING_LARGE
        content_y = y + SPACING_MEDIUM
        
        # Players
        players_text = f"{white_player} (White) vs {black_player} (Black)"
        players_surface = self.font_medium.render(players_text, True, COLOR_TEXT)
        self.screen.blit(players_surface, (content_x, content_y))
        
        # Result
        result_surface = self.font_large.render(result_text, True, result_color)
        result_rect = result_surface.get_rect(right=x + width - SPACING_LARGE, centery=y + height // 2)
        self.screen.blit(result_surface, result_rect)
        
        # Match details
        details_y = content_y + 40
        
        # Date
        date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))
        date_surface = self.font_small.render(f"📅 {date_str}", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(date_surface, (content_x, details_y))
        
        # Move count
        moves_text = f"Moves: {move_count}"
        moves_surface = self.font_small.render(moves_text, True, COLOR_TEXT_SECONDARY)
        self.screen.blit(moves_surface, (content_x, details_y + 25))
        
        # Match ID (shortened)
        match_id_short = match_id[:8] + "..." if len(match_id) > 8 else match_id
        id_surface = self.font_small.render(f"ID: {match_id_short}", True, COLOR_TEXT_MUTED)
        self.screen.blit(id_surface, (content_x + 250, details_y + 25))
    
    def _draw_scroll_indicator(self):
        """Draw scroll indicator"""
        # Scroll bar
        bar_height = 200
        bar_width = 8
        bar_x = SCREEN_WIDTH - 30
        bar_y = 200
        
        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, COLOR_SURFACE, bg_rect, border_radius=BORDER_RADIUS_FULL)
        
        # Thumb
        thumb_height = max(30, bar_height * (SCREEN_HEIGHT - 270) / (self.max_scroll + SCREEN_HEIGHT - 270))
        thumb_y = bar_y + (bar_height - thumb_height) * (self.scroll_offset / self.max_scroll) if self.max_scroll > 0 else bar_y
        thumb_rect = pygame.Rect(bar_x, thumb_y, bar_width, thumb_height)
        pygame.draw.rect(self.screen, COLOR_ACCENT_PRIMARY, thumb_rect, border_radius=BORDER_RADIUS_FULL)
    
    def should_go_back(self):
        """Check if should go back"""
        return self._should_go_back
    
    def reset(self):
        """Reset state"""
        self._should_go_back = False
        self.scroll_offset = 0
