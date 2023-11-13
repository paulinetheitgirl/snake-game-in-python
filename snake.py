import pygame
import sys
import random
from pygame.math import Vector2

SCREEN_UPDATE = pygame.USEREVENT
screen_update_interval = 150
cell_size = 40
cell_number = 20
board_width = cell_size * cell_number
board_height = cell_size * cell_number
screen = pygame.display.set_mode((board_width, board_height))
apple = pygame.image.load('assets/images/apple.png').convert_alpha()
GAME_OVER_MSG = "Game Over!"
CLOSE_MSG = "Press Esc to Go Back"


class Snake:
    def __init__(self,
                 _body=[Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)],
                 _direction=Vector2(1, 0)):
        self.body = _body
        # start moving to the right
        self.direction = _direction
        # flag to add new tail section
        self.new_section = False
        # head images
        self.head_up = pygame.image.load(
            'assets/images/head_up.png').convert_alpha()
        self.head_down = pygame.image.load(
            'assets/images/head_down.png').convert_alpha()
        self.head_left = pygame.image.load(
            'assets/images/head_left.png').convert_alpha()
        self.head_right = pygame.image.load(
            'assets/images/head_right.png').convert_alpha()
        self.head_image_dict = {
            (0, -1): self.head_up,
            (0, 1): self.head_down,
            (-1, 0): self.head_left,
            (1, 0): self.head_right
        }
        # body images
        self.body_horizontal = pygame.image.load(
            'assets/images/body_horizontal.png').convert_alpha()
        self.body_vertical = pygame.image.load(
            'assets/images/body_vertical.png').convert_alpha()
        self.body_image_dict = {
            (0, -1): self.body_vertical,
            (0, 1): self.body_vertical,
            (-1, 0): self.body_horizontal,
            (1, 0): self.body_horizontal
        }
        # corner images
        self.corner_up_from_left = pygame.image.load(
            'assets/images/body_tl.png').convert_alpha()
        self.corner_up_from_right = pygame.image.load(
            'assets/images/body_tr.png').convert_alpha()
        self.corner_down_from_left = pygame.image.load(
            'assets/images/body_bl.png').convert_alpha()
        self.corner_down_from_right = pygame.image.load(
            'assets/images/body_br.png').convert_alpha()
        # these track the coordinates of the previous and next section, so
        # there is always a difference of 1
        self.corner_image_dict = {
            (1, 1): self.corner_down_from_right,
            (-1, 1): self.corner_down_from_left,
            (1, -1): self.corner_up_from_right,
            (-1, -1): self.corner_up_from_left
        }
        # tail images
        self.tail_up = pygame.image.load(
            'assets/images/tail_up.png').convert_alpha()
        self.tail_down = pygame.image.load(
            'assets/images/tail_down.png').convert_alpha()
        self.tail_left = pygame.image.load(
            'assets/images/tail_left.png').convert_alpha()
        self.tail_right = pygame.image.load(
            'assets/images/tail_right.png').convert_alpha()
        self.tail_image_dict = {
            (0, -1): self.tail_down,
            (0, 1): self.tail_up,
            (-1, 0): self.tail_right,
            (1, 0): self.tail_left
        }

    def draw_snake(self):
        for index, section in enumerate(self.body):
            snake_section = pygame.Rect(section.x * cell_size,
                                        section.y * cell_size,
                                        cell_size,
                                        cell_size)
            if index == 0:
                screen.blit(self.head_image_dict.get(
                    tuple(self.direction)), snake_section)
            elif index == len(self.body) - 1:
                tail_direction = self.body[-2] - self.body[index]
                screen.blit(self.tail_image_dict.get(
                    tuple(tail_direction)), snake_section)
            else:
                next_pos_diff = self.body[index + 1] - self.body[index]
                previous_pos_diff = self.body[index - 1] - self.body[index]
                # try to get a corner image
                corner_image = self.corner_image_dict.get(
                    tuple(previous_pos_diff + next_pos_diff))
                if corner_image is not None:
                    screen.blit(corner_image, snake_section)
                else:
                    screen.blit(self.body_image_dict.get(
                        tuple(previous_pos_diff)), snake_section)

    def move_snake(self):
        if self.new_section == True:
            snake_copy = self.body[:]
            snake_copy.insert(0, snake_copy[0] + self.direction)
            self.body = snake_copy[:]
            self.new_section = False
        else:
            snake_copy = self.body[:-1]
            snake_copy.insert(0, snake_copy[0] + self.direction)
            self.body = snake_copy[:]

    def add_section(self):
        self.new_section = True


class Fruit:
    def __init__(self):
        self.x = random.randint(0, cell_number - 1)
        self.y = random.randint(0, cell_number - 1)
        self.pos = Vector2(self.x, self.y)
        self.crunch_sound = pygame.mixer.Sound("assets/sounds/crunch.wav")

    def draw_fruit(self):
        fruit_rect = pygame.Rect(
            self.pos.x * cell_size, self.pos.y * cell_size, cell_size, cell_size)
        screen.blit(apple, fruit_rect)

    def randomize(self):
        self.x = random.randint(0, cell_number - 1)
        self.y = random.randint(0, cell_number - 1)
        self.pos = Vector2(self.x, self.y)

    def play_sound(self):
        self.crunch_sound.play()


class Game:
    def __init__(self, font):
        self.snake = Snake()
        self.fruit = Fruit()
        self.can_move = True
        self.font = font

    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()

    def draw_objects(self):
        self.fruit.draw_fruit()
        self.snake.draw_snake()
        self.draw_score()

    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.play_sound()
            # make snake longer
            self.snake.add_section()
            # draw new fruit
            self.fruit.randomize()
            # don't place fruit on snake!
            if self.fruit.pos in self.snake.body[1:]:
                self.fruit.randomize()

    def check_fail(self):
        # if snake hit edges
        if (not 0 <=
            self.snake.body[0].x
            < cell_number) or (not 0 <=
                               self.snake.body[0].y
                               < cell_number):
            self.game_over()
        # if snake hit itself
        for section in self.snake.body[1:]:
            if section == self.snake.body[0]:
                self.game_over()

    def draw_score(self):
        score_text = str(f'Score: {len(self.snake.body) - 3}')
        score_surface = self.font.render(
            score_text, True, pygame.Color('black'))
        screen.blit(score_surface, (cell_size, cell_size))

    def game_over(self):
        self.can_move = False
        # disable timer
        pygame.time.set_timer(SCREEN_UPDATE, 0)


def play(update_func):
    # control snake movement rate
    pygame.time.set_timer(SCREEN_UPDATE, screen_update_interval)
    # Create the font (only needs to be done once)
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    main_game = Game(font)
    close_surface = small_font.render(CLOSE_MSG, True, pygame.Color('black'))
    game_over_dialog = pygame.Surface((board_width, board_height / 2))
    game_over_message = font.render(
        GAME_OVER_MSG, True, pygame.Color(175, 215, 70))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == SCREEN_UPDATE:
                main_game.update()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    update_func(False)
                if main_game.can_move:
                    if event.key == pygame.K_UP:
                        if main_game.snake.direction.y != 1:
                            main_game.snake.direction = Vector2(0, -1)
                    if event.key == pygame.K_DOWN:
                        if main_game.snake.direction.y != -1:
                            main_game.snake.direction = Vector2(0, 1)
                    if event.key == pygame.K_LEFT:
                        if main_game.snake.direction.x != 1:
                            main_game.snake.direction = Vector2(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        if main_game.snake.direction.x != -1:
                            main_game.snake.direction = Vector2(1, 0)

        screen.fill((175, 215, 70))
        main_game.draw_objects()
        screen.blit(close_surface, close_surface.get_rect(
            topright=(screen.get_rect().topright)))
        # game-over screen layer
        if not main_game.can_move:
            game_over_dialog.fill(pygame.Color('black'))
            # center the message
            message_rect = game_over_message.get_rect(
                center=(game_over_dialog.get_rect().center))
            game_over_dialog.blit(game_over_message, message_rect)
            screen.blit(game_over_dialog, (0, board_height / 4))

        pygame.display.update()
