import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    """管理外星人的类"""

    def __init__(self, ai_game):
        """初始化并设置其初始位置"""
        super().__init__()
        self.screen = ai_game.screen
        # self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        # 加载外星人图像并获取其外接矩形
        self.image = pygame.image.load('images/alien.bmp')
        self.rect = self.image.get_rect()

        # 每个外星人放置在屏幕左上角
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # 存储外星人的精确水平位置
        self.x = float(self.rect.x)

    def check_edges(self):
        """如果外星人位于边缘，返回True"""
        screen_rect=self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True

    def update(self):
        self.x+=(self.settings.fleet_direction*self.settings.alien_speed)
        self.rect.x=self.x
