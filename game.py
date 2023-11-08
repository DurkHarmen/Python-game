import pygame

# Initialize pygame
pygame.init()

# Load your custom icon
icon = pygame.image.load('_internal/gameintro.ico')

# Set the application icon
pygame.display.set_icon(icon)


import pygame
import time
import random
import tkinter as tk
from tkinter import simpledialog
import psycopg2
import sqlite3
import tkinter.messagebox as messagebox


# Initialize Pygame modules
pygame.font.init()
pygame.init()
pygame.mixer.init()

# Get the current screen width and height
screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h

# Create a Pygame display surface
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape the Matrix")

def play_main_menu_music():
    global main_menu_music_playing
    if not main_menu_music_playing:
        pygame.mixer.music.load("_internal/sound/lobbysound.mp3")
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)  # Play the music in a loop
        main_menu_music_playing = True

# Load and scale the background image
BG = pygame.transform.scale(pygame.image.load("_internal/images/bg.jpg"), (WIDTH, HEIGHT))

# Define player properties
PLAYER_WIDTH = WIDTH // 24
PLAYER_HEIGHT = HEIGHT // 6
PLAYER_VEL = WIDTH // 192

# Define star properties
STAR_WIDTH = WIDTH // 96
STAR_HEIGHT = HEIGHT // 27
STAR_VEL = WIDTH // 320

# Load hit sound effect
HIT_SOUND = pygame.mixer.Sound("_internal/sound/hit_sound.mp3")

# Define game states
GAME_STATE_START_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_SCOREBOARD = 3
GAME_STATE_HIGH_SCORES = 4

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
LOGO = pygame.image.load("_internal/images/gameintro.jpg")

def play_gameplay_music():
    pygame.mixer.music.load("_internal/sound/gamesound.mp3")
    pygame.mixer.music.set_volume(0.8)
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
        self.root.title("Scoreboard")
        self.conn = sqlite3.connect('game_scores.db')  # Create a connection to the SQLite database
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS high_scores (
                id INTEGER PRIMARY KEY,
                name TEXT,
                time REAL
            )
        ''')
        self.conn.commit()
        self.load_scores()  # Call the method to load scores at initialization

    def load_scores(self):
        self.cursor.execute('''
            SELECT name, time FROM high_scores
            ORDER BY time DESC
            LIMIT 3
        ''')
        top_scores = self.cursor.fetchall()

        display_text = ""
        for i, (name, time) in enumerate(top_scores):
            display_text += f"{i + 1}. {name}: {time} seconds\n"
        print(display_text)  # Displaying scores for testing purposes

    def add_score(self, name, time):
        self.cursor.execute("INSERT INTO high_scores (name, time) VALUES (?, ?)", (name, time))
        self.conn.commit()

    def get_top_scores(self):
        self.cursor.execute('''
            SELECT name, time FROM high_scores
            ORDER BY time DESC
            LIMIT 3
        ''')
        top_scores = self.cursor.fetchall()
        return top_scores

    def handle_events(self):
        global game_state

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
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
def draw_start_menu():
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


# Function to create stars
def create_stars():
    new_stars = []
    for _ in range(3):
        star_x = random.randint(0, WIDTH - STAR_WIDTH)
        star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
        new_stars.append(star)
    return new_stars


def menu_loop(player, elapsed_time):
    global stars, hit, game_state, running, game_over, game_start_time, paused, paused_time, main_menu_music_playing

    menu_running = True

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not paused:
                        pygame.mixer.music.stop()
                        elapsed_time = reset_game(player)
                        stars.clear()
                        stars.extend(create_stars())
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
                    elapsed_time = reset_game(player)
                    return GAME_STATE_HIGH_SCORES

                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()

                elif event.key == pygame.K_m:
                    if game_state != GAME_STATE_START_MENU:
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.unpause()
                        game_state = GAME_STATE_START_MENU
                        game_start_time = None
                        running = True
                        return

        if not paused:
            draw_start_menu()
            pygame.display.update()

    return elapsed_time


# Function to reset the game
def reset_game(player):
    global game_state, hit, game_start_time

    game_state = GAME_STATE_START_MENU
    hit = False

    if not game_start_time:
        game_start_time = time.time()

    stars.clear()
    stars.extend(create_stars())

    player.x = WIDTH // 3
    player.y = HEIGHT - PLAYER_HEIGHT


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


def start_game():
    global game_state, stars, elapsed_time, restart_prompt, game_start_time, paused_time, main_menu_music_playing
    game_start_time = None
    in_game = False
    restart_prompt = False
    main_menu_music_playing = False

    elapsed_time = 0
    paused_time = 0

    while True:
        run = True
        introduction = True

        intro_timer = 0
        intro_duration = 5

        paused = False

        player = pygame.Rect(WIDTH // 3, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        clock = pygame.time.Clock()
        FPS = 60

        star_add_increment = 2000
        star_count = 0

        stars = []
        hit = False

        first_run = True

        root = tk.Tk()
        root.withdraw()

        app = Scoreboard(root)

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
                    reset_game(player)
                    game_state = menu_loop(player, elapsed_time)
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
                        game_state = menu_loop(player, elapsed_time)
                        game_start_time = None
                    else:
                        draw_start_menu()
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

                    if star_count > star_add_increment:
                        for _ in range(3):
                            star_x = random.randint(0, WIDTH - STAR_WIDTH)
                            star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
                            stars.append(star)

                        star_add_increment = max(200, star_add_increment - 50)
                        star_count = 0

                    for star in stars[:]:
                        star.y += STAR_VEL
                        if star.y > HEIGHT:
                            stars.remove(star)
                        elif star.y + star.height >= player.y and star.colliderect(player):
                            stars.remove(star)
                            hit = True
                            HIT_SOUND.play()
                            break

                    if hit:
                        reset_game(player)
                        game_state = GAME_STATE_START_MENU
                        elapsed_time = round(elapsed_time)
                        name = input_player_name()
                        if name is not None:
                            app.add_score(name, elapsed_time)
                            app.load_scores()
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

        if restart_prompt:
            result, elapsed_time, game_start_time, first_run = \
                prompt_restart_on_screen(player, elapsed_time, game_start_time, first_run)
            if result:
                game_state = GAME_STATE_PLAYING
            restart_prompt = False
        else:
            game_state = GAME_STATE_START_MENU
            restart_prompt = False

def prompt_restart_on_screen(player, elapsed_time, game_start_time, first_run):
    global restart_prompt
    restart_prompt = True
    restart_text = FONT.render("Do you want to restart? (Y/N)", 1, "white")
    WIN.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    restart_prompt = False
                    reset_game(player)
                    elapsed_time = 0
                    game_start_time = time.time()
                    first_run = True
                    return True, elapsed_time, game_start_time, first_run
                elif event.key == pygame.K_n:
                    restart_prompt = False
                    first_run = False
                    play_main_menu_music()
                    draw_start_menu()
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
