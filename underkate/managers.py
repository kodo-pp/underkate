from typing import TypeVar, Generic, Hashable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .object import Object
    from .texture import Texture


__all__ = ['texture_manager', 'object_manager', 'ResourceId', 'GroupId', 'ResourceManager']

T = TypeVar('T')


ResourceId = str
GroupId = Hashable


class ResourceManager(Generic[T]):
    def __init__(self):
        self._counter = 0
        self._resources: Dict[ResourceId, T] = {}
        self._groups: Dict[GroupId, List[ResourceId]]

    def unique_id(self) -> ResourceId:
        self._counter += 1
        return str(self._counter)

    def add(self, resource: T, group: Optional[GroupId] = None) -> ResourceId:
        resource_id = self.unique_id()
        self._resources[resource_id] = resource
        if group is not None:
            self._groups.setdefault(group, []).append(resource_id)
        return resource_id

    def delete_group(self, group: GroupId):
        resource_ids = self._groups.setdefault(group, [])
        for resource_id in resource_ids:
            self.delete(resource_id, must_exist=False)
        del self._groups[group]

    def delete(self, resource_id: ResourceId, must_exist: bool = True):
        if must_exist:
            del self._resources[resource_id]
        else:
            self._resources.pop(resource_id, None)

    def __getitem__(self, resource_id: ResourceId) -> T:
        return self._resources[resource_id]

    def __contains__(self, resource_id: ResourceId) -> bool:
        return resource_id in self._resources


texture_manager: ResourceManager['Texture'] = ResourceManager()
object_manager: ResourceManager['Object'] = ResourceManager()
