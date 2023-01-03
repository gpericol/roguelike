from component import Component
from entity import Entity
from system import System
from screen_system import ScreenSystem
from state_system import StateSystem
from visibility_system import VisibilitySystem
from curses_manager import CursesManager
from keyboard_system import KeyboardSystem  
from init_system import InitSystem
from dungeon_system import DungeonSystem
from enemies_system import EnemiesSystem
from animation_system import AnimationSystem
from gameover_system import GameoverSystem

def main():
    # crate state entity
    entity_state = Entity()

    curses_manager = CursesManager()
    component_curses = Component('curses')
    component_curses.data['value'] = curses_manager

    component_state = Component('state')

    entity_state.append(component_curses)
    entity_state.append(component_state)

    System.add_entity(entity_state)

    System.push_event({
        "type": "state_change",
        "value": "init"
    })

    system_state = StateSystem()
    system_screen = ScreenSystem()
    system_keyboard = KeyboardSystem()
    system_init = InitSystem()
    system_dungeon = DungeonSystem()
    system_visibility = VisibilitySystem()
    system_enemies = EnemiesSystem()
    system_animation = AnimationSystem()
    system_gameover = GameoverSystem()
    

    while(True):
        system_state.update()
        system_visibility.update()
        system_screen.update()
        system_animation.update()
        system_keyboard.update()
        system_init.update()
        system_dungeon.update()
        system_enemies.update()
        system_gameover.update()

if __name__ == '__main__':
    main()