from main import *

class GameObject(Widget):
    def __init__(self, x, y, width, height, **kwargs):
        super().__init__(**kwargs)
        self.bounds = (x, y, width, height)

class Obstacle(GameObject):
    def __init__(self, id, size, **kwargs):
        self.id = id
        self.size = size
        self.pos = (random.randint(int(Window.width * 1/8), int(Window.width * 4/5)),
                    random.randint(int(Window.height * 1/8), int(Window.height * 4/5)))
        x, y = self.pos[0], self.pos[1]
        width, height = self.size[0], self.size[1]
        super().__init__(x, y, width, height)
        with self.canvas:
            Color(rgb = color_creator())
            self.shape = Rectangle(pos = self.pos, size = self.size)


class Ammo(GameObject):
    def __init__(self, ammoType, id, initPos, size, angle, power, weight, imgSource, gameScreen, *args, **kwargs):

        self.size = size
        self.pos = initPos
        super().__init__(self.pos[0], self.pos[1], self.width, self.height)

        self.do_scale = False  # Disable scaling transformations
        self.do_translation = True  # Allow translation (moving)
        self.do_rotation = True  # Allow rotation

        self.image = Image(source = imgSource, size = self.size)
        self.add_widget(self.image)
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
        # Reference to the GameScreen where obstacles are managed
        self.gameScreen = gameScreen
        print(self.init_vX, self.init_vY)
        self.vX, self.vY = self.init_vX, self.init_vY

    def on_size(self, *args):
        # Force the size to stay consistent
        self.size = self.size
        self.image.size = self.size

    def on_pos(self, *args):
        if hasattr(self, 'image'):
            # Ensure that changing position doesn't affect size
            self.size = self.size
            self.image.size = self.size

    def removed(self):
        # Stop the scheduled callbacks
        Clock.unschedule(self.speedCallBack)
        if self.id in self.gameScreen.ammosShot:
            Clock.unschedule(self.gameScreen.ammosShot[self.id])
            del self.gameScreen.ammosShot[self.id]
        # Remove the ammo from the parent widget
        if self.parent:
            self.parent.remove_widget(self)

    def speed(self, dt):
        self.vX = self.init_vX * dt
        self.vY = self.init_vY - gravity * dt
        newX = self.vX * dt + self.x
        newY = self.y + 0.5 * (self.init_vY + self.vY) * dt
        print(self.vX, self.vY, newX, newY)
        self.pos = (newX, newY)
        self.angle = math.radians(self.vY/self.vX)
        self.size = self.size
        self.bounds = (newX, newY, self.width, self.height)

    def obstacleRemoved(self, obstacle):
        self.gameScreen.obstacles.remove(obstacle)  # Remove from the list
        self.gameScreen.remove_widget(obstacle)  # Remove from the screen

    def collisionChecker(self, quadtree, *args):
        # First, check if the projectile is off-screen.
        if (self.pos[0] < 0 or self.pos[0] > Window.size[0] or
                self.pos[1] < 0 or self.pos[1] > Window.size[1]):
            self.removed()
            return
        print(quadtree)
        # Prepare the quadtree: clear it and re-insert obstacles.
        quadtree.clear()  # Optional: clear previous frame's objects
        for obstacle in obstacles:
            quadtree.insert(obstacle)



class Bomb(Ammo):
    def __init__(self, id, initPos, size, angle, power, imgSource, gameScreen, *args):
        super().__init__('bomb', id, initPos, size, angle, power, 40, imgSource, gameScreen)
        GameScreen.ammosShot[self.id] = self

class Laser(Ammo):
    def __init__(self, id, initPos, size, angle, power, imgSource, gameScreen, *args):
        super().__init__('laser', id, initPos, size, angle, power, 2, imgSource, gameScreen)
        GameScreen.ammosShot[self.id] = self
        self.rotation = math.tan(self.vX / self.vY)

class Bullet(Ammo):
    def __init__(self, id, initPos, size, angle, power, imgSource, gameScreen, *args):
        super().__init__('bullet', id, initPos, size, angle, power, 25, imgSource, gameScreen)
        GameScreen.ammosShot[self.id] = self