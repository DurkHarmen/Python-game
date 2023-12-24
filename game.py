import pygame
import sys
import os
import base64
import io
import time
import random
import tkinter as tk
from tkinter import simpledialog
import psycopg2
import sqlite3
import tkinter.messagebox as messagebox
from pygame.sprite import Sprite
import mysql.connector
import uuid
from pygame import quit

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Initialize pygame
pygame.init()

# Get the directory containing the executable
resource_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Load your custom icon
icon_image_path = os.path.join(resource_path, "gameintro.ico")
icon_image = pygame.image.load(icon_image_path)
pygame.display.set_icon(icon_image)
# Initialize Pygame modules
pygame.font.init()
pygame.mixer.init()

# Get the current screen width and height
screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h

# Create a Pygame display surface
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape the Matrix")

# Load and scale the background image
bg_image_path = os.path.join(resource_path, 'images', 'bg.jpg')
BG = pygame.transform.scale(pygame.image.load(bg_image_path), (WIDTH, HEIGHT))

# Define player properties
PLAYER_WIDTH = WIDTH // 24
PLAYER_HEIGHT = HEIGHT // 6
PLAYER_VEL = WIDTH // 192

# Define star properties
STAR_WIDTH = WIDTH // 96
STAR_HEIGHT = HEIGHT // 27
STAR_VEL = WIDTH // 320

# Load hit sound effect
hit_sound_path = os.path.join(resource_path, 'sound', 'hit_sound.mp3')
HIT_SOUND = pygame.mixer.Sound(hit_sound_path)

# Define game states
GAME_STATE_START_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_SCOREBOARD = 3
GAME_STATE_HIGH_SCORES = 4

# level time and when completed
LEVEL_DURATIONS = [30 + i * 15 for i in range(10)]  # Levels 1-10, increasing by 15 seconds each
DIFFICULTY_INCREASE_INTERVAL = 60

current_level = 0

game_state = GAME_STATE_START_MENU
paused = False
paused_time = 0

# Initialize game variables
running = False
game_over = False
game_state = GAME_STATE_START_MENU
restart_prompt = False
in_game = False
main_menu_music_playing = False

# Define font properties
FONT_SIZE = min(WIDTH // 32, HEIGHT // 18)
FONT = pygame.font.SysFont("comicsans", FONT_SIZE)

# Load game logo
logo_image_path = os.path.join(resource_path, 'images', 'gameintro.jpg')
LOGO = pygame.image.load(logo_image_path)

def play_main_menu_music():
    global main_menu_music_playing
    if not main_menu_music_playing:
        pygame.mixer.music.load(os.path.join(resource_path, 'sound', 'lobbysound.mp3'))
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)  # Play the music in a loop
        main_menu_music_playing = True

def play_gameplay_music():
    pygame.mixer.music.load(os.path.join(resource_path, 'sound', 'gamesound.mp3'))
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)  # Play the music in a loop
# Function to draw game elements
def draw(player, elapsed_time, stars, intro=False):
    WIN.blit(BG, (0, 0))

    if not intro:
        time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
        
        WIN.blit(time_text, (10, 10))
        

        pygame.draw.rect(WIN, "yellow", player)

        for star in stars:
            pygame.draw.rect(WIN, "white", star)

    pygame.display.update()


# Class to handle the scoreboard
class Scoreboard:
    def __init__(self, root):
        self.root = root
        self.conn = mysql.connector.connect(
            user='root',
            password='Fg3w9pKs',
            host='176.117.59.185',
            database='escapethematrix'
        )
        self.cursor = self.conn.cursor()
        self.create_high_scores_table()

    

    def load_user_scores(self):
        self.cursor.execute('''
            SELECT name, time FROM high_scores
            ORDER BY time ASC
            LIMIT 3
        ''')
        user_scores = self.cursor.fetchall()

        display_text = ""
        for i, (name, time) in enumerate(user_scores):
            display_text += f"{i + 1}. {name}: {time} seconds\n"
        print(display_text)  # Displaying scores for testing purposes

    def add_score(self, name, elapsed_time):
        # Use the player_id to associate scores with the player
        self.cursor.execute(
            "INSERT INTO high_scores (name, time) VALUES (%s, %s)",
            (name, elapsed_time)
        )
        self.conn.commit()

    def create_high_scores_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS high_scores (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255),
                name TEXT,
                time REAL,
                points INTEGER,
                FOREIGN KEY (user_id) REFERENCES player_info(user_id)
            );
        ''')
        self.conn.commit()

    def get_top_scores(self):
        self.cursor.execute('''
            SELECT name, time FROM high_scores
            ORDER BY time DESC
            LIMIT 3
        ''')
        top_scores = self.cursor.fetchall()
        return top_scores
# Example usage
def initialize_player(player_name):
    # Check if the player already has a user_id
    Scoreboard.cursor.execute("SELECT user_id FROM player_info WHERE player_name = %s", (player_name,))
    result = Scoreboard.cursor.fetchone()

    if result:
        user_id = result[0]
    else:
        # If not, generate a new user_id
        user_id = str(uuid.uuid4())
        # Insert the new user_id into the database
        Scoreboard.cursor.execute("INSERT INTO player_info (player_name, user_id) VALUES (%s, %s)", (player_name, user_id))
        Scoreboard.conn.commit()

    return user_id


# Create an instance of the Scoreboard class
    scoreboard = Scoreboard()

# Example usage
    player_name = 'Player1'
    player_id = initialize_player(player_name)
    print(f"Player ID for {player_name}: {player_id}")

    # Simulate a game with some points
    scoreboard.start_new_game(player_id)
    scoreboard.add_score(player_id, "Level 1", 60, 100)
    scoreboard.load_user_scores(player_id)
    global game_state

    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = GAME_STATE_PLAYING
                    play_gameplay_music()
                elif event.key == pygame.K_m:
                    game_state = GAME_STATE_START_MENU
                    self.root.withdraw()


# Function to draw the scoreboard
def draw_scoreboard(scores):
    WIN.blit(BG, (0, 0))

    title_text = FONT.render("Scoreboard", 1, "white")
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
    
    scoreboard_text = FONT.render("Press M to go back to main menu", 1, "white")
    WIN.blit(scoreboard_text, (WIDTH // 2 - scoreboard_text.get_width() // 2, HEIGHT // 8))

    y_offset = HEIGHT // 4 + title_text.get_height() + 20
    for i, (name, time) in enumerate(scores):
        score_text = FONT.render(f"{i + 1}. {name}: {time} seconds", 1, "white")
        WIN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, y_offset))
        y_offset += score_text.get_height() + 10

    pygame.display.update()


# Function to draw the game introduction
def draw_intro():
    intro_win = pygame.Surface((WIDTH, HEIGHT))
    intro_win.fill((0, 0, 0))

    logo_x = WIDTH // 2 - LOGO.get_width() // 2
    logo_y = HEIGHT // 4 - LOGO.get_height() // 2
    intro_win.blit(LOGO, (logo_x, logo_y))

    title_text = FONT.render("Escape the Matrix", 1, "white")
    title_x = WIDTH // 2 - title_text.get_width() // 2
    intro_win.blit(title_text, (title_x, HEIGHT // 2))

    WIN.blit(intro_win, (0, 0))
    pygame.display.update()

    # Add a delay to display the introduction for a specific duration
    intro_duration = 5  # Adjust this duration as needed (in seconds)
    pygame.time.delay(intro_duration * 500)  # Delay in milliseconds

# Function to draw the start menu
def draw_start_menu(player):
    WIN.blit(BG, (0, 0))

    title_text = FONT.render("Escape the Matrix", 1, "white")
    play_text = FONT.render("Press SPACE to Start", 1, "white")
    scoreboard_text = FONT.render("Press S for Scoreboard", 1, "white")
    exit_text = FONT.render("Press Q to Quit", 1, "white")

    title_x = WIDTH // 2 - title_text.get_width() // 2
    play_x = WIDTH // 2 - play_text.get_width() // 2
    scoreboard_x = WIDTH // 2 - scoreboard_text.get_width() // 2
    exit_x = WIDTH // 2 - exit_text.get_width() // 2

    WIN.blit(title_text, (title_x, HEIGHT // 3))
    WIN.blit(play_text, (play_x, HEIGHT // 2))
    WIN.blit(scoreboard_text, (scoreboard_x, HEIGHT // 2 + FONT_SIZE))
    WIN.blit(exit_text, (exit_x, HEIGHT // 2 + 2 * FONT_SIZE))

    

    keys = pygame.key.get_pressed()
    if keys[pygame.K_m] and game_state != GAME_STATE_SCOREBOARD:
        play_main_menu_music()
    


def create_stars(level):
    new_stars = []

    # Adjust the number of white stars based on the level
    num_white_stars = 4 + level

    for _ in range(num_white_stars):
        star_x = random.randint(0, WIDTH - STAR_WIDTH)
        star_y = random.randint(-STAR_HEIGHT, 0)
        white_star = pygame.Rect(star_x, star_y, STAR_WIDTH, STAR_HEIGHT)
        new_stars.append(white_star)

    return new_stars

def menu_loop(player, elapsed_time, level):
    global stars, hit, game_state, running, game_over, game_start_time, paused, paused_time, main_menu_music_playing

    menu_running = True
    stars = []
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not paused:
                        pygame.mixer.music.stop()
                        elapsed_time = reset_game(player, level)
                        stars.clear()
                        stars.extend(create_stars(level))
                        running = True
                        game_over = False
                        game_start_time = None
                        play_gameplay_music()
                    else:
                        game_start_time = time.time() - paused_time
                    paused = False
                    return GAME_STATE_PLAYING

                elif event.key == pygame.K_s:
                    pygame.mixer.music.pause()
                    elapsed_time = reset_game(player, level)
                    return GAME_STATE_HIGH_SCORES

                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                    
                elif event.key == pygame.K_m:
                    if game_state != GAME_STATE_START_MENU:
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.unpause()
                        game_state = GAME_STATE_START_MENU
                        game_start_time = None
                        running = True
                        return

        if not paused:
            draw_start_menu(player)
            pygame.display.update()

    return elapsed_time


# Function to reset the game
def reset_game(player, level):
    stars = []
    
    global game_state, hit, game_start_time

    game_state = GAME_STATE_START_MENU
    hit = False

    if not game_start_time:
        game_start_time = time.time()

    stars.clear()
    stars.extend(create_stars(level))

    player.x = WIDTH // 3
    player.y = HEIGHT - PLAYER_HEIGHT

def draw_message(message):
    message_text = FONT.render(message, 1, "white")
    WIN.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 4))
    pygame.display.update()
    pygame.time.delay(2000)  # Display the message for 2 seconds

# Function to input player name
def input_player_name():
    root = tk.Tk()
    root.withdraw()

    name = simpledialog.askstring("Enter Your Name", "Enter your name:")

    if name is None:
        return None

    name = name.strip()

    if name:
        return name
    else:
        error_message = "Please enter a name!"
        messagebox.showerror("Error", error_message)
        return None
    
    
"""hier onder zie je de code voor de functionaliteit van de powerups"""     
     
def start_game():
    global game_state, stars, elapsed_time, restart_prompt, game_start_time, paused_time, main_menu_music_playing, current_level
    game_start_time = None
    in_game = False
    restart_prompt = False
    main_menu_music_playing = False

    player = pygame.Rect(WIDTH // 3, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)

    elapsed_time = reset_game(player, current_level)

    paused_time = 0
    current_level = 0

    while True:
        run = True
        introduction = True

        intro_timer = 0
        intro_duration = 5
        
        star_count = 0
        star_add_increment = 5000

        paused = False

        player = pygame.Rect(WIDTH // 3, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        clock = pygame.time.Clock()
        FPS = 60

        last_speed_increase_time = time.time()

        first_run = True
        hit = False

        root = tk.Tk()
        root.withdraw()
        app = Scoreboard(root)
        app.create_high_scores_table()
        
        
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()
            
            
            if keys[pygame.K_m]:
                if not paused:
                    if game_state == GAME_STATE_PLAYING:
                        paused_time = elapsed_time
                    game_state = GAME_STATE_START_MENU
                    stars.clear()
                    hit = False
                    reset_game(player, current_level)
                    game_state = menu_loop(player, elapsed_time, current_level)
                    if game_state == GAME_STATE_PLAYING:
                        if paused_time > 0:
                            game_start_time = time.time() - paused_time
                            paused_time = 0
                            elapsed_time = 0
                    in_game = False
                    main_menu_music_playing = False
            

            if game_state == GAME_STATE_START_MENU and not main_menu_music_playing:
                play_main_menu_music()
                main_menu_music_playing = True
            elif game_state == GAME_STATE_START_MENU:
                main_menu_music_playing = True
            else:
                main_menu_music_playing = False

            if game_state == GAME_STATE_START_MENU:
                if introduction and not intro_duration > 0:
                    draw_intro()
                    intro_timer += 1
                    if intro_timer >= intro_duration * FPS:
                        introduction = False
                else:
                    if not restart_prompt:
                        if not main_menu_music_playing:
                            play_main_menu_music()
                            main_menu_music_playing = True
                        game_state = menu_loop(player, elapsed_time, current_level)
                        game_start_time = None
                    else:
                        draw_start_menu(player)
                        pygame.display.update()
                        restart_prompt = False
                        in_game = False

            elif game_state == GAME_STATE_PLAYING:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        game_state = GAME_STATE_START_MENU
                        reset_game(player)
                        in_game = False
                        main_menu_music_playing = False

                if game_start_time is None:
                    game_start_time = time.time()
                    elapsed_time = 0
                else:
                    elapsed_time = time.time() - game_start_time
                    star_count += clock.tick(FPS)

                    if current_level < len(LEVEL_DURATIONS) and elapsed_time > LEVEL_DURATIONS[current_level]:
                        level_completed_message = f"Completed Level {current_level + 1}"
                        draw_message(level_completed_message)
                        current_level += 1

                    if star_count > star_add_increment:
                        if current_level < 5:
                            stars.extend(create_stars(1))  # Generate fewer stars in early levels
                        else:
                            stars.extend(create_stars(current_level))

                        star_add_increment = max(200, star_add_increment - 50)
                        star_count = 0

                    # Inside the game_state == GAME_STATE_PLAYING block

                    for star in stars.copy():  # Iterate through a copy of the stars list
                        star.y += STAR_VEL
                        if star.y > HEIGHT:
                            stars.remove(star)
                        else:
        # Update the player's rectangle
                            player_rect = pygame.Rect(player.x, player.y, PLAYER_WIDTH, PLAYER_HEIGHT)
                        if player_rect.colliderect(star):
            # Handle the collision (e.g., set 'hit' to True)
                            hit = True
                            stars.remove(star)  # Remove the star when there's a collision

# Rest of the code


                    if hit:
                        reset_game(player, current_level)
                        game_state = GAME_STATE_START_MENU
                        elapsed_time = round(elapsed_time)
                        name = input_player_name()
                        if name is not None:
                            app.add_score(name, elapsed_time)
                            app.load_user_scores()
                            restart_prompt = True
                            in_game = False
                            main_menu_music_playing = False
                            break
                        hit = False
                    else:
                        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
                            player.x -= PLAYER_VEL
                        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
                            player.x += PLAYER_VEL

                draw(player, elapsed_time, stars)

            elif game_state == GAME_STATE_SCOREBOARD:
                app.handle_events()
                root.deiconify()
                if not main_menu_music_playing:
                    play_main_menu_music()
                    main_menu_music_playing = True
                app.load_scores()
                pygame.time.delay(100)

            elif game_state == GAME_STATE_HIGH_SCORES:
                draw_scoreboard(app.get_top_scores())

        app.conn.close()
        if not run:
            pygame.mixer.music.stop()
            pygame.quit()
            sys.exit()

        if restart_prompt:
            result, elapsed_time, game_start_time, first_run = \
            prompt_restart_on_screen(player, current_level, elapsed_time, game_start_time, first_run)
            if result:
                game_state = GAME_STATE_PLAYING
            restart_prompt = False
        else:
            game_state = GAME_STATE_START_MENU
            restart_prompt = False

def prompt_restart_on_screen(player, current_level, elapsed_time, game_start_time, first_run):
    global restart_prompt, stars
    restart_prompt = True
    restart_text = FONT.render("Do you want to restart? (Y/N)", 1, "white")
    WIN.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
    
    stars = []  # Clear stars
    reset_game(player, current_level)
    elapsed_time = 0
    game_start_time = time.time()
    first_run = True
    pygame.display.update()  # Move the update here to ensure the prompt is displayed
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    restart_prompt = False
                    reset_game(player, current_level)
                    elapsed_time = 0
                    game_start_time = time.time()
                    first_run = True
                    return True, elapsed_time, game_start_time, first_run
                elif event.key == pygame.K_n:
                    restart_prompt = False
                    first_run = False
                    play_main_menu_music()
                    draw_start_menu(player)
                    pygame.display.update()
                    return False, elapsed_time, game_start_time, first_run

if __name__ == "__main__":
    # Initialize Pygame modules
    pygame.font.init()
    pygame.init()
    pygame.mixer.init()

    # Stop any music that might be playing
    pygame.mixer.music.stop()

    introduction_shown = False  # Variable to track if the introduction has been shown

    while not introduction_shown:
        # Draw the introduction without music
        draw_intro()
        pygame.display.update()
        pygame.time.delay(500)  # Display the introduction for 3 seconds
        introduction_shown = True

    play_main_menu_music()  # Play the main menu music after the introduction

    start_game()
