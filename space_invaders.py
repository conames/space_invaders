import pygame
import random
import math
import sys
from pygame import mixer

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width, screen_height = 1024, 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Falcon Invaders: Space Battle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.Font('freesansbold.ttf', 32)
over_font = pygame.font.Font('freesansbold.ttf', 64)

# Load assets
background = pygame.image.load('background.png')
player_img = pygame.image.load('player.png')
player_img = pygame.transform.scale(player_img, (64, 64))
enemy_img = pygame.image.load('enemy.png')
enemy_img = pygame.transform.scale(enemy_img, (50, 50))
bullet_img = pygame.image.load('bullet.png')
ufo_icon = pygame.image.load('ufo.png')
pygame.display.set_icon(ufo_icon)

# Load sounds
mixer.music.load('background.wav')
mixer.music.play(-1)
laser_sound = mixer.Sound('laser.wav')
explosion_sound = mixer.Sound('explosion.wav')

# Game states
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"

# Initialize variables
state = MENU
lives = 3
score = 0
high_score = 0
level = 1
player_speed = 5
player_x = (screen_width - 64) // 2
player_y = 700
player_x_change = 0
bullet_speed = -10
bullet_state = "ready"
bullet_x, bullet_y = 0, player_y

# Enemy setup
num_of_enemies = 6
enemy_speed = 2
enemies = []

for i in range(num_of_enemies):
    enemies.append({
        'img': enemy_img,
        'x': random.randint(0, screen_width - 50),
        'y': random.randint(50, 150),
        'x_change': enemy_speed,
        'y_change': 40,
        'alive': True
    })

# Collision detection using Rect
def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    enemy_rect = pygame.Rect(enemy_x, enemy_y, 50, 50)  # Assuming enemies are 50x50
    bullet_rect = pygame.Rect(bullet_x, bullet_y, bullet_img.get_width(), bullet_img.get_height())
    return enemy_rect.colliderect(bullet_rect)

# Check if all enemies are defeated
def all_enemies_defeated():
    return all(not enemy['alive'] for enemy in enemies)

# Level progression
def next_level():
    global level, enemy_speed, num_of_enemies, enemies
    level += 1
    enemy_speed += 1
    num_of_enemies += 2  # Add more enemies
    for _ in range(2):  # Add new enemies
        enemies.append({
            'img': enemy_img,
            'x': random.randint(0, screen_width - 50),
            'y': random.randint(50, 150),
            'x_change': enemy_speed,
            'y_change': 40,
            'alive': True
        })
    # Reset existing enemies
    for enemy in enemies:
        enemy['x'] = random.randint(0, screen_width - 50)
        enemy['y'] = random.randint(50, 150)
        enemy['alive'] = True

# Reset game
def reset_game():
    global lives, score, level, player_x, player_y, enemies, state, enemy_speed
    lives = 3
    score = 0
    level = 1
    player_x, player_y = (screen_width - 64) // 2, 700
    enemy_speed = 2
    enemies.clear()
    for _ in range(num_of_enemies):
        enemies.append({
            'img': enemy_img,
            'x': random.randint(0, screen_width - 50),
            'y': random.randint(50, 150),
            'x_change': enemy_speed,
            'y_change': 40,
            'alive': True
        })
    state = MENU  # Return to menu

# Show text on the screen
def show_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    if center:
        x -= surface.get_width() // 2
        y -= surface.get_height() // 2
    screen.blit(surface, (x, y))

# Fire bullet
def fire_bullet():
    global bullet_state, bullet_x, bullet_y
    if bullet_state == "ready":
        bullet_state = "fire"
        bullet_x = player_x + 16
        bullet_y = player_y
        laser_sound.play()

# Main game loop
running = True
while running:
    screen.fill(BLACK)
    screen.blit(background, (0, 0))

    if state == MENU:
        show_text("Falcon Invaders", over_font, GOLD, screen_width // 2, 200, center=True)
        show_text("Press ENTER to Start", font, WHITE, screen_width // 2, 400, center=True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    state = PLAYING
                if event.key == pygame.K_q:
                    running = False

    elif state == PLAYING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player_x_change = -player_speed
                if event.key == pygame.K_RIGHT:
                    player_x_change = player_speed
                if event.key == pygame.K_SPACE:
                    fire_bullet()
                if event.key == pygame.K_p:
                    state = PAUSED
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    player_x_change = 0

        player_x += player_x_change
        player_x = max(0, min(screen_width - player_img.get_width(), player_x))
        screen.blit(player_img, (player_x, player_y))

        if bullet_state == "fire":
            screen.blit(bullet_img, (bullet_x, bullet_y))
            bullet_y += bullet_speed
            if bullet_y < 0:
                bullet_state = "ready"
                bullet_y = player_y

        for enemy in enemies:
            if enemy['alive']:
                enemy['x'] += enemy['x_change']
                if enemy['x'] <= 0 or enemy['x'] >= screen_width - 50:
                    enemy['x_change'] *= -1
                    enemy['y'] += enemy['y_change']
                
                if is_collision(enemy['x'], enemy['y'], bullet_x, bullet_y):
                    explosion_sound.play()
                    bullet_state = "ready"
                    bullet_y = player_y
                    score += 10
                    enemy['alive'] = False

                if enemy['y'] > player_y:
                    lives -= 1
                    enemy['alive'] = False
                    enemy['x'] = random.randint(0, screen_width - 50)
                    enemy['y'] = random.randint(50, 150)

                screen.blit(enemy['img'], (enemy['x'], enemy['y']))

        if all_enemies_defeated():
            show_text(f"Level {level + 1}", font, GOLD, screen_width // 2, screen_height // 2, center=True)
            pygame.display.update()
            pygame.time.delay(2000)
            next_level()

        if lives <= 0:
            state = GAME_OVER

        show_text(f"Score: {score}", font, WHITE, 10, 10)
        show_text(f"Lives: {lives}", font, WHITE, 10, 50)
        show_text(f"Level: {level}", font, WHITE, 10, 90)

    elif state == PAUSED:
        show_text("Paused", over_font, GOLD, screen_width // 2, 200, center=True)
        show_text("Press P to Resume", font, WHITE, screen_width // 2, 400, center=True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    state = PLAYING

    elif state == GAME_OVER:
        show_text("Game Over", over_font, RED, screen_width // 2, 200, center=True)
        show_text("Press R to Restart or Q to Quit", font, WHITE, screen_width // 2, 400, center=True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                if event.key == pygame.K_q:
                    running = False

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
