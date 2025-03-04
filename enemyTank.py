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
            self.chase_interval = 2
            self.chase_probability = 1.0
            self.chase_range = 300
            self.shoot_range = 200
            self.path_update_interval = 5
            self.random_move_chance = 0.15  # 更高的随机性
        elif self.kind == 3:  # 生命值高的坦克稳定追踪
            self.chase_interval = 3
            self.chase_probability = 0.98
            self.chase_range = 250
            self.shoot_range = 180
            self.path_update_interval = 8
            self.random_move_chance = 0.1
        else:  # 普通坦克
            self.chase_interval = 4
            self.chase_probability = 0.95
            self.chase_range = 200
            self.shoot_range = 150
            self.path_update_interval = 10
            self.random_move_chance = 0.08

        # 射击相关参数
        self.shoot_delay = 0
        self.shoot_interval = 60  # 射击冷却时间
        self.last_target_pos = None  # 记录上一次目标位置

        # 路径规划相关参数
        self.path_update_delay = 0
        self.current_path = []  # 当前规划的路径
        self.path_index = 0  # 当前路径点索引
        self.obstacle_avoidance_range = 50  # 障碍物避让范围

        # 增加新的移动相关参数
        self.stuck_time = 0  # 记录卡住的时间
        self.last_position = None  # 记录上一次位置
        self.stuck_threshold = 30  # 卡住判定阈值
        self.escape_direction = None  # 逃离方向
        self.escape_time = 0  # 逃离时间

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

    def find_path_to_target(self, target_tank, brickGroup, ironGroup, riverGroup):
        """使用改进的A*算法寻找路径"""
        if not target_tank:
            return []

        # 获取起点和终点
        start = (self.rect.centerx, self.rect.centery)
        end = (target_tank.rect.centerx, target_tank.rect.centery)

        # 创建网格
        grid_size = 24  # 一个格子的大小
        start_grid = (start[0] // grid_size, start[1] // grid_size)
        end_grid = (end[0] // grid_size, end[1] // grid_size)

        # 使用A*算法
        open_set = {start_grid}
        closed_set = set()
        came_from = {}
        g_score = {start_grid: 0}
        f_score = {start_grid: abs(start_grid[0] - end_grid[0]) + abs(start_grid[1] - end_grid[1])}

        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == end_grid:
                # 重建路径
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_grid)
                path.reverse()
                return path

            open_set.remove(current)
            closed_set.add(current)

            # 获取相邻节点
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # 检查边界
                if not (0 <= neighbor[0] < 26 and 0 <= neighbor[1] < 26):
                    continue
                    
                if neighbor in closed_set:
                    continue

                # 检查碰撞
                test_rect = pygame.Rect(neighbor[0] * grid_size, neighbor[1] * grid_size, grid_size, grid_size)
                collision = False
                for brick in brickGroup:
                    if test_rect.colliderect(brick.rect):
                        collision = True
                        break
                for iron in ironGroup:
                    if test_rect.colliderect(iron.rect):
                        collision = True
                        break
                for river in riverGroup:
                    if test_rect.colliderect(river.rect):
                        collision = True
                        break
                
                if collision:
                    continue

                tentative_g_score = g_score[current] + 1

                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                    continue

                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + abs(neighbor[0] - end_grid[0]) + abs(neighbor[1] - end_grid[1])

        # 如果找不到路径，返回直接路径
        return [(start_grid[0], start_grid[1]), (end_grid[0], end_grid[1])]

    def update_path(self, target_tank, brickGroup, ironGroup, riverGroup):
        """更新路径规划"""
        self.path_update_delay += 1
        if self.path_update_delay >= self.path_update_interval:
            self.path_update_delay = 0
            # 重新规划路径
            self.current_path = self.find_path_to_target(target_tank, brickGroup, ironGroup, riverGroup)
            self.path_index = 0

    def follow_path(self):
        """沿着规划的路径移动"""
        if not self.current_path or self.path_index >= len(self.current_path):
            return False

        # 获取下一个路径点
        next_point = self.current_path[self.path_index]
        current_pos = (self.rect.centerx, self.rect.centery)
        target_pos = (next_point[0] * 24 + 12, next_point[1] * 24 + 12)

        # 计算移动方向
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]

        # 如果足够接近当前路径点，移动到下一个点
        if abs(dx) < 5 and abs(dy) < 5:
            self.path_index += 1
            return True

        # 设置移动方向
        if abs(dx) > abs(dy):
            self.dir_x = 1 if dx > 0 else -1
            self.dir_y = 0
        else:
            self.dir_x = 0
            self.dir_y = 1 if dy > 0 else -1

        return True

    def is_stuck(self):
        """检查坦克是否卡住"""
        if self.last_position is None:
            self.last_position = (self.rect.centerx, self.rect.centery)
            return False
            
        current_pos = (self.rect.centerx, self.rect.centery)
        distance = math.sqrt((current_pos[0] - self.last_position[0])**2 + 
                           (current_pos[1] - self.last_position[1])**2)
        
        if distance < 2:  # 如果移动距离很小
            self.stuck_time += 1
        else:
            self.stuck_time = 0
            self.last_position = current_pos
            
        return self.stuck_time > self.stuck_threshold

    def find_escape_direction(self, tankGroup, brickGroup, ironGroup, riverGroup):
        """寻找逃离方向"""
        best_direction = None
        max_distance = 0
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            test_rect = self.rect.copy()
            test_rect.move_ip(dx * self.speed * 3, dy * self.speed * 3)  # 测试更远的距离
            
            # 检查是否与障碍物碰撞
            collision = False
            for iron in ironGroup:
                if test_rect.colliderect(iron.rect):
                    collision = True
                    break
            for tank in tankGroup:
                if test_rect.colliderect(tank.rect):
                    collision = True
                    break
            for river in riverGroup:
                if test_rect.colliderect(river.rect):
                    collision = True
                    break
            
            if not collision:
                # 计算这个方向能移动的距离
                distance = math.sqrt((test_rect.centerx - self.rect.centerx)**2 + 
                                  (test_rect.centery - self.rect.centery)**2)
                if distance > max_distance:
                    max_distance = distance
                    best_direction = (dx, dy)
        
        return best_direction

    def move(self, tankGroup, brickGroup, ironGroup, riverGroup):
        # 获取最近的玩家坦克
        target_tank = self.get_nearest_player_tank(tankGroup)

        # 检查是否卡住
        if self.is_stuck():
            # 如果卡住，尝试逃离
            if self.escape_direction is None:
                self.escape_direction = self.find_escape_direction(tankGroup, brickGroup, ironGroup, riverGroup)
                self.escape_time = 0
            
            if self.escape_direction:
                self.escape_time += 1
                if self.escape_time < 20:  # 逃离一段时间
                    self.dir_x, self.dir_y = self.escape_direction
                else:
                    self.escape_direction = None
                    self.escape_time = 0
                    self.stuck_time = 0
            else:
                # 如果找不到逃离方向，随机移动
                self.dir_x, self.dir_y = random.choice(([0, 1], [0, -1], [1, 0], [-1, 0]))
                self.stuck_time = 0
        else:
            # 正常追踪逻辑
            self.update_path(target_tank, brickGroup, ironGroup, riverGroup)
            
            # 实时更新追踪
            self.chase_delay += 1
            if self.chase_delay >= self.chase_interval:
                self.chase_delay = 0
                if random.random() < self.chase_probability:
                    # 随机移动检查
                    if random.random() < self.random_move_chance:
                        self.dir_x, self.dir_y = random.choice(([0, 1], [0, -1], [1, 0], [-1, 0]))
                    else:
                        # 尝试沿着规划的路径移动
                        if not self.follow_path():
                            # 如果无法沿着路径移动，使用直接追踪
                            self.chase_player(target_tank)

        # 智能射击判断
        self.shoot_delay += 1
        if self.shoot_delay >= self.shoot_interval:
            if self.should_shoot(target_tank):
                self.shoot()
                self.shoot_delay = 0

        # 保存当前位置
        old_rect = self.rect.copy()

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

        # 边界检查
        if self.rect.top < 3:
            self.rect = old_rect
            # 在边缘处优先选择水平移动
            if target_tank:
                if target_tank.rect.centerx > self.rect.centerx:
                    self.dir_x, self.dir_y = 1, 0
                else:
                    self.dir_x, self.dir_y = -1, 0
            else:
                self.dir_x, self.dir_y = random.choice(([1, 0], [-1, 0]))
        elif self.rect.bottom > 630 - 3:
            self.rect = old_rect
            if target_tank:
                if target_tank.rect.centerx > self.rect.centerx:
                    self.dir_x, self.dir_y = 1, 0
                else:
                    self.dir_x, self.dir_y = -1, 0
            else:
                self.dir_x, self.dir_y = random.choice(([1, 0], [-1, 0]))
        elif self.rect.left < 3:
            self.rect = old_rect
            # 在边缘处优先选择垂直移动
            if target_tank:
                if target_tank.rect.centery > self.rect.centery:
                    self.dir_x, self.dir_y = 0, 1
                else:
                    self.dir_x, self.dir_y = 0, -1
            else:
                self.dir_x, self.dir_y = random.choice(([0, 1], [0, -1]))
        elif self.rect.right > 630 - 3:
            self.rect = old_rect
            if target_tank:
                if target_tank.rect.centery > self.rect.centery:
                    self.dir_x, self.dir_y = 0, 1
                else:
                    self.dir_x, self.dir_y = 0, -1
            else:
                self.dir_x, self.dir_y = random.choice(([0, 1], [0, -1]))

        # 碰撞检测
        if pygame.sprite.spritecollide(self, ironGroup, False, None) \
                or pygame.sprite.spritecollide(self, tankGroup, False, None) \
                or pygame.sprite.spritecollide(self, riverGroup, False, None):
            self.rect = old_rect
            # 碰撞时重新规划路径
            self.current_path = []
            self.path_index = 0
            
            # 智能选择新方向
            possible_directions = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                test_rect = self.rect.copy()
                test_rect.move_ip(dx * self.speed, dy * self.speed)
                # 检查是否与任何障碍物碰撞
                collision = False
                for iron in ironGroup:
                    if test_rect.colliderect(iron.rect):
                        collision = True
                        break
                for tank in tankGroup:
                    if test_rect.colliderect(tank.rect):
                        collision = True
                        break
                for river in riverGroup:
                    if test_rect.colliderect(river.rect):
                        collision = True
                        break
                
                if not collision:
                    possible_directions.append((dx, dy))
            
            if possible_directions:
                # 选择最接近目标的方向
                best_direction = min(possible_directions, 
                    key=lambda d: abs(d[0] * (target_tank.rect.centerx - self.rect.centerx) + 
                                    d[1] * (target_tank.rect.centery - self.rect.centery)))
                self.dir_x, self.dir_y = best_direction
            else:
                # 如果没有可行方向，随机选择一个方向
                self.dir_x, self.dir_y = random.choice(([0, 1], [0, -1], [1, 0], [-1, 0]))
