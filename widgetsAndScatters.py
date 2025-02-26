from main import *

class GameObject(Widget):
    def __init__(self, x, y, width, height, size, **kwargs):
        super().__init__(**kwargs)
        self.bounds = (x, y, width, height)
        self.pos = (x, y)
        self.size = size

class Obstacle(GameObject):
    def __init__(self, id, size, **kwargs):
        self.id = id
        width, height = self.size[0], self.size[1]
        super().__init__(random.randint(int(Window.width * 1/8), int(Window.width * 4/5)),
                         random.randint(int(Window.width * 1/8), int(Window.width * 4/5)),
                         width, height, size)
        with self.canvas:
            Color(rgb = color_creator())
            self.shape = Rectangle(pos = self.pos, size = self.size)


class Ammo(GameObject):
    def __init__(self, ammoType, id, initPos, size, angle, power, weight, imgSource, gameScreen, *args, **kwargs):

        super().__init__(initPos[0], initPos[1], self.width, self.height, size)

        self.image = Image(source = imgSource, size = self.size)
        self.add_widget(self.image)
        self.do_scale = False  # Disable scaling transformations
        self.do_translation = True  # Allow translation (moving)
        self.do_rotation = True  # Allow rotation

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

        print(self.init_vX, self.init_vY)

    def on_resize(self, *args):
        # Force the size to stay consistent
        self.size = self.size
        self.image.size = self.size

    def on_pos(self, *args):
        if hasattr(self, 'image'):
            # Ensure that changing position doesn't affect size
            self.size = self.size
            self.image.size = self.size

    def remove(self):
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

    def collisionChecker(self, quadtree, *args):
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