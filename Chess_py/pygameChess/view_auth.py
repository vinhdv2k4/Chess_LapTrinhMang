"""
Authentication View for Chess Client
Modern design with gradient background and smooth animations
"""

import pygame
from config import *
from network import NetworkClient
from ui_components import Button, InputField, Toast, draw_gradient_rect


class AuthView:
    """Modern authentication screen with login/register functionality"""
    
    def __init__(self, screen, network_client):
        self.screen = screen
        self.network = network_client
        
        # Fonts
        self.font_title = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        
        # UI state
        self.mode = "login"  # "login" or "register"
        self.authenticated = False
        self.session_data = None
        
        # Toast notifications
        self.toasts = []
        
        # Create UI components
        self._create_components()
        
        # Animation
        self.fade_in_progress = 0.0
        
    def _create_components(self):
        """Create UI components"""
        center_x = SCREEN_WIDTH // 2
        
        # Input fields with modern design
        input_width = 400
        input_height = 60
        input_x = center_x - input_width // 2
        
        self.input_username = InputField(
            input_x, 300, input_width, input_height,
            placeholder="Username",
            font_size=FONT_SIZE_MEDIUM
        )
        
        self.input_password = InputField(
            input_x, 410, input_width, input_height,
            placeholder="Password",
            font_size=FONT_SIZE_MEDIUM,
            password=True
        )
        
        # Buttons with modern design
        button_width = 180
        button_height = 60
        button_spacing = 20
        total_width = button_width * 2 + button_spacing
        button_start_x = center_x - total_width // 2
        
        self.button_submit = Button(
            button_start_x, 520,
            button_width, button_height,
            "Login",
            color=COLOR_ACCENT_PRIMARY,
            hover_color=COLOR_ACCENT_PRIMARY_HOVER,
            font_size=FONT_SIZE_MEDIUM
        )
        
        self.button_switch = Button(
            button_start_x + button_width + button_spacing, 520,
            button_width, button_height,
            "Register",
            color=COLOR_SURFACE,
            hover_color=COLOR_SURFACE_LIGHT,
            font_size=FONT_SIZE_MEDIUM
        )
    
    def handle_event(self, event):
        """Handle pygame events"""
        # Handle input fields
        if self.input_username.handle_event(event):
            self.input_password.is_focused = True
            self.input_username.is_focused = False
        
        if self.input_password.handle_event(event):
            self.submit()
        
        # Handle buttons
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_submit.is_clicked(event.pos):
                self.submit()
            elif self.button_switch.is_clicked(event.pos):
                self.switch_mode()
        
        # Pass events to buttons for hover effects
        self.button_submit.handle_event(event)
        self.button_switch.handle_event(event)
    
    def switch_mode(self):
        """Switch between login and register modes"""
        self.mode = "register" if self.mode == "login" else "login"
        self.button_submit.text = "Register" if self.mode == "register" else "Login"
        self.button_switch.text = "Login" if self.mode == "register" else "Register"
        self.input_username.clear()
        self.input_password.clear()
    
    def submit(self):
        """Submit login or registration"""
        username = self.input_username.get_text()
        password = self.input_password.get_text()
        
        if not username or not password:
            self.show_toast("Please enter username and password", "error")
            return
        
        # Check if network is connected
        if not self.network.is_connected():
            if not self.network.connect():
                self.show_toast("Cannot connect to server", "error")
                return
        
        # Send request
        action = "LOGIN" if self.mode == "login" else "REGISTER"
        data = {
            "username": username,
            "password": password
        }
        
        if self.network.send_message(action, data):
            self.show_toast("Waiting for response...", "info")
            # Receive response
            response = self.network.receive_message(timeout=5.0)
            
            if response:
                self.handle_response(response)
            else:
                self.show_toast("No response from server", "error")
        else:
            self.show_toast("Failed to send request", "error")
    
    def handle_response(self, response):
        """Handle server response"""
        action = response.get("action", "")
        data = response.get("data", {})
        
        if action == "LOGIN_SUCCESS":
            self.show_toast("Login successful!", "success")
            self.authenticated = True
            self.session_data = data
        elif action == "LOGIN_FAIL":
            reason = data.get("reason", "Unknown error")
            self.show_toast(f"Login failed: {reason}", "error")
        elif action == "REGISTER_SUCCESS":
            message = data.get("message", "Account created")
            self.show_toast(message, "success")
            # Switch to login mode after successful registration
            self.mode = "login"
            self.button_submit.text = "Login"
            self.button_switch.text = "Register"
            self.input_password.clear()
        elif action == "REGISTER_FAIL":
            reason = data.get("reason", "Unknown error")
            self.show_toast(f"Registration failed: {reason}", "error")
        else:
            self.show_toast(f"Unknown response: {action}", "error")
    
    def show_toast(self, message, type="info"):
        """Show a toast notification"""
        toast = Toast(message, type, duration=3.0)
        self.toasts.append(toast)
    
    def update(self, dt=0.016):
        """Update animations"""
        # Fade in animation
        if self.fade_in_progress < 1.0:
            self.fade_in_progress += dt * 2
            self.fade_in_progress = min(1.0, self.fade_in_progress)
        
        # Update components
        self.input_username.update(dt)
        self.input_password.update(dt)
        self.button_submit.update(dt)
        self.button_switch.update(dt)
        
        # Update toasts
        self.toasts = [toast for toast in self.toasts if toast.update(dt)]
    
    def draw(self):
        """Draw the authentication screen"""
        # Update animations first
        self.update()
        
        # Draw gradient background
        bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_gradient_rect(self.screen, bg_rect, 
                          COLOR_BACKGROUND_PRIMARY, 
                          COLOR_BACKGROUND_SECONDARY,
                          vertical=True)
        
        # Draw decorative elements (chess pieces silhouettes in corners)
        self._draw_decorations()
        
        # Draw title with fade-in
        title_text = "Chess Login" if self.mode == "login" else "Chess Register"
        title_surface = self.font_title.render(title_text, True, COLOR_TEXT)
        title_surface.set_alpha(int(255 * self.fade_in_progress))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle = "Sign in to play" if self.mode == "login" else "Create your account"
        subtitle_surface = self.font_small.render(subtitle, True, COLOR_TEXT_SECONDARY)
        subtitle_surface.set_alpha(int(255 * self.fade_in_progress))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 210))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw input field labels
        label_font = self.font_small
        
        username_label = label_font.render("USERNAME", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(username_label, (self.input_username.rect.x, 
                                         self.input_username.rect.y - 25))
        
        password_label = label_font.render("PASSWORD", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(password_label, (self.input_password.rect.x, 
                                         self.input_password.rect.y - 25))
        
        # Draw input fields
        self.input_username.draw(self.screen)
        self.input_password.draw(self.screen)
        
        # Draw buttons
        self.button_submit.draw(self.screen)
        self.button_switch.draw(self.screen)
        
        # Draw instructions
        instructions = "Press TAB to switch fields • ENTER to submit"
        inst_surface = self.font_small.render(instructions, True, COLOR_TEXT_MUTED)
        inst_rect = inst_surface.get_rect(center=(SCREEN_WIDTH // 2, 620))
        self.screen.blit(inst_surface, inst_rect)
        
        # Draw connection status
        status_text = "● Connected" if self.network.is_connected() else "○ Disconnected"
        status_color = COLOR_SUCCESS if self.network.is_connected() else COLOR_ERROR
        status_surface = self.font_small.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        self.screen.blit(status_surface, status_rect)
        
        # Draw toasts
        for toast in self.toasts:
            toast.draw(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def _draw_decorations(self):
        """Draw decorative elements"""
        # Draw subtle chess piece silhouettes in corners
        decoration_color = (*COLOR_SURFACE, 50)  # Semi-transparent
        
        # Top-left corner - King silhouette
        pygame.draw.circle(self.screen, decoration_color, (100, 100), 80)
        
        # Top-right corner - Queen silhouette  
        pygame.draw.circle(self.screen, decoration_color, (SCREEN_WIDTH - 100, 100), 80)
        
        # Bottom corners - smaller pieces
        pygame.draw.circle(self.screen, decoration_color, (100, SCREEN_HEIGHT - 100), 60)
        pygame.draw.circle(self.screen, decoration_color, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 60)
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.authenticated
    
    def get_session_data(self):
        """Get session data after successful login"""
        return self.session_data

