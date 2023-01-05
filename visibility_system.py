from system import System
import math
from constants import *

class VisibilitySystem(System):
    
    def diag_dist(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        return max(abs(dx), abs(dy))

    def lerp(self, a, b, t):
        return a + (b - a) * t

    def fov(self, map, x, y, dist):
        glare = [[False for x in range(len(map[0]))] for y in range(len(map))]

        for i in range(360):
            deg = i * (math.pi / 180)
            nx = round(math.cos(deg) * dist) + x
            ny = round(math.sin(deg) * dist) + y

            d = self.diag_dist(x, y, nx, ny)
                        
            for j in range(d):
                tx = self.lerp(x, nx, j / d)
                ty = self.lerp(y, ny, j / d)

                if tx < 0 or ty < 0 or tx >= len(map[0]) or ty >= len(map):
                    continue
                
                glare[int(ty)][int(tx)] = True

                if map[int(ty)][int(tx)] >= WALL_FULL:
                    glare[int(ty)][int(tx)] = True
                    break

                glare[int(ty)][int(tx)] = True

        return glare

    def shadow_cast(self, player_entity, dungeon_entity):
        # get map from dungeon
        map_value = dungeon_entity.get('dungeon')['map'][player_entity.get('position')['floor']]
        radius = round(player_entity.get('status')['sanity']/10) + 2 

        map_visible = dungeon_entity.get('visibility')['visible']
        map_visited = dungeon_entity.get('dungeon')['visited'][player_entity.get('position')['floor']]

        # get the player position
        player_x = player_entity.get('position')['x']
        player_y = player_entity.get('position')['y']

        # fov size
        fov_size = radius * 2 + 1

        map_fov = [[0 for x in range(fov_size)] for y in range(fov_size)]

        # fill map fov
        for y in range(len(map_fov)):
            for x in range(len(map_fov[y])):
                new_x = x + player_x - radius
                new_y = y + player_y - radius

                # check if new_x and new_y are into the map
                if new_x >= 0 and new_y >= 0 and new_x < len(map_value[0]) and new_y < len(map_value):
                    map_fov[y][x] = map_value[new_y][new_x]

        fov = self.fov(map_fov, radius, radius, radius)

        # set visibility to false on all map
        for y in range(len(map_visible)):
            for x in range(len(map_visible[y])):
                map_visible[y][x] = False

        # set visibility to true on fov and visited
        for y in range(len(fov)):
            for x in range(len(fov[y])):
                new_x = x + player_x - radius
                new_y = y + player_y - radius

                if new_x >= 0 and new_y >= 0 and new_x < len(map_value[0]) and new_y < len(map_value):
                    map_visible[new_y][new_x] = fov[y][x]
                    if fov[y][x] == True:
                        map_visited[new_y][new_x] = fov[y][x]

    def update(self):
        # get state and verify that is a dungeon
        state = System.get_entity_component('state')['value']
        if state != 'dungeon':
            return

        # get the map
        dungeon = [e for e in System.filter_entities(['dungeon'])][0]
        
        # get the player
        player = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'player'][0]

        self.shadow_cast(player, dungeon)