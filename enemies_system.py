from system import System
from constants import *
import random

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



    def update(self):
        # verify that state si dungeon
        state = self.get_entity_component('state')['value']
        if state != 'dungeon':
            return

        # get the map
        dungeon = self.get_entity_component('dungeon')

        # get player entity
        player = [e for e in self.filter_entities(['role']) if e.get('role')['value'] == 'player'][0]

        # get enemies entities and are in the same player floor
        enemies = [enemy for enemy in self.filter_entities(['role', 'position']) if enemy.get('role')['value'] == 'enemy' and enemy.get('position')['floor'] == player.get('position')['floor']]

        # get map on player floor
        map = dungeon['map'][player.get('position')['floor']]

        # get rooms center on player floor
        rooms_center = dungeon['rooms_center'][player.get('position')['floor']]

        for enemy in enemies:
            # if enemy has no direction, get a random room center position but only one time because it's slow
            calculated = False
            
            # si può fare meglio solo precalcolando i path (magari quando si fanno le stanze) ma sticazzi
            if len(enemy.get('direction')["value"]) == 0 and not calculated:
                calculated = True
                nearest_rooms = []
                for room in rooms_center:
                    distance = abs(enemy.get('position')['x'] - room[0]) + abs(enemy.get('position')['y'] - room[1])
                    nearest_rooms.append((room, distance))

                nearest_rooms.sort(key=lambda x: x[1])
                random_room = random.choice(nearest_rooms[:3])[0]

                enemy.get('direction')["value"] = self.a_star(map, (enemy.get('position')['x'], enemy.get('position')['y']), (random_room[0], random_room[1]))

            # go to direction
            if len(enemy.get('direction')["value"]) > 0:
                direction = enemy.get('direction')["value"].pop(0)
                enemy.get('position')['x'] = direction[0]
                enemy.get('position')['y'] = direction[1]
            
                       

            
            
