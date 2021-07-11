class GameStats:
    """跟踪游戏的信息"""
    def __init__(self,ai_game):
        self.settings=ai_game.settings
        self.reset_stats()
        # 游戏开始处于非活动状态
        self.game_active=False

    def reset_stats(self):
        """初始化游戏运行过程中可能变化的统计信息"""
        self.ship_left=self.settings.ship_limit
