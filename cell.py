DEAD = 0
ALIVE = 1
PERMANENT = 2
OBJECTIVE = 3


class Cell:
    def __init__(self, state=DEAD):
        self.state = state

    @property
    def is_alive(self):
        return self.state in (ALIVE, PERMANENT)

    @property
    def is_permanent(self):
        return self.state == PERMANENT

    @property
    def is_objective(self):
        return self.state == OBJECTIVE

    def copy(self):
        return Cell(self.state)
