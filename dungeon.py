import random
from constants import *

class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (int(center_x), int(center_y))

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def is_into(self, x, y):
        return (x >= self.x1 and x <= self.x2 and y >= self.y1 and y <= self.y2)

class Floor:
    def __init__(self, width, height, max_rooms, max_room_size, min_room_size, floor_number):
        self.width = width
        self.height = height
        self.rooms = []
        self.corridors = []
        self.max_rooms = max_rooms
        self.max_room_size = max_room_size
        self.min_room_size = min_room_size
        self.floor_number = floor_number
        self.map = [[WALL_FULL for x in range(width)] for y in range(height)]
        self.visited = [[False for x in range(width)] for y in range(height)]
        self.blood = [[False for x in range(width)] for y in range(height)]
        self.stair_up = None
        self.stair_down = None
        self.enemies = []
        self.crates = []
        self.paths = []
        self.generate_map()
        
        # add to self paths also reverse paths
        for i in range(len(self.paths)):
            self.paths.append(self.paths[i][::-1])

        self.create_enemies()
        self.create_crates()

    def create_crates(self):
        # select random room and put just one enemy
        for room in self.rooms:
            # select a random corner of room    
            x = room.x1 + 2
            y = room.y1 + 2
            if random.randint(0, 100) > 50:
                x = room.x2 - 2
            if random.randint(0, 100) > 50:
                y = room.y2 - 2

            self.crates.append((x, y))
            # set crate closed on the map
            self.map[y][x] = CRATE
   

    def create_enemies(self):
        # select random corner of the room
        for room in self.rooms:
            # if room is not the first or the last
            if self.rooms.index(room) != 0 and self.rooms.index(room) != len(self.rooms) - 1:
                if random.randint(0, 100) > 50:
                    (x, y) = room.center()
                    self.enemies.append((x, y, random.randint(0, 2)))
        
    def get_enemies(self):
        return self.enemies

    def get_rooms_center(self):
        return [room.center() for room in self.rooms]

    def generate_map(self):
        for _ in range(self.max_rooms):
            w = random.randint(self.min_room_size, self.max_room_size)
            h = random.randint(self.min_room_size, self.max_room_size)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            new_room = Rect(x, y, w, h)

            failed = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                self.create_room(new_room)
                self.rooms.append(new_room)

        # copy rooms list
        rooms_copy = self.rooms.copy()

        while len(rooms_copy)>1:
            room_before = rooms_copy.pop(0)
            # create the array of distances from the room_before
            (x1, y1) = room_before.center()
            distances = []
            for room in rooms_copy:
                (x2, y2) = room.center()
                distance = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
                distances.append(distance)

            # find the index of the minimum distance
            min_index = distances.index(min(distances))

            (new_x, new_y) = rooms_copy[min_index].center()
            (prev_x, prev_y) = room_before.center()

            paths = []

            if random.randint(0, 1) == 1:
                path = self.create_h_tunnel(prev_x, new_x, prev_y)
                
                # if the path is not from the prev_x, prev_y
                if path[0] != (prev_x, prev_y):
                    path = path[::-1]
                paths += path

                path = self.create_v_tunnel(prev_y, new_y, new_x)
                
                # if the path not stop on the new_x, new_y
                if path[-1] != (new_x, new_y):
                    path = path[::-1]
                
                paths += path
            else:
                path = self.create_v_tunnel(prev_y, new_y, prev_x)
                if path[0] != (prev_x, prev_y):
                    path = path[::-1]
                paths += path
                
                path = self.create_h_tunnel(prev_x, new_x, new_y)
                if path[-1] != (new_x, new_y):
                    path = path[::-1]
                paths += path

            self.paths.append(paths)
            
        # stairs
        self.stair_up = self.rooms[0].center()
        self.stair_down = self.rooms[-1].center()

    def create_room(self, room):
        # generate ground
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.map[y][x] = GROUND_NORMAL

        # generate horizontal walls
        for x in range(room.x1, room.x2 + 1):
            self.map[room.y1][x] = WALL_HORIZONTAL
            self.map[room.y2][x] = WALL_HORIZONTAL

        # generate vertical walls
        for y in range(room.y1, room.y2 + 1):
            self.map[y][room.x1] = WALL_VERTICAL
            self.map[y][room.x2] = WALL_VERTICAL

        # generate corners
        self.map[room.y1][room.x1] = WALL_CORNER
        self.map[room.y1][room.x2] = WALL_CORNER
        self.map[room.y2][room.x1] = WALL_CORNER
        self.map[room.y2][room.x2] = WALL_CORNER


    def create_h_tunnel(self, x1, x2, y):
        path = []
        for x in range(min(x1, x2), max(x1, x2) + 1):
            path.append((x, y))
            if self.map[y][x] >= WALL_FULL:
                self.map[y][x] = GROUND_NORMAL

                if self.map[y-1][x] >= WALL_FULL:
                    if self.map[y-1][x] == WALL_VERTICAL:
                        self.map[y-1][x] = WALL_CORNER
                    else:
                        self.map[y-1][x] = WALL_HORIZONTAL

                if self.map[y+1][x] >= WALL_FULL:
                    if self.map[y+1][x] == WALL_VERTICAL:
                        self.map[y+1][x] = WALL_CORNER
                    else:
                        self.map[y+1][x] = WALL_HORIZONTAL

        end = [max(x1, x2)+1, min(x1, x2)-1] 
        

        for x in end:
            if self.map[y][x] >= WALL_FULL:
                self.map[y][x] = WALL_VERTICAL
                
                if self.map[y-1][x] >= WALL_FULL:
                    self.map[y-1][x] = WALL_CORNER

                if self.map[y+1][x] >= WALL_FULL:
                        self.map[y+1][x] = WALL_CORNER
        
        return path



    def create_v_tunnel(self, y1, y2, x):
        path = []
        for y in range(min(y1, y2), max(y1, y2) + 1):
            path.append((x, y))
            if self.map[y][x] >= WALL_FULL:
                self.map[y][x] = GROUND_NORMAL
            
                if self.map[y][x-1] >= WALL_FULL:
                    if self.map[y][x-1] == WALL_HORIZONTAL:
                        self.map[y][x-1] = WALL_CORNER
                    else:
                        self.map[y][x-1] = WALL_VERTICAL

                if self.map[y][x+1] >= WALL_FULL:
                    if self.map[y][x+1] == WALL_HORIZONTAL:
                        self.map[y][x+1] = WALL_CORNER
                    else:
                        self.map[y][x+1] = WALL_VERTICAL

        end = [max(y1, y2)+1, min(y1, y2)-1] 
        for y in end:
            if self.map[y][x] >= WALL_FULL:
                self.map[y][x] = WALL_HORIZONTAL

                if self.map[y][x-1] >= WALL_FULL:
                    self.map[y][x-1] = WALL_CORNER

                if self.map[y][x+1] >= WALL_FULL:
                    self.map[y][x+1] = WALL_CORNER
        
        return path

    def get_map(self):
        return self.map

    def get_visited(self):
        return self.visited

    def get_visibility(self):
        return self.visibility
        
    def get_stair_up(self):
        return self.stair_up

    def get_stair_down(self):
        return self.stair_down

    def get_crates(self):
        return self.crates

    def get_paths(self):
        return self.paths

    def get_blood(self):
        return self.blood

class Dungeon:
    def __init__(self, width, height, max_rooms, max_room_size, min_room_size, floors):
        self.floors_num = floors
        self.floors = []
        for floor in range(floors):
            self.floors.append(Floor(width, height, max_rooms, max_room_size, min_room_size, floor))


