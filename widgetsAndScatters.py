from kivy.clock import Clock
from main import *

class GameObject(Widget):
    def __init__(self, x, y, width, height, size, **kwargs):
        super().__init__(**kwargs)
        self.bounds = (x, y, width, height)
        self.pos = (x, y)
        self.size = size

    def collides_with(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

class Obstacle(GameObject):
    def __init__(self, id, size, obstacle_type, **kwargs):
        super().__init__(random.randint(int(Window.width * 1/8), int(Window.width * 4/5)),
                         random.randint(int(Window.width * 1/8), int(Window.width * 4/5)),
                         size[0], size[1], size)
        self.id = id
        self.obstacle_type = obstacle_type
        self.state = "active"
        self.marked_for_removal = False
        with self.canvas:
            Color(rgb=color_creator())
            self.shape = Rectangle(pos=self.pos, size=self.size)

    def handle_collision(self, projectile):
        if self.state == "active":
            if self.obstacle_type == "Rock":
                self.destroy()
            elif self.obstacle_type == "Bulletproof Mirror":
                self.reflect(projectile)

    def destroy(self):
        self.state = "destroyed"
        self.marked_for_removal = True
        Clock.schedule_once(self._remove_widget)

    def _remove_widget(self, dt):
        if self.parent and self.marked_for_removal:
            self.parent.remove_widget(self)

class Ammo(GameObject):
    def __init__(self, ammoType, id, initPos, size, angle, power, weight, imgSource, gameScreen, *args, **kwargs):
        super().__init__(initPos[0], initPos[1], size[0], size[1], size)
        self.image = Image(source=imgSource, size=self.size)
        self.add_widget(self.image)
        self.do_scale = False
        self.do_translation = True
        self.do_rotation = True
        self.ammoType = ammoType
        self.id = id
        self.angle = angle
        self.size_hint = (None, None)
        self.velocity = power * 2
        self.startTime = time.time()
        self.weight = weight
        self.init_vX = self.velocity * math.cos(math.radians(self.angle))
        self.init_vY = self.velocity * math.sin(math.radians(self.angle))
        self.speedCallBack = Clock.schedule_interval(self.speed, 1 / FPS)
        self.vX, self.vY = self.init_vX, self.init_vY
        self.gameScreen = gameScreen

    def on_resize(self, *args):
        self.size = self.size
        self.image.size = self.size

    def on_pos(self, *args):
        if hasattr(self, 'image'):
            self.size = self.size
            self.image.size = self.size

    def remove(self):
        Clock.unschedule(self.speedCallBack)
        if self.id in self.gameScreen.ammosShot:
            del self.gameScreen.ammosShot[self.id]
        if self.parent:
            self.parent.remove_widget(self)

    def speed(self, dt):
        newX = self.vX * dt + self.x
        newY = self.y + 0.5 * (self.init_vY + self.vY) * dt
        self.pos = (newX, newY)
        self.angle = math.radians(self.vY / self.vX)
        self.bounds = (newX, newY, self.width, self.height)
        self.image.pos = self.pos

    def has_moved_significantly(self):
        return True  # Placeholder for actual logic

    def handle_collision(self, obstacle):
        if self.ammoType == "bomb":
            if obstacle.obstacle_type == "Rock":
                print(f"Bomb {self.id} collided with Rock {obstacle.id}")  # Debugging
                obstacle.destroy()
                self.remove()

class Bomb(Ammo):
    def __init__(self, id, initPos, size, angle, power, imgSource, gameScreen, *args):
        super().__init__('bomb', id, initPos, size, angle, power, 40, imgSource, gameScreen)
        GameScreen.ammosShot[self.id] = self