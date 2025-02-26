class Quadtree:
    def __init__(self, x, y, width, height, level=0, max_objects=4, max_levels=5):
        self.bounds = (x, y, width, height)
        self.level = level
        self.max_objects = max_objects
        self.max_levels = max_levels
        self.objects = []
        self.nodes = []

    def resize(self, width, height):
        self.bounds = (0, 0, width, height)
        self.objects.clear()
        self.nodes.clear()

    def split(self):
        x, y, w, h = self.bounds
        sub_w, sub_h = w / 2, h / 2

        self.nodes = [
            Quadtree(x + sub_w, y, sub_w, sub_h, self.level + 1),
            Quadtree(x, y, sub_w, sub_h, self.level + 1),
            Quadtree(x, y + sub_h, sub_w, sub_h, self.level + 1),
            Quadtree(x + sub_w, y + sub_h, sub_w, sub_h, self.level + 1),
        ]

    def get_index(self, obj):
        x, y, w, h = self.bounds
        obj_x, obj_y, obj_w, obj_h = obj.bounds

        top_half = obj_y < y + h / 2 and obj_y + obj_h < y + h / 2
        bottom_half = obj_y > y + h / 2
        left_half = obj_x < x + w / 2 and obj_x + obj_w < x + w / 2
        right_half = obj_x > x + w / 2

        if top_half and right_half:
            return 0  # Top-right
        elif top_half and left_half:
            return 1  # Top-left
        elif bottom_half and left_half:
            return 2  # Bottom-left
        elif bottom_half and right_half:
            return 3  # Bottom-right
        return -1  # Object overlaps multiple quadrants

    def insert(self, obj):
        if self.nodes:
            index = self.get_index(obj)
            if index != -1:
                self.nodes[index].insert(obj)
                return

        self.objects.append(obj)

        if len(self.objects) > self.max_objects and self.level < self.max_levels:
            if not self.nodes:
                self.split()

            i = 0
            while i < len(self.objects):
                index = self.get_index(self.objects[i])
                if index != -1:
                    self.nodes[index].insert(self.objects.pop(i))
                else:
                    i += 1

    def retrieve(self, obj):
        potential_collisions = self.objects[:]

        if self.nodes:
            index = self.get_index(obj)
            if index != -1:
                potential_collisions.extend(self.nodes[index].retrieve(obj))
            else:
                for node in self.nodes:
                    potential_collisions.extend(node.retrieve(obj))

        return potential_collisions

    def clear(self):
        self.objects.clear()
        for node in self.nodes:
            node.clear()
        self.nodes.clear()