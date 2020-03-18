from underkate.vector import Vector
from underkate.scriptlib.script_module import script_import

madecs = script_import('madecs', file=__file__, name=__name__)


async def main(**kwargs):
    manager = madecs.SpawnerManager()
    manager.add_spawner(position=Vector(1105, 179), speed=Vector(-120, 120), interval=1.5)
    manager.add_spawner(position=Vector(-101, 894), speed=Vector(130, -140), interval=1.0)
    manager.add_spawner(position=Vector(969, 1012), speed=Vector(-200, -200), interval=0.7)
    await madecs.setup(manager)
