from underkate.room_transition import RoomTransitionBase


class FightEnterAnimation(RoomTransitionBase):
    def __init__(self, size, length, on_finish):
        super().__init__(size, length)
        self._on_finish = on_finish


    def on_stop(self):
        return self._on_finish()


    def calculate_alpha_coefficient(self, elapsed_time):
        k = int(round(elapsed_time / self.length * 4))
        return 0.0 if k % 2 == 0 else 1.0
