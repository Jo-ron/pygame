import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 确保中文正常显示
pygame.font.init()

try:
  font_path = "SimHei.ttf"
  default_font = pygame.font.Font('C:/Windows/Fonts/simhei.ttf', 24)
except:
  print("警告: 未找到字体文件，将使用系统默认字体")
  default_font = pygame.font.SysFont(None, 24)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
SURFER_JUMP = -12
SURFER_SPEED = 6
OBSTACLE_SPEED = 6

# 颜色定义
SKY_BLUE = (135, 206, 235)
SEA_BLUE = (0, 100, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)


class Surfer(pygame.sprite.Sprite):
  def __init__(self, x: int, y: int):
    super().__init__()
    try:
      # 加载单个冲浪者图片并缩小
      self.image = pygame.image.load('surfer1.png').convert_alpha()
      scale_factor = 1 / 7
      self.image = pygame.transform.scale(
        self.image,
        (int(self.image.get_width() * scale_factor),
         int(self.image.get_height() * scale_factor))
      )
      self.rect = self.image.get_rect()
      self.rect.x = x
      self.rect.y = y
    except pygame.error as e:
      print(f"加载冲浪者图片时出错: {e}")
      pygame.quit()
      sys.exit()

    self.vel_y = 0
    self.jumping = False
    self.score = 0
    self.lives = 3
    self.invincible = False  # 无敌状态
    self.invincible_duration = 0  # 无敌持续时间
    self.shield_image = self._create_shield_image()  # 护盾图像

  def _create_shield_image(self):
    """创建护盾效果的半透明圆形"""
    size = max(self.rect.width, self.rect.height) + 20
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(
      image,
      (*BLUE, 128),  # 半透明蓝色
      (size // 2, size // 2),
      size // 2
    )
    return image

  def update(self):
    # 应用重力
    self.vel_y += GRAVITY
    self.rect.y += self.vel_y

    # 限制在屏幕内
    if self.rect.bottom > SCREEN_HEIGHT - 100:
      self.rect.bottom = SCREEN_HEIGHT - 100
      self.vel_y = 0
      self.jumping = False

    if self.rect.top < 0:
      self.rect.top = 0
      self.vel_y = 0

    # 更新无敌状态
    if self.invincible:
      self.invincible_duration -= 1
      if self.invincible_duration <= 0:
        self.invincible = False

    # 增加分数
    self.score += 0.1

  def jump(self):
    if not self.jumping:
      self.vel_y = SURFER_JUMP
      self.jumping = True

  def move_left(self):
    self.rect.x -= SURFER_SPEED
    if self.rect.left < 0:
      self.rect.left = 0

  def move_right(self):
    self.rect.x += SURFER_SPEED
    if self.rect.right > SCREEN_WIDTH:
      self.rect.right = SCREEN_WIDTH

  def lose_life(self):
    if not self.invincible:
      self.lives -= 1
      return self.lives <= 0
    return False

  def activate_shield(self):
    """激活无敌护盾"""
    self.invincible = True
    self.invincible_duration = 3 * FPS  # 3秒无敌时间


class Obstacle(pygame.sprite.Sprite):
  def __init__(self, x: int, y: int, obstacle_type: str = "rock"):
    super().__init__()
    self.obstacle_type = obstacle_type

    # 不同类型障碍物的视觉表现
    if obstacle_type == "rock":
      try:
        self.image = pygame.image.load('rock.png').convert_alpha()
        scale_factor = 1 / 4
        self.image = pygame.transform.scale(
          self.image,
          (int(self.image.get_width() * scale_factor),
           int(self.image.get_height() * scale_factor))
        )
      except pygame.error as e:
        print(f"加载岩石障碍物图片时出错: {e}")
        pygame.quit()
        sys.exit()
    elif obstacle_type == "bird":
      try:
        self.image = pygame.image.load('bird.png').convert_alpha()
        scale_factor = 1 / 8
        self.image = pygame.transform.scale(
          self.image,
          (int(self.image.get_width() * scale_factor),
           int(self.image.get_height() * scale_factor))
        )
      except pygame.error as e:
        print(f"加载鸟障碍物图片时出错: {e}")
        pygame.quit()
        sys.exit()

    elif obstacle_type == "wave":
      try:
        self.image = pygame.image.load('wave.png').convert_alpha()
        scale_factor = 1 / 3
        self.image = pygame.transform.scale(
          self.image,
          (int(self.image.get_width() * scale_factor),
           int(self.image.get_height() * scale_factor))
        )
      except pygame.error as e:
        print(f"加载海浪障碍物图片时出错: {e}")
        pygame.quit()
        sys.exit()

    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y

    if obstacle_type == "rock":
      # 海平面位置是 SCREEN_HEIGHT - 100
      self.rect.bottom = SCREEN_HEIGHT - 100

  def update(self):
    self.rect.x -= OBSTACLE_SPEED

  def off_screen(self) -> bool:
    return self.rect.right < 0


class PowerUp(pygame.sprite.Sprite):
  def __init__(self, x: int, y: int, power_type: str = "life", heart_image=None):
    super().__init__()
    self.power_type = power_type
    self.image = pygame.Surface((30, 30), pygame.SRCALPHA)

    # 根据道具类型设置图像
    if power_type == "life" and heart_image:
      self.image = heart_image
    elif power_type == "shield":
      # 绘制护盾图标（蓝色半圆）
      pygame.draw.arc(self.image, BLUE, (0, 0, 30, 30), 0, 3.14, 3)
      pygame.draw.line(self.image, BLUE, (0, 15), (30, 15))

    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y

  def update(self):
    self.rect.x -= OBSTACLE_SPEED

  def off_screen(self) -> bool:
    return self.rect.right < 0


class Explosion(pygame.sprite.Sprite):
  """障碍物被护盾摧毁时的爆炸特效"""

  def __init__(self, center):
    super().__init__()
    self.radius = 10
    self.max_radius = 30
    self.speed = 2
    self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
    self.rect = self.image.get_rect(center=center)
    self.update()

  def update(self):
    # 绘制爆炸圆环
    self.image.fill((0, 0, 0, 0))
    pygame.draw.circle(
      self.image,
      (*RED, 150 - self.radius * 5),  # 随时间变淡
      (self.max_radius, self.max_radius),
      self.radius,
      max(1, 5 - self.radius // 6)  # 圆环宽度随时间变化
    )
    self.radius += self.speed
    if self.radius > self.max_radius:
      self.kill()


class Game:
  def __init__(self):
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("冲浪游戏无尽模式")
    self.clock = pygame.time.Clock()
    self.running = True
    self.obstacle_timer = 0
    self.powerup_timer = 0
    self.game_time = 0  # 游戏运行时间（秒）

    # 精灵组
    self.all_sprites = pygame.sprite.Group()
    self.obstacles = pygame.sprite.Group()
    self.powerups = pygame.sprite.Group()
    self.explosions = pygame.sprite.Group()  # 爆炸特效组

    # 创建冲浪者
    self.surfer = Surfer(100, SCREEN_HEIGHT - 200)
    self.all_sprites.add(self.surfer)

    # 游戏状态
    self.game_over = False
    self.score = 0
    self.high_score = 0
    self.obstacle_frequency = 120  # 初始障碍物频率
    self.min_frequency = 60  # 最大频率限制（避免太快）
    self.frequency_decrement = 1  # 每秒减少的频率值
    self.last_difficulty_update = 0  # 上次更新难度的时间

    try:
      # 加载并缩放爱心图片
      self.heart_image = pygame.image.load('heart.png').convert_alpha()
      self.heart_image = pygame.transform.scale(self.heart_image, (30, 30))
    except pygame.error as e:
      print(f"加载爱心图片时出错: {e}")
      # 创建一个备用的红色爱心
      self.heart_image = pygame.Surface((30, 30), pygame.SRCALPHA)
      self._draw_heart(self.heart_image, RED)

  def _draw_heart(self, surface, color):
    """绘制一个简单的爱心形状（备用方案）"""
    points = [
      (15, 0), (5, 10), (0, 20),
      (15, 30), (30, 20), (25, 10)
    ]
    pygame.draw.polygon(surface, color, points)

  def handle_events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.running = False

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
          if self.game_over:
            self.reset_game()
          else:
            self.surfer.jump()

    # 持续检测按键状态（独立于事件循环）
    keys = pygame.key.get_pressed()
    moving = False

    if keys[pygame.K_LEFT]:
      self.surfer.move_left()
      moving = True
    if keys[pygame.K_RIGHT]:
      self.surfer.move_right()
      moving = True

  def spawn_obstacles(self):
    self.obstacle_timer += 1
    if self.obstacle_timer >= self.obstacle_frequency:
      # 随机选择障碍物类型
      obstacle_types = ["rock", "bird", "wave"]
      obstacle_type = random.choice(obstacle_types)

      # 根据障碍物类型设置位置
      if obstacle_type == "wave":
        y_pos = SCREEN_HEIGHT - 150
      elif obstacle_type == "rock":
        # 岩石固定在海平面上，不需要随机高度
        y_pos = SCREEN_HEIGHT - 100  # 初始位置设为海平面
      else:
        y_pos = SCREEN_HEIGHT - 120 - random.randint(0, 100)

      obstacle = Obstacle(SCREEN_WIDTH, y_pos, obstacle_type)
      self.all_sprites.add(obstacle)
      self.obstacles.add(obstacle)
      self.obstacle_timer = 0

      # 随机生成道具
      if random.random() < 0.1:
        # 调整道具生成概率：生命80%，护盾20%
        power_type = random.choices(["life", "shield"], weights=[8, 2])[0]
        # 传递爱心图片给PowerUp
        powerup = PowerUp(SCREEN_WIDTH, SCREEN_HEIGHT - 200 - random.randint(0, 100), power_type, self.heart_image)
        self.all_sprites.add(powerup)
        self.powerups.add(powerup)

  def update(self):
    if not self.game_over:
      self.all_sprites.update()
      self.explosions.update()  # 更新爆炸特效
      self.game_time += 1 / FPS  # 更新游戏时间（秒）

      # 移除离开屏幕的障碍物和道具
      for obstacle in self.obstacles:
        if obstacle.off_screen():
          obstacle.kill()

      for powerup in self.powerups:
        if powerup.off_screen():
          powerup.kill()

      # 检测碰撞
      hits = pygame.sprite.spritecollide(self.surfer, self.obstacles, False)
      for hit in hits:
        if self.surfer.invincible:
          # 护盾激活时摧毁障碍物并生成爆炸特效
          hit.kill()
          self.create_explosion(hit.rect.center)
          self.score += 5  # 奖励分数
        else:
          if self.surfer.lose_life():
            self.game_over = True
          hit.kill()  # 无论如何都移除障碍物

      # 检测道具碰撞
      power_hits = pygame.sprite.spritecollide(self.surfer, self.powerups, True)
      for powerup in power_hits:
        if powerup.power_type == "life" and self.surfer.lives < 3:
          self.surfer.lives += 1  # 增加一条生命
        elif powerup.power_type == "shield":
          self.surfer.activate_shield()  # 激活护盾

      # 更新分数
      self.score = int(self.surfer.score)
      if self.score > self.high_score:
        self.high_score = self.score

      # 匀速调整障碍物频率（每秒更新一次）
      self.adjust_obstacle_frequency()

      # 生成新障碍物
      self.spawn_obstacles()

  def create_explosion(self, center):
    """创建爆炸特效"""
    explosion = Explosion(center)
    self.all_sprites.add(explosion)
    self.explosions.add(explosion)

  def adjust_obstacle_frequency(self):
    # 每秒更新一次难度
    if self.game_time - self.last_difficulty_update >= 1:
      self.last_difficulty_update = self.game_time

      # 匀速减少频率值
      new_frequency = max(
        self.min_frequency,
        self.obstacle_frequency - self.frequency_decrement
      )

      if new_frequency != self.obstacle_frequency:
        self.obstacle_frequency = new_frequency
        print(f"障碍物频率已调整为: {self.obstacle_frequency}")

  def draw(self):
    # 绘制背景
    self.screen.fill(SKY_BLUE)
    pygame.draw.rect(self.screen, SEA_BLUE, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))

    # 绘制精灵
    self.all_sprites.draw(self.screen)
    self.explosions.draw(self.screen)  # 绘制爆炸特效

    # 绘制护盾效果（如果激活）
    if self.surfer.invincible:
      # 闪烁效果：根据剩余时间改变透明度
      alpha = 255 if (self.surfer.invincible_duration // 5) % 2 == 0 else 150
      shield_surf = self.surfer.shield_image.copy()
      shield_surf.set_alpha(alpha)
      shield_rect = shield_surf.get_rect(center=self.surfer.rect.center)
      self.screen.blit(shield_surf, shield_rect)

    # 绘制游戏信息
    score_text = default_font.render(f"分数: {self.score}", True, WHITE)
    self.screen.blit(score_text, (10, 10))

    high_score_text = default_font.render(f"最高分: {self.high_score}", True, WHITE)
    self.screen.blit(high_score_text, (10, 40))

    # 绘制生命值
    heart_x = 10
    for _ in range(self.surfer.lives):
      self.screen.blit(self.heart_image, (heart_x, 70))
      heart_x += 35

    # 绘制护盾状态（如果激活）
    if self.surfer.invincible:
      shield_time = max(0, self.surfer.invincible_duration // FPS)
      shield_text = default_font.render(f"护盾: {shield_time}s", True, WHITE)
      self.screen.blit(shield_text, (10, 105))

    # 绘制频率信息（调试用）
    # freq_text = default_font.render(f"障碍物频率: {int(self.obstacle_frequency)}", True, WHITE)
    # self.screen.blit(freq_text, (10, 130))

    # 绘制游戏时间
    # time_text = default_font.render(f"游戏时间: {int(self.game_time)}秒", True, WHITE)
    # self.screen.blit(time_text, (10, 160))

    # 绘制游戏结束界面
    if self.game_over:
      s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
      s.fill((0, 0, 0, 128))
      self.screen.blit(s, (0, 0))

      game_over_text = default_font.render("游戏结束!", True, WHITE)
      game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
      self.screen.blit(game_over_text, game_over_rect)

      final_score_text = default_font.render(f"最终分数: {self.score}", True, WHITE)
      final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
      self.screen.blit(final_score_text, final_score_rect)

      restart_text = default_font.render("按空格键重新开始", True, WHITE)
      restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
      self.screen.blit(restart_text, restart_rect)

    pygame.display.flip()

  def reset_game(self):
    global OBSTACLE_SPEED
    # 清空精灵组
    self.all_sprites.empty()
    self.obstacles.empty()
    self.powerups.empty()
    self.explosions.empty()

    # 创建新的冲浪者
    self.surfer = Surfer(100, SCREEN_HEIGHT - 200)
    self.all_sprites.add(self.surfer)

    # 重置游戏状态
    self.game_over = False
    self.surfer.score = 0
    OBSTACLE_SPEED = 6
    self.obstacle_frequency = 150  # 重置频率
    self.game_time = 0  # 重置游戏时间
    self.last_difficulty_update = 0  # 重置难度更新时间

  def run(self):
    while self.running:
      self.handle_events()
      self.update()
      self.draw()
      self.clock.tick(FPS)

    pygame.quit()
    sys.exit()


# 启动游戏
if __name__ == "__main__":
  game = Game()
  game.run()
