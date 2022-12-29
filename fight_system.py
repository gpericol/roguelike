from system import System
import time

class FightSystem(System):
    def __init__(self):
        super().__init__()
        self.last_time = 0
        # 20 per second
        self.delay = 50
        
    def update(self):
        # get state and verify that is fight
        state = self.get_entity_component('state')['value']
        if state != 'fight':
            return

        # wait for delay
        now = int(round(time.time() * 1000))
        if now - self.last_time < self.delay:
            return
        
        self.last_time = now

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
        # just test

        key_sequence = self.get_entity_component('key_sequence')['value']
        # if bigger than 10 remove last
        if len(key_sequence) > 10:
            key_sequence.pop(0)
        
        # add key to sequence
        key_sequence.append(key)
        
        """
        curses = self.filter_entities(['curses'])[0].get('curses')['value']
        curses.screen.addstr(0, 0, 'key: ' + str("".join(self.sequence)))
        curses.screen.refresh()
        """
        System.remove_events('key_stroke')