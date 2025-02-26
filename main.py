from statistics import variance
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.storage.jsonstore import JsonStore
from functools import partial
import keyboard
import random
import math
import time
import widgetsAndScatters as wAS
from quadtree import Quadtree

db = JsonStore('main.json')
FPS = 120
gravity = 9.81

def color_creator():
    return random.random(), random.random(), random.random()

class Movements:
    def __init__(self):
        self.movement_buffer = {'left': False, 'right': False}

    def onKeyboard(self, *args):
        if args[1] in [100, 275]:
            self.movement_buffer['right'] = True
        elif args[1] in [97, 276]:
            self.movement_buffer['left'] = True

    def onKeyboardUp(self, *args):
        if args[1] in [100, 275]:  # 'd' or right arrow
            self.movement_buffer['right'] = False
        elif args[1] in [97, 276]:  # 'a' or left arrow
            self.movement_buffer['left'] = False

    def update(self, dt):
        if self.movement_buffer['right']:
            self.ids.cannon.pos[0] += dp(2)
        if self.movement_buffer['left']:
            self.ids.cannon.pos[0] -= dp(2)

class MenuScreen(Screen, Movements):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.cursorPosition, 1 / FPS)
        Clock.schedule_interval(self.update, 1 / FPS)
        Window.bind(on_key_down=self.onKeyboard)
        Window.bind(on_key_up=self.onKeyboardUp)

    def on_kv_post(self, base_widget):
        self.update_coin_display()

    def update_coin_display(self):
        app = MDApp.get_running_app()
        self.ids.coinValue.text = str(app.coins)

    def on_enter(self, *args):
        Window.show_cursor = False

    def on_leave(self, *args):
        Window.show_cursor = True

    def cursorPosition(self, dt):
        self.ids.cursor.pos = Window.mouse_pos[0] - self.ids.cursor.width/2, \
                              Window.mouse_pos[1] - self.ids.cursor.height/2

class GameScreen(Screen, Movements):
    laserImageVar = StringProperty('lasers/laser_red_off.png')
    ammosShot = {}
    obstacles = []


    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        Window.bind(on_key_down=self.onKeyboard)
        Window.bind(on_key_up=self.onKeyboardUp)
        self.quadtree = Quadtree(0, 0, Window.width, Window.height)
        self.activeAmmo = None
        self.bulletCounter = 0
        self.obstacleCounter = 0
        self.debug_mode = False  # Debug mode for visualizing quadtree
        self.frame_count = 0
        Clock.schedule_interval(self.update, 1 / FPS)

    def on_enter(self):
        app = MDApp.get_running_app()
        self.ids.coinValue.text = str(app.coins)

    def on_leave(self):
        self.ammosShot.clear()
        self.bulletCounter = 0

    def laserImage(self):
        if self.laserImageVar == 'lasers/laser_red_off.png':
            self.laserImageVar = 'lasers/laser_red_on.png'
        else:
            self.laserImageVar = 'lasers/laser_red_off.png'

    def activeRadioButton(self, sel):
        self.activeAmmo = sel

    def remove_obstacle(self, obstacle):
        self.obstacles.remove(obstacle)
        self.remove_widget(obstacle)

    def onKeyboard(self, *args):
        if args[1] == 103:  # 'g'
            obstacle = wAS.Obstacle(self.obstacleCounter,
                                    ((Window.size[0] + Window.size[1]) / 2 / 20,
                                    (Window.size[0] + Window.size[1]) / 2 / 20),
                                    "Rock")
            self.add_widget(obstacle)
            self.obstacles.append(obstacle)
            self.obstacleCounter += 1
        elif args[1] == 116:  # 't'
            match self.activeAmmo:
                case 1:
                    bomb = wAS.Bomb(self.bulletCounter,
                                    (self.ids.cannon.pos[0] + self.ids.cannon.width, self.ids.cannon.pos[1] + self.ids.cannon.height / 3),
                                    (Window.size[0] / 50, Window.size[0] / 50),
                                    self.ids.angle.value,
                                    self.ids.power.value,
                                    'weapons/grenade.png',
                                    self)
                    self.add_widget(bomb)
                case 2:
                    laser = wAS.Laser(self.bulletCounter,
                                    (self.ids.cannon.pos[0] + self.ids.cannon.width, self.ids.cannon.pos[1] + self.ids.cannon.height / 3),
                                    (Window.size[0] / 50, Window.size[0] / 200),
                                    self.ids.angle.value,
                                    self.ids.power.value,
                                    'lasers/blue_laser.png',
                                    self)
                    self.add_widget(laser)
                case 3:
                    bullet = wAS.Bullet(self.bulletCounter,
                                        (self.ids.cannon.pos[0] + self.ids.cannon.width,  self.ids.cannon.pos[1] + (self.ids.cannon.height / 2) - dp(9)),
                                        (Window.size[0] / 100, Window.size[0] / 100),
                                        self.ids.angle.value,
                                        self.ids.power.value,
                                        'cannons/shell.png',
                                        self)
                    self.add_widget(bullet)
                case _:
                    pass
            self.bulletCounter += 1

    def update_coin_display(self):
        app = MDApp.get_running_app()
        self.ids.coinValue.text = str(app.coins)

    def update(self, dt):
        self.frame_count += 1
        if self.frame_count % 5 == 0:  # Update quadtree every 5 frames
            self.quadtree.clear()
            for obstacle in self.obstacles:
                self.quadtree.insert(obstacle)

        for id, projectile in self.ammosShot.items():
            if projectile.has_moved_significantly():
                potential_collisions = self.quadtree.retrieve(projectile)
                for obj in potential_collisions:
                    if projectile.collides_with(obj):
                        projectile.handle_collision(obj)

        if self.debug_mode:
            self.draw_quadtree(self.quadtree)

    def draw_quadtree(self, quadtree):
        x, y, w, h = quadtree.bounds
        with self.canvas:
            Color(1, 0, 0, 0.5)  # Red color with 50% opacity
            Line(rectangle=(x, y, w, h), width=1)
        for node in quadtree.nodes:
            self.draw_quadtree(node)

class SettingScreen(Screen):
    pass

class LevelScreen(Screen):
    pass

class Manager(ScreenManager):
    pass

class MainApp(MDApp):
    coins = 0

    def build(self):
        self.title = "Cannons"
        self.icon = "cannons/right-1.png"
        Window.bind(size=self.on_resize)

    def on_start(self):
        if db.exists('coins'):
            self.coins = db.get('coins')['value']
        else:
            self.coins = 0  # Default to 0 if not found
            db.put('coins', value=self.coins)
        self.root.get_screen('menu').update_coin_display()

    def on_stop(self):
        self.save_coins()

    def save_coins(self):
        db.put('coins', value=self.coins)

    def on_resize(self, *args):
        width, height = Window.size
        expected_height = int(width * (3 / 4))
        expected_width = int(height * (4 / 3))

        if expected_height > height:
            new_width = expected_width
            new_height = height
        else:
            new_width = width
            new_height = expected_height

        Window.size = (new_width, new_height)

if __name__ == "__main__":
    MainApp().run()