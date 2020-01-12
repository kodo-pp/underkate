class CounterError(Exception):
    pass


class Counter:
    def __init__(self):
        self._count = 0


    def is_zero(self) -> bool:
        assert self._count >= 0
        return self._count == 0


    def increase(self):
        self._count += 1


    def decrease(self):
        if self._count <= 0:
            raise CounterError('Counter decreased at zero')
        self._count -= 1


    def with_increased(self) -> 'Increaser':
        return Increaser(self)


class Increaser:
    def __init__(self, counter: Counter):
        self.counter = counter


    def __enter__(self):
        self.counter.increase()
        return self.counter


    def __exit__(self, *args):
        self.counter.decrease()
