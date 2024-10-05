import math
import time
from datetime import datetime, timedelta
import pygame


class DrawObject:
    def __init__(self, view, pos=None, color=None):
        self.view = view
        self.screen = view.screen
        self.pos = pos if pos is not None else None
        self.color = color if color is not None else None

class ObjectBorder(DrawObject):
    def __init__(self, view, thickness, color, pos, width, height):
        super().__init__(view, pos, color)
        self.width = width
        self.height = height
        self.thickness = thickness
        self.draw()

    def draw(self):
        border_rect = []
        border_rect.extend(self.pos)
        border_rect.extend([self.width, self.height])
        pygame.draw.rect(self.screen, self.color, border_rect, self.thickness)
        pygame.display.flip()


    def remove_instant(self):
        border_rect = []
        border_rect.extend(self.pos)
        border_rect.extend([self.width, self.height])
        pygame.draw.rect(self.screen, (0,0,0), border_rect, self.thickness)

    def remove_unzip(self):
        self.remove_instant()

        # positions
        top_left = self.pos
        top_right = (self.pos[0]+self.width, self.pos[1])
        bottom_left = (self.pos[0], self.pos[1]+self.height)
        bottom_right = (self.pos[0]+self.width, self.pos[1]+self.height)

        step_sequence = calculate_steps([self.width, self.height])
        vertical_steps, horizontal_steps = 0, 0

        for i in range(max(self.width, self.height)):
            self.remove_instant()
            vertical_steps += step_sequence[self.height][i]
            horizontal_steps += step_sequence[self.width][i]

            # topline
            pygame.draw.line(self.screen, (0, 0, 0), top_left, top_right, 1)
            pygame.draw.line(self.screen, self.color, top_left, (top_right[0] - horizontal_steps, top_right[1]), 1)
            # bottomline
            pygame.draw.line(self.screen, (0, 0, 0), bottom_left, bottom_right, 1)
            pygame.draw.line(self.screen, self.color, (bottom_left[0] + horizontal_steps, bottom_left[1]), bottom_right, 1)

            # leftline
            pygame.draw.line(self.screen, (0, 0, 0), top_left, bottom_left, 1)
            pygame.draw.line(self.screen, self.color, top_left, (bottom_left[0], bottom_left[1] - vertical_steps), 1)
            # rightline
            pygame.draw.line(self.screen, (0, 0, 0), top_right, bottom_right, 1)
            pygame.draw.line(self.screen, self.color, (top_right[0], top_right[1] + vertical_steps), bottom_right, 1)
            pygame.display.flip()
            time.sleep(.001)

        pygame.draw.line(self.screen, (0, 0, 0), top_left, top_right, 1)
        pygame.draw.line(self.screen, (0, 0, 0), bottom_left, bottom_right, 1)


class StockSquare(DrawObject):
    def __init__(self, view, pos, size, percent):
        super().__init__(view, pos, get_color(percent))
        self.size = size
        self.draw()

    def draw(self):
        pygame.draw.rect(self.screen, self.color, (self.pos[0], self.pos[1], self.size, self.size))

class StockLine(DrawObject):
    def __init__(self, view, stock, pos = None, pos2 = None):
        super().__init__(view, pos)
        self.stock = stock
        self.squares = []
        self.percents = []
        self.pos2 = pos2

    def add_square(self, pos, percent, size):
        square = StockSquare(self.view, pos, size, percent)
        self.squares.append(square)
        self.percents.append(percent)
        if self.pos is None:
            self.pos = pos
        self.pos2 = pos

    def draw(self):
        for square in self.squares:
            square.draw()

    def get_average(self):
        average = sum(self.percents) / len(self.percents) if self.percents else None
        return average

    def __len__(self):
        return len(self.squares)

class StockBlock(DrawObject):
    def __init__(self, view, lines=None):
        super().__init__(view)
        self.lines = lines if lines is not None else {'stock_lines':{},'block_lines':{}}
        self.subblocks = []

    def add_line(self, stock_line):
        self.lines["stock_lines"][stock_line.stock] = stock_line

    def draw_lines(self, speed=None):
        stock_lines = self.lines['stock_lines'].values()
        num_minutes = len(list(stock_lines)[0]) - 1
        for i in range(num_minutes, -1, speed * -1):
            offset = 0 if num_minutes % speed == i and i != 0 else i
            for stock_line in stock_lines:
                color = get_color(stock_line.percents[-1])
                self.lines['block_lines'][stock_line.stock] = {
                    "stock": stock_line.stock,
                    "color": tuple(color),
                    "start_pos": [stock_line.pos[0] + offset, stock_line.pos2[1]],
                    "end_pos": list(stock_line.pos2)
                }
                pygame.draw.line(self.screen, color, (stock_line.pos[0] + offset, stock_line.pos2[1]), stock_line.pos2, 1)
            pygame.display.flip()
            time.sleep(.02)

    def draw_subblocks(self, speed):
        num_minutes = len(list(self.lines['stock_lines'].values())[0]) - 1

        for i in range(num_minutes, -1, speed * -1):
            offset = 0 if num_minutes % speed == i and i != 0 else i
            block_num = 0
            for subblock in self.subblocks:
                color = get_color(subblock.average_block())
                block_lines = subblock.lines['block_lines'].values()
                for block_line in block_lines:
                    if block_num % 2 == 0:
                        pos = (block_line["start_pos"][0] + offset, block_line["start_pos"][1])
                        pygame.draw.line(self.screen, color, pos, block_line["end_pos"], 1)
                    else:
                        end_pos = (block_line["end_pos"][0] - offset, block_line["end_pos"][1])
                        pygame.draw.line(self.screen, color, block_line["start_pos"], end_pos, 1)
                block_num += 1
            pygame.display.flip()
            time.sleep(.02)

    def draw_border(self, thickness, color):
        block_lines = list(self.lines['block_lines'].values())
        pos = [pos-thickness for pos in block_lines[0]['start_pos']]
        pos2 = [pos+2*thickness for pos in block_lines[-1]['end_pos']]
        width = pos2[0] - pos[0]
        height = pos2[1] - pos[1]
        ObjectBorder(view=self.view, thickness=thickness, color=color, pos=pos, width=width, height=height)

    def shift_block(self, distance):
        index = 0 if distance > 0 else -1
        cover_ref_line = list(self.lines["block_lines"].values())[index]
        width = cover_ref_line["end_pos"][0] - cover_ref_line["start_pos"][0] + 1

        cover_rect = []
        cover_pos = cover_ref_line["start_pos"] if distance > 0 else [cover_ref_line["start_pos"][0], cover_ref_line["start_pos"][1] - distance-1]
        cover_rect.extend(cover_pos)
        cover_rect.extend([width, abs(distance)])
        pygame.draw.rect(self.screen, (0, 0, 0), cover_rect)

        for block_line in self.lines["block_lines"].values():
            block_line["start_pos"][1] = block_line["start_pos"][1] + distance
            block_line["end_pos"][1] = block_line["end_pos"][1] + distance
            pygame.draw.line(self.screen, block_line["color"], block_line["start_pos"], block_line["end_pos"], 1)

    def split_block(self, num_blocks, separation=0):
        new_blocks = []
        num_lines = len(self.lines["block_lines"])
        block_size = math.ceil(num_lines / num_blocks)

        for i in range(0, num_lines, block_size):
            new_block_lines = {
                'stock_lines': {k: self.lines['stock_lines'][k] for k in list(self.lines['stock_lines'])[i:i + block_size]},
                'block_lines': {k: self.lines['block_lines'][k] for k in list(self.lines['block_lines'])[i:i + block_size]}
            }
            new_block = StockBlock(self.view, lines=new_block_lines)
            new_blocks.append(new_block)

        target_y_pos = []
        middle_index = (num_blocks // 2)
        if separation !=0 and num_blocks % 2 == 0:
            for i in range(num_blocks):
                target = (i-middle_index+1)*separation - separation//2
                target_y_pos.append(target)

        step_sequence = calculate_steps(target_y_pos)

        for step_index in range(max(target_y_pos)):
            for i in range(num_blocks):
                step_key = target_y_pos[i]
                step = step_sequence[step_key][step_index]
                new_blocks[i].shift_block(step)
                pygame.display.flip()
                time.sleep(.003)

        self.subblocks = new_blocks
        return new_blocks

    def average_block(self):
        stock_lines = list(self.lines['stock_lines'].values())
        return sum(stock_line.percents[-1] for stock_line in stock_lines) / len(stock_lines)


    def __str__(self):
        return f"Block(numstocks={len(self)})"

    def __len__(self):
        return len(self.lines["stock_lines"])

class Timeline(DrawObject):
    def __init__(self, view, start_pos, color):
        super().__init__(view, pos=start_pos)
        self.current_pos = start_pos
        self.color = color
        self.view = view
        self.timeline_parts = {}
        self.draw(0)

    def draw(self, elapsed_time):
        self.current_pos = (self.pos[0] + elapsed_time, self.pos[1])
        self.draw_main_line(thickness=2)

        draw_tickmark_time = False
        if elapsed_time == 0 or elapsed_time == 390:
            self.draw_tickmark(tickmark_size=20, thickness=1)
        elif (elapsed_time + 30) % 60 == 0:
            self.draw_tickmark(tickmark_size=5, thickness=1)
            draw_tickmark_time = True

        draw_time = (datetime.strptime("09:30", "%H:%M") + timedelta(minutes=elapsed_time)).strftime("%I:%M %p")
        self.draw_time(draw_time, draw_tickmark_time)

    def draw_main_line(self, thickness):
        pygame.draw.line(self.screen, self.color, self.pos, self.current_pos, thickness)
        self.timeline_parts["Main Line"] = {
            "line": True,
            "start_pos": self.pos,
            "end_pos": self.current_pos,
            "thickness": thickness
        }

    def draw_tickmark(self, tickmark_size, thickness):
        pos1 = (self.current_pos[0], self.current_pos[1] - tickmark_size)
        pos2 = (self.current_pos[0], self.current_pos[1] + tickmark_size)
        pygame.draw.line(self.screen, self.color, pos1, pos2, thickness)

        self.timeline_parts["Tickmark " + str(self.current_pos[0])] = {
            "line": True,
            "start_pos": pos1,
            "end_pos": pos2,
            "thickness": thickness
        }

    def draw_time(self, draw_time, tickmark_time=False):
        display_time = "MARKET CLOSE" if draw_time == "04:00 PM" else draw_time.lstrip('0')

        # clear previous time and draw new
        clock_font = pygame.font.SysFont('Verdana', 24)
        text_width, text_height = clock_font.size("MARKET CLOSE")
        time_rect = pygame.Rect(
            (self.view.width / 2 - text_width / 2, 100 - text_height / 2),
            (text_width, text_height)
        )
        self.screen.fill((0, 0, 0), time_rect)
        time_text = clock_font.render(display_time, True, (255, 255, 255))
        self.screen.blit(time_text, time_text.get_rect(center=time_rect.center))

        if tickmark_time:
            hour = draw_time.split(':')[0].lstrip('0')
            meridiem = draw_time[-2:]
            tickmark_time_str = f"{hour}{meridiem}"

            # render and position tickmark time
            tickmark_font = pygame.font.SysFont('Verdana', 10)
            tickmark_text = tickmark_font.render(tickmark_time_str, True, self.color)
            tickmark_rect = tickmark_text.get_rect(center=(self.current_pos[0], self.current_pos[1] - 30))
            self.screen.blit(tickmark_text, tickmark_rect)

            self.timeline_parts["Time Label " + tickmark_time_str] = {
                "line": False,
                "font": tickmark_font,
                "string": tickmark_time_str,
                "rect": tickmark_rect
            }

    def fade_out(self):
        while self.color != (0,0,0):
            color_list = list(self.color)
            self.color = tuple([max(0, x - 3) for x in color_list])
            for timeline_part in self.timeline_parts.values():
                if timeline_part['line']:
                    pygame.draw.line(self.screen, self.color,
                                     timeline_part['start_pos'],
                                     timeline_part['end_pos'],
                                     timeline_part['thickness'])

                else:
                    tickmark_rect = timeline_part['rect']
                    self.screen.fill((0, 0, 0), tickmark_rect)
                    tickmark_font = timeline_part['font']
                    tickmark_text = tickmark_font.render(timeline_part['string'], True, self.color)
                    self.screen.blit(tickmark_text, tickmark_rect)
                pygame.display.flip()

def get_color(percent):
    norm = abs(percent) / 0.05 if abs(percent) < 0.05 else 1
    return (0, int(norm * 255), 0) if percent > 0 else (int(norm * 255), 0, 0)

def calculate_steps(distances, step_size=1):
    result = {}
    max_distance = max(abs(d) for d in distances)

    for distance in distances:
        step_array = []
        abs_distance = abs(distance)
        step_interval = max_distance / abs_distance if abs_distance > 0 else 0
        num_steps = int(max_distance // step_size)
        cumulative_sum = 0

        for i in range(num_steps):
            if abs_distance > 0 and i % step_interval < 1:
                step = step_size if distance > 0 else -step_size
                cumulative_sum += step
            else:
                step = 0
            step_array.append(step)

        if cumulative_sum != distance:
            correction = distance - cumulative_sum
            for j in reversed(range(num_steps)):
                if step_array[j] != 0:
                    step_array[j] += correction
                    break

        result[distance] = list(reversed(step_array))

    return result
