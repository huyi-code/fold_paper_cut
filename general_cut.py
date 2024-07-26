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
"""

"""
7.23 创建项目，写固定折法展开逻辑
7.24 写通用的展开图形逻辑，写折叠逻辑，还无法展示
7.25 正常展示折叠后效果
7.26 解决不对的方向直接崩溃的问题：不对的方向提示在后台，页面不反应 
7.27 todo:小图放大（+按钮），对应比例再创作
"""

# 初始化Pygame
pygame.init()

# 设置窗口大小
GRID_WIDTH, GRID_HEIGHT = 800, 800
screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
pygame.display.set_caption("剪窗花")

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

start_surface = pygame.Surface((400, 400))


class PaperCut():
    def __init__(self):
        self.start_surface = pygame.Surface((400, 400))
        self.start_surface.fill(RED)
        self.shape = SQUARE
        self.surface = pygame.Surface((600, 600))
        self.surface.fill(WHITE)


    def init_show(self, screen):
        self.surface.blit(self.start_surface, (0, 0))
        screen.blit(self.surface, (0, 0))


    def fold_once(self, shape=SQUARE, direction="UP"):
        print("shape:", shape)
        valid_fold = {SQUARE: {UP: (RECTANGLE, 1, 0.5), LEFT: (RECTANGLE, 0.5, 1), LEFT_UP: (TRIANGLE_LEFT_UP, 1, 1), RIGHT_UP: (TRIANGLE_RIGHT_UP, 1, 1)},
                      TRIANGLE_LEFT_UP: {RIGHT_UP: (TRIANGLE, 1, 0.5)},
                      TRIANGLE_RIGHT_UP: {LEFT_UP: (TRIANGLE, 1, 0.5)},
                      TRIANGLE: {LEFT: (TRIANGLE_RIGHT_UP, 0.5, 1)},
                      RECTANGLE: {UP: (RECTANGLE, 1, 0.5), LEFT: (RECTANGLE, 0.5, 1)}}
        width, height = self.start_surface.get_width(), self.start_surface.get_height()
        if direction not in valid_fold[shape]: return None
        res = valid_fold[shape][direction]
        width, height = int(width * res[1]), int(height * res[2])
        next_shape = SQUARE if (res[0] == RECTANGLE and width == height) else res[0]
        return (next_shape, width, height)


    def fold(self, op, shape, x, y):
        print("op: ", op)
        res = self.fold_once(shape, op)
        if not res:
            return None
        else:
            (shape, width, height) = res
            self.start_surface = pygame.Surface((width, height))
            self.start_surface.fill(WHITE)
            print("start surface update: ", res)

            if shape == RECTANGLE or shape == SQUARE:
                pygame.draw.rect(self.start_surface, RED, (x, y , width, height))
            elif shape == TRIANGLE_RIGHT_UP:
                pygame.draw.polygon(self.start_surface, RED, [(x, y), (x + width, y), (x + width, y + height)])
            elif shape == TRIANGLE_LEFT_UP:
                pygame.draw.polygon(self.start_surface, RED, [(x, y), (x + width, y), (x, y + height)])
            elif shape == TRIANGLE:
                pygame.draw.polygon(self.start_surface, RED, [(x, y), (x + width, y), (x + width//2, y + height)])

        return shape



    # def draw_one(self, has_line=True):
    #     basic_surface = pygame.Surface((PAPER_HALF * 2, PAPER_HALF), pygame.SRCALPHA)
    #     # basic_surface.fill(RED)
    #
    #     #剪基础图案
    #     pygame.draw.polygon(basic_surface, RED, [(0, 0), (PAPER_HALF * 2, 0), (PAPER_HALF, PAPER_HALF)])
    #     pygame.draw.rect(basic_surface, WHITE, (20, 0, 20, 20))
    #     pygame.draw.rect(basic_surface, WHITE, (120, 100, 20, 20))
    #     pygame.draw.line(basic_surface, WHITE, (199, 1), (199, 199), 10)
    #
    #     return basic_surface


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


    #正方形or直角三角形左上方翻折
    def draw_up_left(self, last_surface, x, y, type=TRIANGLE_LEFT_UP, has_fold_line=True):
        width, height = last_surface.get_width(), last_surface.get_height()
        if type == TRIANGLE_LEFT_UP:
            surface = pygame.Surface((width, height * 2), pygame.SRCALPHA)
            last_surface_flip = pygame.transform.flip(last_surface, True, False)
            last_surface_flip = pygame.transform.rotate(last_surface_flip, 90)
            surface.blit(last_surface, (x, y))
            surface.blit(last_surface_flip, (x, y))
            if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + width//2 - 1, y + height - 1), (x, y), 1)
            return surface
        elif type == SQUARE:
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            last_surface_flip = pygame.transform.flip(last_surface, True, False)
            last_surface_flip = pygame.transform.rotate(last_surface_flip, 90)
            surface.blit(last_surface, (x, y))
            surface.blit(last_surface_flip, (x, y))
            if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + width - 1, y + height - 1), (x, y), 1)
            return surface



    #正方形or直角三角形右上方翻折
    def draw_up_right(self, last_surface, x, y, type=TRIANGLE_RIGHT_UP, has_fold_line=True):
        width, height = last_surface.get_width(), last_surface.get_height()
        if type == TRIANGLE_RIGHT_UP:
            surface = pygame.Surface((width, height * 2), pygame.SRCALPHA)
            last_surface_flip = pygame.transform.rotate(last_surface, 90)
            last_surface_flip = pygame.transform.flip(last_surface_flip, True, False)
            surface.blit(last_surface, (x, y))
            surface.blit(last_surface_flip, (x + width//2, y))
            if has_fold_line: pygame.draw.line(surface, LIGHT_RED, (x + width//2 + 1, y + height - 1), (x + width - 1, y), 1)
            return surface
        elif type == SQUARE:
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


    def handle_click(self, surface, pos, button_rects):
        for rect, op in button_rects:
            if rect.collidepoint(pos):
                shape = self.fold(op, self.shape, 0, 0)
                if shape is None:
                    print("can't fold in this direction!")
                else:
                    self.shape = shape
                    self.surface.fill(WHITE)
                    self.surface.blit(self.start_surface, (0, 0))
                    surface.blit(self.surface, (0, 0))


def draw_button(surface):
    # 按钮设置
    button_rects = []
    button_width, button_height = 100, 80
    button_y = GRID_HEIGHT - button_height - 10  # 按钮在窗口底部

    for index, color_name in enumerate(ALL_OPS):
        button_rect = pygame.Rect(100 + index * 150, button_y, button_width, button_height)
        button_rects.append((button_rect, color_name))

    for rect, color_name in button_rects:
        pygame.draw.rect(screen, (200, 200, 200), rect)  # 按钮背景
        font = pygame.font.Font(None, 36)
        text_surface = font.render(color_name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

    return button_rects

screen.fill(WHITE)
button_rects = draw_button(screen)
pygame.display.flip()

clock = pygame.time.Clock()
running = True

papercut = PaperCut()
papercut.init_show(screen)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            papercut.handle_click(screen, event.pos, button_rects)


    pygame.display.flip()
    clock.tick(60)
