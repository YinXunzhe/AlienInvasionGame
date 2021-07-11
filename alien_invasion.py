import sys
import pygame
from time import sleep

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
    """管理游戏资源和行为的类"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()

        self.settings = Settings()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        self.play_button = Button(self, "Play")

        self.stats = GameStats(self)
        self.score_board = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._creat_fleet()

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        # 监视鼠标和键盘
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            if self.stats.game_active:
                self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_play_button(self, mouse_pos):
        """玩家单击Play按钮时开始新游戏"""
        button_checked = self.play_button.rect.collidepoint(mouse_pos)
        # 仅在按下Play按钮并且游戏处于非活动状态时才重新开始游戏，防止游戏时误触
        if button_checked and not self.stats.game_active:
            # 重置游戏设置
            self.settings.initialize_dynamic_settings()
            # 重置游戏统计信息
            self.stats.reset_stats()
            self.stats.game_active = True
            # 记分等指示牌需要重新渲染
            self.score_board.prep_score()
            self.score_board.prep_level()
            self.score_board.prep_ships()

            # 清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()

            # 创建新的外星人并让飞船居中
            self._creat_fleet()
            self.ship.center_ship()

            # 隐藏鼠标光标
            pygame.mouse.set_visible(False)

    def _update_bullets(self):
        """更新子弹位置、删除消失或者击中外星人的子弹"""
        self.bullets.update()
        # 删除消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
            # print(len(self.bullets))

        # 消除被击中的外星人
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """响应子弹和外星人碰撞"""
        # 删除发生碰撞的子弹和外星人
        collision = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True
        )
        # 计分
        if collision:
            for aliens in collision.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.score_board.prep_score()
                self.score_board.check_high_score()
        # 外星人被消灭之后会新建一群
        if not self.aliens:
            self.bullets.empty()
            self._creat_fleet()
            # 增加游戏难度和等级
            self.settings.increase_speed()
            self.stats.level += 1
            self.score_board.prep_level()

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _creat_fleet(self):
        """创建外星人群"""
        alien = Alien(self)
        self.aliens.add(alien)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - 2 * alien_width
        number_aliens_x = available_space_x // (2 * alien_width)

        # 计算可以容纳多少行
        ship_height = self.ship.rect.height
        available_space_y = self.settings.screen_height - (3 * alien_height) - ship_height
        number_aliens_y = available_space_y // (2 * alien_height)

        # 创建外星人群
        for row_number in range(number_aliens_y):
            for alien_number in range(number_aliens_x):
                self._creat_alien(alien_number, row_number)

    def _creat_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien.x = alien.rect.width + 2 * alien.rect.width * alien_number
        alien.y = alien.rect.height + 2 * alien.rect.height * row_number
        alien.rect.x = alien.x
        alien.rect.y = alien.y
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """有外星人到达边缘时改变方向"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _check_aliens_bottom(self):
        """检查是否有外星人触底"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _change_fleet_direction(self):
        """将整群外星人下移并改变方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self):
        """检查是否有外星人位于边缘，
        并更新整群外星人的位置"""
        self._check_fleet_edges()
        self.aliens.update()

        # 检查外星人和飞船的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            print("Ship hit!!!")
            self._ship_hit()
        # 检查外星人是否触底
        self._check_aliens_bottom()

    def _ship_hit(self):
        """响应飞船被外星人撞到"""
        if self.stats.ship_left > 0:
            # 拥有的飞船数量减一并更新指示牌
            self.stats.ship_left -= 1
            self.score_board.prep_ships()

            # 清空余下的子弹和外星人
            self.aliens.empty()
            self.bullets.empty()

            # 创建新的外星人，让飞船恢复到底部中央
            self._creat_fleet()
            self.ship.center_ship()

            # 暂停
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _update_screen(self):
        # 每次循环时都重绘屏幕
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        self.score_board.show_score()

        # 如果非活动状态就绘制Play按钮
        if not self.stats.game_active:
            self.play_button.draw_button()

        # 让最近绘制的屏幕可见
        pygame.display.flip()


if __name__ == '__main__':
    # 创建游戏实例并运行
    ai = AlienInvasion()
    ai.run_game()
