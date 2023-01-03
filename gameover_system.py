from system import System

class GameoverSystem(System):
    def update(self):
        # get state
        state = System.get_entity_component('state')['value']
        if state != 'gameover':
            return

        # get event key_press
        key_press = None
        for event in self._events:
            if event['type'] == 'key_stroke':
                key_press = event
                break
                
        # no keypress
        if key_press is None:
            return

        key = key_press['value']

        if key == 'enter':
            System.push_event({
                "type": "state_change",
                "value": "init"
            })

        System.remove_events('key_stroke')