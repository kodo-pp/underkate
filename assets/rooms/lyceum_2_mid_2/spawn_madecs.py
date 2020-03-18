from underkate.vector import Vector
from underkate.scriptlib.script_module import script_import

madecs = script_import('madecs', file=__file__, name=__name__)


async def main(**kwargs):
    manager = madecs.SpawnerManager()
    for i in range(100, 2100, 200):
        manager.add_spawner(position=Vector(i, 700), speed=Vector(10, -200), interval=1.1)
    await madecs.setup(manager)
