from underkate.counter import Counter

from abc import abstractmethod
from typing import Generic, TypeVar, Iterable, List, Callable


__all__ = ['WalList']
T = TypeVar('T')


class Operation(Generic[T]):
    @abstractmethod
    def __call__(self, raw_list: List[T]) -> List[T]:
        ...


class Append(Operation, Generic[T]):
    def __init__(self, item: T):
        self._item = item


    def __call__(self, raw_list: List[T]) -> List[T]:
        raw_list.append(self._item)
        return raw_list


class Filter(Operation, Generic[T]):
    def __init__(self, predicate: Callable[[T], bool]):
        self._predicate = predicate


    def __call__(self, raw_list: List[T]) -> List[T]:
        return [item for item in raw_list if self._predicate(item)]


class WalList(Generic[T]):
    def __init__(self, sequence: Iterable[T]):
        self._list: List[T] = list(sequence)
        self._wal: List[Operation]
        self._lock_counter = Counter()


    def __enter__(self):
        self._lock_counter.increase()
        return self


    def __exit__(self, *args):
        self._lock_counter.decrease()
        if not self.is_locked():
            self._apply_wal()


    def is_locked(self):
        return self._lock_counter.is_zero()


    def __iter__(self):
        return iter(self._list)


    def __len__(self):
        return len(self._list)


    def append(self, item: T):
        if self.is_locked():
            self._wal.append(Append(item))
        else:
            self._list.append(item)


    def filter(self, predicate: Callable[[T], bool]):
        if self.is_locked():
            self._wal.append(Filter(predicate))
        else:
            self._list = [item for item in self._list if predicate(item)]
