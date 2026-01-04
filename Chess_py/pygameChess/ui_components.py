"""
UI Components for Chess Client
Reusable UI elements with modern design and animations
"""

import pygame
import math
from config import *


class Button:
    """Modern button with hover effects and animations"""
    
    def __init__(self, x, y, width, height, text, 
                 color=None, hover_color=None, text_color=None,
                 border_radius=BORDER_RADIUS_MEDIUM, font_size=FONT_SIZE_MEDIUM):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color or COLOR_BUTTON_PRIMARY
        self.hover_color = hover_color or COLOR_BUTTON_PRIMARY_HOVER
        self.text_color = text_color or COLOR_BUTTON_TEXT
        self.border_radius = border_radius
        self.font = pygame.font.Font(FONT_NAME, font_size)
        
        self.is_hovered = False
        self.is_pressed = False
        self.hover_progress = 0.0  # 0.0 to 1.0 for smooth transition
        
    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_pressed = False
        return False
    
    def update(self, dt=0.016):
        """Update animation state"""
        target = 1.0 if self.is_hovered else 0.0
        speed = 5.0  # Transition speed
        self.hover_progress += (target - self.hover_progress) * speed * dt
        self.hover_progress = max(0.0, min(1.0, self.hover_progress))
    
    def draw(self, surface):
        """Draw the button"""
        # Interpolate color based on hover progress
        current_color = self._lerp_color(self.color, self.hover_color, self.hover_progress)
        
        # Draw shadow for depth
        shadow_rect = self.rect.copy()
        shadow_rect.y += 2
        pygame.draw.rect(surface, (0, 0, 0, 50), shadow_rect, border_radius=self.border_radius)
        
        # Draw button
        pygame.draw.rect(surface, current_color, self.rect, border_radius=self.border_radius)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def _lerp_color(self, color1, color2, t):
        """Linear interpolation between two colors"""
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))
    
    def is_clicked(self, pos):
        """Check if button was clicked at position"""
        return self.rect.collidepoint(pos)


class Card:
    """Modern card component with shadow and hover effect"""
    
    def __init__(self, x, y, width, height, 
                 bg_color=None, border_radius=BORDER_RADIUS_LARGE):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color or COLOR_SURFACE
        self.border_radius = border_radius
        self.hover_offset = 0
        self.is_hovered = False
    
    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
    
    def update(self, dt=0.016):
        """Update hover animation"""
        target = HOVER_LIFT if self.is_hovered else 0
        speed = 10.0
        self.hover_offset += (target - self.hover_offset) * speed * dt
    
    def draw(self, surface):
        """Draw the card"""
        # Adjust rect for hover effect
        draw_rect = self.rect.copy()
        draw_rect.y -= int(self.hover_offset)
        
        # Draw shadow
        shadow_rect = draw_rect.copy()
        shadow_rect.y += CARD_SHADOW_OFFSET + int(self.hover_offset)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, COLOR_SHADOW_MEDIUM, 
                        shadow_surface.get_rect(), border_radius=self.border_radius)
        surface.blit(shadow_surface, shadow_rect)
        
        # Draw card
        pygame.draw.rect(surface, self.bg_color, draw_rect, border_radius=self.border_radius)
        
        return draw_rect  # Return adjusted rect for content positioning


class InputField:
    """Modern input field with focus effects"""
    
    def __init__(self, x, y, width, height, placeholder="",
                 font_size=FONT_SIZE_MEDIUM, password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.text = ""
        self.font = pygame.font.Font(FONT_NAME, font_size)
        self.password = password
        self.is_focused = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.focus_progress = 0.0
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.is_focused = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True  # Submit signal
            elif event.unicode.isprintable():
                self.text += event.unicode
        return False
    
    def update(self, dt=0.016):
        """Update animations"""
        # Focus animation
        target = 1.0 if self.is_focused else 0.0
        self.focus_progress += (target - self.focus_progress) * 5.0 * dt
        
        # Cursor blink
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, surface):
        """Draw the input field"""
        # Interpolate border color based on focus
        border_color = self._lerp_color(COLOR_INPUT_BORDER, 
                                       COLOR_INPUT_BORDER_FOCUS, 
                                       self.focus_progress)
        
        # Draw background
        pygame.draw.rect(surface, COLOR_INPUT_BG, self.rect, border_radius=BORDER_RADIUS_MEDIUM)
        
        # Draw border with glow effect when focused
        border_width = 2 if not self.is_focused else 3
        pygame.draw.rect(surface, border_color, self.rect, border_width, border_radius=BORDER_RADIUS_MEDIUM)
        
        # Draw text or placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = COLOR_INPUT_TEXT if self.text else COLOR_INPUT_PLACEHOLDER
        
        if self.password and self.text:
            display_text = "•" * len(self.text)
        
        text_surface = self.font.render(display_text, True, text_color)
        text_rect = text_surface.get_rect(midleft=(self.rect.x + SPACING_MEDIUM, self.rect.centery))
        surface.blit(text_surface, text_rect)
        
        # Draw cursor
        if self.is_focused and self.cursor_visible and self.text:
            cursor_x = text_rect.right + 2
            cursor_y1 = self.rect.centery - 12
            cursor_y2 = self.rect.centery + 12
            pygame.draw.line(surface, COLOR_INPUT_TEXT, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
    
    def _lerp_color(self, color1, color2, t):
        """Linear interpolation between two colors"""
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))
    
    def get_text(self):
        """Get current text"""
        return self.text
    
    def clear(self):
        """Clear the input"""
        self.text = ""


class Badge:
    """Badge component for ELO, status, etc."""
    
    def __init__(self, x, y, text, color=None, font_size=FONT_SIZE_SMALL):
        self.x = x
        self.y = y
        self.text = text
        self.color = color or COLOR_ACCENT_PRIMARY
        self.font = pygame.font.Font(FONT_NAME, font_size)
        self.padding = SPACING_SMALL
    
    def draw(self, surface):
        """Draw the badge"""
        text_surface = self.font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surface.get_rect()
        
        # Create badge rect with padding
        badge_rect = pygame.Rect(
            self.x, self.y,
            text_rect.width + self.padding * 2,
            text_rect.height + self.padding
        )
        
        # Draw badge background
        pygame.draw.rect(surface, self.color, badge_rect, border_radius=BORDER_RADIUS_FULL)
        
        # Draw text
        text_pos = (badge_rect.x + self.padding, badge_rect.y + self.padding // 2)
        surface.blit(text_surface, text_pos)
        
        return badge_rect


class StatusIndicator:
    """Animated status indicator (online/offline/in-match)"""
    
    def __init__(self, x, y, status="offline", size=12):
        self.x = x
        self.y = y
        self.status = status
        self.size = size
        self.pulse_progress = 0
        
        self.color_map = {
            "online": COLOR_STATUS_ONLINE,
            "offline": COLOR_STATUS_OFFLINE,
            "in_match": COLOR_STATUS_IN_MATCH
        }
    
    def update(self, dt=0.016):
        """Update pulse animation"""
        if self.status == "online":
            self.pulse_progress += dt * 2
            if self.pulse_progress > 1.0:
                self.pulse_progress = 0
    
    def draw(self, surface):
        """Draw the status indicator"""
        color = self.color_map.get(self.status, COLOR_STATUS_OFFLINE)
        
        # Draw outer pulse ring for online status
        if self.status == "online":
            pulse_radius = int(self.size + self.pulse_progress * 5)
            pulse_alpha = int(255 * (1 - self.pulse_progress))
            pulse_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surface, (*color, pulse_alpha), 
                             (pulse_radius, pulse_radius), pulse_radius)
            surface.blit(pulse_surface, (self.x - pulse_radius, self.y - pulse_radius))
        
        # Draw main circle
        pygame.draw.circle(surface, color, (self.x, self.y), self.size)
        pygame.draw.circle(surface, COLOR_TEXT, (self.x, self.y), self.size, 2)


class Toast:
    """Toast notification component"""
    
    def __init__(self, message, type="info", duration=3.0):
        self.message = message
        self.type = type
        self.duration = duration
        self.elapsed = 0
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        
        self.color_map = {
            "success": COLOR_SUCCESS,
            "error": COLOR_ERROR,
            "warning": COLOR_WARNING,
            "info": COLOR_INFO
        }
        
        self.bg_color = self.color_map.get(type, COLOR_INFO)
        self.alpha = 0
        self.y_offset = 50
    
    def update(self, dt=0.016):
        """Update animation and lifetime"""
        self.elapsed += dt
        
        # Fade in/out animation
        if self.elapsed < 0.3:
            self.alpha = int(255 * (self.elapsed / 0.3))
            self.y_offset = 50 * (1 - self.elapsed / 0.3)
        elif self.elapsed > self.duration - 0.3:
            remaining = self.duration - self.elapsed
            self.alpha = int(255 * (remaining / 0.3))
        else:
            self.alpha = 255
            self.y_offset = 0
        
        return self.elapsed < self.duration
    
    def draw(self, surface):
        """Draw the toast"""
        text_surface = self.font.render(self.message, True, COLOR_TEXT)
        text_rect = text_surface.get_rect()
        
        # Create toast rect
        toast_width = text_rect.width + SPACING_LARGE * 2
        toast_height = text_rect.height + SPACING_MEDIUM * 2
        toast_x = (SCREEN_WIDTH - toast_width) // 2
        toast_y = 50 + int(self.y_offset)
        
        toast_rect = pygame.Rect(toast_x, toast_y, toast_width, toast_height)
        
        # Create surface with alpha
        toast_surface = pygame.Surface((toast_width, toast_height), pygame.SRCALPHA)
        pygame.draw.rect(toast_surface, (*self.bg_color, self.alpha), 
                        toast_surface.get_rect(), border_radius=BORDER_RADIUS_MEDIUM)
        
        # Draw text on toast surface
        text_surface.set_alpha(self.alpha)
        text_pos = (SPACING_LARGE, SPACING_MEDIUM)
        toast_surface.blit(text_surface, text_pos)
        
        # Blit to main surface
        surface.blit(toast_surface, toast_rect)


class ProgressBar:
    """Animated progress bar"""
    
    def __init__(self, x, y, width, height, progress=0.0, 
                 bg_color=None, fill_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.progress = progress  # 0.0 to 1.0
        self.bg_color = bg_color or COLOR_SURFACE
        self.fill_color = fill_color or COLOR_ACCENT_PRIMARY
        self.animated_progress = 0.0
    
    def update(self, dt=0.016):
        """Smooth progress animation"""
        speed = 3.0
        self.animated_progress += (self.progress - self.animated_progress) * speed * dt
    
    def set_progress(self, progress):
        """Set progress value (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
    
    def draw(self, surface):
        """Draw the progress bar"""
        # Draw background
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=BORDER_RADIUS_FULL)
        
        # Draw fill
        fill_width = int(self.rect.width * self.animated_progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(surface, self.fill_color, fill_rect, border_radius=BORDER_RADIUS_FULL)


def draw_gradient_rect(surface, rect, color_start, color_end, vertical=True):
    """Draw a rectangle with gradient fill"""
    if vertical:
        for y in range(rect.height):
            progress = y / rect.height
            color = tuple(int(c1 + (c2 - c1) * progress) 
                         for c1, c2 in zip(color_start, color_end))
            pygame.draw.line(surface, color, 
                           (rect.x, rect.y + y), 
                           (rect.x + rect.width, rect.y + y))
    else:
        for x in range(rect.width):
            progress = x / rect.width
            color = tuple(int(c1 + (c2 - c1) * progress) 
                         for c1, c2 in zip(color_start, color_end))
            pygame.draw.line(surface, color, 
                           (rect.x + x, rect.y), 
                           (rect.x + x, rect.y + rect.height))
