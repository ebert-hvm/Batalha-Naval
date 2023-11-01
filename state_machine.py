
class StateMachine:
    CONNECTION = 0
    SETUP = 1
    GAME = 2
    END = 3
    def __init__(self):
        self._state = 0
        self.stateChange = True
    def connection(self):
        pass
    def setup(self):
        pass
    def game(self):
        pass
    def end(self):
        pass
    def execute(self):
        match self._state:
            case self.CONNECTION:
                self.stateChange = self.connection()
            case self.SETUP:
                self.stateChange = self.setup()
            case self.GAME:
                self.stateChange = self.game()
            case self.END:
                self.stateChange = self.end()
                return False
        if self.stateChange:
            self._state += 1
        return True