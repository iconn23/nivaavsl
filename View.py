import sys
import os
import time

import pygame
import json
import DrawObject


class Canvas:
    def __init__(self, width=540, height=960, data_filepath=None):
        pygame.init()
        pygame.display.set_caption('S&P 500 Recap')
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Lucida Console', 24)
        self.scene = 1
        self.draw_objects = {}

        if data_filepath is not None:
            self.data_filepath = data_filepath
            if os.path.exists(self.data_filepath):
                with open(self.data_filepath, 'r') as json_file:
                    self.data = json.load(json_file)
                print(f"Data loaded from {self.data_filepath}")
            else:
                print(f"File {self.data_filepath} does not exist.")
                sys.exit()
        else:
            print("No data filepath entered.")
            sys.exit()

        self.stocks = list(self.data.keys())

    def draw(self):
        if self.scene == 1:
            self.screen.fill((0, 0, 0))
            self.draw_scene_1()
        elif self.scene ==2:
            self.draw_scene_2()
        pygame.display.flip()

    def draw_scene_1(self):
        square_size = 1
        minutes = self.data[self.stocks[0]]['minutes'][:]
        minutes.append("16:00")
        num_minutes = len(minutes)
        num_stocks = len(self.stocks)

        start_x = (self.width - (len(minutes) * square_size)) // 2
        start_y = (self.height - (len(self.stocks) * square_size)) // 2

        main_border = DrawObject.ObjectBorder(self, thickness=1, color=(255,255,255), pos=(start_x-2, start_y-2),
                                              width=num_minutes+3, height=num_stocks+3)
        main_stock_block = DrawObject.StockBlock(self)
        timeline = DrawObject.Timeline(self, (start_x, start_y - 50), (255, 255, 255))
        self.draw_objects["Timeline"] = timeline

        for minute_index in range(num_minutes):
            timeline.draw(minute_index)
            if minute_index < len(minutes) - 1:
                for stock_index in range(num_stocks):
                    stock = self.stocks[stock_index]
                    try:
                        percent = self.data[stock]['percents'][minute_index]
                    except IndexError as e:
                        print(f"IndexError: {e}")
                        print(f"Stock: {stock}, x: {minute_index}, y: {stock_index}")
                        percent = 0

                    if minute_index == 0:
                        stock_line = DrawObject.StockLine(self, stock)
                        self.draw_objects["Main Stock Block"] = main_stock_block
                        main_stock_block.add_line(stock_line)

                    stock_line = main_stock_block.lines['stock_lines'][stock]
                    stock_line.add_square((start_x + minute_index * square_size, start_y + stock_index * square_size),
                                          percent, square_size)
            pygame.display.flip()
            self.clock.tick(60)
        time.sleep(1.5)
        main_border.remove_unzip()
        self.scene = 2

    def draw_scene_2(self):
        stock_block = self.draw_objects["Main Stock Block"]
        timeline = self.draw_objects['Timeline']
        timeline.fade_out()

        stock_block.draw_lines(speed=7)
        time.sleep(1.5)
        stock_block.split_block(num_blocks=4, separation=40)
        for subblock in stock_block.subblocks:
            subblock.draw_border(1, (255,255,255))
            time.sleep(.4)
        stock_block.draw_subblocks(speed=3)

        self.scene = 3

    def redraw_sorted_lines(self, square_size):
        sorted_lines = sorted(self.draw_objects.values(), key=lambda sl: sl.percents[-1], reverse=True)

        middle_index = len(sorted_lines) // 2
        start_y = (self.height - (len(sorted_lines) * square_size)) / 2

        for i in range(middle_index + 1):
            top_index = middle_index - i
            bottom_index = middle_index + i

            if top_index >= 0:
                top_y_position = start_y + top_index * square_size
                stock_line_top = sorted_lines[top_index]
                stock_line_top.move(top_y_position)
                stock_line_top.draw()

            if bottom_index < len(sorted_lines) and bottom_index != top_index:
                bottom_y_position = start_y + bottom_index * square_size
                stock_line_bottom = sorted_lines[bottom_index]
                stock_line_bottom.move(bottom_y_position)
                stock_line_bottom.draw()

            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.draw()
        pygame.quit()
