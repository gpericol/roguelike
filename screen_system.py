from system import System
from constants import * 

class ScreenSystem(System):    

    def get_wall_char(self, ch):
        if ch == WALL_FULL:
            return '#'
        elif ch == WALL_VERTICAL:
            return '|'
        elif ch == WALL_HORIZONTAL:
            return '-'
        elif ch == WALL_CORNER:
            return '+'
        return '#'

    # print map using ncurses putting player in the middle and map around
    def print_dungeon(self):
        curses = self.get_entity_component('curses')['value']
        curses.screen.clear()
        
        player = [e for e in self.filter_entities(['role']) if e.get('role')['value'] == 'player'][0]
        dungeon_entity = [e for e in self.filter_entities(['dungeon'])][0]

        map = dungeon_entity.get('dungeon')['map'][player.get('position')['floor']]
        visited = dungeon_entity.get('dungeon')['visited'][player.get('position')['floor']]
        visible = dungeon_entity.get('visibility')['visible']
        

        player_x = player.get('position')['x']
        player_y = player.get('position')['y']

        # get map size
        map_h = len(map)
        map_w = len(map[0])

        # get map start position
        map_start_x = player_x - int(curses.w / 2)
        map_start_y = player_y - int(curses.h / 2)

        # get map end position
        map_end_x = player_x + int(curses.w / 2)
        map_end_y = player_y + int(curses.h / 2)

        # check if map start position is out of map
        if map_start_x < 0:
            map_start_x = 0
        if map_start_y < 0:
            map_start_y = 0

        # check if map end position is out of map
        if map_end_x > map_w:
            map_end_x = map_w
        if map_end_y > map_h:
            map_end_y = map_h

        # print map
        for y in range(map_start_y, map_end_y):
            for x in range(map_start_x, map_end_x):
                if x == player_x and y == player_y:
                    # color red
                    curses.screen.addch(y - map_start_y, x - map_start_x, '@', curses.color_pair(1))
                    #curses.screen.addch(y - map_start_y, x - map_start_x, '@')
                else:
                    if map[y][x] >= WALL_FULL:
                        if visible[y][x] == True:
                            curses.screen.addch(y - map_start_y, x - map_start_x, self.get_wall_char(map[y][x]))
                        elif visited[y][x] == True:
                            curses.screen.addch(y - map_start_y, x - map_start_x, self.get_wall_char(map[y][x]))
                        else:
                            curses.screen.addch(y - map_start_y, x - map_start_x, ' ')

                    elif map[y][x] == GROUND_NORMAL:
                        if visible[y][x] == True:
                            curses.screen.addch(y - map_start_y, x - map_start_x, ' ')
                        elif visited[y][x] == True:
                            curses.screen.addch(y - map_start_y, x - map_start_x, '.')
                        else:
                            curses.screen.addch(y - map_start_y, x - map_start_x, ' ')
        curses.screen.refresh()
    
                  
    def print_fight(self):
        curses = self.get_entity_component('curses')['value']
        curses.screen.clear()
        key_sequence = self.get_entity_component('key_sequence')['value']
        curses.screen.addstr(0, 0, 'key: ' + str("".join(key_sequence)))
        curses.screen.refresh()

    def print_init(self):
        curses = self.get_entity_component('curses')['value']
        curses.screen.clear()
        curses.screen.addstr(0, 0, 'The Greatest Game Ever')
        curses.screen.addstr(1, 0, 'Press [Enter] to start')
        curses.screen.refresh()

    def update(self):
        state = self.get_entity_component('state')['value']
        if state == 'dungeon':
            self.print_dungeon()
        elif state == 'fight':
            self.print_fight()
        elif state == 'init':
            self.print_init()