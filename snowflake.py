from pygame import gfxdraw
import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Window parameters
WIDTH, HEIGHT = 738, 918
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snowflake Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

BLUR_INTENSITY = 8  # Number of layers for the blur effect
BLUR_STEP = 2       # Step for increasing size for each layer
BLUR_ALPHA_STEP = 100 # Step for decreasing transparency for each layer

# Load background
background_image = pygame.image.load("background.jpg")
main_background_image = pygame.image.load("main_background.jpg")
score_image = pygame.image.load("score.jpg")
# Font
font = pygame.font.Font(None, 36)

# Snowflake parameters
snowflakes = []
snowflake_speed = 1.2
max_snowflakes = 10
missed_snowflakes = 5
max_missed = 0
destroyed_snowflakes = 0

# Timer for creating snowflakes
CREATE_SNOWFLAKE = pygame.USEREVENT + 1
pygame.time.set_timer(CREATE_SNOWFLAKE, 1000)

# Game state
game_state = "start"  # "start", "playing", "scores"

# Score table
score_table = []


def draw_text(text, x, y, size=36, color=WHITE, center=False):
    """Function to display text."""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def handle_start_screen():
    """Handles the start screen."""
    global game_state
    screen.blit(main_background_image, (0, 0))

    # Button coordinates
    start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 60)
    scores_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 60)

    # Draw buttons
    pygame.draw.rect(screen, WHITE, start_button, border_radius=10)
    pygame.draw.rect(screen, WHITE, scores_button, border_radius=10)
    draw_text("Start Game", start_button.centerx, start_button.centery, size=36, color=BLACK, center=True)
    draw_text("Score Table", scores_button.centerx, scores_button.centery, size=36, color=BLACK, center=True)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if start_button.collidepoint(mouse_pos):  # If "Start Game" button is clicked
                game_state = "playing"
            elif scores_button.collidepoint(mouse_pos):  # If "Score Table" button is clicked
                game_state = "scores"

def handle_game_over_screen():
    """Handles the game over screen."""
    global game_state

    screen.blit(main_background_image, (0, 0))
    draw_text("Game Over", WIDTH // 2, HEIGHT // 4, size=64, color=RED, center=True)
    draw_text(f"Your Score: {destroyed_snowflakes}", WIDTH // 2, HEIGHT // 2 - 50, size=48, color=WHITE, center=True)

    # "Play Again" button
    play_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 60)
    pygame.draw.rect(screen, WHITE, play_again_button, border_radius=10)
    draw_text("Play Again", play_again_button.centerx, play_again_button.centery, size=36, color=BLACK, center=True)

    # "Main Menu" button
    main_menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 60)
    pygame.draw.rect(screen, WHITE, main_menu_button, border_radius=10)
    draw_text("Main Menu", main_menu_button.centerx, main_menu_button.centery, size=36, color=BLACK, center=True)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if play_again_button.collidepoint(mouse_pos):  # Restart the game
                reset_game()  # Reset game parameters
                game_state = "playing"  # Switch to the game screen
            elif main_menu_button.collidepoint(mouse_pos):  # Return to main menu
                reset_game()  # Reset parameters
                game_state = "start"  # Return to the main menu

def reset_game():
    """Resets the game parameters for a new start."""
    global snowflakes, missed_snowflakes, destroyed_snowflakes, max_snowflakes, snowflake_speed
    snowflakes = []
    missed_snowflakes = 5  # Restore lives
    destroyed_snowflakes = 0  # Reset score
    max_snowflakes = 10  # Restore initial number of snowflakes
    snowflake_speed = 1.2  # Reset speed

def handle_score_screen():
    """Handles the score table screen."""
    global game_state
    screen.blit(score_image, (0, 0))
    draw_text("Score Table", WIDTH // 2, HEIGHT // 4, size=64, color=WHITE, center=True)

    if not score_table:
        draw_text("No scores yet!", WIDTH // 2, HEIGHT // 2, size=48, color=WHITE, center=True)
    else:
        for i, score in enumerate(score_table[:10], start=1):
            # Coordinates and size of the rectangle
            rect_width, rect_height = 400, 40
            rect_x = WIDTH // 2 - rect_width // 2
            rect_y = HEIGHT // 2 + i * 50 - rect_height // 2
            
            # Debug information (output coordinates to the console)
            print(f"Drawing rect at ({rect_x}, {rect_y}), size ({rect_width}, {rect_height})")

            # Draw white rectangle
            pygame.draw.rect(screen, WHITE, (rect_x, rect_y, rect_width, rect_height), border_radius=10)
            
            # Draw text on top of the rectangle
            draw_text(f"{i}. {score} points", WIDTH // 2, rect_y + rect_height // 2, size=36, color=BLACK, center=True)

    draw_text("Press ESC to return to the main menu", WIDTH // 2, HEIGHT - 50, size=36, color=RED, center=True)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game_state = "start"

def draw_blurred_snowflake(surface, color, x, y, size):
    """Draws a snowflake with a blur effect."""
    for i in range(1, BLUR_INTENSITY + 1):
        alpha = max(255 - i * BLUR_ALPHA_STEP, 50)
        blurred_color = (color[0], color[1], color[2], alpha)
        gfxdraw.filled_circle(surface, int(x), int(y), int(size + i * BLUR_STEP), blurred_color)
    gfxdraw.filled_circle(surface, int(x), int(y), int(size), color)

# Main game loop
clock = pygame.time.Clock()

def handle_game_screen():
    """Handles the game screen."""
    global snowflakes, missed_snowflakes, destroyed_snowflakes, game_state

    screen.blit(background_image, (0, 0))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == CREATE_SNOWFLAKE:
            for _ in range(random.randint(1, 4)):
                if len(snowflakes) < max_snowflakes:
                    x = random.randint(0, WIDTH)
                    size = random.randint(10, 20)
                    amplitude = random.randint(2, 5)
                    frequency = random.uniform(0.005, 0.02)
                    snowflakes.append([x, 0, size, amplitude, frequency])
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for snowflake in snowflakes:
                enlarged_hitbox = 10
                if snowflake[0] - snowflake[2] - enlarged_hitbox < mouse_pos[0] < snowflake[0] + snowflake[2] + enlarged_hitbox and \
                   snowflake[1] - snowflake[2] - enlarged_hitbox < mouse_pos[1] < snowflake[1] + snowflake[2] + enlarged_hitbox:
                    snowflakes.remove(snowflake)
                    destroyed_snowflakes += 1
                    break

    # Update snowflakes
    new_snowflakes = []
    for snowflake in snowflakes:
        snowflake[1] += snowflake_speed
        snowflake[0] += math.sin(snowflake[1] * snowflake[4]) * snowflake[3] * 0.5

        if 0 <= snowflake[0] <= WIDTH and snowflake[1] <= HEIGHT:
            new_snowflakes.append(snowflake)
        elif snowflake[1] > HEIGHT:
            if missed_snowflakes > max_missed:
                missed_snowflakes -= 1

    snowflakes = new_snowflakes

    # Draw snowflakes
    for snowflake in snowflakes:
        draw_blurred_snowflake(screen, WHITE, snowflake[0], snowflake[1], snowflake[2])

    # Display score
    draw_text(f"Destroyed: {destroyed_snowflakes}", 10, 10)
    draw_text(f"HP: {missed_snowflakes}", 10, 50)

    # Check for game over
    if missed_snowflakes <= max_missed:
        score_table.append(destroyed_snowflakes)
        score_table.sort(reverse=True)
        game_state = "game_over"  # Switch to Game Over screen

while True:
    if game_state == "start":
        handle_start_screen()
    elif game_state == "playing":
        handle_game_screen()
    elif game_state == "scores":
        handle_score_screen()
    elif game_state == "game_over":
        handle_game_over_screen()

    pygame.display.flip()
    clock.tick(60)
