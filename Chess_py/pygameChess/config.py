# Configuration file for Chess Python UI
# Modern Dark Theme with Vibrant Accents

# ============================================================================
# NETWORK CONFIGURATION
# ============================================================================
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8888

# ============================================================================
# MODERN COLOR PALETTE - Dark Theme
# ============================================================================

# Background Colors (Dark Slate)
COLOR_BACKGROUND_PRIMARY = (15, 23, 42)      # Slate-900 - Main background
COLOR_BACKGROUND_SECONDARY = (30, 41, 59)    # Slate-800 - Secondary surfaces
COLOR_SURFACE = (51, 65, 85)                 # Slate-700 - Cards, panels
COLOR_SURFACE_LIGHT = (71, 85, 105)          # Slate-600 - Hover states

# Text Colors
COLOR_TEXT = (248, 250, 252)                 # Slate-50 - Primary text
COLOR_TEXT_SECONDARY = (203, 213, 225)       # Slate-300 - Secondary text
COLOR_TEXT_MUTED = (148, 163, 184)           # Slate-400 - Muted text
COLOR_TEXT_DISABLED = (100, 116, 139)        # Slate-500 - Disabled text

# Accent Colors (Vibrant)
COLOR_ACCENT_PRIMARY = (59, 130, 246)        # Blue-500 - Primary actions
COLOR_ACCENT_PRIMARY_HOVER = (96, 165, 250)  # Blue-400 - Hover state
COLOR_ACCENT_PRIMARY_DARK = (37, 99, 235)    # Blue-600 - Active state

COLOR_ACCENT_SECONDARY = (168, 85, 247)      # Purple-500 - Secondary actions
COLOR_ACCENT_SECONDARY_HOVER = (192, 132, 252) # Purple-400
COLOR_ACCENT_SECONDARY_DARK = (147, 51, 234)   # Purple-600

# Status Colors
COLOR_SUCCESS = (34, 197, 94)                # Green-500 - Success states
COLOR_SUCCESS_LIGHT = (74, 222, 128)         # Green-400
COLOR_SUCCESS_DARK = (22, 163, 74)           # Green-600

COLOR_WARNING = (251, 191, 36)               # Amber-400 - Warning states
COLOR_WARNING_LIGHT = (252, 211, 77)         # Amber-300
COLOR_WARNING_DARK = (245, 158, 11)          # Amber-500

COLOR_ERROR = (239, 68, 68)                  # Red-500 - Error states
COLOR_ERROR_LIGHT = (248, 113, 113)          # Red-400
COLOR_ERROR_DARK = (220, 38, 38)             # Red-600

COLOR_INFO = (14, 165, 233)                  # Sky-500 - Info states
COLOR_INFO_LIGHT = (56, 189, 248)            # Sky-400

# Button Colors
COLOR_BUTTON_PRIMARY = COLOR_ACCENT_PRIMARY
COLOR_BUTTON_PRIMARY_HOVER = COLOR_ACCENT_PRIMARY_HOVER
COLOR_BUTTON_TEXT = COLOR_TEXT

COLOR_BUTTON_SECONDARY = COLOR_SURFACE
COLOR_BUTTON_SECONDARY_HOVER = COLOR_SURFACE_LIGHT

COLOR_BUTTON_DANGER = COLOR_ERROR
COLOR_BUTTON_DANGER_HOVER = COLOR_ERROR_LIGHT

# Input Colors
COLOR_INPUT_BG = (30, 41, 59)                # Slate-800
COLOR_INPUT_BORDER = (71, 85, 105)           # Slate-600
COLOR_INPUT_BORDER_FOCUS = COLOR_ACCENT_PRIMARY
COLOR_INPUT_TEXT = COLOR_TEXT
COLOR_INPUT_PLACEHOLDER = COLOR_TEXT_MUTED

# Chess Board Colors (Modern Warm Tones)
COLOR_BOARD_LIGHT = (240, 217, 181)          # Cream - Light squares
COLOR_BOARD_DARK = (181, 136, 99)            # Brown - Dark squares
COLOR_BOARD_HIGHLIGHT = (186, 202, 68)       # Yellow-green - Selected piece
COLOR_BOARD_VALID_MOVE = (130, 151, 105)     # Olive - Valid move indicator
COLOR_BOARD_LAST_MOVE = (205, 210, 118, 128) # Semi-transparent yellow - Last move
COLOR_BOARD_CHECK = (239, 68, 68)            # Red - King in check

# Glassmorphism Effect Colors (with alpha)
COLOR_GLASS_BG = (51, 65, 85, 180)           # Semi-transparent surface
COLOR_GLASS_BORDER = (148, 163, 184, 100)    # Semi-transparent border

# Shadow Colors (for depth)
COLOR_SHADOW_LIGHT = (0, 0, 0, 50)           # Light shadow
COLOR_SHADOW_MEDIUM = (0, 0, 0, 100)         # Medium shadow
COLOR_SHADOW_HEAVY = (0, 0, 0, 150)          # Heavy shadow

# Gradient Colors (for backgrounds)
GRADIENT_PRIMARY_START = (59, 130, 246)      # Blue
GRADIENT_PRIMARY_END = (147, 51, 234)        # Purple
GRADIENT_SECONDARY_START = (16, 185, 129)    # Emerald
GRADIENT_SECONDARY_END = (59, 130, 246)      # Blue

# ELO Badge Colors
COLOR_ELO_BRONZE = (205, 127, 50)            # Bronze (<1000)
COLOR_ELO_SILVER = (192, 192, 192)           # Silver (1000-1200)
COLOR_ELO_GOLD = (255, 215, 0)               # Gold (1200-1400)
COLOR_ELO_DIAMOND = (185, 242, 255)          # Diamond (1400+)

# Status Indicator Colors
COLOR_STATUS_ONLINE = COLOR_SUCCESS          # Green - Online
COLOR_STATUS_OFFLINE = (100, 116, 139)       # Gray - Offline
COLOR_STATUS_IN_MATCH = COLOR_WARNING        # Amber - In match

# ============================================================================
# FONT CONFIGURATION
# ============================================================================
FONT_NAME = 'freesansbold.ttf'

# Font Sizes (Improved Scale)
FONT_SIZE_TINY = 16
FONT_SIZE_SMALL = 20
FONT_SIZE_MEDIUM = 28
FONT_SIZE_LARGE = 40
FONT_SIZE_XLARGE = 50
FONT_SIZE_TITLE = 64
FONT_SIZE_DISPLAY = 80

# ============================================================================
# SCREEN CONFIGURATION
# ============================================================================
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 900

# ============================================================================
# UI CONSTANTS
# ============================================================================

# Border Radius (for rounded corners)
BORDER_RADIUS_SMALL = 5
BORDER_RADIUS_MEDIUM = 10
BORDER_RADIUS_LARGE = 15
BORDER_RADIUS_XLARGE = 20
BORDER_RADIUS_FULL = 999  # For circles

# Spacing (for consistent padding/margins)
SPACING_TINY = 4
SPACING_SMALL = 8
SPACING_MEDIUM = 16
SPACING_LARGE = 24
SPACING_XLARGE = 32
SPACING_XXLARGE = 48

# Animation Durations (in milliseconds)
ANIMATION_FAST = 150
ANIMATION_NORMAL = 300
ANIMATION_SLOW = 500

# Z-Index Layers (for rendering order)
Z_INDEX_BACKGROUND = 0
Z_INDEX_BOARD = 10
Z_INDEX_PIECES = 20
Z_INDEX_UI = 30
Z_INDEX_MODAL = 40
Z_INDEX_TOOLTIP = 50

# Button Sizes
BUTTON_HEIGHT_SMALL = 40
BUTTON_HEIGHT_MEDIUM = 50
BUTTON_HEIGHT_LARGE = 60

# Card Sizes
CARD_PADDING = SPACING_LARGE
CARD_SHADOW_OFFSET = 4

# Avatar Sizes
AVATAR_SIZE_SMALL = 32
AVATAR_SIZE_MEDIUM = 48
AVATAR_SIZE_LARGE = 64

# ============================================================================
# GAME BOARD CONFIGURATION
# ============================================================================
BOARD_SIZE = 800  # 8x8 board
SQUARE_SIZE = BOARD_SIZE // 8  # 100px per square
BOARD_OFFSET_X = 0
BOARD_OFFSET_Y = 0

# Piece Animation
PIECE_MOVE_DURATION = 300  # ms
PIECE_CAPTURE_DURATION = 200  # ms

# ============================================================================
# EFFECTS CONFIGURATION
# ============================================================================

# Glow Effect
GLOW_RADIUS = 20
GLOW_INTENSITY = 0.5

# Hover Effect
HOVER_SCALE = 1.05
HOVER_LIFT = 5  # pixels

# Ripple Effect
RIPPLE_DURATION = 600  # ms
RIPPLE_MAX_RADIUS = 100
