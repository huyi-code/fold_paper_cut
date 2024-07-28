import pygame
import math


"""
todo:
1.从折叠后开始剪，提供剪的线，简单图案，展示图时显示之前剪的小图，可重新放大操作
2.如果剪出两个不连通区域，则去掉面积小的部分
3.剪的调整大小，线调整起始点
4.保存图片，背景图找个好看的
5.撤回操作
6.可选是否要折叠线
7.折叠时动画效果
"""

"""
7.23 创建项目，写固定折法展开逻辑
7.24 写通用的展开图形逻辑，写折叠逻辑，还无法展示
7.25 正常展示折叠后效果
7.26 解决不对的方向直接崩溃的问题：不对的方向提示在后台，页面不反应；模拟画笔 
7.27 封装Button类，可以实现按正常流程先fold再draw再unfold，特殊情况未考虑，不能不按顺序或反复没考虑特殊情况
"""

# 初始化Pygame
pygame.init()

# 设置窗口大小
GRID_WIDTH, GRID_HEIGHT = 800, 800
screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
pygame.display.set_caption("jianchuanghua")

# 定义颜色
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
LIGHT_RED = (210, 65, 65)
RED = (200, 50, 50)


#形状
TRIANGLE_RIGHT_UP = "triangle_right_up"
TRIANGLE_LEFT_UP = "triangle_left_up"
TRIANGLE = "triangle"
SQUARE = "square"
RECTANGLE = "rectangle"


#操作
UP = "up"
LEFT = "left"
LEFT_UP = "left_up"
RIGHT_UP = "right_up"
ALL_OPS = [UP, LEFT, LEFT_UP, RIGHT_UP]

#展示大小
#纸张一半大小
PAPER_HALF = 200

DRAW_MODE = "draw"


# 按钮类
class Button:
    def __init__(self, x, y, width, height, color=GRAY, text=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, 20)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        screen.blit(text_surf, text_rect)

    def cover(self, pos):
        return self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height



class PaperCut():
    def __init__(self, surface_start_width=0, surface_start_height=0):
        self.paper_surface = pygame.Surface((400, 400), pygame.SRCALPHA)
        self.paper_surface.fill(RED)
        self.shape = SQUARE
        self.surface = pygame.Surface((400, 400), pygame.SRCALPHA)
        self.surface.fill(WHITE)
        self.use_pen = False
        self.lines = []
        self.surface_start_width = surface_start_width
        self.surface_start_height = surface_start_height
        self.mode = None
        self.op_list = []
        self.shape_list = []


    def init_show(self, screen):
        self.surface.blit(self.paper_surface, (0, 0))
        screen.blit(self.surface, (self.surface_start_width, self.surface_start_height))


    def fold_once(self, shape=SQUARE, direction="UP"):
        valid_fold = {SQUARE: {UP: (RECTANGLE, 1, 0.5), LEFT: (RECTANGLE, 0.5, 1), LEFT_UP: (TRIANGLE_LEFT_UP, 1, 1), RIGHT_UP: (TRIANGLE_RIGHT_UP, 1, 1)},
                      TRIANGLE_LEFT_UP: {RIGHT_UP: (TRIANGLE, 1, 0.5)},
                      TRIANGLE_RIGHT_UP: {LEFT_UP: (TRIANGLE, 1, 0.5)},
                      TRIANGLE: {LEFT: (TRIANGLE_RIGHT_UP, 0.5, 1)},
                      RECTANGLE: {UP: (RECTANGLE, 1, 0.5), LEFT: (RECTANGLE, 0.5, 1)}}
        width, height = self.paper_surface.get_width(), self.paper_surface.get_height()
        if direction not in valid_fold[shape]: return None
        res = valid_fold[shape][direction]
        width, height = int(width * res[1]), int(height * res[2])
        next_shape = SQUARE if (res[0] == RECTANGLE and width == height) else res[0]
        return (next_shape, width, height)


    def fold(self, op, shape, x, y):
        res = self.fold_once(shape, op)
        if not res:
            return None
        else:
            (shape, width, height) = res
            self.op_list.append(op)
            self.shape_list.append(shape)
            self.paper_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            #self.paper_surface.fill(WHITE)
            print("start surface update: ", res)

            if shape == RECTANGLE or shape == SQUARE:
                pygame.draw.rect(self.paper_surface, RED, (x, y , width, height))
            elif shape == TRIANGLE_RIGHT_UP:
                pygame.draw.polygon(self.paper_surface, RED, [(x, y), (x + width, y), (x + width, y + height)])
            elif shape == TRIANGLE_LEFT_UP:
                pygame.draw.polygon(self.paper_surface, RED, [(x, y), (x + width, y), (x, y + height)])
            elif shape == TRIANGLE:
                pygame.draw.polygon(self.paper_surface, RED, [(x, y), (x + width, y), (x + width//2, y + height)])
        return shape


    def unfold(self, x, y):
        paper_surface = self.paper_surface
        while len(self.op_list) > 0:
            op = self.op_list.pop()
            shape = self.shape_list.pop()
            print(op, shape, paper_surface)
            if op == UP:
                paper_surface = self.draw_up(paper_surface, x, y)
            elif op == LEFT:
                paper_surface = self.draw_left(paper_surface, x, y)
            elif op == LEFT_UP:
                if shape == TRIANGLE_LEFT_UP:
                    paper_surface = self.draw_up_left_from_square(paper_surface, x, y)
                elif shape == TRIANGLE:
                    paper_surface = self.draw_up_left_from_triangle(paper_surface, x, y)
            elif op == RIGHT_UP:
                if shape == TRIANGLE_RIGHT_UP:
                    paper_surface = self.draw_up_right_from_square(paper_surface, x, y)
                elif shape == TRIANGLE:
                    paper_surface = self.draw_up_right_from_triangle(paper_surface, x, y)

        return paper_surface


    #TODO:只画在图区域？
    def pen_draw(self, type, pos):
        if type == 1:
            self.use_pen = True
            self.lines.append([(pos[0] - self.surface_start_width, pos[1] - self.surface_start_height)])
        elif type == 2:
            self.use_pen = False
        elif type == 3:
            if self.use_pen:
                self.lines[-1].append((pos[0] - self.surface_start_width, pos[1] - self.surface_start_height))


    def pen_draw_show(self, screen):
        for line in self.lines:
            for i in range(1, len(line)):
                pygame.draw.line(self.paper_surface, WHITE, line[i-1], line[i], 5)

        screen.blit(self.paper_surface, (self.surface_start_width, self.surface_start_height))


    #方形向上翻折变成长方形，展开时向下翻折
    def draw_up(self, last_surface, x, y, has_fold_line=True):
        width, height = last_surface.get_width(), last_surface.get_height()
        surface = pygame.Surface((width, height*2), pygame.SRCALPHA)
        last_surface_flip = pygame.transform.flip(last_surface, False, True)
        surface.blit(last_surface, (x, y))
        surface.blit(last_surface_flip, (x, y + height))
        if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x, y + height - 1), (x + width, y + height - 1), 1)
        return surface


    #方形or等腰三角形向左翻折
    def draw_left(self, last_surface, x, y, has_fold_line=True):
        width, height = last_surface.get_width(), last_surface.get_height()
        surface = pygame.Surface((width * 2, height), pygame.SRCALPHA)
        last_surface_flip = pygame.transform.flip(last_surface, True, False)
        surface.blit(last_surface, (x, y))
        surface.blit(last_surface_flip, (x + width, y))
        if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + width - 1, y), (x + width - 1, y + height), 1)
        return surface


    def draw_up_left_from_square(self, last_surface, x, y, has_fold_line=True):
        print("draw_up_left_from_square")
        width, height = last_surface.get_width(), last_surface.get_height()
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        last_surface_flip = pygame.transform.flip(last_surface, True, False)
        last_surface_flip = pygame.transform.rotate(last_surface_flip, -90)
        surface.blit(last_surface, (x, y))
        surface.blit(last_surface_flip, (x, y))
        if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + 1, y + height - 1), (x + width - 1, y + 1), 1)
        return surface


    def draw_up_left_from_triangle(self, last_surface, x, y, has_fold_line=True):
       print("draw_up_left_from_triangle")
       width, height = last_surface.get_width(), last_surface.get_height()
       surface = pygame.Surface((width, height * 2), pygame.SRCALPHA)
       last_surface_flip = pygame.transform.flip(last_surface, True, False)
       last_surface_flip = pygame.transform.rotate(last_surface_flip, -90)
       surface.blit(last_surface, (x, y))
       surface.blit(last_surface_flip, (x + width // 2, y))
       if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + width // 2 - 1, y + height - 1), (x + width, y), 1)
       return surface


    def draw_up_right_from_square(self, last_surface, x, y, has_fold_line=True):
        print("draw_up_right_from_square")
        width, height = last_surface.get_width(), last_surface.get_height()
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        last_surface_flip = pygame.transform.rotate(last_surface, -90)
        last_surface_flip = pygame.transform.flip(last_surface_flip, True, False)
        surface.blit(last_surface, (x, y))
        surface.blit(last_surface_flip, (x, y))
        if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + 1, y + 1), (x + width - 1, y + height - 1), 1)
        return surface


    def draw_up_right_from_triangle(self, last_surface, x, y, has_fold_line=True):
        print("draw_up_right_from_triangle")
        width, height = last_surface.get_width(), last_surface.get_height()
        surface = pygame.Surface((width, height * 2), pygame.SRCALPHA)
        last_surface_flip = pygame.transform.rotate(last_surface, -90)
        last_surface_flip = pygame.transform.flip(last_surface_flip, True, False)
        surface.blit(last_surface, (x, y))
        surface.blit(last_surface_flip, (x, y))
        if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + 1, y + 1), (x + width//2 - 1, y + height - 1),
                                           1)
        return surface



    #正方形or直角三角形左上方翻折
    def draw_up_left(self, last_surface, x, y, type=TRIANGLE_LEFT_UP, has_fold_line=True):
        print(last_surface, x, y, type)
        width, height = last_surface.get_width(), last_surface.get_height()
        if type == TRIANGLE:
            surface = pygame.Surface((width, height * 2), pygame.SRCALPHA)
            last_surface_flip = pygame.transform.flip(last_surface, True, False)
            last_surface_flip = pygame.transform.rotate(last_surface_flip, 90)
            surface.blit(last_surface, (x, y))
            surface.blit(last_surface_flip, (x, y))
            if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + width//2 - 1, y + height - 1), (x, y), 1)
            return surface
        elif type == TRIANGLE_LEFT_UP:
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            last_surface_flip = pygame.transform.flip(last_surface, True, False)
            last_surface_flip = pygame.transform.rotate(last_surface_flip, 90)
            surface.blit(last_surface, (x, y))
            surface.blit(last_surface_flip, (x, y))
            if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + width - 1, y + height - 1), (x, y), 1)
            return surface


    #正方形or直角三角形右上方翻折
    def draw_up_right(self, last_surface, x, y, type=TRIANGLE_RIGHT_UP, has_fold_line=True):
        print(last_surface, x, y, type)
        width, height = last_surface.get_width(), last_surface.get_height()
        if type == TRIANGLE:
            surface = pygame.Surface((width, height * 2), pygame.SRCALPHA)
            last_surface_flip = pygame.transform.rotate(last_surface, 90)
            last_surface_flip = pygame.transform.flip(last_surface_flip, True, False)
            surface.blit(last_surface, (x, y))
            surface.blit(last_surface_flip, (x + width//2, y))
            if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + width//2 + 1, y + height - 1), (x + width - 1, y), 1)
            return surface
        elif type == TRIANGLE_LEFT_UP:
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            last_surface_flip = pygame.transform.rotate(last_surface, 90)
            last_surface_flip = pygame.transform.flip(last_surface_flip, True, False)
            surface.blit(last_surface, (x, y))
            surface.blit(last_surface_flip, (x, y))
            if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + 1, y + height - 1), (x + width - 1, y + 1), 1)
            return surface


    # def draw_all(self, surface, x, y):
    #     one = draw_one()
    #     #all_one = draw_left(one, x, y)
    #     all_one = draw_up_left(one, x, y)
    #     all_one = draw_up_right(all_one, x, y, type=SQUARE)
    #     surface.blit(all_one, (x, y))


    def handle_click(self, surface, pos, up_button, left_button, left_up_button, right_up_button, unfold_button):
        for button, op in zip((up_button, left_button, left_up_button, right_up_button), (UP, LEFT, LEFT_UP, RIGHT_UP)):
            if button.cover(pos):
                shape = self.fold(op, self.shape, 0, 0)
                if shape is None:
                    print("can't fold in this direction!")
                else:
                    self.shape = shape
                    self.surface.fill(WHITE)
                    self.surface.blit(self.paper_surface, (0, 0))
                    surface.blit(self.surface, (self.surface_start_width, self.surface_start_height))
                return "fold"
        if unfold_button.cover(pos):
            paper_surface = self.unfold(0, 0)
            self.surface.fill(WHITE)
            self.surface.blit(paper_surface, (0, 0))
            surface.blit(self.surface, (self.surface_start_width, self.surface_start_height))
            return "unfold"





def draw_buttons(surface):
    up_button = Button(100, 700, 100, 50, text = "up")
    left_button = Button(250, 700, 100, 50, text="left")
    left_up_button = Button(400, 700, 100, 50, text="left up")
    right_up_button = Button(550, 700, 100, 50, text="right up")

    draw_button = Button(650, 300, 100, 50, text="draw")

    unfold_button = Button(650, 400, 100, 50, text="unfold")

    up_button.draw(surface)
    left_button.draw(surface)
    left_up_button.draw(surface)
    right_up_button.draw(surface)
    draw_button.draw(surface)
    unfold_button.draw(surface)

    return up_button, left_button, left_up_button, right_up_button, draw_button, unfold_button


screen.fill(WHITE)
up_button, left_button, left_up_button, right_up_button, draw_button, unfold_button = draw_buttons(screen)
pygame.display.flip()

clock = pygame.time.Clock()
running = True

papercut = PaperCut()
papercut.init_show(screen)
paper_surface = None
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and draw_button.cover(event.pos):
            papercut.mode = DRAW_MODE
        if papercut.mode == DRAW_MODE:
            papercut.pen_draw_show(screen)
            if event.type == pygame.MOUSEBUTTONDOWN: # and event.button == 1
                papercut.pen_draw(1, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:  #and event.button == 1
                papercut.pen_draw(2, event.pos)
            elif event.type == pygame.MOUSEMOTION:
                papercut.pen_draw(3, event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mode = papercut.handle_click(screen, event.pos, up_button, left_button, left_up_button, right_up_button, unfold_button)
            if mode: papercut.mode = mode


    pygame.display.flip()
    clock.tick(60)
