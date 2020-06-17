import pygame
from solver import solve, valid
import time
import create_sudoku
import sys

pygame.font.init()

class Button():
    def __init__(self, ai_settings, screen, msg,x,y):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.width, self.height = 200, 50
        self.button_color = (0, 255, 0)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 48)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center =(x,y)   #self.screen_rect.center
        self.prep_msg(msg)

    def prep_msg(self, msg):
        self.msg_image = self.font.render(msg, True, self.text_color,
                                          self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center
    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)


class Settings():

    def __init__(self):
        self.screen_width = 540
        self.screen_height = 600
        self.bg_color = (230, 230, 230)

class Grid:
    def __init__(self, rows, cols, width, height):
        self.board = create_sudoku.generate()
        print(self.board)
        self.rows = rows
        self.cols = cols
        self.cubes = [[Cube(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.width = width
        self.height = height
        self.model = None
        self.selected = None

    def update_model(self):
        self.model = [[self.cubes[i][j].fill for j in range(self.cols)] for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].fill == 0:
            self.cubes[row][col].set(val)
            self.update_model()

            if valid(self.model, val, (row, col)) and solve(self.model):
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False

    def sketch(self, val):
        row, col = self.selected

        self.cubes[row][col].set_temp(val)

    def draw(self, win):
        # Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(win, (0, 0, 0), (0, i * gap), (self.width, i * gap), thick)
            pygame.draw.line(win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(win)

    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].fill != 0:
            self.cubes[row][col].fill = 0
            self.cubes[row][col].set_temp(0)
        if self.cubes[row][col].temp != 0:
            self.cubes[row][col].set_temp(0)

    def click(self, pos):
        """
        :param: pos
        :return: (row, col)
        """
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return int(y), int(x)
        else:
            return None

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].fill == 0:
                    return False
        return True


class Cube:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.fill = value
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.fill == 0:
            text = fnt.render(str(self.temp), 1, (128, 128, 128))
            win.blit(text, (x + 5, y + 5))
        elif not (self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))
        elif not (self.fill == 0):
            text = fnt.render(str(self.fill), 1, (0, 255, 0))
            win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))
        if self.selected:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def set(self, val):
        self.fill = val

    def set_temp(self, val):
        self.temp = val


def redraw_window(win, board, time, strikes):
    win.fill((255, 255, 255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0, 0, 0))
    win.blit(text, (540 - 160, 560))
    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw grid and board
    board.draw(win)


def format_time(secs):
    sec = secs % 60
    minute = secs // 60
    hour = minute // 60

    mat = " " + str(minute) + ":" + str(sec)
    return mat

def gamestart(win):
    board = Grid(9, 9, 540, 540)
    key = None
    run = True
    start = time.time()
    strikes = 0
    while run:

        play_time = round(time.time() - start)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_BACKSPACE:
                    board.clear()
                    key = None
                if event.key == pygame.K_DELETE:
                    board.clear()
                    pygame.display.update()
                    key = None
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Success")
                        else:
                            print("Wrong")
                            strikes += 1
                        key = None

                        if board.is_finished():
                            print("Game over")
                            run = False
                            return 0;

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key is not None:
            board.sketch(key)

        redraw_window(win, board, play_time, strikes)
        pygame.display.update()

def main():
    ai_settings = Settings()
    win = pygame.display.set_mode(
        (ai_settings.screen_width, ai_settings.screen_height))
    win.fill(ai_settings.bg_color)
    pygame.display.set_caption("Sudoku")
    play_button = Button(ai_settings, win, "Play",270,150)
    quit_button = Button(ai_settings, win, "quit",270,450)
    play_button.draw_button()
    quit_button.draw_button()
    while 1:
        pygame.display.update()
        for event in pygame.event.get():
             if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if play_button.rect.collidepoint(mouse_x, mouse_y):
                    gamestart(win)

                    win.fill(ai_settings.bg_color)
                    play_button = Button(ai_settings, win, "restart", 270, 150)
                    play_button.draw_button()
                    quit_button.draw_button()
                if quit_button.rect.collidepoint(mouse_x, mouse_y):
                    return 0

main()
pygame.quit()
