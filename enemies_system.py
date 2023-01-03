from system import System
from constants import *
import random
import math

class EnemiesSystem(System):
    class Node:
        def __init__(self, parent=None, position=None):
            self.parent = parent
            self.position = position

            # g = distance from start
            self.g = 0

            # h = distance to end
            self.h = 0

            # f = g + h
            self.f = 0

        def calc_g(self, parent):
            self.g = parent.g + 1

        def calc_h(self, end):
            self.h = abs(self.position[0] - end.position[0]) + abs(self.position[1] - end.position[1])

        def calc_f(self):
            self.f = self.g + self.h

        def __eq__(self, other):
            return self.position == other.position

        def __repr__(self) :
            return f"Node({self.position})"

    def a_star(self, map, start, end):
        map_width = len(map[0])
        map_height = len(map)

        open_list = []
        closed_list = []

        start_node = EnemiesSystem.Node(None, start)
        end_node = EnemiesSystem.Node(None, end)

        # start node on open list
        open_list.append(start_node)

        while len(open_list) > 0:

            # sort by least f
            open_list.sort(key=lambda x: x.f)

            # remove first element from open list
            current_node = open_list.pop(0)

            closed_list.append(current_node)

            # if current node is end node, return path
            if current_node == end_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]

            children = [EnemiesSystem.Node(current_node,(current_node.position[0] + p[0], current_node.position[1] + p[1])) for p in [(0, -1), (0, 1), (-1, 0), (1, 0)]]
            

            for child in children:
                # check child in range
                if child.position[0] > map_width or child.position[0] < 0 or child.position[1] > map_height or child.position[1] < 0:
                    continue

                # if child is on closed list, skip
                if child in closed_list:
                    continue
                
                # if child is not walkable, skip
                if map[child.position[1]][child.position[0]] >= WALL_FULL:
                    continue

                # calculate f, g, h
                child.calc_g(current_node)
                child.calc_h(end_node)
                child.calc_f()

                # if child is already on open list
                if child in open_list:
                    # if child.g is greater than current node g, skip
                    if child.g > current_node.g:
                        continue
                
                # add child to open list
                open_list.append(child)


    def find_path(self, paths, point):
        selected_paths = []

        for path in paths:
            if point == path[0]:
                selected_paths.append(path)
        
        if len(selected_paths) == 0:
            return None

        # choose random path
        return random.choice(selected_paths).copy()

    # todo refactor: this is a copy of fov in visibility system
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

    def update(self):
        # verify that state si dungeon
        state = System.get_entity_component('state')['value']
        if state != 'dungeon':
            return

        # get the map
        dungeon = System.get_entity_component('dungeon')

        # get player entity
        player = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'player'][0]

        # get enemies entities and are in the same player floor
        enemies = [enemy for enemy in System.filter_entities(['role', 'position']) if enemy.get('role')['value'] == 'enemy' and enemy.get('position')['floor'] == player.get('position')['floor']]

        # get map on player floor
        map = dungeon['map'][player.get('position')['floor']]

        # get blood on player floor
        blood = dungeon['blood'][player.get('position')['floor']]

        # get rooms center on player floor
        rooms_center = dungeon['rooms_center'][player.get('position')['floor']]

        # get paths on player floor
        paths = dungeon['paths'][player.get('position')['floor']]

        player_x = player.get('position')['x']
        player_y = player.get('position')['y']

        noise_event = System.get_event('noise_event')
        for enemy in enemies:
            enemy_x = enemy.get('position')['x']
            enemy_y = enemy.get('position')['y']
            
            hear_noise = False
            if noise_event is not None:
                noise_x = noise_event["value"]['x']
                noise_y = noise_event["value"]['y']
                distance = self.diag_dist(enemy_x, enemy_y, noise_x, noise_y)
                if distance <= NOISE_RADIUS:
                    # find path to player
                    path_to_player = self.a_star(map, (enemy_x, enemy_y), (player_x, player_y))
                    enemy.get('direction')['value'] = path_to_player[1:]
                    hear_noise = True

            if not hear_noise and self.diag_dist(enemy.get('position')['x'], enemy.get('position')['y'], player.get('position')['x'], player.get('position')['y']) <= enemy.get('race')['fov']:
                radius = enemy.get('race')['fov']
                fov_size = radius * 2 + 1

                # get portion of the map that is in fov
                map_fov = [[0 for x in range(fov_size)] for y in range(fov_size)]
                for y in range(len(map_fov)):
                    for x in range(len(map_fov[y])):
                        new_x = x + enemy_x - radius
                        new_y = y + enemy_y - radius

                    # check if new_x and new_y are into the map
                    if new_x >= 0 and new_y >= 0 and new_x < len(map[0]) and new_y < len(map):
                        map_fov[y][x] = map[new_y][new_x]

                
                # verify if player is in fov
                glare = self.fov(map_fov, radius, radius, radius)

                # find in map_fov the player position and verify if is in glare
                if glare[player_y - enemy_y + radius][player_x - enemy_x + radius]:
                    # find path to player
                    path_to_player = self.a_star(map, (enemy_x, enemy_y), (player_x, player_y))
                    enemy.get('direction')['value'] = path_to_player[1:]
            
            if len(enemy.get('direction')["value"]) == 0:
                # find nearest path
                path = self.find_path(paths, (enemy.get('position')['x'], enemy.get('position')['y']))
      
                if path is None:
                    # find romm nearest
                    nearest_room_center = None
                    distance_room = 99999

                    for room_center in rooms_center:
                        distance = abs(enemy.get('position')['x'] - room_center[0]) + abs(enemy.get('position')['y'] - room_center[1])
                        if distance < distance_room:
                            distance_room = distance
                            nearest_room_center = room_center
                    
                    path = self.a_star(map, (enemy.get('position')['x'], enemy.get('position')['y']), (nearest_room_center[0], nearest_room_center[1]))

                enemy.get('direction')["value"] = path

            if len(enemy.get('direction')["value"]) > 0:
                direction = enemy.get('direction')["value"][0]
                if direction[0] == player.get('position')['x'] and direction[1] == player.get('position')['y']:
                    blood[direction[1]][direction[0]] = True
                    player.get('status')['hp'] -= 20
                    System.push_event({
                        'type': 'damage_event',
                        'value': 20
                    })
                    if player.get('status')['hp'] <= 0:
                        System.push_event({
                            "type": "state_change",
                            "value": "gameover"
                        })
                else:
                    # stun enemies
                    bonk = 0
                    if enemy.has('bonk'):
                        enemy.get('bonk')['value'] -= 1
                        bonk = enemy.get('bonk')['value']
                        if bonk <= 0:
                            enemy.remove('bonk')
                    if bonk <= 0:
                        enemy.get('direction')["value"].pop(0)
                        enemy.get('position')['x'] = direction[0]
                        enemy.get('position')['y'] = direction[1]