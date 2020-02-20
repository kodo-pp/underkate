from underkate.counter import Counter

from abc import abstractmethod
from typing import Generic, TypeVar, Iterable, List, Callable, Optional


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


class FilterWithDeleter(Operation, Generic[T]):
    def __init__(self, predicate: Callable[[T], bool], deleter: Callable[[T], None]):
        self._predicate = predicate
        self._deleter = deleter


    def __call__(self, raw_list: List[T]) -> List[T]:
        kept_items: List[T] = []
        for item in raw_list:
            if self._predicate(item):
                kept_items.append(item)
            else:
                self._deleter(item)
        return kept_items


class WalList(Generic[T]):
    def __init__(self, sequence: Iterable[T]):
        self._list: List[T] = list(sequence)
        self._wal: List[Operation] = []
        self._lock_counter = Counter()


    def __enter__(self):
        #print('==================================== LOCK')
        self._lock_counter.increase()
        return self


    def __exit__(self, *args):
        #print('==================================== UNLOCK')
        self._lock_counter.decrease()
        if not self.is_locked():
            self._apply_wal()


    def is_locked(self):
        return not self._lock_counter.is_zero()


    def __iter__(self):
        return iter(self._list)


    def __len__(self):
        return len(self._list)


    def _apply(self, operation: Operation):
        self._list = operation(self._list)


    def _apply_or_defer(self, operation: Operation):
        if self.is_locked():
            self._wal.append(operation)
        else:
            self._apply(operation)


    def append(self, item: T):
        self._apply_or_defer(Append(item))


    def filter(
        self,
        predicate: Callable[[T], bool],
        deleter: Optional[Callable[[T], None]] = None,
        now: bool = False,
    ):
        operation: Operation
        if deleter is None:
            operation = Filter(predicate)
        else:
            operation = FilterWithDeleter(predicate, deleter)

        if now:
            self._apply(operation)
        else:
            self._apply_or_defer(operation)


    def _apply_wal(self):
        for operation in self._wal:
            self._apply(operation)
        self._wal = []
