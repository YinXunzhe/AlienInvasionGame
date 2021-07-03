import pygame

class Ship:
    """管理飞船的类"""

    def __init__(self,ai_game):
        """初始化并设置其初始位置"""
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings=ai_game.settings

        #加载飞船图像并获取其外接矩形
        self.image=pygame.image.load('images/ship.bmp')
        self.rect=self.image.get_rect()

        #新飞船放置在屏幕底部中央
        self.rect.midbottom=self.screen_rect.midbottom
        # rect的x无法存储小数，需要定义新属性
        self.x=float(self.rect.x)

        #移动标志
        self.moving_right=False;
        self.moving_left=False;

    def blitme(self):
        """指定位置绘制飞船"""
        self.screen.blit(self.image,self.rect)

    def update(self):
        """更新飞船位置"""
        if self.moving_right and self.rect.right<self.screen_rect.right:
            self.x+=self.settings.ship_speed
        if self.moving_left and self.rect.left>self.screen_rect.left:
            self.x-=self.settings.ship_speed
        self.rect.x=self.x
