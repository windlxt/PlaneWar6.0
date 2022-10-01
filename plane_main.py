import os
import threading
import time

import pygame

from plane_sprites import *

# 创建敌人飞机速度
CREATE_ENEMY_TIME = 1000


class PlaneGame(object):
    """飞机大战主游戏"""

    def __init__(self):
        print("游戏初始化...")
        pygame.init()
        pygame.font.init()
        self.my_font = pygame.font.Font('/home/liuxintao/PycharmProjects/微软雅黑.ttf', 32)
        # 1.创建游戏窗口,宽度x和高度y,常量SCREEN_RECT = pygame.Rect(0, 0, 480, 700)，SCREEN_RECT.size=(480,700)
        # self.screen = pygame.display.set_mode(SCREEN_RECT.size)
        self.screen = pygame.display.set_mode(flags=(pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF))
        # 2.创建游戏的时钟
        self.clock = pygame.time.Clock()
        # 3.调用私有方法，精灵和精灵组的创建
        self.__create_sprites()
        # 4.设置定时时间 - 创建敌机 1s，CREATE_ENEMY_EVENT创建敌机频率，HERO_FIRE_EVENT发射子弹频率
        pygame.time.set_timer(CREATE_ENEMY_EVENT, CREATE_ENEMY_TIME)
        pygame.time.set_timer(HERO_FIRE_EVENT, 200)
        pygame.time.set_timer(ENEMY_FIRE_EVENT, CREATE_ENEMY_TIME)
        # pygame.mixer.init()  # 初始化，用于放音乐
        pygame.mixer.init()
        # 播放背景音乐
        PlaneGame.play_bg_sound_thread(r"./music/bj.mp3")
        # 消灭飞机数量统计，显示位置
        self.plane_small = 0
        self.plane_mid = 0
        self.plane_big = 0
        self.self_die = 0
        self.screen_rect = self.screen.get_rect()

    @staticmethod
    def play_bg_sound_thread(mp3):
        # 播放背景音乐
        print("播放背景音乐！")
        my_music = pygame.mixer.Sound(mp3)  # 加载音频文件
        my_music.play(-1)  # 循环播放

    @staticmethod
    def play_music_thread(mp3):
        # 播放其他音乐
        bj_mp3 = mp3
        print("播放爆炸音乐！")
        pygame.mixer.music.load(bj_mp3)
        pygame.mixer.music.play()

    def __create_sprites(self):

        # 创建背景精灵和精灵组，调用plane_sprites的Background()类
        bg1 = Background()
        bg2 = Background(True)
        self.back_ground = pygame.sprite.Group(bg1, bg2)

        # 创建敌机的精灵组
        self.enemy_group = pygame.sprite.Group()

        # 创建敌机炸毁的精灵组
        self.enemy_collide_group = pygame.sprite.Group()

        # 创建英雄的精灵和精灵组
        self.hero = Hero()
        self.hero_group = pygame.sprite.Group(self.hero)

        # 创建英雄坠毁的精灵组
        self.hero_collide_group = pygame.sprite.Group()
        self.enemy = Enemy()

    def start_game(self):
        print("游戏开始...")
        while True:
            # 1.设置刷新帧率
            self.clock.tick(FRAME_PER_SEC)
            # 2.事件监听
            self.__event_handler()
            # 3.碰撞检测
            self.__check_collide()
            # 4.更新/绘制精灵组
            self.__update_sprites()
            # 显示统计数字文本
            self.display_font()
            # 5.更新刷新显示
            pygame.display.update()

    def display_font(self):
        # ================== 显示字体 ===========================
        # 1
        font_image1 = self.my_font.render("歼灭 {:3d} 架小飞机".format(self.plane_small), True, (255, 125, 125))
        font_image_rect = font_image1.get_rect()
        # 让图像文本居中
        font_image_rect.x = self.screen_rect.width - 270
        font_image_rect.y = self.screen_rect.height - 830
        self.screen.blit(font_image1, font_image_rect)
        # 2
        font_image2 = self.my_font.render("歼灭 {:3d} 架中飞机".format(self.plane_mid), True, (125, 255, 125))
        font_image_rect = font_image2.get_rect()
        # 让图像文本居中
        font_image_rect.x = self.screen_rect.width - 270
        font_image_rect.y = self.screen_rect.height - 770
        self.screen.blit(font_image2, font_image_rect)
        # 3
        font_image3 = self.my_font.render("歼灭 {:3d} 架大飞机".format(self.plane_big), True, (125, 125, 255))
        font_image_rect = font_image3.get_rect()
        # 让图像文本居中
        font_image_rect.x = self.screen_rect.width - 270
        font_image_rect.y = self.screen_rect.height - 710
        self.screen.blit(font_image3, font_image_rect)
        # 4
        font_image4 = self.my_font.render("自己死亡  {:3d}  次".format(self.self_die), True, (255, 0, 0))
        font_image_rect = font_image4.get_rect()
        # 让图像文本居中
        font_image_rect.x = self.screen_rect.width - 270
        font_image_rect.y = self.screen_rect.height - 650
        self.screen.blit(font_image4, font_image_rect)

    def __event_handler(self):
        # 获取事件
        for event in pygame.event.get():
            # 使用键盘提供的方法获取键盘按键
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_ESCAPE]:
                PlaneGame.__game_over()
            # 判断元组中对应的按键索引值，调节英雄飞机左右位置
            if keys_pressed[pygame.K_RIGHT]:
                self.hero.speed_x = 10
            elif keys_pressed[pygame.K_LEFT]:
                self.hero.speed_x = -10
            else:
                self.hero.speed_x = 0
            # ======================，调节英雄飞机上下位置
            if keys_pressed[pygame.K_DOWN]:
                self.hero.speed_y = 5
            elif keys_pressed[pygame.K_UP]:
                self.hero.speed_y = -5
            else:
                self.hero.speed_y = 0

            # + - 调节敌人飞机创建速度
            global CREATE_ENEMY_TIME
            if keys_pressed[pygame.K_EQUALS]:
                if CREATE_ENEMY_TIME > 300:
                    CREATE_ENEMY_TIME -= 200
                else:
                    CREATE_ENEMY_TIME = 300
                pygame.time.set_timer(CREATE_ENEMY_EVENT, CREATE_ENEMY_TIME)
            elif keys_pressed[pygame.K_MINUS]:
                if CREATE_ENEMY_TIME < 2000:
                    CREATE_ENEMY_TIME += 200
                else:
                    CREATE_ENEMY_TIME = 2000
                pygame.time.set_timer(CREATE_ENEMY_EVENT, CREATE_ENEMY_TIME)

            # 大招1，英雄发射螺旋导弹
            if keys_pressed[pygame.K_z]:
                self.hero.fire_missile()
            # 大招2，底部导弹清屏
            if keys_pressed[pygame.K_c]:
                self.hero.fire_clear_screen()
            # 大招3，四周导弹清屏
            if keys_pressed[pygame.K_x]:
                self.hero.fire_circle()
            # 大招4，四周导弹清屏
            if keys_pressed[pygame.K_SPACE]:
                self.hero.fire_bomb()

            # 判断是否点×退出游戏
            if event.type == pygame.QUIT:
                PlaneGame.__game_over()
            elif event.type == CREATE_ENEMY_EVENT:
                # print("敌机出场...")
                # 1.创建敌机精灵
                self.enemy = Enemy()
                # 2.将敌机精灵添加到精灵组
                self.enemy_group.add(self.enemy)
            elif event.type == HERO_FIRE_EVENT:
                # 换子弹
                if keys_pressed[pygame.K_LCTRL]:
                    self.hero.fire1()
                elif keys_pressed[pygame.K_LALT]:
                    self.hero.fire2()
                else:
                    self.hero.fire0()
            elif event.type == ENEMY_FIRE_EVENT:
                self.enemy.fire()

    def __check_collide(self):
        # 1.子弹摧毁敌机，子弹和敌机都销毁
        bullet_enemy_collide_thread = threading.Thread(target=self.display_bullet_enemy_colliding)
        bullet_enemy_collide_thread.start()
        # 2.导弹摧毁敌机，导弹和敌机都销毁
        missile_enemy_collide_thread = threading.Thread(target=self.display_missile_enemy_colliding)
        missile_enemy_collide_thread.start()
        # 3.敌机摧毁英雄
        hero_collide_thread = threading.Thread(target=self.display_hero_colliding)
        hero_collide_thread.start()
        # 4.敌机子弹摧毁英雄
        enemy_bullet_collide_thread = threading.Thread(target=self.display_hero_enemy_bullet_colliding)
        enemy_bullet_collide_thread.start()

    def __update_sprites(self):
        # 背景精灵组更新
        self.back_ground.update()
        self.back_ground.draw(self.screen)
        # 敌机精灵组更新
        self.enemy_group.update()
        self.enemy_group.draw(self.screen)
        # 敌机炸毁精灵组更新
        self.enemy_collide_group.update()
        self.enemy_collide_group.draw(self.screen)
        # 英雄精灵组更新
        self.hero_group.update()
        self.hero_group.draw(self.screen)
        # 英雄被炸精灵组更新
        self.hero_collide_group.update()
        self.hero_collide_group.draw(self.screen)
        # 英雄子弹精灵组更新
        self.hero.bullets.update()
        self.hero.bullets.draw(self.screen)
        # 英雄导弹精灵组更新
        self.hero.missiles.update()
        self.hero.missiles.draw(self.screen)
        # 敌人子弹精灵组更新
        bullets_enemy.update()
        bullets_enemy.draw(self.screen)
        # 英雄炸弹精灵组更新
        bomb_hero.update()
        bomb_hero.draw(self.screen)

    @staticmethod
    def __game_over():
        print("游戏结束...")
        pygame.mixer.music.stop()
        pygame.quit()
        exit()

    def __game_restart(self):
        pygame.init()
        # 3.调用私有方法，精灵和精灵组的创建
        # self.__create_sprites()
        pygame.time.set_timer(HERO_FIRE_EVENT, 200)
        # 创建英雄的精灵和精灵组
        self.hero = Hero()
        self.hero_group = pygame.sprite.Group(self.hero)

    # 碰撞被调函数
    def enemy_collide_images(self, i, enemy):
        # for i in s2:
        enemy1 = enemy + "_down1.png"
        enemy2 = enemy + "_down2.png"
        enemy3 = enemy + "_down3.png"
        enemy4 = enemy + "_down4.png"

        enemy_collide1 = EnemyCollide(os.path.join("./images", enemy1))
        enemy_collide1.rect = i.rect
        self.enemy_collide_group.add(enemy_collide1)
        time.sleep(0.15)
        self.enemy_collide_group.remove(enemy_collide1)

        enemy_collide2 = EnemyCollide(os.path.join("./images", enemy2))
        enemy_collide2.rect = i.rect
        self.enemy_collide_group.add(enemy_collide2)
        time.sleep(0.15)
        self.enemy_collide_group.remove(enemy_collide2)

        enemy_collide3 = EnemyCollide(os.path.join("./images", enemy3))
        enemy_collide3.rect = i.rect
        self.enemy_collide_group.add(enemy_collide3)
        time.sleep(0.15)
        self.enemy_collide_group.remove(enemy_collide3)

        enemy_collide4 = EnemyCollide(os.path.join("./images", enemy4))
        enemy_collide4.rect = i.rect
        self.enemy_collide_group.add(enemy_collide4)
        time.sleep(0.15)
        self.enemy_collide_group.remove(enemy_collide4)

        if enemy == "enemy3":
            enemy5 = enemy + "_down5.png"
            enemy6 = enemy + "_down6.png"

            enemy_collide5 = EnemyCollide(os.path.join("./images", enemy5))
            enemy_collide5.rect = i.rect
            self.enemy_collide_group.add(enemy_collide5)
            time.sleep(0.2)
            self.enemy_collide_group.remove(enemy_collide5)

            enemy_collide6 = EnemyCollide(os.path.join("./images", enemy6))
            enemy_collide6.rect = i.rect
            self.enemy_collide_group.add(enemy_collide6)
            time.sleep(0.25)
            self.enemy_collide_group.remove(enemy_collide6)

    # 子弹与敌人飞机碰撞
    def display_bullet_enemy_colliding(self):
        kw_sprite = pygame.sprite.groupcollide(self.hero.bullets, self.enemy_group, True, True)
        # kw_sprite: <class 'dict'> {<Bullet Sprite(in 0 groups)>: [<Enemy Sprite(in 0 groups)>]}
        print("kw_sprite:", type(kw_sprite), kw_sprite)
        # enemy_plane bomb
        for s2 in kw_sprite.values():
            # s2: <class 'list'> [<Enemy Sprite(in 0 groups)>]
            print("s2:", type(s2), s2)
            # 播放音乐
            PlaneGame.play_music_thread(r"./music/enemy_broken.mp3")

            # for i in s2:
            i = s2.pop()  # s2: <class 'list'> [<Enemy Sprite(in 0 groups)>] list的第0个位置
            if i.number == 0 or i.number == 1:
                self.enemy_collide_images(i, "enemy1")
                self.plane_small += 1
            elif i.number == 2 or i.number == 3:
                self.enemy_collide_images(i, "enemy2")
                self.plane_mid += 1
            elif i.number == 4:
                self.enemy_collide_images(i, "enemy3")
                self.plane_big += 1
            else:
                print("i.number 没有匹配")

    # 导弹与敌人飞机碰撞
    def display_missile_enemy_colliding(self):
        # 共用函数
        def func(s2):
            # 播放音乐
            PlaneGame.play_music_thread(r"./music/enemy_broken.mp3")

            for i in s2:
                if i.number == 0 or i.number == 1:
                    collide_thread = threading.Thread(target=self.enemy_collide_images, args=(i, "enemy1"))
                    collide_thread.start()
                    self.plane_small += 1
                elif i.number == 2 or i.number == 3:
                    collide_thread = threading.Thread(target=self.enemy_collide_images, args=(i, "enemy2"))
                    collide_thread.start()
                    self.plane_mid += 1
                elif i.number == 4:
                    collide_thread = threading.Thread(target=self.enemy_collide_images, args=(i, "enemy3"))
                    collide_thread.start()
                    self.plane_big += 1
                else:
                    print("i.number 没有匹配")
        # ================ 英雄导弹与敌人飞机碰撞检测==============
        kw_sprite = pygame.sprite.groupcollide(self.hero.missiles, self.enemy_group, False, True)
        for s2 in kw_sprite.values():
            func(s2)
        # ================ bomb_hero 英雄炸弹组与敌人飞机碰撞检测==============
        kw_sprite = pygame.sprite.groupcollide(bomb_hero, self.enemy_group, False, True)
        for s2 in kw_sprite.values():
            func(s2)

    # 英雄与敌人飞机碰撞
    def display_hero_colliding(self):
        kw_sprite = pygame.sprite.groupcollide(self.hero_group, self.enemy_group, True, True)

        for s1 in kw_sprite.values():
            # 播放音乐
            PlaneGame.play_music_thread(r"./music/hero_die.mp3")

            for i in s1:
                self.self_die += 1
                self.hero.kill()
                pygame.time.set_timer(HERO_FIRE_EVENT, 0)

                if i.number == 0 or i.number == 1:
                    collide_thread = threading.Thread(target=self.enemy_collide_images, args=(i, "enemy1"))
                    collide_thread.start()
                    self.plane_small += 1
                elif i.number == 2 or i.number == 3:
                    collide_thread = threading.Thread(target=self.enemy_collide_images, args=(i, "enemy2"))
                    collide_thread.start()
                    self.plane_mid += 1
                elif i.number == 4:
                    collide_thread = threading.Thread(target=self.enemy_collide_images, args=(i, "enemy3"))
                    collide_thread.start()
                    self.plane_big += 1
                else:
                    print("i.number 没有匹配")

                # ====================================
                hero_collide1 = HeroCollide("./images/me_destroy_1.png")
                hero_collide1.rect = self.hero.rect
                self.hero_collide_group.add(hero_collide1)
                time.sleep(0.2)
                self.hero_collide_group.remove(hero_collide1)
                # ==============================================
                hero_collide2 = HeroCollide("./images/me_destroy_2.png")
                hero_collide2.rect = self.hero.rect
                self.hero_collide_group.add(hero_collide2)
                time.sleep(0.2)
                self.hero_collide_group.remove(hero_collide2)
                # ==================================================
                hero_collide3 = HeroCollide("./images/me_destroy_3.png")
                hero_collide3.rect = self.hero.rect
                self.hero_collide_group.add(hero_collide3)
                time.sleep(0.2)
                self.hero_collide_group.remove(hero_collide3)
                # ===================================================
                hero_collide4 = HeroCollide("./images/me_destroy_4.png")
                hero_collide4.rect = self.hero.rect
                self.hero_collide_group.add(hero_collide4)
                time.sleep(0.2)
                self.hero_collide_group.remove(hero_collide4)
                # =====================================================
                time.sleep(0.5)
                self.__game_restart()

    # 英雄与敌人飞机子弹碰撞
    def display_hero_enemy_bullet_colliding(self):
        kw_sprite = pygame.sprite.groupcollide(self.hero_group, bullets_enemy, True, True)

        if len(kw_sprite.values()) > 0:
            # 播放音乐
            PlaneGame.play_music_thread(r"./music/hero_die.mp3")

            self.self_die += 1
            self.hero.kill()
            pygame.time.set_timer(HERO_FIRE_EVENT, 0)
            # ====================================
            hero_collide1 = HeroCollide("./images/me_destroy_1.png")
            hero_collide1.rect = self.hero.rect
            self.hero_collide_group.add(hero_collide1)
            time.sleep(0.2)
            self.hero_collide_group.remove(hero_collide1)
            # ==============================================
            hero_collide2 = HeroCollide("./images/me_destroy_2.png")
            hero_collide2.rect = self.hero.rect
            self.hero_collide_group.add(hero_collide2)
            time.sleep(0.2)
            self.hero_collide_group.remove(hero_collide2)
            # ==================================================
            hero_collide3 = HeroCollide("./images/me_destroy_3.png")
            hero_collide3.rect = self.hero.rect
            self.hero_collide_group.add(hero_collide3)
            time.sleep(0.2)
            self.hero_collide_group.remove(hero_collide3)
            # ===================================================
            hero_collide4 = HeroCollide("./images/me_destroy_4.png")
            hero_collide4.rect = self.hero.rect
            self.hero_collide_group.add(hero_collide4)
            time.sleep(0.2)
            self.hero_collide_group.remove(hero_collide4)
            # =====================================================
            time.sleep(0.5)
            self.__game_restart()


if __name__ == '__main__':
    # 创建游戏对象
    game = PlaneGame()
    # 启动游戏
    game.start_game()
