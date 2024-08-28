import sys
from datetime import datetime, timedelta

import pygame
import json


class DrawObject:
    def __init__(self, screen, x_pos, y_pos, color):
        self.screen = screen
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = color


class MinuteSquare(DrawObject):
    def __init__(self, screen, x_pos, y_pos, color, size):
        super().__init__(screen, x_pos, y_pos, color)
        self.size = size
        self.draw()

    def draw(self):
        pygame.draw.rect(self.screen, self.color, (self.x_pos, self.y_pos, self.size, self.size))


class Canvas:
    def __init__(self, width=540, height=960, data_file=None):
        pygame.init()
        pygame.display.set_caption('S&P500 Recap')
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Lucida Console', 24)
        self.scene = 1

        if data_file is not None:
            self.data_filepath = data_file
            with open(self.data_filepath, 'r') as json_file:
                self.data = json.load(json_file)
        else:
            print("No data filepath entered.")
            sys.exit()

    def draw(self):
        if self.scene == 1:
            self.screen.fill((0, 0, 0))
            self.draw_squares()
        pygame.display.flip()

    def draw_timeline(self, start_pos, end_pos, elapsed_time):
        pygame.draw.line(self.screen, (255,255,255), start_pos, end_pos, 3)

        draw_time = (datetime.strptime("09:30", "%H:%M") + timedelta(minutes=elapsed_time)).strftime("%I:%M %p")
        time_text = self.font.render(draw_time, True, (255, 255, 255))
        time_rect = time_text.get_rect(center=(self.width / 2, 100))
        self.screen.blit(time_text, time_rect)

        for m in range(elapsed_time):
            if (m+30)%60 == 0:
                hour_tick_x = start_pos[0]+m
                pygame.draw.line(self.screen, (255, 255, 255), (hour_tick_x, start_pos[1]-12), (hour_tick_x, start_pos[1]+12), 1)

        pygame.draw.line(self.screen, (255, 255, 255), (start_pos[0], start_pos[1] - 8), (start_pos[0], start_pos[1] + 8))
        if elapsed_time == 390:
            pygame.draw.line(self.screen, (255, 255, 255), (end_pos[0], end_pos[1] - 8), (end_pos[0], end_pos[1] + 8))


    def draw_squares(self):
        square_size = 1
        stocks = list(self.data.keys())
        minutes = self.data[stocks[0]]['minutes']
        minutes.append("16:00")

        start_x = (self.width - (len(minutes) * square_size)) / 2
        start_y = (self.height - (len(stocks) * square_size)) / 2

        # draw squares and time
        for x in range(len(minutes)):
            self.screen.fill((0, 0, 0), (0, 0, self.width, 150))

            # draw timeline
            self.draw_timeline((start_x, start_y - 50), (start_x + x, start_y - 50), x)

            if x!= len(minutes)-1:
                for y in range(len(stocks)):
                    try:
                        percent = self.data[stocks[y]]['percents'][x]
                    except IndexError as e:
                        print(f"IndexError: {e}")
                        print(f"Stock: {stocks[y]}, x: {x}, y: {y}")
                        percent = 0
                    norm = abs(percent) / 0.05 if abs(percent) < 0.05 else 1
                    color = (0, int(norm * 255), 0) if percent > 0 else (int(norm * 255), 0, 0)
                    pygame.draw.rect(self.screen, color,
                                     pygame.Rect(start_x + x * square_size, start_y + y * square_size, square_size,
                                                 square_size))

            pygame.display.flip()
            self.clock.tick(40)
            self.scene = 2

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.draw()
        pygame.quit()
