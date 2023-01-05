from system import System
from constants import * 
import curses
import math
import time

class ScreenSystem(System):    
    def get_top_string(self, player, curses_component):
        status = player.get('status')
        #get screen width
        width = curses_component.w
        text = f"HP: {status['hp']}/{status['max_hp']} | Sanity: {status['sanity']}/{status['max_sanity']} | Floor: {player.get('position')['floor']}"
        return " "*(width - len(text) - 1) + text

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

    def get_crate_char(self, crate):
        #get crate state
        state = crate.get('state')['value']
        if state == 'closed':
            return '#'
        elif state == 'open':
            return 'O'
        elif state == 'locked':
            return '&'
        return '_'

    # print map using ncurses putting player in the middle and map around
    def print_dungeon(self):
        curses_component = System.get_entity_component('curses')['value']
        curses_component.screen.clear()
        
        player = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'player'][0]
        dungeon_entity = System.filter_entities(['dungeon'])[0]

        map = dungeon_entity.get('dungeon')['map'][player.get('position')['floor']]
        blood = dungeon_entity.get('dungeon')['blood'][player.get('position')['floor']]
        visited = dungeon_entity.get('dungeon')['visited'][player.get('position')['floor']]
        visible = dungeon_entity.get('visibility')['visible']

        player_x = player.get('position')['x']
        player_y = player.get('position')['y']

        # get enemies in same floor
        enemies = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'enemy' and e.get('position')['floor'] == player.get('position')['floor']]

        # get crates in same floor
        crates = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'crate' and e.get('position')['floor'] == player.get('position')['floor']]

        # get stair up in same floor
        stair_up = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'stair_up' and e.get('position')['floor'] == player.get('position')['floor']]
        if stair_up:
            stair_up = stair_up[0]
        else:
            stair_up = None

        # get stair down in same floor
        stair_down = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'stair_down' and e.get('position')['floor'] == player.get('position')['floor']]
        if stair_down:
            stair_down = stair_down[0]
        else:
            stair_down = None

        # get goal in same floor
        goal = [e for e in System.filter_entities(['role']) if e.get('role')['value'] == 'goal' and e.get('position')['floor'] == player.get('position')['floor']]
        if goal:
            goal = goal[0]
        else:
            goal = None

        # get map size
        map_h = len(map)
        map_w = len(map[0])

        # get map start position
        map_start_x = player_x - int(curses_component.w / 2)
        map_start_y = player_y - int(curses_component.h / 2)

        # get map end position
        map_end_x = player_x + int(curses_component.w / 2)
        map_end_y = player_y + int(curses_component.h / 2)

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
                    curses_component.screen.addch(y - map_start_y, x - map_start_x, '@', curses.color_pair(COLOR_RED))
                else:
                    # wall or crate
                    if map[y][x] >= WALL_FULL:
                        if not visible[y][x] and not visited[y][x]:
                            curses_component.screen.addch(y - map_start_y, x - map_start_x, ' ')
                        else:
                            # look if there is a crate in this position
                            new_crate = None
                            for crate in crates:
                                if crate.get('position')['x'] == x and crate.get('position')['y'] == y:
                                    new_crate = crate

                            # define symbol to paint
                            if new_crate:
                                value = self.get_crate_char(new_crate)
                                if visible[y][x] == True:
                                    color = COLOR_LIGHT_BROWN
                                elif visited[y][x] == True:
                                    color = COLOR_BROWN
                            else: # it is a wall
                                value = self.get_wall_char(map[y][x])
                                if visible[y][x] == True:
                                    color = COLOR_WHITE
                                elif visited[y][x] == True:
                                    color = COLOR_GRAY

                            curses_component.screen.addch(y - map_start_y, x - map_start_x, value, curses.color_pair(color))
 

                    
                    elif map[y][x] == GROUND_NORMAL: 
                        # print enemies
                        print_enemy = False
                        for enemy in enemies:
                            if visible[y][x] == True and enemy.get('position')['x'] == x and enemy.get('position')['y'] == y:
                                print_enemy = True
                                curses_component.screen.addch(y - map_start_y, x - map_start_x, enemy.get('race')['symbol'], curses.color_pair(COLOR_GREEN))
                                break

                        if print_enemy:
                            continue

                        # print stair up
                        print_stair= False

                        if stair_up:
                            if stair_up.get('position')['x'] == x and stair_up.get('position')['y'] == y:
                                print_stair = True
                                if visible[y][x] == True:
                                    curses_component.screen.addch(y - map_start_y, x - map_start_x, '<', curses.color_pair(COLOR_STAIR_VISIBLE))
                                elif visited[y][x] == True:
                                    curses_component.screen.addch(y - map_start_y, x - map_start_x, '<', curses.color_pair(COLOR_STAIR_HIDDEN))
                                else:
                                    curses_component.screen.addch(y - map_start_y, x - map_start_x, ' ')
                                

                        # print stair down
                        if stair_down:
                            if stair_down.get('position')['x'] == x and stair_down.get('position')['y'] == y:
                                print_stair = True
                                if visible[y][x] == True:
                                    curses_component.screen.addch(y - map_start_y, x - map_start_x, '>', curses.color_pair(COLOR_STAIR_VISIBLE))
                                elif visited[y][x] == True:
                                    curses_component.screen.addch(y - map_start_y, x - map_start_x, '>', curses.color_pair(COLOR_STAIR_HIDDEN))
                                else:
                                    curses_component.screen.addch(y - map_start_y, x - map_start_x, ' ')

                        # print goal
                        if goal:
                            if goal.get('position')['x'] == x and goal.get('position')['y'] == y:
                                print_stair = True
                                if visible[y][x] == True:
                                    curses_component.screen.addch(y - map_start_y, x - map_start_x, 'X', curses.color_pair(COLOR_STAIR_VISIBLE))
                                elif visited[y][x] == True:
                                    curses_component.screen.addch(y - map_start_y, x - map_start_x, 'X', curses.color_pair(COLOR_STAIR_HIDDEN))
                                else:
                                    curses_component.screen.addch(y - map_start_y, x - map_start_x, ' ')
                                
                        if print_stair:
                            continue

                        if visible[y][x] == True:
                            color = COLOR_WHITE
                            if blood[y][x]:
                                color = COLOR_RED
                            curses_component.screen.addch(y - map_start_y, x - map_start_x, '.', curses.color_pair(color))
                        elif visited[y][x] == True:
                            color = COLOR_DARK_GRAY
                            if blood[y][x]:
                                color = COLOR_LIGHT_RED
                            curses_component.screen.addch(y - map_start_y, x - map_start_x, '.', curses.color_pair(color))
                        else:
                            curses_component.screen.addch(y - map_start_y, x - map_start_x, ' ')


        # get noise event from system
        noise = System.get_event('noise')

        if noise:
            symbol = noise["value"]['symbol']
            color = noise["value"]['color']
            radius = noise["value"]['radius']
            x = noise["value"]['position']['x']
            y = noise["value"]['position']['y']

            for i in range(360):
                deg = i * (math.pi / 180)
                nx = round(math.cos(deg) * radius) + x - map_start_x
                ny = round(math.sin(deg) * radius) + y - map_start_y
                if nx >= 0 and nx < curses_component.w and ny >= 0 and ny < curses_component.h:
                    curses_component.screen.addch(ny, nx, symbol, curses.color_pair(color))

            # remove noise from system
            self.remove_events('noise')

        damage = System.get_event('damage')

        if damage:
            value = "-" + damage["value"]['value'] 
            count = damage["value"]['count']
            color = COLOR_LIGHT_RED

            nx = player_x - map_start_x
            ny = player_y - map_start_y + count

            if nx >= 0 and nx < curses_component.w and ny >= 0 and ny < curses_component.h:
                curses_component.screen.addstr(ny, nx, value, curses.color_pair(color))

            self.remove_events('damage')

        bonk = System.get_event('bonk')

        if bonk:
            value = "*BONK*"
            count = bonk["value"]['count']
            color = COLOR_GRAY

            nx = player_x - map_start_x
            ny = player_y - map_start_y - count

            if nx >= 0 and nx < curses_component.w and ny >= 0 and ny < curses_component.h:
                curses_component.screen.addstr(ny, nx, value, curses.color_pair(color))

            self.remove_events('bonk')

        death = System.get_event('death')

        if death:
            color = death["value"]['color']
            x = death["value"]['position']['x']
            y = death["value"]['position']['y']

            nx = x - map_start_x
            ny = y - map_start_y

            if nx >= 0 and nx < curses_component.w and ny >= 0 and ny < curses_component.h:
                curses_component.screen.addch(ny, nx, '±', curses.color_pair(color))

            self.remove_events('death')

        sanity = System.get_event('sanity')

        if sanity:
            value = "+10 SANITY"
            count = sanity["value"]['count']
            color = COLOR_WHITE

            nx = player_x - map_start_x
            ny = player_y - map_start_y - count

            if nx >= 0 and nx < curses_component.w and ny >= 0 and ny < curses_component.h:
                curses_component.screen.addstr(ny, nx, value, curses.color_pair(color))

            self.remove_events('sanity')

        health = System.get_event('health')

        if health:
            value = "+10 HEALTH"
            count = health["value"]['count']
            color = COLOR_WHITE

            nx = player_x - map_start_x
            ny = player_y - map_start_y - count

            if nx >= 0 and nx < curses_component.w and ny >= 0 and ny < curses_component.h:
                curses_component.screen.addstr(ny, nx, value, curses.color_pair(color))

            self.remove_events('health')

        
        
        # print top bar
        curses_component.screen.addstr(0, 0, self.get_top_string(player, curses_component), curses.color_pair(COLOR_TOP))
        
        # DEBUG
        debug = None
        for event in System._events:
            if event['type'] == 'debug':
                debug = event
                break
        if debug:
            curses_component.screen.addstr(1, 0, debug['value'], curses.color_pair(COLOR_TOP))
            self.remove_events('debug')

        curses_component.screen.refresh()
    

    def print_init(self):
        curses_component = System.get_entity_component('curses')['value']
        curses_component.screen.clear()
        curses_component.screen.addstr(5, 0, TITLE, curses.color_pair(COLOR_RED))
        curses_component.screen.addstr(1, 0, 'Press [Enter] to start', )
        curses_component.screen.addstr(15, 0, DISCLAIMER, curses.color_pair(COLOR_WHITE))
        curses_component.screen.refresh()

    def print_gameover(self):
        curses_component = System.get_entity_component('curses')['value']
        curses_component.screen.clear()
        curses_component.screen.addstr(5, 0, GAMEOVER, curses.color_pair(COLOR_RED))
        curses_component.screen.addstr(1, 0, 'Press [Enter] to start')
        curses_component.screen.refresh()

    def print_win(self):
        curses_component = System.get_entity_component('curses')['value']
        curses_component.screen.clear()
        curses_component.screen.addstr(5, 0, VICTORY, curses.color_pair(COLOR_GREEN))
        curses_component.screen.addstr(1, 0, 'Press [Enter] to start')
        curses_component.screen.refresh()

    def update(self):
        state = System.get_entity_component('state')['value']
        if state == 'dungeon':
            self.print_dungeon()
        elif state == 'init':
            self.print_init()
        elif state == 'gameover':
            self.print_gameover()
        elif state == 'win':
            self.print_win()