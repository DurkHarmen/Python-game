import pygame
import time
import random
import tkinter as tk
from tkinter import simpledialog
import psycopg2
import tkinter.messagebox as messagebox

pygame.font.init()
pygame.init()
pygame.mixer.init()

# Get the current screen width and height
screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h

# Create a Pygame display surface
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if WIDTH >= 1920 else 0)
pygame.display.set_caption("Escape the Matrix")

BG = pygame.transform.scale(pygame.image.load("game/images/bg.jpg"), (WIDTH, HEIGHT))

PLAYER_WIDTH = WIDTH // 24
PLAYER_HEIGHT = HEIGHT // 6
PLAYER_VEL = WIDTH // 192

STAR_WIDTH = WIDTH // 96
STAR_HEIGHT = HEIGHT // 27
STAR_VEL = WIDTH // 320

HIT_SOUND = pygame.mixer.Sound("game/sound/hit_sound.mp3")  # Replace with the path to your hit sound file

GAME_STATE_START_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_SCOREBOARD = 3
GAME_STATE_HIGH_SCORES = 4

game_state = GAME_STATE_START_MENU

FONT_SIZE = min(WIDTH // 32, HEIGHT // 18)
FONT = pygame.font.SysFont("comicsans", FONT_SIZE)

LOGO = pygame.image.load("game/gameintro.jpg")

# Initialize Pygame's mixer module and load the background music
pygame.mixer.music.load("game/sound/gamesound.mp3")
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(-1)

def draw(player, elapsed_time, stars, intro=False):
    WIN.blit(BG, (0, 0))

    if not intro:
        time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
        WIN.blit(time_text, (10, 10))

        pygame.draw.rect(WIN, "yellow", player)

        for star in stars:
            pygame.draw.rect(WIN, "white", star)

    pygame.display.update()

class Scoreboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Scoreboard")

        # Connect to the PostgreSQL database
        self.conn = psycopg2.connect(
            dbname="game_scores",
            user="postgres",
            password="3dRtva!",
            host="localhost"  # Change this if your database is hosted elsewhere
        )
        self.cursor = self.conn.cursor()

        # Create the "high_scores" table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS high_scores (
                                id SERIAL PRIMARY KEY,
                                name TEXT,
                                time REAL
                            )''')
        self.conn.commit()

        # Create widgets and update methods as needed
        self.score_label = tk.Label(root, text="Top Three High Scores")
        self.score_label.pack()

        self.score_display = tk.Label(root, text="", justify="left")
        self.score_display.pack()

    def load_scores(self):
        # Fetch scores from the database and update the display
        self.cursor.execute('''SELECT name, time FROM high_scores
                              ORDER BY time DESC
                              LIMIT 3''')
        top_scores = self.cursor.fetchall()

        display_text = ""
        for i, (name, time) in enumerate(top_scores):
            display_text += f"{i + 1}. {name}: {time} seconds\n"
        self.score_display.config(text=display_text)

    def add_score(self, name, time):
        # Insert a new score into the database
        self.cursor.execute("INSERT INTO high_scores (name, time) VALUES (%s, %s)", (name, time))
        self.conn.commit()

    def get_top_scores(self):
        # Fetch the top scores from the database
        self.cursor.execute('''SELECT name, time FROM high_scores
                              ORDER BY time DESC
                              LIMIT 3''')
        top_scores = self.cursor.fetchall()
        return top_scores

    def handle_events(self):
        global game_state  # Declare 'game_state' as global to modify its value

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Handle "Esc" key press (return to main menu)
                    game_state = GAME_STATE_START_MENU
                    self.root.withdraw()
                elif event.key == pygame.K_m:  # Add this block to return to the main menu
                    game_state = GAME_STATE_START_MENU
                    self.root.withdraw()

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

    pygame.display.update()

def reset_game(player):
    global game_state, stars, hit, game_start_time

    game_state = GAME_STATE_START_MENU
    hit = False
    game_start_time = None
    stars.clear()

    player.x = WIDTH // 3
    player.y = HEIGHT - PLAYER_HEIGHT


def create_stars():
    stars = []  # Create a new list for stars
    for _ in range(3):
        star_x = random.randint(0, WIDTH - STAR_WIDTH)
        star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
        stars.append(star)
    return stars

def menu_loop(player):
    global star_count, star_add_increment, stars, hit, game_state  # Use the global variables

    menu_running = True

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        draw_start_menu()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            reset_game(player)  # Reset the game state, player position, elapsed time, and stars
            return GAME_STATE_PLAYING
        elif keys[pygame.K_s]:
            return GAME_STATE_HIGH_SCORES
        elif keys[pygame.K_q]:
            pygame.quit()
            quit()
        elif keys[pygame.K_m]:
            reset_game(player)  # Reset the game state, player position, elapsed time, and stars
            game_state = GAME_STATE_START_MENU  # Add this line to ensure the correct game state

def main():
    global game_state, stars

    run = True
    introduction = True

    intro_timer = 0
    intro_duration = 10

    player = pygame.Rect(WIDTH // 3, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    clock = pygame.time.Clock()
    FPS = 60

    star_add_increment = 2000
    star_count = 0

    stars = []  # Initialize the stars list
    hit = False

    game_start_time = None

    # Create a Scoreboard object
    root = tk.Tk()
    root.withdraw()  # Hide the root window for the scoreboard

    app = Scoreboard(root)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        # Reset the game when 'm' key is pressed or after death
        if keys[pygame.K_m]:
            game_state = GAME_STATE_START_MENU
            stars.clear()
            hit = False
            reset_game(player)
            game_state = menu_loop(player)

        if game_state == GAME_STATE_START_MENU:

            if introduction:
                draw_intro()
                intro_timer += 1
                if intro_timer >= intro_duration * FPS:
                    introduction = False
            else:
                game_state = menu_loop(player)  # Pass the player object to menu_loop
                game_start_time = None

        elif game_state == GAME_STATE_PLAYING:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_state = GAME_STATE_START_MENU
                    reset_game(player)  # Reset the game when transitioning to the main menu
                    break  # Exit the loop immediately after processing ESC key

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
                        HIT_SOUND.play()  # Play the hit sound effect
                        break

                if hit:
                    reset_game(player)  # Reset the game state, stars, and player position
                    game_state = GAME_STATE_START_MENU
                    elapsed_time = round(elapsed_time)
                    name = input_player_name()
                    if name is not None:
                        app.add_score(name, elapsed_time)
                        app.load_scores()
                    hit = False
                else:
                    if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
                        player.x -= PLAYER_VEL
                    if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
                        player.x += PLAYER_VEL

            draw(player, elapsed_time, stars)

        elif game_state == GAME_STATE_SCOREBOARD:
            app.handle_events()  # Call handle_events in the scoreboard object
            root.deiconify()
            app.load_scores()
            pygame.time.delay(100)

        elif game_state == GAME_STATE_HIGH_SCORES:
            draw_scoreboard(app.get_top_scores())

    # Close the PostgreSQL database connection
    app.conn.close()

    pygame.mixer.music.stop()
    pygame.quit()

def input_player_name():
    root = tk.Tk()
    root.withdraw()
    
    while True:
        name = simpledialog.askstring("Enter Your Name", "Enter your name:")
        
        if name is None:
            # User clicked Cancel or closed the dialog
            return None  # Return None to indicate cancellation

        name = name.strip()  # Remove leading and trailing spaces
        
        if name:
            return name  # Return the non-empty name
        
        # Show an error message if the name is empty
        messagebox.showerror("Error", "Name cannot be empty. Please enter your name.")

if __name__ == "__main__":
    main()
