import pygame
import sys
from pygame.math import Vector2
import snake

cell_size = 40
cell_number = 20
board_width = cell_size * cell_number
board_height = cell_size * cell_number
screen = pygame.display.set_mode((board_width, board_height))
is_playing = False
clock = pygame.time.Clock()
frame_rate = 60
apple = pygame.image.load('assets/images/apple.png').convert_alpha()

# preload sounds
# for default values see https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.pre_init
pygame.mixer.pre_init()
pygame.init()
pygame.display.set_caption("Classic Snake Game")
default_font = pygame.font.Font(pygame.font.get_default_font(), 36)
start_message = default_font.render(
    "Press Space to Start", True, pygame.Color('white'))
snake_y_pos = (cell_number - 1) / 2
static_snake = snake.Snake(_body=[Vector2(cell_number - 3, snake_y_pos), Vector2(cell_number - 2, snake_y_pos), Vector2(cell_number - 1, snake_y_pos)],
                           _direction=Vector2(-1, 0))


def update_state(_is_playing):
    global is_playing
    is_playing = _is_playing
    main_menu()


def play_game():
    snake.play(update_state)


def main_menu():
    global is_playing
    while not is_playing:
        screen.fill(pygame.Color('black'))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not is_playing:
                    is_playing = True
                    play_game()
                if event.key == pygame.K_ESCAPE:
                    if not is_playing:
                        pygame.quit()
                        sys.exit()
                    is_playing = False
                    main_menu()

        apple_rect = apple.get_rect(center=screen.get_rect().center)
        screen.blit(apple, apple_rect)
        screen.blit(start_message, start_message.get_rect(
            midtop=(apple_rect.centerx, apple_rect.centery + 36)))
        static_snake.draw_snake()
        pygame.display.update()


# makes screen update timing consistent
clock.tick(frame_rate)
main_menu()
