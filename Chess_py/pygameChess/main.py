# two player chess in python with Pygame!
# part one, set up variables images and game loop

import pygame
from config import *
from network import NetworkClient
from view_auth import AuthView
from view_menu import MenuView
from view_players import OnlinePlayersView
from view_profile import ProfileModal
from view_match_history import MatchHistoryView
from async_handler import AsyncMessageHandler
from view_challenge import ChallengeNotification

pygame.init()
WIDTH = SCREEN_WIDTH
HEIGHT = SCREEN_HEIGHT
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Two-Player Pygame Chess!')
font = pygame.font.Font('freesansbold.ttf', 20)
medium_font = pygame.font.Font('freesansbold.ttf', 40)
big_font = pygame.font.Font('freesansbold.ttf', 50)
timer = pygame.time.Clock()
fps = 60

# Game states
STATE_AUTH = 0
STATE_MENU = 1
STATE_PLAYERS = 2
STATE_GAME = 3
STATE_MATCH_HISTORY = 4
STATE_REPLAY = 5
STATE_FIND_MATCH = 6
STATE_FIND_MATCH = 6
current_state = STATE_AUTH

# Network and session
network_client = NetworkClient()
auth_view = None
menu_view = None
players_view = None
profile_modal = None
match_history_view = None
async_handler = None
challenge_notification = None
session_data = None

# Online multiplayer game state
online_match_id = None
online_my_role = None  # 'white' or 'black'
online_opponent_name = None
online_is_my_turn = False
online_game_active = False
waiting_for_game_start = False  # Flag to block menu actions after accepting challenge

# Offer state (for Draw)
pending_offer = None  # 'draw' or 'rematch'
offer_sender = None

# Timers
white_time = 600 # 10 minutes in seconds
black_time = 600
last_timer_update = 0

# Matchmaking
is_finding_match = False
matchmaking_text = "Searching for opponent..."

# game variables and images
white_pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
# White pieces at bottom (rank 1, 2) -> y=7, y=6 in pygame coordinates
white_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                   (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
black_pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
# Black pieces at top (rank 8, 7) -> y=0, y=1 in pygame coordinates
black_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                   (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
captured_pieces_white = []
captured_pieces_black = []
# 0 - whites turn no selection: 1-whites turn piece selected: 2- black turn no selection, 3 - black turn piece selected
turn_step = 0
selection = 100
valid_moves = []
# load in game piece images (queen, king, rook, bishop, knight, pawn) x 2
black_queen = pygame.image.load('assets/images/black queen.png')
black_queen = pygame.transform.scale(black_queen, (80, 80))
black_queen_small = pygame.transform.scale(black_queen, (45, 45))
black_king = pygame.image.load('assets/images/black king.png')
black_king = pygame.transform.scale(black_king, (80, 80))
black_king_small = pygame.transform.scale(black_king, (45, 45))
black_rook = pygame.image.load('assets/images/black rook.png')
black_rook = pygame.transform.scale(black_rook, (80, 80))
black_rook_small = pygame.transform.scale(black_rook, (45, 45))
black_bishop = pygame.image.load('assets/images/black bishop.png')
black_bishop = pygame.transform.scale(black_bishop, (80, 80))
black_bishop_small = pygame.transform.scale(black_bishop, (45, 45))
black_knight = pygame.image.load('assets/images/black knight.png')
black_knight = pygame.transform.scale(black_knight, (80, 80))
black_knight_small = pygame.transform.scale(black_knight, (45, 45))
black_pawn = pygame.image.load('assets/images/black pawn.png')
black_pawn = pygame.transform.scale(black_pawn, (65, 65))
black_pawn_small = pygame.transform.scale(black_pawn, (45, 45))
white_queen = pygame.image.load('assets/images/white queen.png')
white_queen = pygame.transform.scale(white_queen, (80, 80))
white_queen_small = pygame.transform.scale(white_queen, (45, 45))
white_king = pygame.image.load('assets/images/white king.png')
white_king = pygame.transform.scale(white_king, (80, 80))
white_king_small = pygame.transform.scale(white_king, (45, 45))
white_rook = pygame.image.load('assets/images/white rook.png')
white_rook = pygame.transform.scale(white_rook, (80, 80))
white_rook_small = pygame.transform.scale(white_rook, (45, 45))
white_bishop = pygame.image.load('assets/images/white bishop.png')
white_bishop = pygame.transform.scale(white_bishop, (80, 80))
white_bishop_small = pygame.transform.scale(white_bishop, (45, 45))
white_knight = pygame.image.load('assets/images/white knight.png')
white_knight = pygame.transform.scale(white_knight, (80, 80))
white_knight_small = pygame.transform.scale(white_knight, (45, 45))
white_pawn = pygame.image.load('assets/images/white pawn.png')
white_pawn = pygame.transform.scale(white_pawn, (65, 65))
white_pawn_small = pygame.transform.scale(white_pawn, (45, 45))
white_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop]
small_white_images = [white_pawn_small, white_queen_small, white_king_small, white_knight_small,
                      white_rook_small, white_bishop_small]
black_images = [black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]
small_black_images = [black_pawn_small, black_queen_small, black_king_small, black_knight_small,
                      black_rook_small, black_bishop_small]
piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']
# check variables/ flashing counter
counter = 0
winner = ''
game_over = False


# Helper functions
def board_to_screen(x, y, role):
    if role == 'black':
        return 7 - x, 7 - y
    return x, y

def screen_to_board(x, y, role):
    if role == 'black':
        return 7 - x, 7 - y
    return x, y

def position_to_notation(pos):
    x, y = pos
    file = chr(ord('a') + x)
    rank = str(8 - y)
    return file + rank

def notation_to_position(notation):
    file = notation[0].lower()
    rank = notation[1]
    x = ord(file) - ord('a')
    y = 8 - int(rank)
    return (x, y)

def reset_game_state():
    global white_pieces, white_locations, black_pieces, black_locations
    global captured_pieces_white, captured_pieces_black, turn_step, selection
    global valid_moves, winner, game_over, pending_offer, offer_sender
    global white_time, black_time
    
    white_pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook',
                    'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
    white_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                       (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
    black_pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook',
                    'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
    black_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                       (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
    captured_pieces_white = []
    captured_pieces_black = []
    turn_step = 0
    selection = 100
    valid_moves = []
    winner = ''
    game_over = False
    pending_offer = None
    offer_sender = None
    white_time = 600
    black_time = 600

# Globals for Replay
replay_snapshots = []
replay_index = 0

def simulate_move_logic(move_str, w_pieces, w_locs, b_pieces, b_locs):
    # Parse e2e4
    if len(move_str) < 4: return
    
    start_pos = notation_to_position(move_str[:2])
    end_pos = notation_to_position(move_str[2:4])
    
    # Identify moving piece
    moving_piece = None
    start_list = None
    start_locs = None
    
    # Try finding in White
    try:
        idx = w_locs.index(start_pos)
        moving_piece = w_pieces[idx]
        start_list = w_pieces
        start_locs = w_locs
    except ValueError:
        # Try finding in Black
        try:
            idx = b_locs.index(start_pos)
            moving_piece = b_pieces[idx]
            start_list = b_pieces
            start_locs = b_locs
        except ValueError:
            return # No piece found

    # Determine Target List (Opponent)
    target_list = None
    target_locs = None
    if start_list is w_pieces:
        target_list = b_pieces
        target_locs = b_locs
    else:
        target_list = w_pieces
        target_locs = w_locs
        
    # En Passant Detection
    # Pawn moves diagonal but target is empty
    if 'pawn' in moving_piece and start_pos[0] != end_pos[0]:
        if end_pos not in target_locs:
             # Capture pawn at (end_x, start_y)
             capture_pos = (end_pos[0], start_pos[1])
             try:
                 c_idx = target_locs.index(capture_pos)
                 target_locs.pop(c_idx)
                 target_list.pop(c_idx)
             except ValueError:
                 pass

    # Normal Capture
    if end_pos in target_locs:
        try:
            c_idx = target_locs.index(end_pos)
            target_locs.pop(c_idx)
            target_list.pop(c_idx)
        except ValueError:
            pass
        
    # Update Position
    try:
        idx = start_locs.index(start_pos)
        start_locs[idx] = end_pos
    except ValueError:
        return
    
    # Castling Logic
    # King moves 2 squares
    if 'king' in moving_piece and abs(start_pos[0] - end_pos[0]) == 2:
        rook_start = None
        rook_end = None
        y = start_pos[1]
        
        if end_pos[0] > start_pos[0]: # Kingside (Right) e->g
            rook_start = (7, y) # h file
            rook_end = (5, y)   # f file
        else: # Queenside (Left) e->c
            rook_start = (0, y) # a file
            rook_end = (3, y)   # d file
            
        if rook_start in start_locs:
            try:
                r_idx = start_locs.index(rook_start)
                start_locs[r_idx] = rook_end
            except ValueError:
                pass
            
    # Promotion Logic
    # White (y=6->0), Black (y=1->7)
    if 'pawn' in moving_piece:
        if end_pos[1] == 0 or end_pos[1] == 7:
            start_list[idx] = 'queen'

def load_replay_data(moves):
    global replay_snapshots, replay_index
    replay_snapshots = []
    replay_index = 0
    
    # Initial state (Standard Chess)
    w_p = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook',
           'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
    w_l = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
           (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
    b_p = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook',
           'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
    b_l = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
           (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
    
    # Save Initial Snapshot
    replay_snapshots.append({
        'white_pieces': list(w_p), 'white_locations': list(w_l),
        'black_pieces': list(b_p), 'black_locations': list(b_l)
    })
    
    # Simulate moves
    current_w_p = list(w_p)
    current_w_l = list(w_l)
    current_b_p = list(b_p)
    current_b_l = list(b_l)
    
    for move in moves:
        simulate_move_logic(move, current_w_p, current_w_l, current_b_p, current_b_l)
        
        replay_snapshots.append({
            'white_pieces': list(current_w_p), 'white_locations': list(current_w_l),
            'black_pieces': list(current_b_p), 'black_locations': list(current_b_l)
        })

# draw main game board
def draw_board():
    for i in range(32):
        column = i % 4
        row = i // 4
        if row % 2 == 0:
            pygame.draw.rect(screen, 'light gray', [600 - (column * 200), row * 100, 100, 100])
        else:
            pygame.draw.rect(screen, 'light gray', [700 - (column * 200), row * 100, 100, 100])
    pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
    pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
    pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)
    
    status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
                   'Black: Select a Piece to Move!', 'Black: Select a Destination!']
    screen.blit(big_font.render(status_text[turn_step], True, 'black'), (20, 820))
    
    for i in range(9):
        pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
        pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)
    screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))


# draw pieces onto board
def draw_pieces():
    my_role = globals().get('online_my_role', 'white') if online_game_active else 'white'
    
    for i in range(len(white_pieces)):
        index = piece_list.index(white_pieces[i])
        screen_x, screen_y = board_to_screen(white_locations[i][0], white_locations[i][1], my_role)
        
        if white_pieces[i] == 'pawn':
            screen.blit(white_pawn, (screen_x * 100 + 22, screen_y * 100 + 30))
        else:
            screen.blit(white_images[index], (screen_x * 100 + 10, screen_y * 100 + 10))
        if turn_step < 2:
            if selection == i:
                pygame.draw.rect(screen, 'red', [screen_x * 100 + 1, screen_y * 100 + 1, 100, 100], 2)

    for i in range(len(black_pieces)):
        index = piece_list.index(black_pieces[i])
        screen_x, screen_y = board_to_screen(black_locations[i][0], black_locations[i][1], my_role)
        
        if black_pieces[i] == 'pawn':
            screen.blit(black_pawn, (screen_x * 100 + 22, screen_y * 100 + 30))
        else:
            screen.blit(black_images[index], (screen_x * 100 + 10, screen_y * 100 + 10))
        if turn_step >= 2:
            if selection == i:
                pygame.draw.rect(screen, 'blue', [screen_x * 100 + 1, screen_y * 100 + 1, 100, 100], 2)


# draw valid moves on screen
def draw_valid(moves):
    my_role = globals().get('online_my_role', 'white') if online_game_active else 'white'
    color = 'red' if turn_step < 2 else 'blue'
    for i in range(len(moves)):
        screen_x, screen_y = board_to_screen(moves[i][0], moves[i][1], my_role)
        pygame.draw.circle(screen, color, (screen_x * 100 + 50, screen_y * 100 + 50), 5)


# draw captured pieces on side of screen
def draw_captured():
    for i in range(len(captured_pieces_white)):
        captured_piece = captured_pieces_white[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_black_images[index], (825, 5 + 50 * i))
    for i in range(len(captured_pieces_black)):
        captured_piece = captured_pieces_black[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_white_images[index], (925, 5 + 50 * i))


# draw a flashing square around king if in check
def draw_check():
    pass # Managed by server

def draw_timers():
    # Helper to format time
    def format_time(seconds):
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02d}:{seconds:02d}"

    # Draw White Timer
    white_str = f"White: {format_time(white_time)}"
    screen.blit(font.render(white_str, True, 'black'), (620, 750))
    
    # Draw Black Timer
    black_str = f"Black: {format_time(black_time)}"
    screen.blit(font.render(black_str, True, 'black'), (620, 20))

def draw_game_over():
    pygame.draw.rect(screen, 'black', [200, 200, 400, 100])
    screen.blit(font.render(f'{winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render(f'Press ENTER to Restart!', True, 'white'), (210, 240))
    
    # Rematch Button if game over
    rematch_btn_rect = pygame.Rect(250, 270, 120, 30)
    pygame.draw.rect(screen, 'green', rematch_btn_rect, border_radius=5)
    pygame.draw.rect(screen, 'white', rematch_btn_rect, 2, border_radius=5)
    rematch_text = font.render("Rematch?", True, 'white')
    screen.blit(rematch_text, (260, 275))

def draw_offer_popup():
    """Draw popup for Draw / Rematch offers"""
    if not pending_offer:
        return
        
    # Draw background overlay
    s = pygame.Surface((WIDTH, HEIGHT))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    screen.blit(s, (0, 0))
    
    # Draw popup box
    box_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 100, 300, 200)
    pygame.draw.rect(screen, 'white', box_rect)
    pygame.draw.rect(screen, 'black', box_rect, 2)
    
    # Draw text
    title_text = "Offer Received"
    if pending_offer == 'draw':
        msg_text = f"Draw offered by {offer_sender}"
    else: # rematch
        msg_text = f"Rematch request from {offer_sender}"
        
    title_surf = font.render(title_text, True, 'black')
    msg_surf = font.render(msg_text, True, 'black')
    
    screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, HEIGHT//2 - 70))
    screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//2 - 30))
    
    # Draw Accept/Decline buttons
    accept_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 20, 100, 40)
    decline_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 20, 100, 40)
    
    pygame.draw.rect(screen, 'green', accept_rect)
    pygame.draw.rect(screen, 'black', accept_rect, 2)
    pygame.draw.rect(screen, 'red', decline_rect)
    pygame.draw.rect(screen, 'black', decline_rect, 2)
    
    accept_text = font.render("Accept", True, 'white')
    decline_text = font.render("Decline", True, 'white')
    
    screen.blit(accept_text, (accept_rect.centerx - accept_text.get_width()//2, accept_rect.centery - accept_text.get_height()//2))
    screen.blit(decline_text, (decline_rect.centerx - decline_text.get_width()//2, decline_rect.centery - decline_text.get_height()//2))


# Cleanup function
def cleanup_and_exit():
    """Send logout and cleanup before exit"""
    global async_handler
    
    # Stop async handler thread
    if async_handler:
        async_handler.stop()
        async_handler = None
    
    if current_state in [STATE_MENU, STATE_GAME] and session_data:
        session_id = session_data.get('sessionId', '')
        if network_client.is_connected() and session_id:
            try:
                 network_client.send_message("LOGOUT", {"sessionId": session_id})
                 network_client.clear_session()  # Clear persisted session on logout
                 print("[Main] Sent LOGOUT before exit")
            except Exception as e:
                 print(f"[Main] Error sending LOGOUT: {e}")
    
    network_client.disconnect()
    pygame.quit()

# Initialize views
auth_view = AuthView(screen, network_client)
menu_view = MenuView(screen, network_client)
async_handler = AsyncMessageHandler(network_client)
profile_modal = ProfileModal(screen, network_client)
match_history_view = MatchHistoryView(screen, network_client)
players_view = OnlinePlayersView(screen, network_client, async_handler, profile_modal)
challenge_notification = ChallengeNotification(screen, network_client)

# Note: Session sẽ được kiểm tra sau khi login
# Server sẽ thông báo nếu user có game đang chơi

run = True
while run:
    dt_ms = timer.tick(fps)
    dt_sec = dt_ms / 1000.0
    
    # Handle different states
    if current_state == STATE_AUTH:
        # Authentication state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanup_and_exit()
                run = False
            else:
                auth_view.handle_event(event)
        
        try:
            auth_view.draw()
        except pygame.error as e:
            print(f"[Main] Display error: {e}")
            cleanup_and_exit()
            run = False
            continue
        
        if auth_view.is_authenticated():
            session_data = auth_view.get_session_data()
            print(f"[Main] Logged in as: {session_data.get('username', 'Unknown')}")
            
            # Save session for reconnect
            network_client.save_session(
                session_data.get('sessionId', ''),
                session_data.get('username', '')
            )
            
            menu_view.set_session_data(session_data)
            challenge_notification.set_session_data(session_data)
            async_handler.start()
            print("[Main] Started async message handler")
            current_state = STATE_MENU
    
    elif current_state == STATE_MENU:
        # Menu state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_view.exit_app()  # This handles LOGOUT
                run = False
            elif profile_modal.is_visible:
                profile_modal.handle_event(event)
            else:
                challenge_notification.handle_event(event)
                if not challenge_notification.is_visible:
                    menu_view.handle_event(event)
        
        if async_handler:
            challenger = async_handler.get_incoming_challenge()
            if challenger:
                print(f"[Main] Received challenge from {challenger}")
                challenge_notification.show_challenge(challenger)
            
            game_start_data = async_handler.get_game_start()
            if game_start_data:
                online_match_id = game_start_data.get('matchId')
                white_player = game_start_data.get('white')
                black_player = game_start_data.get('black')
                my_username = session_data.get('username')
                online_my_role = 'white' if white_player == my_username else 'black'
                online_opponent_name = black_player if online_my_role == 'white' else white_player
                online_is_my_turn = (online_my_role == 'white')
                online_game_active = True
                waiting_for_game_start = False
                
                # Reset game vars
                winner = ''
                game_over = False
                pending_offer = None
                
                print(f"[Main] Game starting: Match {online_match_id}")
                print(f"[Main] I am {online_my_role}, opponent is {online_opponent_name}")
                print(f"[Main] My turn: {online_is_my_turn}")
                current_state = STATE_GAME
        
        try:
            menu_view.draw()
        except pygame.error as e:
            print(f"[Main] Display error in menu: {e}")
            cleanup_and_exit()
            run = False
            continue
        
        try:
            challenge_notification.draw()
        except pygame.error:
            pass
        
        # Draw profile modal if visible
        if profile_modal.is_visible:
            try:
                profile_modal.draw()
            except pygame.error:
                pass
        
        if challenge_notification.should_accept():
            print("[Main] Challenge accepted, waiting for game to start...")
            challenge_notification.reset()
            waiting_for_game_start = True
        elif challenge_notification.should_decline():
            print("[Main] Challenge declined")
            challenge_notification.reset()
        elif not waiting_for_game_start:
            if menu_view.should_start_game():
                print("[Main] Starting game...")
                current_state = STATE_GAME
            elif menu_view.should_show_players():
                print("[Main] Showing online players...")
                players_view.set_session_data(session_data)
                players_view.load_online_players()
                current_state = STATE_PLAYERS
                menu_view.reset()
            elif menu_view.should_show_history():
                print("[Main] Showing match history...")
                match_history_view.set_session_data(session_data)
                match_history_view.load_match_history()
                current_state = STATE_MATCH_HISTORY
                menu_view.reset()
            elif menu_view.should_do_logout():
                print("[Main] Logging out...")
                async_handler.stop()
                async_handler.clear_all()
                challenge_notification.reset()
                current_state = STATE_AUTH
                auth_view = AuthView(screen, network_client)
                menu_view.reset()
            elif menu_view.should_do_find_match():
                print("[Main] Finding match...")
                network_client.send_message("FIND_MATCH", {})
                is_finding_match = True
                matchmaking_text = "Searching for opponent..."
                current_state = STATE_FIND_MATCH
                menu_view.reset()
            elif menu_view.should_view_profile():
                print("[Main] Viewing my profile...")
                profile_modal.show(session_data.get("username", ""), session_data.get("sessionId", ""))
                menu_view.reset()
            elif menu_view.should_do_exit():
                print("[Main] Exiting...")
                run = False
    
    elif current_state == STATE_FIND_MATCH:
        # Matchmaking state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                network_client.send_message("CANCEL_FIND_MATCH", {})
                cleanup_and_exit()
                run = False
            
            # Allow cancelling
            if event.type == pygame.MOUSEBUTTONDOWN:
                 cancel_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
                 if cancel_rect.collidepoint(event.pos):
                     print("[Main] Cancelling matchmaking...")
                     network_client.send_message("CANCEL_FIND_MATCH", {})
                     current_state = STATE_MENU

        # Poll async handler for MATCHMAKING_STATUS
        if async_handler:
            status_data = async_handler.get_matchmaking_status()
            if status_data:
                status = status_data.get('status')
                if status == 'SEARCHING':
                    matchmaking_text = "Searching for opponent..."
                elif status == 'CANCELLED':
                    current_state = STATE_MENU
            
            # Check for Game Start (Match Found)
            game_start_data = async_handler.get_game_start()
            if game_start_data:
                online_match_id = game_start_data.get('matchId')
                white_player = game_start_data.get('white')
                black_player = game_start_data.get('black')
                my_username = session_data.get('username')
                online_my_role = 'white' if white_player == my_username else 'black'
                online_opponent_name = black_player if online_my_role == 'white' else white_player
                online_game_active = True
                
                # Correctly set turn
                online_is_my_turn = (online_my_role == 'white')
                
                # Reset game vars
                reset_game_state()
                
                print(f"[Main] Match Found! ID: {online_match_id}")
                current_state = STATE_GAME
        
        # Draw logic
        screen.fill('white')
        
        text = big_font.render(matchmaking_text, True, 'black')
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
        
        # Draw Cancel Button
        cancel_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
        pygame.draw.rect(screen, 'red', cancel_rect)
        pygame.draw.rect(screen, 'black', cancel_rect, 2)
        cancel_txt = font.render("Cancel", True, 'white')
        screen.blit(cancel_txt, (cancel_rect.centerx - cancel_txt.get_width()//2, cancel_rect.centery - cancel_txt.get_height()//2))
    
    elif current_state == STATE_PLAYERS:
        # Online players state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanup_and_exit()
                run = False
            else:
                if profile_modal.is_visible:
                    profile_modal.handle_event(event)
                elif challenge_notification.is_visible:
                    challenge_notification.handle_event(event)
                else:
                    players_view.handle_event(event)
        
        if async_handler:
            challenger = async_handler.get_incoming_challenge()
            if challenger:
                print(f"[Main] Received challenge from {challenger}")
                challenge_notification.show_challenge(challenger)
            
            game_start_data = async_handler.get_game_start()
            if game_start_data:
                online_match_id = game_start_data.get('matchId')
                white_player = game_start_data.get('white')
                black_player = game_start_data.get('black')
                my_username = session_data.get('username')
                online_my_role = 'white' if white_player == my_username else 'black'
                online_opponent_name = black_player if online_my_role == 'white' else white_player
                online_is_my_turn = (online_my_role == 'white')
                online_game_active = True
                
                # Reset game vars
                winner = ''
                game_over = False
                pending_offer = None

                print(f"[Main] Game starting: Match {online_match_id}")
                print(f"[Main] I am {online_my_role}, opponent is {online_opponent_name}")
                print(f"[Main] My turn: {online_is_my_turn}")
                current_state = STATE_GAME
        
        try:
            players_view.draw()
        except pygame.error as e:
            print(f"[Main] Display error in players view: {e}")
            cleanup_and_exit()
            run = False
            continue
        
        try:
            profile_modal.draw()
        except pygame.error:
            pass
        
        try:
            challenge_notification.draw()
        except pygame.error:
            pass
        
        if challenge_notification.should_accept():
            print("[Main] Challenge accepted, waiting for game to start...")
            challenge_notification.reset()
            players_view.reset()
        elif challenge_notification.should_decline():
            print("[Main] Challenge declined")
            challenge_notification.reset()
            players_view.reset()
        elif players_view.should_go_back():
            print("[Main] Returning to menu...")
            current_state = STATE_MENU
            players_view.reset()
        elif players_view.should_start_game():
            print("[Main] Starting game...")
            current_state = STATE_GAME
    
    elif current_state == STATE_MATCH_HISTORY:
        # Match history state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanup_and_exit()
                run = False
            else:
                match_history_view.handle_event(event)

        # Check selection
        selected_match_id = match_history_view.get_selected_match_id()
        if selected_match_id:
             print(f"[Main] Requesting replay for {selected_match_id}")
             network_client.send_message("GET_MATCH_REPLAY", {"matchId": selected_match_id})

        # Check async handler for REPLAY response
        if async_handler:
            replay_data_resp = async_handler.get_match_replay()
            if replay_data_resp:
                 data = replay_data_resp or {}
                 moves = data.get("moves", [])
                 #final_board = data.get("finalBoard", "")
                 print(f"[Main] Loaded replay for match {data.get('matchId')} with {len(moves)} moves")
                 load_replay_data(moves)
                 current_state = STATE_REPLAY
                 online_game_active = False

        try:
            match_history_view.draw()
        except pygame.error as e:
            print(f"[Main] Display error in match history: {e}")
            cleanup_and_exit()
            run = False
            continue
        
        if match_history_view.should_go_back():
            print("[Main] Returning to menu from match history...")
            current_state = STATE_MENU
            match_history_view.reset()

    elif current_state == STATE_REPLAY:
         # Apply current snapshot
         if replay_snapshots and 0 <= replay_index < len(replay_snapshots):
             snap = replay_snapshots[replay_index]
             white_pieces = snap['white_pieces']
             white_locations = snap['white_locations']
             black_pieces = snap['black_pieces']
             black_locations = snap['black_locations']
         
         # Draw Board & Pieces (Reuse Game UI)
         draw_board()
         draw_pieces()
         draw_captured() # Show captured pieces
         
         # Overwrite "FORFEIT" / Status Text with Replay Controls
         # Cover bottom status area
         pygame.draw.rect(screen, 'dark gray', [0, 800, WIDTH, 100])
         pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
         
         # Replay Title / Status
         move_num = (replay_index + 1) // 2
         turn_color = "White" if replay_index % 2 == 0 else "Black"
         if replay_index == 0: turn_color = "Start"
         
         title_txt = f"Replay: Move {move_num} ({turn_color})"
         title_surf = medium_font.render(title_txt, True, 'black')
         screen.blit(title_surf, (20, 820))

         # Navigation Buttons
         # PREV
         prev_rect = pygame.Rect(WIDTH - 250, 815, 100, 70)
         pygame.draw.rect(screen, 'light gray', prev_rect)
         pygame.draw.rect(screen, 'black', prev_rect, 2)
         prev_txt = font.render("< Prev", True, 'black')
         screen.blit(prev_txt, (prev_rect.centerx - prev_txt.get_width()//2, prev_rect.centery - prev_txt.get_height()//2))
         
         # NEXT
         next_rect = pygame.Rect(WIDTH - 130, 815, 100, 70)
         pygame.draw.rect(screen, 'light gray', next_rect)
         pygame.draw.rect(screen, 'black', next_rect, 2)
         next_txt = font.render("Next >", True, 'black')
         screen.blit(next_txt, (next_rect.centerx - next_txt.get_width()//2, next_rect.centery - next_txt.get_height()//2))
         
         # Back Button (Top Left - keep consistent with others or put in corner)
         back_rect = pygame.Rect(10, 10, 80, 40)
         # Using a small icon or button for "Exit Replay"
         pygame.draw.rect(screen, 'red', back_rect) 
         pygame.draw.rect(screen, 'black', back_rect, 2)
         back_text = font.render("Exit", True, 'white')
         screen.blit(back_text, (20, 20))
         
         # Handle events
         for event in pygame.event.get():
             if event.type == pygame.QUIT:
                 cleanup_and_exit()
                 run = False
             
             if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                 if back_rect.collidepoint(event.pos):
                     current_state = STATE_MATCH_HISTORY
                     reset_game_state()
                 elif prev_rect.collidepoint(event.pos):
                     if replay_index > 0:
                         replay_index -= 1
                 elif next_rect.collidepoint(event.pos):
                     if replay_index < len(replay_snapshots) - 1:
                         replay_index += 1
             
             # Key navigation for convenience
             if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_LEFT:
                     if replay_index > 0:
                         replay_index -= 1
                 elif event.key == pygame.K_RIGHT:
                     if replay_index < len(replay_snapshots) - 1:
                         replay_index += 1
    
    elif current_state == STATE_GAME:
        # Game state - online multiplayer ONLY (Offline removed)
        
        if counter < 30:
            counter += 1
        else:
            counter = 0
        
        # Poll async handler messages
        if async_handler:
            # Game Over / Result
            game_result_data = async_handler.get_game_over()
            if game_result_data:
                winner_name = game_result_data.get('winner', 'Unknown')
                reason = game_result_data.get('reason', '')
                print(f"[Main] GAME OVER. Winner: {winner_name}, Reason: {reason}")
                
                game_over = True
                winner = winner_name
                if winner == 'DRAW':
                    winner = 'No one'
                elif winner == 'ABORT': # Should not happen with new resign logic, but keep safe
                    winner = 'Nobody (Aborted)'
                
            # Offers (Draw)
            draw_offer = async_handler.get_draw_offered()
            if draw_offer:
                sender = draw_offer.get('from', 'Opponent')
                print(f"[Main] Draw offered by {sender}")
                pending_offer = 'draw'
                offer_sender = sender
            
            # Rematch Offer
            rematch_offer = async_handler.get_rematch_offered()
            if rematch_offer:
                sender = rematch_offer.get('from', 'Opponent')
                print(f"[Main] Rematch offered by {sender}")
                pending_offer = 'rematch'
                offer_sender = sender

            # Log declines
            if async_handler.get_draw_declined():
                print("[Main] Draw request declined by opponent")
            
            if async_handler.get_rematch_declined():
                print("[Main] Rematch request declined by opponent")
            
            # === RECONNECT HANDLING ===
            reconnect_data = async_handler.get_reconnect_success()
            if reconnect_data:
                print(f"[Main] Reconnect successful!")
                in_game = reconnect_data.get('inGame', False)
                
                if in_game:
                    # Restore game state from server
                    online_match_id = reconnect_data.get('matchId')
                    white_player = reconnect_data.get('white')
                    black_player = reconnect_data.get('black')
                    current_turn = reconnect_data.get('currentTurn', 0)
                    white_time = reconnect_data.get('whiteTime', 600)
                    black_time = reconnect_data.get('blackTime', 600)
                    board_str = reconnect_data.get('board', '')
                    
                    my_username = session_data.get('username')
                    online_my_role = 'white' if white_player == my_username else 'black'
                    online_opponent_name = black_player if online_my_role == 'white' else white_player
                    online_is_my_turn = (current_turn == 0 and online_my_role == 'white') or \
                                       (current_turn == 1 and online_my_role == 'black')
                    online_game_active = True
                    
                    print(f"[Main] Restored game: {online_match_id}")
                    print(f"[Main] I am {online_my_role}, my turn: {online_is_my_turn}")
                    
                    # Restore board from board_str (64 chars)
                    if len(board_str) == 64:
                        white_pieces.clear()
                        white_locations.clear()
                        black_pieces.clear()
                        black_locations.clear()
                        
                        piece_map = {
                            'p': 'pawn', 'r': 'rook', 'n': 'knight', 
                            'b': 'bishop', 'q': 'queen', 'k': 'king',
                            'P': 'pawn', 'R': 'rook', 'N': 'knight',
                            'B': 'bishop', 'Q': 'queen', 'K': 'king'
                        }
                        
                        for row in range(8):
                            for col in range(8):
                                char = board_str[row * 8 + col]
                                if char != '.':
                                    piece_name = piece_map.get(char)
                                    if piece_name:
                                        if char.islower():  # White
                                            white_pieces.append(piece_name)
                                            white_locations.append((col, row))
                                        else:  # Black
                                            black_pieces.append(piece_name)
                                            black_locations.append((col, row))
                        
                        print(f"[Main] Board restored: {len(white_pieces)} white, {len(black_pieces)} black pieces")
                    
                    # Restore turn
                    turn_step = 0 if current_turn == 0 else 2
                    game_over = False
                    winner = ''
                else:
                    print("[Main] Reconnected but not in game")
            
            reconnect_fail = async_handler.get_reconnect_fail()
            if reconnect_fail:
                reason = reconnect_fail.get('reason', 'Unknown')
                print(f"[Main] Reconnect failed: {reason}")
                # Go back to auth screen
                current_state = STATE_AUTH
                auth_view = AuthView(screen, network_client)
            
            # Game Start (Rematch)
            new_game_data = async_handler.get_game_start()
            if new_game_data:
                match_id = new_game_data.get('matchId')
                white_username = new_game_data.get('white')
                black_username = new_game_data.get('black')
                is_rematch = new_game_data.get('isRematch', False)
                print(f"[Main] Game starting (Rematch): Match {match_id}")
                
                my_username = session_data.get("username")
                if my_username == white_username:
                    online_my_role = 'white'
                else:
                    online_my_role = 'black'
                
                print(f"[Main] I am {online_my_role}, opponent is {black_username if online_my_role == 'white' else white_username}")
                online_match_id = match_id
                online_is_my_turn = (online_my_role == 'white')
                
                # RESET STATE
                reset_game_state()
                current_state = STATE_GAME
            
            # Incoming challenge during game (less likely but possible)
            challenger = async_handler.get_incoming_challenge()
            if challenger:
                print(f"[Main] Received challenge from {challenger} during game")
                challenge_notification.show_challenge(challenger)
            
            if not game_over and not pending_offer:
                # 1. Handle VALID_MOVES response
                valid_moves_data = async_handler.get_valid_moves()
                if valid_moves_data:
                    moves_notation = valid_moves_data.get('moves', [])
                    valid_moves = []
                    for move_not in moves_notation:
                        valid_moves.append(notation_to_position(move_not))
                
                # 2. Handle OPPONENT_MOVE
                move_data = async_handler.get_move_made()
                if move_data:
                    from_notation = move_data.get('from')
                    to_notation = move_data.get('to')
                    print(f"[Main] Opponent moved: {from_notation} -> {to_notation}")
                    
                    from_pos = notation_to_position(from_notation)
                    to_pos = notation_to_position(to_notation)
                    
                    if online_my_role == 'white':
                        if from_pos in black_locations:
                            idx = black_locations.index(from_pos)
                            moving_piece = black_pieces[idx]
                            black_locations[idx] = to_pos
                            
                            # Check Castling (Black)
                            if moving_piece == 'king' and abs(from_pos[0] - to_pos[0]) == 2:
                                y = from_pos[1]
                                if to_pos[0] > from_pos[0]: # Kingside e->g
                                    rook_start = (7, y)
                                    rook_end = (5, y)
                                else: # Queenside e->c
                                    rook_start = (0, y)
                                    rook_end = (3, y)
                                if rook_start in black_locations:
                                    r_idx = black_locations.index(rook_start)
                                    black_locations[r_idx] = rook_end

                            if to_pos in white_locations:
                                w_idx = white_locations.index(to_pos)
                                captured_pieces_black.append(white_pieces[w_idx])
                                white_pieces.pop(w_idx)
                                white_locations.pop(w_idx)
                    else:
                        if from_pos in white_locations:
                            idx = white_locations.index(from_pos)
                            moving_piece = white_pieces[idx]
                            white_locations[idx] = to_pos
                            
                            # Check Castling (White)
                            if moving_piece == 'king' and abs(from_pos[0] - to_pos[0]) == 2:
                                y = from_pos[1]
                                if to_pos[0] > from_pos[0]: # Kingside e->g
                                    rook_start = (7, y)
                                    rook_end = (5, y)
                                else: # Queenside e->c
                                    rook_start = (0, y)
                                    rook_end = (3, y)
                                if rook_start in white_locations:
                                    r_idx = white_locations.index(rook_start)
                                    white_locations[r_idx] = rook_end

                            if to_pos in black_locations:
                                b_idx = black_locations.index(to_pos)
                                captured_pieces_white.append(black_pieces[b_idx])
                                black_pieces.pop(b_idx)
                                black_locations.pop(b_idx)
                    
                    # Sync timers from message
                    if 'white_time' in move_data:
                        white_time = move_data['white_time']
                    if 'black_time' in move_data:
                        black_time = move_data['black_time']

                    globals()['online_is_my_turn'] = True
                    print(f"[Main] Turn switched! My turn: True")
                    selection = 100
                    valid_moves = []
                
                # 3. Handle MOVE_OK (Confirmation)
                move_ok = async_handler.get_move_ok()
                if move_ok:
                    # Sync timer if server sent it
                    if 'white_time' in move_ok:
                         white_time = move_ok['white_time']
                    if 'black_time' in move_ok:
                         black_time = move_ok['black_time']
        
        # Decrement local timer
        if online_game_active and not game_over:
             if globals().get('online_is_my_turn', False):
                 # My turn
                 if online_my_role == 'white':
                     white_time -= dt_sec
                 else:
                     black_time -= dt_sec
             else:
                 # Opponent turn
                 if online_my_role == 'white':
                     black_time -= dt_sec
                 else:
                     white_time -= dt_sec
             
             # Prevent negative display locally
             if white_time < 0: white_time = 0
             if black_time < 0: black_time = 0

        screen.fill('dark gray')
        draw_board()
        draw_pieces()
        draw_captured()
        draw_check()
        draw_timers()
        
        # Display online game info
        if online_game_active:
            white_text = f"White: {online_opponent_name if online_my_role == 'black' else session_data.get('username')}"
            black_text = f"Black: {online_opponent_name if online_my_role == 'white' else session_data.get('username')}"
            screen.blit(font.render(white_text, True, 'white'), (820, 50))
            screen.blit(font.render(black_text, True, 'white'), (820, 80))
            
            if game_over:
                turn_text = "GAME OVER"
                turn_color = 'red'
            elif globals().get('online_is_my_turn', False):
                turn_text = f"Your turn ({online_my_role})"
                turn_color = 'green'
            else:
                turn_text = "Opponent's turn"
                turn_color = 'yellow'
            screen.blit(font.render(turn_text, True, turn_color), (820, 120))
            
            match_text = f"Match: {online_match_id[:8]}..."
            screen.blit(font.render(match_text, True, 'gray'), (820, 150))
        
        # Draw Back to Menu
        menu_button_rect = pygame.Rect(820, 10, 160, 40)
        pygame.draw.rect(screen, (100, 100, 100), menu_button_rect, border_radius=5)
        pygame.draw.rect(screen, (200, 200, 200), menu_button_rect, 2, border_radius=5)
        menu_text = font.render("Back to Menu", True, 'white')
        menu_text_rect = menu_text.get_rect(center=menu_button_rect.center)
        screen.blit(menu_text, menu_text_rect)
        
        # Draw Draw Button
        draw_btn_rect = pygame.Rect(820, 200, 160, 40)
        pygame.draw.rect(screen, 'orange', draw_btn_rect, border_radius=5)
        pygame.draw.rect(screen, 'black', draw_btn_rect, 2, border_radius=5)
        draw_text = font.render("Offer Draw", True, 'black')
        draw_text_rect = draw_text.get_rect(center=draw_btn_rect.center)
        screen.blit(draw_text, draw_text_rect)
        
        # Draw Resign (Surrender) Button - Replaced Pause
        resign_btn_rect = pygame.Rect(820, 250, 160, 40)
        pygame.draw.rect(screen, 'red', resign_btn_rect, border_radius=5)
        pygame.draw.rect(screen, 'black', resign_btn_rect, 2, border_radius=5)
        resign_text = font.render("Surrender", True, 'white')
        resign_text_rect = resign_text.get_rect(center=resign_btn_rect.center)
        screen.blit(resign_text, resign_text_rect)
        
        # Draw valid moves
        if selection != 100 and valid_moves:
             draw_valid(valid_moves)
        
        # Draw Game Over
        if game_over:
            draw_game_over()
            
        # Draw Offer Popup
        if pending_offer:
            draw_offer_popup()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanup_and_exit()
                run = False
            
            challenge_notification.handle_event(event)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and game_over:
                # Reset game or go back to menu?
                print("[Main] Game Over -> Returning to menu...")
                globals()['online_game_active'] = False
                current_state = STATE_MENU
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x_coord = event.pos[0]
                y_coord = event.pos[1]
                
                # Handle Popup Clicks (Offer)
                if pending_offer:
                    accept_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 20, 100, 40)
                    decline_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 20, 100, 40)
                    
                    if accept_rect.collidepoint(x_coord, y_coord):
                        print(f"[Main] Accepted {pending_offer}")
                        if pending_offer == 'draw':
                            network_client.send_message("ACCEPT_DRAW", {"matchId": online_match_id})
                        elif pending_offer == 'rematch':
                            network_client.send_message("ACCEPT_REMATCH", {"matchId": online_match_id})
                        pending_offer = None
                        
                    elif decline_rect.collidepoint(x_coord, y_coord):
                        print(f"[Main] Declined {pending_offer}")
                        if pending_offer == 'draw':
                            network_client.send_message("DECLINE_DRAW", {"matchId": online_match_id})
                        elif pending_offer == 'rematch':
                            network_client.send_message("DECLINE_REMATCH", {"matchId": online_match_id})
                        pending_offer = None
                        
                    continue # Block other clicks when popup open
                
                # Handle Rematch Button (Only when Game Over)
                if game_over:
                    # Rematch Button: 250, 270, 120, 30
                    rematch_btn_rect = pygame.Rect(250, 270, 120, 30)
                    if rematch_btn_rect.collidepoint(x_coord, y_coord):
                        print("[Main] Offering Rematch...")
                        network_client.send_message("OFFER_REMATCH", {"matchId": online_match_id})
                        # Keep game over screen until new game starts
                        continue

                # Back button
                if 820 <= x_coord <= 980 and 10 <= y_coord <= 50:
                    print("[Main] Returning to menu...")
                    globals()['online_game_active'] = False
                    current_state = STATE_MENU
                    continue
                
                # Draw Button: 820, 200, 160, 40
                if 820 <= x_coord <= 980 and 200 <= y_coord <= 240 and not game_over:
                    print("[Main] Sending Offer Draw...")
                    network_client.send_message("OFFER_DRAW", {"matchId": online_match_id})
                    continue

                # Resign Button: 820, 250, 160, 40
                if 820 <= x_coord <= 980 and 250 <= y_coord <= 290 and not game_over:
                    print("[Main] Sending Offer Abort (Resign)...")
                    # We still use "OFFER_ABORT" as action, but server logic is modified to Resign info
                    network_client.send_message("OFFER_ABORT", {"matchId": online_match_id})
                    continue
                
                # Game Board Click (Blocked if Game Over)
                if not game_over and x_coord <= 800 and y_coord <= 800:
                    x_board = x_coord // 100
                    y_board = y_coord // 100
                    
                    # Convert screen to board
                    my_role = globals().get('online_my_role', 'white')
                    click_coords = screen_to_board(x_board, y_board, my_role)
                    
                    if not globals().get('online_is_my_turn', False):
                        print("[Main] Not your turn!")
                        continue
                    
                    clicked_own_piece = False
                    if my_role == 'white':
                        if click_coords in white_locations:
                            selection = white_locations.index(click_coords)
                            clicked_own_piece = True
                    else:
                        if click_coords in black_locations:
                             selection = black_locations.index(click_coords)
                             clicked_own_piece = True
                    
                    if clicked_own_piece:
                        # Request valid moves
                        valid_moves = [] # Clear old valid moves
                        pos_not = position_to_notation(click_coords)
                        print(f"[Main] Selected {pos_not}, requesting moves...")
                        network_client.send_message("GET_VALID_MOVES", {
                            "matchId": online_match_id,
                            "position": pos_not
                        })
                    
                    elif click_coords in valid_moves and selection != 100:
                        # Executing a move
                        if my_role == 'white':
                             old_pos = white_locations[selection]
                             moving_piece = white_pieces[selection]
                             white_locations[selection] = click_coords
                             
                             # Optimistic Castling Update (White)
                             if moving_piece == 'king' and abs(old_pos[0] - click_coords[0]) == 2:
                                 y = old_pos[1]
                                 if click_coords[0] > old_pos[0]: # Kingside
                                     rook_start = (7, y)
                                     rook_end = (5, y)
                                 else: # Queenside
                                     rook_start = (0, y)
                                     rook_end = (3, y)
                                 if rook_start in white_locations:
                                     r_idx = white_locations.index(rook_start)
                                     white_locations[r_idx] = rook_end

                             if click_coords in black_locations:
                                 idx = black_locations.index(click_coords)
                                 captured_pieces_white.append(black_pieces[idx])
                                 black_pieces.pop(idx)
                                 black_locations.pop(idx)
                        else:
                             old_pos = black_locations[selection]
                             moving_piece = black_pieces[selection]
                             black_locations[selection] = click_coords
                             
                             # Optimistic Castling Update (Black)
                             if moving_piece == 'king' and abs(old_pos[0] - click_coords[0]) == 2:
                                 y = old_pos[1]
                                 if click_coords[0] > old_pos[0]: # Kingside
                                     rook_start = (7, y)
                                     rook_end = (5, y)
                                 else: # Queenside
                                     rook_start = (0, y)
                                     rook_end = (3, y)
                                 if rook_start in black_locations:
                                     r_idx = black_locations.index(rook_start)
                                     black_locations[r_idx] = rook_end

                             if click_coords in white_locations:
                                 idx = white_locations.index(click_coords)
                                 captured_pieces_black.append(white_pieces[idx])
                                 white_pieces.pop(idx)
                                 white_locations.pop(idx)
                        
                        # Send Move
                        from_not = position_to_notation(old_pos)
                        to_not = position_to_notation(click_coords)
                        network_client.send_message("MOVE", {
                            "matchId": online_match_id,
                            "from": from_not,
                            "to": to_not
                        })
                        print(f"[Main] Sent move: {from_not} -> {to_not}")
                        
                        globals()['online_is_my_turn'] = False
                        selection = 100
                        valid_moves = []
    
    pygame.display.flip()

pygame.quit()
