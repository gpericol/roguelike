from system import System

class StateSystem(System):
    """
        event: state_change
        {
            "type": "state_change",
            "value": "state"
        }

        states:
            - init
            - dungeon
            - gameover
    """
    def update(self):

        new_state = None
        # find event with type state_change
        for event in self._events:
            if event.get('type') == 'state_change':
                new_state = event["value"]
                break

        if new_state is None:
            return
        
        state_entity = self.filter_entities(['state'])[0]
        curses = state_entity.get('curses')["value"]

        if new_state == 'gameover':
            curses.screen.nodelay(False)
            self.get_entity_component('state')['value'] = "gameover"

        if new_state == 'dungeon':
            curses.screen.nodelay(False)
            self.get_entity_component('state')['value'] = "dungeon"

        if new_state == 'init':
            curses.screen.nodelay(False)
            self.get_entity_component('state')['value'] = "init"

        # remove change state event
        System.remove_events('state_change')