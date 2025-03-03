import pygame
import random
import bulletClass
import math
"""
修改时间：2021.12.15
修改人：2019051604048 詹孝东
模块描述：
该模块是敌方坦克类
该类组合了子弹类，因为坦克都有子弹嘛
敌方坦克类继承了pygame的精灵类，从而实现敌方坦克的相关功能 详情情况下方描述
"""
class EnemyTank(pygame.sprite.Sprite):
    def __init__(self, x=None, kind=None, isred=None):
        pygame.sprite.Sprite.__init__(self)

        # 坦克出现前动画是否播放
        self.flash = False
        self.times = 90

        # 参数:坦克种类
        self.kind = kind
        # 随机选择坦克的种类
        if not kind:
            self.kind = random.choice([1, 2, 3, 4])

        # 根据坦克的种类，加载不同种类坦克的图片
        if self.kind == 1:
            self.enemy_x_0 = pygame.image.load(r"image\enemy_1_0.png").convert_alpha()
            self.enemy_x_3 = pygame.image.load(r"image\enemy_1_3.png").convert_alpha()
        if self.kind == 2:
            self.enemy_x_0 = pygame.image.load(r"image\enemy_2_0.png").convert_alpha()
            self.enemy_x_3 = pygame.image.load(r"image\enemy_2_3.png").convert_alpha()
        if self.kind == 3:
            self.enemy_x_0 = pygame.image.load(r"image\enemy_3_1.png").convert_alpha()
            self.enemy_x_3 = pygame.image.load(r"image\enemy_3_0.png").convert_alpha()
        if self.kind == 4:
            self.enemy_x_0 = pygame.image.load(r"image\enemy_4_0.png").convert_alpha()
            self.enemy_x_3 = pygame.image.load(r"image\enemy_4_3.png").convert_alpha()
        self.enemy_3_0 = pygame.image.load(r"image\enemy_3_0.png").convert_alpha()
        self.enemy_3_2 = pygame.image.load(r"image\enemy_3_2.png").convert_alpha()

        # 参数:是否携带道具
        self.isred = isred
        # 随机选择是否携带道具（5分之1的概率）
        if not None:
            self.isred = random.choice((True, False, False, False, False))
        # 如果携带道具则更新图片
        if self.isred:
            self.tank = self.enemy_x_3
        else:
            self.tank = self.enemy_x_0

        # 参数:坦克位置
        self.x = x
        # 随机选择坦克出现的位置（因为只有上方3个复活地）
        if not self.x:
            self.x = random.choice([1, 2, 3])
        self.x -= 1

        # 运动中的两种图片
        self.tank_R0 = self.tank.subsurface((0, 48), (48, 48))
        self.tank_R1 = self.tank.subsurface((48, 48), (48, 48))
        self.rect = self.tank_R0.get_rect()
        # 设置位置
        self.rect.left, self.rect.top = 3 + self.x * 12 * 24, 3 + 0 * 24

        # 坦克速度   方向   生命   子弹生命   子弹延迟
        self.speed = 2  # 提高基础速度
        self.dir_x, self.dir_y = 0, 1
        self.life = 1
        self.bulletNotCooling = True
        self.bullet = bulletClass.Bullet()

        # 是否撞墙，撞墙则改变方向
        self.dirChange = False

        # 每种坦克不同的属性
        if self.kind == 2:
            self.speed = 4  # 提高速度
        if self.kind == 3:
            self.life = 3
            self.speed = 3  # 增加生命值高的坦克速度

        # 追踪相关参数
        self.chase_delay = 0
        # 不同类型坦克有不同的追踪参数
        if self.kind == 2:  # 速度快的坦克更频繁更新方向
            self.chase_interval = 3  # 更快的更新频率
            self.chase_probability = 1.0  # 100%追踪
            self.chase_range = 200  # 更大的追踪范围
            self.shoot_range = 150  # 射击范围
        elif self.kind == 3:  # 生命值高的坦克稳定追踪
            self.chase_interval = 4
            self.chase_probability = 0.98
            self.chase_range = 180
            self.shoot_range = 130
        else:  # 普通坦克
            self.chase_interval = 5
            self.chase_probability = 0.95
            self.chase_range = 150
            self.shoot_range = 100

        # 射击相关参数
        self.shoot_delay = 0
        self.shoot_interval = 60  # 射击冷却时间
        self.last_target_pos = None  # 记录上一次目标位置

    # 射击子弹方法
    def shoot(self):
        # 赋予子弹生命 并调用方法改变相应图片
        self.bullet.life = True
        self.bullet.changeImage(self.dir_x, self.dir_y)

        if self.dir_x == 0 and self.dir_y == -1:
            self.bullet.rect.left = self.rect.left + 20
            self.bullet.rect.bottom = self.rect.top + 1
        elif self.dir_x == 0 and self.dir_y == 1:
            self.bullet.rect.left = self.rect.left + 20
            self.bullet.rect.top = self.rect.bottom - 1
        elif self.dir_x == -1 and self.dir_y == 0:
            self.bullet.rect.right = self.rect.left - 1
            self.bullet.rect.top = self.rect.top + 20
        elif self.dir_x == 1 and self.dir_y == 0:
            self.bullet.rect.left = self.rect.right + 1
            self.bullet.rect.top = self.rect.top + 20

    def get_nearest_player_tank(self, tankGroup):
        min_distance = float('inf')
        target_tank = None
        
        for tank in tankGroup:
            if hasattr(tank, 'life') and tank.life > 0 and isinstance(tank, pygame.sprite.Sprite):
                # 计算与玩家坦克的距离
                dx = tank.rect.centerx - self.rect.centerx
                dy = tank.rect.centery - self.rect.centery
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < min_distance:
                    min_distance = distance
                    target_tank = tank
        
        return target_tank

    def predict_target_position(self, target_tank, bullet_speed=6):
        """预测目标位置，用于提前射击"""
        if not target_tank or not self.last_target_pos:
            return None

        # 计算目标移动速度
        current_pos = (target_tank.rect.centerx, target_tank.rect.centery)
        if self.last_target_pos:
            dx = current_pos[0] - self.last_target_pos[0]
            dy = current_pos[1] - self.last_target_pos[1]
            
            # 计算子弹到达时间
            distance = math.sqrt((target_tank.rect.centerx - self.rect.centerx)**2 + 
                               (target_tank.rect.centery - self.rect.centery)**2)
            time_to_hit = distance / bullet_speed
            
            # 预测位置
            predicted_x = current_pos[0] + dx * time_to_hit
            predicted_y = current_pos[1] + dy * time_to_hit
            
            # 更新上一次位置
            self.last_target_pos = current_pos
            
            return (predicted_x, predicted_y)
        
        self.last_target_pos = current_pos
        return current_pos

    def should_shoot(self, target_tank):
        """判断是否应该射击"""
        if not target_tank:
            return False

        # 计算与目标的距离
        dx = target_tank.rect.centerx - self.rect.centerx
        dy = target_tank.rect.centery - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)

        # 如果目标在射程内
        if distance <= self.shoot_range:
            # 检查当前方向是否对准了目标
            if abs(dx) > abs(dy):  # 水平方向
                if dx > 0 and self.dir_x == 1:  # 目标在右边且朝右
                    return True
                if dx < 0 and self.dir_x == -1:  # 目标在左边且朝左
                    return True
            else:  # 垂直方向
                if dy > 0 and self.dir_y == 1:  # 目标在下方且朝下
                    return True
                if dy < 0 and self.dir_y == -1:  # 目标在上方且朝上
                    return True
        return False

    def chase_player(self, target_tank):
        if target_tank:
            # 计算方向向量
            dx = target_tank.rect.centerx - self.rect.centerx
            dy = target_tank.rect.centery - self.rect.centery
            distance = math.sqrt(dx * dx + dy * dy)

            # 获取预测位置
            predicted_pos = self.predict_target_position(target_tank)
            if predicted_pos:
                dx = predicted_pos[0] - self.rect.centerx
                dy = predicted_pos[1] - self.rect.centery
            
            # 根据坦克类型调整追踪策略
            if self.kind == 2:  # 速度快的坦克采用更灵活的追踪
                if distance < self.chase_range:
                    # 允许斜向移动，实现更灵活的追踪
                    self.dir_x = 1 if dx > 0 else -1
                    self.dir_y = 1 if dy > 0 else -1
                    # 根据距离微调移动方向
                    if abs(dx) < 15:  # 更小的阈值，更精确的追踪
                        self.dir_x = 0
                    if abs(dy) < 15:
                        self.dir_y = 0
                else:
                    # 远距离时选择最优路径
                    if abs(dx) > abs(dy):
                        self.dir_x = 1 if dx > 0 else -1
                        self.dir_y = 0
                    else:
                        self.dir_x = 0
                        self.dir_y = 1 if dy > 0 else -1
            
            elif self.kind == 3:  # 生命值高的坦克使用稳定追踪
                if distance < self.chase_range:
                    if abs(dx) > abs(dy):
                        self.dir_x = 1 if dx > 0 else -1
                        self.dir_y = 0
                    else:
                        self.dir_x = 0
                        self.dir_y = 1 if dy > 0 else -1
                    # 近距离时尝试预判射击位置
                    if distance < self.shoot_range:
                        if predicted_pos:
                            dx = predicted_pos[0] - self.rect.centerx
                            dy = predicted_pos[1] - self.rect.centery
                            if abs(dx) > abs(dy):
                                self.dir_x = 1 if dx > 0 else -1
                            else:
                                self.dir_y = 1 if dy > 0 else -1
            
            else:  # 普通坦克使用基础追踪
                if abs(dx) > abs(dy):
                    self.dir_x = 1 if dx > 0 else -1
                    self.dir_y = 0
                else:
                    self.dir_x = 0
                    self.dir_y = 1 if dy > 0 else -1

    # 移动方法
    def move(self, tankGroup, brickGroup, ironGroup, riverGroup):
        # 获取最近的玩家坦克
        target_tank = self.get_nearest_player_tank(tankGroup)

        # 实时更新追踪
        self.chase_delay += 1
        if self.chase_delay >= self.chase_interval:
            self.chase_delay = 0
            if random.random() < self.chase_probability:
                self.chase_player(target_tank)

        # 智能射击判断
        self.shoot_delay += 1
        if self.shoot_delay >= self.shoot_interval:
            if self.should_shoot(target_tank):
                self.shoot()
                self.shoot_delay = 0

        # 进行移动
        self.rect = self.rect.move(self.speed * self.dir_x, self.speed * self.dir_y)

        # 选择相应图片
        if self.dir_x == 0 and self.dir_y == -1:
            self.tank_R0 = self.tank.subsurface((0, 0), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 0), (48, 48))
        elif self.dir_x == 0 and self.dir_y == 1:
            self.tank_R0 = self.tank.subsurface((0, 48), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 48), (48, 48))
        elif self.dir_x == -1 and self.dir_y == 0:
            self.tank_R0 = self.tank.subsurface((0, 96), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 96), (48, 48))
        elif self.dir_x == 1 and self.dir_y == 0:
            self.tank_R0 = self.tank.subsurface((0, 144), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 144), (48, 48))

        # 碰撞检测
        if self.rect.top < 3:
            self.rect = self.rect.move(self.speed * 0, self.speed * 1)
            self.dir_x, self.dir_y = random.choice(([0, 1], [0, -1], [1, 0], [-1, 0]))
        elif self.rect.bottom > 630 - 3:
            self.rect = self.rect.move(self.speed * 0, self.speed * -1)
            self.dir_x, self.dir_y = random.choice(([0, 1], [0, -1], [1, 0], [-1, 0]))
        elif self.rect.left < 3:
            self.rect = self.rect.move(self.speed * 1, self.speed * 0)
            self.dir_x, self.dir_y = random.choice(([0, 1], [0, -1], [1, 0], [-1, 0]))
        elif self.rect.right > 630 - 3:
            self.rect = self.rect.move(self.speed * -1, self.speed * 0)
            self.dir_x, self.dir_y = random.choice(([0, 1], [0, -1], [1, 0], [-1, 0]))

        # 碰撞墙体和其他坦克
        if pygame.sprite.spritecollide(self, ironGroup, False, None) \
                or pygame.sprite.spritecollide(self, tankGroup, False, None) \
                or pygame.sprite.spritecollide(self, riverGroup, False, None):
            self.rect = self.rect.move(self.speed * -self.dir_x, self.speed * -self.dir_y)
            self.dir_x, self.dir_y = random.choice(([0, 1], [0, -1], [1, 0], [-1, 0]))
