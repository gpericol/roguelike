from system import System

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


class HungerSystem(System):

    def print_map_with_path(self, map, start_node, end_node, path):
        for y in range(len(map)):
            for x in range(len(map[y])):
                if (x, y) == start_node:
                    print('s', end='')
                elif (x, y) == end_node:
                    print('e', end='')
                elif (x, y) in path:
                    print('p', end='')
                else:
                    if map[y][x] == 0:
                        print('#', end='')
                    else:
                        print('.', end='')
            print()


    def print_map(self, map, closed_list, open_list, start_node, end_node):
        for y in range(len(map)):
            for x in range(len(map[y])):
                if Node(None,(x, y)) == start_node:
                    print('s', end='')
                elif Node(None,(x, y)) == end_node:
                    print('e', end='')
                elif Node(None,(x, y)) in open_list:
                    print('o', end='')
                elif Node(None,(x, y)) in closed_list:
                    print('x', end='')
                else:
                    if map[y][x] == 0:
                        print('#', end='')
                    else:
                        print('.', end='')
            print()

    def a_star(self, map, start, end):
        open_list = []
        closed_list = []

        start_node = Node(None, start)
        end_node = Node(None, end)

        # start node on open list
        open_list.append(start_node)

        count = 0

        while len(open_list) > 0:
            count += 1

            # sort by least f
            open_list.sort(key=lambda x: x.f)

            # remove first element from open list
            current_node = open_list.pop(0)

            closed_list.append(current_node)

            # if current node is end node, return path
            if current_node == end_node:
                print(count)
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]

            children = [Node(current_node,(current_node.position[0] + p[0], current_node.position[1] + p[1])) for p in [(0, -1), (0, 1), (-1, 0), (1, 0)]]

            for child in children:
                # check child in range
                if child.position[0] > (len(map) - 1) or child.position[0] < 0 or child.position[1] > (len(map[len(map)-1]) -1) or child.position[1] < 0:
                    continue

                # if child is on closed list, skip
                if child in closed_list:
                    continue
                
                # if child is not walkable, skip
                if map[child.position[1]][child.position[0]] == 0:
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
        map = [e for e in self.filter_entities("map")][0]

        # get the cake
        cake = [e for e in self.filter_entities("race") if e.get("race")["value"] == 'cake'][0]
        human = [e for e in self.filter_entities("race") if e.get("race")['value'] == 'human'][0]
        
        human_position = human.get('position')
        cake_position = cake.get('position')

        path = self.a_star(map.get('map')["value"], (human_position["x"],human_position["y"]) ,(cake_position["x"],cake_position["y"]))
        
        self.print_map_with_path(map.get('map')["value"], (human_position["x"],human_position["y"]) ,(cake_position["x"],cake_position["y"]), path)
        exit()

        """

        if human_position['x'] == cake_position['x'] and human_position['y'] == cake_position['y']:
            print('You ate the cake!')
            self.push_event('cake_eaten')
        
        else:
            print("human position: ", human_position)
            print("cake position: ", cake_position)

            if human_position['x'] < cake_position['x']:
                human_position['x'] += 1
            elif human_position['x'] > cake_position['x']:
                human_position['x'] -= 1

            if human_position['y'] < cake_position['y']:
                human_position['y'] += 1
            elif human_position['y'] > cake_position['y']:
                human_position['y'] -= 1

        """