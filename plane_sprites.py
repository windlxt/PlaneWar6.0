import pygame
import random
import math
import subprocess


# 获取屏幕分辨率
def get_screen_resolution():
    output = subprocess.Popen(r'xrandr | grep "\*" | cut -d" " -f4',
                              shell=True, stdout=subprocess.PIPE).communicate()[0]
    resolution_list = output.split()[0].split(b'x')
    # return {'width': resolution_list[0], 'height': resolution_list[1]}
    return int(resolution_list[0]), int(resolution_list[1])


my_resolution = get_screen_resolution()
print('屏幕分辨率：', my_resolution)
# 定义屏幕大小的常量
SCREEN_RECT = pygame.Rect(0, 0, my_resolution[0], my_resolution[1])

# 刷新的帧率，画面多少毫秒刷新一次
FRAME_PER_SEC = 60
# 创建敌机的定时器常量
CREATE_ENEMY_EVENT = pygame.USEREVENT
# 英雄发射子弹事件定时器常量
HERO_FIRE_EVENT = pygame.USEREVENT + 1
# 敌人发射子弹事件定时器常量
ENEMY_FIRE_EVENT = pygame.USEREVENT + 2
# 计算需要多少个炸弹从底部飞出
NUM_CLEAR_SCREEN = 15
# 计算需要多少个炸弹从四周飞出
NUM_CIRCLE = 36
# 敌人飞机出现列表
IMAGE_LIST = ["./images/enemy1.png", "./images/enemy1.png",
              "./images/enemy2.png", "./images/enemy2.png",
              "./images/enemy3.png"]
# 创建敌人飞机子弹的精灵组（全局1个组），因为敌人飞机有很多，所有敌人子弹加入这个组
bullets_enemy = pygame.sprite.Group()
# 创建英雄炸弹精灵组
bomb_hero = pygame.sprite.Group()


class GameSprite(pygame.sprite.Sprite):
    """飞机大战游戏精灵"""

    def __init__(self, image_name, speed_y=1):
        # 调用父类的初始化方法
        super().__init__()

        # 定义对象的属性,图像、位置、速度
        self.image = pygame.image.load(image_name)
        self.rect = self.image.get_rect()
        self.speed_y = speed_y
        self.speed_x = 0

    def update(self):
        # 在屏幕的上下左右方向上移动
        self.rect.centerx += self.speed_x
        self.rect.centery += self.speed_y


class Background(GameSprite):
    """游戏背景精灵"""

    def __init__(self, is_alt=False):

        # 1. 调用父类方法实现精灵的创建
        super().__init__("./images/bj4.jpg")
        # 2. 判断是否是交替图像，如果是，需要设置图片初始位置在屏幕上方
        if is_alt:
            self.rect.bottom = 0

    def update(self):

        # 1.调用父类的方法实现垂直移动
        super().update()
        # 2.判断是否移除屏幕，如果移除了，再将图片设置到屏幕的上方
        if self.rect.y >= SCREEN_RECT.height:
            # self.rect.y = -self.rect.height  # 或者
            self.rect.bottom = 0


class Enemy(GameSprite):
    """敌机精灵"""

    def __init__(self):
        # 敌人飞机ID
        self.number = random.randint(0, 4)
        # 1.调用父类方法，创建敌机精灵，同时制定敌机图片
        super().__init__(IMAGE_LIST[self.number])
        # 2.制定敌机的初始随机速度
        self.speed_y = random.randint(4, 10)
        # 3.制定敌机的初始随机位置
        self.rect.bottom = 0
        self.max_x = SCREEN_RECT.width - self.rect.width
        self.rect.x = random.randint(0, self.max_x)
        # 4.敌人飞机左右 speed
        self.speed_x = random.randint(-5, 5)

    def update(self):
        # 1.调用父类方法，保持飞行方向
        super().update()
        # 2.判断是否飞出屏幕，如果是，需要从精灵组删除敌机
        if self.rect.y >= SCREEN_RECT.height:
            # print("飞出屏幕，需要从精灵组删除...")
            # kill方法可以将精灵从所有精灵组中移除，精灵组就会被自动销毁
            self.kill()
        # 3.左右两侧返回，且速度增加
        if self.rect.x >= self.max_x:
            self.speed_x = -self.speed_x * 2
        if self.rect.x < 0:
            self.speed_x = -self.speed_x * 2

    def fire(self):
        # print("发射子弹...")
        for i in range(3):
            if self.number == 0 or self.number == 1:
                self.bullet = BulletEnemy()
            elif self.number == 2 or self.number == 3:
                self.bullet = BulletEnemy("./images/bullet10.png")
            elif self.number == 4:
                self.bullet = BulletEnemy("./images/bullet20.png")
            # 2.设置精灵的位置
            self.bullet.rect.top = self.rect.bottom
            self.bullet.rect.centerx = self.rect.centerx - 65 + 65 * i
            # 3.加入敌人子弹精灵组，是个全局变量
            bullets_enemy.add(self.bullet)

    def __del__(self):
        # print("敌机挂了... %s" % self.rect)
        pass


class Hero(GameSprite):
    """英雄精灵"""

    def __init__(self):
        # 1.调用父类方法，设置初始速度为0,位置不动
        super().__init__("./images/me1.png", 0)
        # 2.设置英雄的初始位置
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = SCREEN_RECT.bottom - 120
        # 3.创建子弹的精灵组
        self.bullets = pygame.sprite.Group()
        # 4.创建导弹的精灵组
        self.missiles = pygame.sprite.Group()

    def update(self):
        # 1.调用父类方法，保持飞行方向
        super().update()
        # 2.控制英雄的位置，不能飞出屏幕
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right

        if self.rect.bottom > SCREEN_RECT.bottom:
            self.rect.bottom = SCREEN_RECT.bottom
        elif self.rect.y <= 0:
            self.rect.y = 0

    def fire0(self):
        """自动发射的子弹"""
        # print("发射子弹...")
        for i in range(1):
            # 1.创建子弹精灵
            bullet1 = Bullet()
            # 2.设置精灵的位置
            bullet1.rect.bottom = self.rect.y - i * 20
            bullet1.rect.centerx = self.rect.centerx
            # 3.将精灵添加到精灵组
            self.bullets.add(bullet1)

            # # 生成其他子弹，确定位置，加入精灵组
            # bullet2 = Bullet()
            # bullet2.rect.bottom = self.rect.y - i * 20
            # bullet2.speed_x = -1
            # bullet2.rect.centerx = self.rect.centerx -10
            # # =========================================
            # bullet3 = Bullet()
            # bullet3.rect.bottom = self.rect.y - i * 20
            # bullet3.speed_x = 1
            # bullet3.rect.centerx = self.rect.centerx +10
            # # =========================================
            # bullet4 = Bullet()
            # bullet4.rect.bottom = self.rect.y - i * 20
            # bullet4.speed_x = -2
            # bullet4.rect.centerx = self.rect.centerx + 15
            # # =========================================
            # bullet5 = Bullet()
            # bullet5.rect.bottom = self.rect.y - i * 20
            # bullet5.speed_x = 2
            # bullet5.rect.centerx = self.rect.centerx - 15
            # # =========================================
            # self.bullets.add(bullet2)
            # self.bullets.add(bullet3)
            # self.bullets.add(bullet4)
            # self.bullets.add(bullet5)

    def fire1(self):
        """发射特殊子弹"""
        # print("发射子弹...")
        for i in range(1):
            # 1.创建子弹精灵
            bullet1 = Bullet("./images/bullet9.png")
            # 2.设置精灵的位置
            bullet1.rect.bottom = self.rect.y - i * 20
            bullet1.rect.centerx = self.rect.centerx

            # 3.创建多列子弹
            bullet2 = Bullet("./images/bullet9.png")
            bullet2.rect.bottom = self.rect.y - i * 20
            bullet2.speed_x = -1
            bullet2.rect.centerx = self.rect.centerx - 10

            bullet3 = Bullet("./images/bullet9.png")
            bullet3.rect.bottom = self.rect.y - i * 20
            bullet3.speed_x = 1
            bullet3.rect.centerx = self.rect.centerx + 10

            bullet4 = Bullet("./images/bullet9.png")
            bullet4.rect.bottom = self.rect.y - i * 20
            bullet4.speed_x = -2
            bullet4.rect.centerx = self.rect.centerx + 15

            bullet5 = Bullet("./images/bullet9.png")
            bullet5.rect.bottom = self.rect.y - i * 20
            bullet5.speed_x = 2
            bullet5.rect.centerx = self.rect.centerx - 15

            # 3.将精灵添加到精灵组
            self.bullets.add(bullet1)
            self.bullets.add(bullet2)
            self.bullets.add(bullet3)
            # self.bullets.add(bullet4)
            # self.bullets.add(bullet5)

    def fire2(self):
        # print("发射导弹...")
        for i in range(1):
            # 1.创建子弹精灵
            bullet1 = Bullet("./images/bullet18.png", -6)
            # 2.设置精灵的位置
            bullet1.rect.bottom = self.rect.y - i * 20
            bullet1.rect.centerx = self.rect.centerx

            # 3.创建多列子弹
            bullet2 = Bullet("./images/bullet18.png", -6)
            bullet2.rect.bottom = self.rect.y - i * 20
            bullet2.speed_x = -1
            bullet2.rect.centerx = self.rect.centerx - 8

            bullet3 = Bullet("./images/bullet18.png", -6)
            bullet3.rect.bottom = self.rect.y - i * 20
            bullet3.speed_x = 1
            bullet3.rect.centerx = self.rect.centerx + 8

            bullet4 = Bullet("./images/bullet18.png", -6)
            bullet4.rect.bottom = self.rect.y - i * 20
            bullet4.speed_x = -3
            bullet4.rect.centerx = self.rect.centerx - 12

            bullet5 = Bullet("./images/bullet18.png", -6)
            bullet5.rect.bottom = self.rect.y - i * 20
            bullet5.speed_x = 3
            bullet5.rect.centerx = self.rect.centerx + 12

            # 3.将精灵添加到精灵组
            self.bullets.add(bullet1)
            self.bullets.add(bullet2)
            self.bullets.add(bullet3)
            self.bullets.add(bullet4)
            self.bullets.add(bullet5)

    def fire_missile(self):
        # 1.创建导弹精灵
        self.missile = Missile()
        # 2.设置精灵的位置
        self.missile.rect.centery = self.rect.centery
        self.missile.rect.centerx = self.rect.centerx
        # 3.将精灵添加到精灵组
        self.missiles.add(self.missile)

    def fire_clear_screen(self):
        for i in range(NUM_CLEAR_SCREEN):
            # 1.创建导弹精灵
            self.missile_clear_screen = MissileClearScreen()
            # 2.设置精灵的位置
            self.missile_clear_screen.rect.x = i * (self.rect.width + 3) + 10
            self.missile_clear_screen.rect.y = 864
            # 3.将精灵添加到精灵组
            self.missiles.add(self.missile_clear_screen)

    def fire_circle(self):
        img_list = ['./images/bullet9.png', './images/bullet10.png', './images/bullet11.png', './images/bullet12.png',
                    './images/bullet13.png', './images/bullet14.png']
        img = random.choice(img_list)
        for i in range(NUM_CIRCLE):
            # 1.创建导弹精灵
            self.missile_circle = MissileCircle(img)
            # 2.设置精灵的位置
            self.missile_circle.angle += i * 10
            self.missile_circle.rect.centerx = self.rect.centerx + 50*math.sin(self.missile_circle.angle)
            self.missile_circle.rect.centery = self.rect.centery + 50*math.cos(self.missile_circle.angle)
            # 3.将精灵添加到精灵组
            self.missiles.add(self.missile_circle)

    def fire_bomb(self):
        self.missile_bomb = MissileBomb()
        # 2.设置精灵的位置
        self.missile_bomb.rect.centerx = self.rect.centerx
        self.missile_bomb.rect.centery = self.rect.y - 20
        # 3.将精灵添加到精灵组
        self.missiles.add(self.missile_bomb)


class EnemyCollide(GameSprite):
    """敌机坠毁精灵"""

    def __init__(self, image):
        # 1.调用父类方法，创建敌机坠毁精灵，同时制定敌机坠毁图片
        super().__init__(image)
        # 2.制定敌机坠毁的速度
        self.speed_y = 1

    def __del__(self):
        # print("Enemy plane 挂了... %s" % self.rect)
        pass


class HeroCollide(GameSprite):
    """英雄挂了精灵"""

    def __init__(self, image):
        # 1.调用父类方法，创建英雄坠毁精灵，同时制定英雄坠毁图片
        super().__init__(image)
        # 2.制定英雄坠毁的速度
        self.speed_y = 1

    def __del__(self):
        # print("Hero plane 挂了... %s" % self.rect)
        pass


class Bullet(GameSprite):
    """子弹精灵"""

    def __init__(self, img="./images/bullet6.png", speed=-4):
        # 调用父类方法，设置子弹图片，设置初始速度
        super().__init__(img, speed)

    def update(self):
        # 调用父类方法，让子弹沿垂直方向飞行
        super().update()

        # 判断子弹是否飞出屏幕
        if self.rect.bottom < 0:
            self.kill()

    def __del__(self):
        # print("子弹被销毁了...")
        pass


class Missile(GameSprite):
    """螺旋导弹精灵"""
    def __init__(self, img="./images/bullet7.png"):
        # 调用父类方法，设置子弹图片，设置初始速度
        super().__init__(img)
        self.distance = 0
        self.angle = 0
        self.ratio = 1

    def update(self):
        # 判断导弹是否飞出屏幕
        if self.distance > 500:
            self.kill()

        # 计算导弹螺旋飞行轨迹
        self.ratio += 0.01
        self.distance += 1 * self.ratio
        self.angle += 0.27
        self.rect.centerx += self.distance * math.sin(self.angle)
        self.rect.centery += self.distance * math.cos(self.angle)

    def __del__(self):
        # print("导弹被销毁了...")
        pass


class MissileClearScreen(GameSprite):
    """清屏导弹精灵"""
    def __init__(self, img="./images/bullet21.png"):
        # 调用父类的初始化方法
        super().__init__(img)
        # 定义对象的属性,图像、位置、速度
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()

        self.speed_y = 1
        self.ratio = 0

    def update(self):
        self.ratio += 0.5
        self.rect.centery -= self.speed_y * self.ratio
        # 判断导弹是否飞出屏幕
        if self.rect.centery <= -self.rect.height:
            self.kill()

    def __del__(self):
        # print("导弹被销毁了...")
        pass


class MissileCircle(GameSprite):
    """清屏导弹精灵"""
    def __init__(self, img="./images/bullet13.png"):
        # 调用父类的初始化方法
        super().__init__(img)
        # 定义对象的属性,图像、位置、速度
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()

        # self.speed_x = 1
        # self.speed_y = 1
        self.ratio = 0
        self.distence = 1
        self.angle = 0

    def update(self):
        self.ratio += 0.05
        self.distence += self.ratio
        self.rect.centerx += self.distence * math.sin(self.angle)
        self.rect.centery += self.distence * math.cos(self.angle)
        # 判断导弹是否飞出屏幕
        if self.rect.bottom < -my_resolution[1] or self.rect.top > 2*my_resolution[1]\
                or self.rect.x < -my_resolution[0] or self.rect.x > 2*my_resolution[0]:
            self.kill()

    def __del__(self):
        # print("导弹被销毁了...")
        pass


class MissileBomb(GameSprite):
    """炸弹精灵"""
    def __init__(self, img="./images/bomb.png", x=600, y=200):
        # 调用父类的初始化方法
        super().__init__(img)
        # 定义对象的属性,图像、位置、速度
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()

        self.distance = 0
        self.ratio = 0
        self.pos = 0

    def update(self):
        # 判断导弹是否飞出屏幕
        if self.pos > 200:
            self.kill()

        self.ratio += 0.01
        self.distance += self.ratio
        self.rect.centery -= self.distance
        self.pos += self.distance

    def __del__(self):
        img_list = ['./images/bullet9.png', './images/bullet10.png', './images/bullet11.png', './images/bullet12.png',
                    './images/bullet13.png', './images/bullet14.png']
        img = random.choice(img_list)
        for i in range(NUM_CIRCLE):
            # 1.创建导弹精灵
            self.missile_circle = MissileCircle(img)
            # 2.设置精灵的位置
            self.missile_circle.angle += i * 10
            self.missile_circle.rect.centerx = self.rect.centerx + 20 * math.sin(self.missile_circle.angle)
            self.missile_circle.rect.centery = self.rect.centery + 20 * math.cos(self.missile_circle.angle)
            # 3.将精灵添加到精灵组
            bomb_hero.add(self.missile_circle)


class BulletEnemy(GameSprite):
    """敌人子弹精灵"""

    def __init__(self, img="./images/bullet4.png", speed=8):
        # 调用父类方法，设置子弹图片，设置初始速度
        super().__init__(img, speed)

    def update(self):
        # 调用父类方法，让子弹沿垂直方向飞行
        super().update()

        # 判断子弹是否飞出屏幕
        if self.rect.centery > SCREEN_RECT.height:
            self.kill()
