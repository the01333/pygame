# 1 引入需要的模块
import pygame
import random

# 1 配置图片地址
IMAGE_PATH = 'imgs/'
# 1 设置页面宽高
scrrr_width = 800
scrrr_height = 560
# 1 创建控制游戏结束的状态
GAMEOVER = False
# 4 图片加载报错处理
LOG = '文件:{}中的方法:{}出错'.format(__file__, __name__)


# 3 创建地图类
class Map():
    # 3 存储两张不同颜色的图片名称
    map_names_list = [IMAGE_PATH + 'map1.png', IMAGE_PATH + 'map2.png']

    # 3 初始化地图
    def __init__(self, x, y, img_index):
        self.image = pygame.image.load(Map.map_names_list[img_index])
        self.position = (x, y)
        # 是否能够种植
        self.can_grow = True

    # 3 加载地图
    def load_map(self):
        MainGame.window.blit(self.image, self.position)


# 4 植物类
class Plant(pygame.sprite.Sprite):
    def __init__(self):
        super(Plant, self).__init__()
        self.live = True

    # 加载图片
    def load_image(self):
        if hasattr(self, 'image') and hasattr(self, 'rect'):
            MainGame.window.blit(self.image, self.rect)
        else:
            print(LOG)


# 5 向日葵类
class Sunflower(Plant):
    def __init__(self, x, y):
        super(Sunflower, self).__init__()
        self.image = pygame.image.load('imgs/sunflower.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.price = 50
        self.hp = 100
        # 5 时间计数器
        self.time_count = 0

    # 5 新增功能：生成阳光
    def produce_money(self):
        self.time_count += 1
        if self.time_count == 25:
            MainGame.money += 5
            self.time_count = 0

    # 5 向日葵加入到窗口中
    def display_sunflower(self):
        MainGame.window.blit(self.image, self.rect)


# 6 豌豆射手类
class PeaShooter(Plant):
    def __init__(self, x, y):
        super(PeaShooter, self).__init__()
        # self.image 为一个 surface
        self.image = pygame.image.load('imgs/peashooter.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.price = 50
        self.hp = 200
        # 6 发射计数器
        self.shot_count = 0

    # 6 增加射击方法
    def shot(self):
        # 6 记录是否应该射击
        should_fire = False
        for zombie in MainGame.zombie_list:
            if zombie.rect.y == self.rect.y and zombie.rect.x < 800 and zombie.rect.x > self.rect.x:
                should_fire = True
        # 6 如果活着
        if self.live and should_fire:
            self.shot_count += 1
            # 将发射速度从25改为40，减慢发射速度
            if self.shot_count == 40:
                # 6 基于当前豌豆射手的位置，创建子弹
                peabullet = PeaBullet(self)
                # 6 将子弹存储到子弹列表中
                MainGame.peabullet_list.append(peabullet)
                self.shot_count = 0

    # 6 将豌豆射手加入到窗口中的方法
    def display_peashooter(self):
        MainGame.window.blit(self.image, self.rect)


# 7 豌豆子弹类
class PeaBullet(pygame.sprite.Sprite):
    def __init__(self, peashooter):
        self.live = True
        self.image = pygame.image.load('imgs/peabullet.png')
        self.damage = 100  # 将伤害从50提高到100
        self.speed = 10
        self.rect = self.image.get_rect()
        self.rect.x = peashooter.rect.x + 60
        self.rect.y = peashooter.rect.y + 15

    def move_bullet(self):
        # 7 在屏幕范围内，实现往右移动
        if self.rect.x < scrrr_width:
            self.rect.x += self.speed
        else:
            self.live = False

    # 7 新增，子弹与僵尸的碰撞
    def hit_zombie(self):
        for zombie in MainGame.zombie_list:
            if pygame.sprite.collide_rect(self, zombie):
                # 打中僵尸之后，修改子弹的状态，
                self.live = False
                # 僵尸掉血
                zombie.hp -= self.damage
                if zombie.hp <= 0:
                    zombie.live = False
                    self.nextLevel()

    # 7闯关方法
    def nextLevel(self):
        MainGame.score += 20
        MainGame.remnant_score -= 20
        for i in range(1, 100):
            if MainGame.score == 100 * i and MainGame.remnant_score == 0:
                MainGame.remnant_score = 100 * i
                MainGame.shaoguan += 1
                MainGame.produce_zombie = max(300, MainGame.produce_zombie - 50)  # 增加间隔，避免密集生成
                # 创建MainGame实例并调用show_level_complete
                main_game = MainGame()
                main_game.show_level_complete()  # 显示通关信息

    def display_peabullet(self):
        MainGame.window.blit(self.image, self.rect)


# 9 僵尸类
class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Zombie, self).__init__()
        self.image = pygame.image.load('imgs/zombie.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # 僵尸血量随关卡提高而增加
        self.hp = 1000 + (MainGame.shaoguan - 1) * 200
        # 僵尸攻击力也随关卡提高而增加
        self.damage = 2 + (MainGame.shaoguan - 1)
        # 僵尸移动速度也随关卡提高而增加，但最大不超过3
        self.speed = min(1 + (MainGame.shaoguan - 1) * 0.5, 3)
        self.live = True
        self.stop = False

    # 9 僵尸的移动
    def move_zombie(self):
        if self.live and not self.stop:
            self.rect.x -= self.speed
            if self.rect.x < -80:
                # 8 调用游戏结束方法
                MainGame().gameOver()

    # 9 判断僵尸是否碰撞到植物，如果碰撞，调用攻击植物的方法
    def hit_plant(self):
        for plant in MainGame.plants_list:
            if pygame.sprite.collide_rect(self, plant):
                # 8  僵尸移动状态的修改
                self.stop = True
                self.eat_plant(plant)

    # 9 僵尸攻击植物
    def eat_plant(self, plant):
        # 9 植物生命值减少
        plant.hp -= self.damage
        # 9 植物死亡后的状态修改，以及地图状态的修改
        if plant.hp <= 0:
            a = plant.rect.y // 80 - 1
            b = plant.rect.x // 80
            map = MainGame.map_list[a][b]
            map.can_grow = True
            plant.live = False
            # 8 修改僵尸的移动状态
            self.stop = False

    # 9 将僵尸加载到地图中
    def display_zombie(self):
        MainGame.window.blit(self.image, self.rect)


# 1 主程序
class MainGame():
    # 2 创建关数，得分，剩余分数，钱数
    shaoguan = 1
    score = 0
    remnant_score = 100
    money = 200
    # 3 存储所有地图坐标点
    map_points_list = []
    # 3 存储所有的地图块
    map_list = []
    # 4 存储所有植物的列表
    plants_list = []
    # 7 存储所有豌豆子弹的列表
    peabullet_list = []
    # 9 新增存储所有僵尸的列表
    zombie_list = []
    count_zombie = 0
    produce_zombie = 100
    # 添加阳光自动生成计时器
    auto_sunshine_count = 0
    auto_sunshine_time = 150  # 自动产生阳光的时间间隔
    # 添加垃圾桶相关变量
    trash_bin_image = None
    trash_bin_rect = None
    is_dragging = False
    dragged_plant = None
    dragged_plant_map = None

    # 1 加载游戏窗口
    def init_window(self):
        # 1 调用显示模块的初始化
        pygame.display.init()
        # 1 创建窗口
        MainGame.window = pygame.display.set_mode([scrrr_width, scrrr_height])
        # 加载垃圾桶图标
        try:
            MainGame.trash_bin_image = pygame.image.load('imgs/trash.png')
            # 调整垃圾桶大小为60x60像素
            MainGame.trash_bin_image = pygame.transform.scale(MainGame.trash_bin_image, (60, 60))
            MainGame.trash_bin_rect = MainGame.trash_bin_image.get_rect()
            # 将垃圾桶放在右上角
            MainGame.trash_bin_rect.topleft = (scrrr_width - 70, 10)
        except pygame.error:
            # 如果没有垃圾桶图片，创建一个简单的方形代替
            MainGame.trash_bin_image = pygame.Surface((60, 60))
            MainGame.trash_bin_image.fill((255, 0, 0))  # 红色
            font = pygame.font.SysFont('kaiti', 20)
            text = font.render('垃圾桶', True, (255, 255, 255))
            text_rect = text.get_rect(center=(30, 30))
            MainGame.trash_bin_image.blit(text, text_rect)
            MainGame.trash_bin_rect = MainGame.trash_bin_image.get_rect()
            MainGame.trash_bin_rect.topleft = (scrrr_width - 70, 10)

    # 2 文本绘制
    def draw_text(self, content, size, color):
        pygame.font.init()
        font = pygame.font.SysFont('kaiti', size)
        text = font.render(content, True, color)
        return text

    # 2 加载帮助提示
    def load_help_text(self):
        text1 = self.draw_text('1.按左键创建向日葵 2.按右键创建豌豆射手 3.按鼠标中键拖拽植物到垃圾桶删除', 20, (255, 0, 0))
        MainGame.window.blit(text1, (5, 5))

    # 3 初始化坐标点
    def init_plant_points(self):
        for y in range(1, 7):
            points = []
            for x in range(10):
                point = (x, y)
                points.append(point)
            MainGame.map_points_list.append(points)
            print("MainGame.map_points_list", MainGame.map_points_list)

    # 3 初始化地图
    def init_map(self):
        for points in MainGame.map_points_list:
            temp_map_list = list()
            for point in points:
                # map = None
                if (point[0] + point[1]) % 2 == 0:
                    map = Map(point[0] * 80, point[1] * 80, 0)
                else:
                    map = Map(point[0] * 80, point[1] * 80, 1)
                # 将地图块加入到窗口中
                temp_map_list.append(map)
                print("temp_map_list", temp_map_list)
            MainGame.map_list.append(temp_map_list)
        print("MainGame.map_list", MainGame.map_list)

    # 3 将地图加载到窗口中
    def load_map(self):
        for temp_map_list in MainGame.map_list:
            for map in temp_map_list:
                map.load_map()

    # 6 增加豌豆射手发射处理
    def load_plants(self):
        for plant in MainGame.plants_list:
            # 6 优化加载植物的处理逻辑
            if plant.live:
                if isinstance(plant, Sunflower):
                    plant.display_sunflower()
                    plant.produce_money()
                elif isinstance(plant, PeaShooter):
                    plant.display_peashooter()
                    plant.shot()
            else:
                MainGame.plants_list.remove(plant)

    # 7 加载所有子弹的方法
    def load_peabullets(self):
        for b in MainGame.peabullet_list:
            if b.live:
                b.display_peabullet()
                b.move_bullet()
                # v1.9 调用子弹是否打中僵尸的方法
                b.hit_zombie()
            else:
                MainGame.peabullet_list.remove(b)

    # 8事件处理
    def deal_events(self):
        # 8 获取所有事件
        eventList = pygame.event.get()
        # 8 遍历事件列表，判断
        for e in eventList:
            if e.type == pygame.QUIT:
                self.gameOver()
            # 处理植物拖拽
            self.handle_plant_drag(e)
            # 处理鼠标点击种植
            if e.type == pygame.MOUSEBUTTONDOWN and not MainGame.is_dragging:
                # print('按下鼠标按键')
                print(e.pos)
                # print(e.button)#左键1  按下滚轮2 上转滚轮为4 下转滚轮为5  右键 3

                # 确保点击在有效的地图区域内
                x = e.pos[0] // 80
                y = e.pos[1] // 80
                print(x, y)
                # 确保坐标在有效范围内
                if y >= 1 and y <= 6 and x >= 0 and x < 10:
                    map = MainGame.map_list[y - 1][x]
                    print(map.position)
                    # 8 增加创建时候的地图装填判断以及金钱判断
                    if e.button == 1:
                        if map.can_grow and MainGame.money >= 50:
                            sunflower = Sunflower(map.position[0], map.position[1])
                            MainGame.plants_list.append(sunflower)
                            print('当前植物列表长度:{}'.format(len(MainGame.plants_list)))
                            map.can_grow = False
                            MainGame.money -= 50
                    elif e.button == 3 and not MainGame.is_dragging:  # 确保不是拖拽过程中
                        if map.can_grow and MainGame.money >= 50:
                            peashooter = PeaShooter(map.position[0], map.position[1])
                            MainGame.plants_list.append(peashooter)
                            print('当前植物列表长度:{}'.format(len(MainGame.plants_list)))
                            map.can_grow = False
                            MainGame.money -= 50

    # 9 新增初始化僵尸的方法
    def init_zombies(self):
        # 检查是否还有僵尸在场
        if not MainGame.zombie_list:
            # 如果没有僵尸，则一定生成一个，无论是否每行都有植物
            rows = list(range(1, 7))
            random.shuffle(rows)  # 打乱顺序
            dis = random.randint(3, 6) * 200
            zombie = Zombie(800 + dis, rows[0] * 80)
            MainGame.zombie_list.append(zombie)
            return

        max_zombies_per_row = 1  # 每行最多 1 只僵尸
        zombie_count_per_row = {i: 0 for i in range(1, 7)}  # 统计每行已有的僵尸数

        # 计算当前每行僵尸数量
        for zombie in MainGame.zombie_list:
            row = zombie.rect.y // 80
            if row in zombie_count_per_row:
                zombie_count_per_row[row] += 1

        # 交替生成僵尸，确保不会连续生成
        rows = list(range(1, 7))
        random.shuffle(rows)  # 打乱顺序，让僵尸随机生成在不同行

        for i in rows:
            if zombie_count_per_row[i] == 0:  # 该行没有僵尸才生成
                dis = random.randint(3, 6) * 200  # 让僵尸生成得更远
                zombie = Zombie(800 + dis, i * 80)
                MainGame.zombie_list.append(zombie)
                break  # 只生成一个僵尸，避免短时间内刷出多个

    # 9将所有僵尸加载到地图中
    def load_zombies(self):
        for zombie in MainGame.zombie_list:
            if zombie.live:
                zombie.display_zombie()
                zombie.move_zombie()
                # v2.0 调用是否碰撞到植物的方法
                zombie.hit_plant()
            else:
                MainGame.zombie_list.remove(zombie)

    # 添加自动生成阳光的方法
    def auto_generate_sunshine(self):
        MainGame.auto_sunshine_count += 1
        if MainGame.auto_sunshine_count >= MainGame.auto_sunshine_time:
            MainGame.money += 25
            MainGame.auto_sunshine_count = 0
            
    # 新增显示通关成功的方法
    def show_level_complete(self):
        # 暂停游戏
        is_paused = True
        # 创建矩形按钮
        next_level_rect = pygame.Rect(300, 250, 200, 50)
        exit_rect = pygame.Rect(300, 320, 200, 50)
        
        while is_paused:
            # 渲染文字和按钮
            MainGame.window.fill((255, 255, 255))
            level_text = self.draw_text('通关成功！', 50, (255, 0, 0))
            MainGame.window.blit(level_text, (300, 180))
            
            # 绘制按钮
            pygame.draw.rect(MainGame.window, (0, 255, 0), next_level_rect)
            pygame.draw.rect(MainGame.window, (255, 0, 0), exit_rect)
            
            # 绘制按钮文字
            next_level_text = self.draw_text('下一关', 36, (0, 0, 0))
            exit_text = self.draw_text('退出游戏', 36, (0, 0, 0))
            MainGame.window.blit(next_level_text, (350, 260))
            MainGame.window.blit(exit_text, (350, 330))
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameOver()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if next_level_rect.collidepoint(mouse_pos):
                        # 继续游戏进入下一关
                        self.prepare_next_level()  # 准备下一关
                        is_paused = False
                    elif exit_rect.collidepoint(mouse_pos):
                        # 退出游戏
                        self.gameOver()
            
            pygame.display.update()
            pygame.time.wait(10)

    # 新增准备下一关的方法
    def prepare_next_level(self):
        # 清空场上所有植物
        MainGame.plants_list.clear()
        
        # 清空子弹
        MainGame.peabullet_list.clear()
        
        # 清空僵尸
        MainGame.zombie_list.clear()
        
        # 将所有地图块重置为可种植状态
        for row in MainGame.map_list:
            for map_block in row:
                map_block.can_grow = True
        
        # 提高游戏难度
        # 1. 僵尸生成速度更快
        MainGame.produce_zombie = max(100, MainGame.produce_zombie - 40)
        
        # 2. 增加初始金钱作为补偿
        MainGame.money += 50 * MainGame.shaoguan
        
        print(f"准备进入第{MainGame.shaoguan}关，僵尸生成速度: {MainGame.produce_zombie}，当前金钱: {MainGame.money}")

    # 添加显示垃圾桶的方法
    def display_trash_bin(self):
        if MainGame.trash_bin_image and MainGame.trash_bin_rect:
            MainGame.window.blit(MainGame.trash_bin_image, MainGame.trash_bin_rect)
            
    # 添加拖拽功能和垃圾桶处理
    def handle_plant_drag(self, event):
        # 处理鼠标中键按下事件（滚轮点击）
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:  # 鼠标中键（滚轮）
            # 检查是否点击了植物
            for plant in MainGame.plants_list:
                if plant.rect.collidepoint(event.pos):
                    MainGame.is_dragging = True
                    MainGame.dragged_plant = plant
                    # 记录植物所在的地图块
                    x = plant.rect.x // 80
                    y = (plant.rect.y // 80) - 1 if plant.rect.y >= 80 else 0
                    if 0 <= y < len(MainGame.map_list) and 0 <= x < len(MainGame.map_list[0]):
                        MainGame.dragged_plant_map = MainGame.map_list[y][x]
                    break
                    
        # 处理鼠标移动事件
        elif event.type == pygame.MOUSEMOTION and MainGame.is_dragging and MainGame.dragged_plant:
            # 更新拖拽的植物位置跟随鼠标
            MainGame.dragged_plant.rect.center = event.pos
            
        # 处理鼠标释放事件
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2 and MainGame.is_dragging:
            # 检查是否放到了垃圾桶上
            if MainGame.trash_bin_rect and MainGame.trash_bin_rect.collidepoint(event.pos):
                # 移除植物并退回金币
                if isinstance(MainGame.dragged_plant, Sunflower) or isinstance(MainGame.dragged_plant, PeaShooter):
                    # 返回一半的金币
                    MainGame.money += MainGame.dragged_plant.price // 2
                # 标记该地图块可种植
                if MainGame.dragged_plant_map:
                    MainGame.dragged_plant_map.can_grow = True
                # 从植物列表中移除
                if MainGame.dragged_plant in MainGame.plants_list:
                    MainGame.plants_list.remove(MainGame.dragged_plant)
            else:
                # 如果没有放到垃圾桶，将植物放回原位
                if MainGame.dragged_plant and MainGame.dragged_plant_map:
                    MainGame.dragged_plant.rect.topleft = MainGame.dragged_plant_map.position
                
            # 重置拖拽状态
            MainGame.is_dragging = False
            MainGame.dragged_plant = None
            MainGame.dragged_plant_map = None

    # 1 开始游戏
    def start_game(self):
        # 1 初始化窗口
        self.init_window()
        # 3 初始化坐标和地图
        self.init_plant_points()
        self.init_map()
        # 9 调用初始化僵尸的方法
        self.init_zombies()
        # 1 只要游戏没结束，就一直循环
        while not GAMEOVER:
            # 1 渲染白色背景
            MainGame.window.fill((255, 255, 255))
            # 2 渲染的文字和坐标位置
            MainGame.window.blit(self.draw_text('当前钱数$: {}'.format(MainGame.money), 26, (255, 0, 0)), (500, 40))
            MainGame.window.blit(self.draw_text(
                '当前关数{}，得分{},距离下关还差{}分'.format(MainGame.shaoguan, MainGame.score, MainGame.remnant_score),
                26,
                (255, 0, 0)), (5, 40))
            self.load_help_text()

            # 3 需要反复加载地图
            self.load_map()
            # 6 调用加载植物的方法
            self.load_plants()
            # 7  调用加载所有子弹的方法
            self.load_peabullets()
            # 显示垃圾桶
            self.display_trash_bin()
            # 8 调用事件处理的方法
            self.deal_events()
            # 9 调用展示僵尸的方法
            self.load_zombies()
            # 调用自动生成阳光的方法
            self.auto_generate_sunshine()
            
            # 如果正在拖拽植物，将其绘制在鼠标位置（确保它显示在最上层）
            if MainGame.is_dragging and MainGame.dragged_plant:
                MainGame.window.blit(MainGame.dragged_plant.image, MainGame.dragged_plant.rect)
            
            # 9 计数器增长，每数到100，调用初始化僵尸的方法
            MainGame.count_zombie += 1
            if MainGame.count_zombie == MainGame.produce_zombie:
                self.init_zombies()
                MainGame.count_zombie = 0
            # 9 pygame自己的休眠
            pygame.time.wait(10)
            # 1 实时更新
            pygame.display.update()

    # 10 程序结束方法
    def gameOver(self):
        is_ended = True
        exit_rect = pygame.Rect(300, 320, 200, 50)

        while is_ended:
            # 渲染背景和文字
            MainGame.window.fill((255, 255, 255))
            MainGame.window.blit(self.draw_text('游戏结束', 50, (255, 0, 0)), (300, 200))

            # 绘制退出按钮
            pygame.draw.rect(MainGame.window, (255, 0, 0), exit_rect)
            exit_text = self.draw_text('退出游戏', 36, (0, 0, 0))
            MainGame.window.blit(exit_text, (350, 330))

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_ended = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if exit_rect.collidepoint(mouse_pos):
                        is_ended = False

            pygame.display.update()
            pygame.time.wait(10)

        print('游戏结束')
        global GAMEOVER
        GAMEOVER = True


# 1 启动主程序
if __name__ == '__main__':
    game = MainGame()
    game.start_game()
