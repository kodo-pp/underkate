from underkate.animated_texture import AnimatedTexture
from underkate.textured_walking_sprite import TexturedWalkingSprite
from underkate.event_manager import get_event_manager
from underkate.font import load_font
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import BulletSpawner, Interaction, RectangularBullet
from underkate.scriptlib.fight import FightScript, Weapon, Spare, UseWeapon, BaseBullet
from underkate.state import get_state
from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.util import collide_beam_and_point, clamp, random_between
from underkate.vector import Vector

import math
import random as rd
import time
from pathlib import Path

import pygame as pg


class Ball(RectangularBullet):
    def get_hitbox(self):
        return pg.Rect(-30, -30, 60, 60)


    def update(self, time_delta):
        super().update(time_delta)
        rect = self.bullet_board.get_rect()
        if self.pos.x < rect.left:
            self.speed.x = abs(self.speed.x)
        if self.pos.x >= rect.right:
            self.speed.x = -abs(self.speed.x)
        if self.pos.y < rect.top:
            self.speed.y = abs(self.speed.y)
        if self.pos.y >= rect.bottom:
            self.speed.y = -abs(self.speed.y)


class Line(BaseBullet):
    def __init__(
        self,
        start: Vector,
        end: Vector,
        thickness: float,
        displayed_thickness: int,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.start = start
        self.end = end
        self.thickness = thickness
        self.displayed_thickness = displayed_thickness
        self._started_at = time.monotonic()


    def get_elapsed_time(self):
        return time.monotonic() - self._started_at


    def is_in_setup_phase(self):
        return self.get_elapsed_time() < self.setup_duration


    def get_setup_phase_completion_percentage(self):
        return clamp(self.get_elapsed_time() / self.setup_duration, 0.0, 1.0)


    def draw(self, destination):
        if self.is_in_setup_phase():
            k = self.get_setup_phase_completion_percentage()
            brightness = int(clamp(256 * k, 0.0, 256 - 1e-9))
            color = (brightness,) * 3
            pg.draw.circle(destination, color, self.start.ints(), 5)
            pg.draw.circle(destination, color, self.end.ints(), 5)
        else:
            pg.draw.circle(destination, (255, 255, 255), self.start.ints(), 5)
            pg.draw.circle(destination, (255, 255, 255), self.end.ints(), 5)
            thickness = self._get_current_displayed_thickness()
            pg.draw.line(
                destination,
                (255, 255, 255),
                self.start.ints(),
                self.end.ints(),
                thickness,
            )


    def does_hit_at(self, pos):
        if self.is_in_setup_phase():
            return False
        return collide_beam_and_point((self.start, self.end, self.thickness), pos)


    def _get_current_displayed_thickness(self):
        t = self.get_elapsed_time()
        factor = 1.0 + 0.3 * math.sin(t * 25.0)
        bound = clamp(
            (self.setup_duration + self.beam_duration + self.teardown_duration - t)
                / self.teardown_duration,
            0.0,
            1.0,
        )
        return int(round(self.displayed_thickness * factor * bound))


    def is_alive(self):
        return (
            self.get_elapsed_time()
                < self.setup_duration + self.beam_duration + self.teardown_duration
        )


    setup_duration = 1.0
    beam_duration = 1.2
    teardown_duration = 0.2


class AttackSpawner(BulletSpawner):
    async def run(self):
        await rd.choice([self.run_lines, self.run_basketballs])()


    def _spawn_line(self, start, end):
        self.spawn(
            Line(
                bullet_board = self.bullet_board,
                pos = Vector(0, 0),
                speed = Vector(0, 0),
                damage = 4,
                start = start,
                end = end,
                thickness = 20,
                displayed_thickness = 8,
            ),
            unrestricted = True,
        )


    def _random_point_on_circle_boundary(self):
        return self._random_diameter()[0]


    def _random_diameter(self):
        rect = self.bullet_board.get_rect()
        r = 0.5 * math.sqrt(rect.width ** 2 + rect.height ** 2) + 20.0
        angle = random_between(0.0, math.pi * 2)
        offset = Vector(math.cos(angle), math.sin(angle)) * r
        center = Vector(*rect.center)

        first = center + offset
        second = center - offset
        return first, second


    async def run_lines(self):
        while True:
            await self.sleep_for(0.27)
            #start = self._random_point_on_circle_boundary()
            #end = self._random_point_on_circle_boundary()
            start, end = self._random_diameter()
            self._spawn_line(start, end)


    async def run_basketballs(self):
        for r, c, vx, vy in [(2, 4, -150, 180), (5, 9, 200, -170), (8, 1, 160, 160)]:
            self.spawn(
                Ball(
                    bullet_board = self.bullet_board,
                    pos = self.bullet_board.get_coords_at(r, c),
                    speed = Vector(vx, vy) * 1.5,
                    damage = 3,
                    texture = self.bullet_board.fight_script.textures['ball'],
                ),
            )
        await self.wait_until_timeout()


class Script(FightScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._has_run = False
        self._has_jumped = False
        self._has_moved = False


    def can_spare(self):
        return self._has_run and self._has_jumped and self._has_moved


    def create_bullet_spawner(self):
        return AttackSpawner(bullet_board=self.bullet_board)


    async def interact(self, interaction):
        await super().interact(interaction)

        if interaction.name == 'move':
            await self.interact_move()
        elif interaction.name == 'run':
            await self.interact_run()
        elif interaction.name == 'jump':
            await self.interact_jump()


    async def interact_move(self):
        if self._has_moved:
            await display_text(
                DisplayedText([
                    TextPage("... but nothing changes"),
                ])
            )
        else:
            await display_text(
                DisplayedText([
                    TextPage("It turns out that this is a good warm-up exercise!"),
                    TextPage("Sportick now allows you to proceed with training"),
                ])
            )
            self._has_moved = True


    async def interact_run(self):
        if self._has_run:
            await display_text(
                DisplayedText([
                    TextPage("... but, having already ran recently, you feel too tired to do it again"),
                ])
            )
        elif self._has_moved:
            await display_text(
                DisplayedText([
                    TextPage("You begin to walk slowly first, but then start to increase your speed"),
                    TextPage("Sportick admits that your running skills are fine"),
                    TextPage("Also, you have warmed up even more"),
                ])
            )
            self._has_run = True
        else:
            await display_text(
                DisplayedText([
                    TextPage("... but, before you run, you have to make your first movements"),
                ])
            )


    async def interact_jump(self):
        if self._has_jumped:
            await display_text(
                DisplayedText([
                    TextPage("... but Sportick is afraid that you can get an injury"),
                ])
            )
        elif self._has_run:
            await display_text(
                DisplayedText([
                    TextPage("... and your attempt is sucessful"),
                    TextPage("You lift yourself up, into the air"),
                    TextPage("Wow, you can jump really high!"),
                    TextPage("You remain in the air for a moment..."),
                    TextPage("But then it's time to fall down"),
                    TextPage("Regretting about the height of your jump, you begin your descent"),
                    TextPage("..."),
                    TextPage("Ouch!"),
                ])
            )
            self._has_jumped = True
            await display_text(load_text('fight/lyceum/sportick/player_jumped'))
        else:
            await display_text(
                DisplayedText([
                    TextPage("... but you haven't warmed up enough"),
                ])
            )


    def get_interactions(self):
        return [
            Interaction(
                name = 'run',
                pretty_name = 'Run',
                description = 'You try to run',
            ),
            Interaction(
                name = 'jump',
                pretty_name = 'Jump',
                description = 'You try to jump',
            ),
            Interaction(
                name = 'move',
                pretty_name = 'Move',
                description = 'You move around the room',
            ),
        ]


    async def _become_grumpylook(self):
        old_sportick = self.enemy.sprite
        texture = AnimatedTexture([old_sportick.texture], fps=1)
        sportick = TexturedWalkingSprite(
            pos = old_sportick.pos,
            left = texture,
            right = texture,
            front = texture,
            back = texture,
            speed = 240,
        )
        self.spawn(sportick)
        old_sportick.kill()
        await sportick.walk_x(500)
        texture = AnimatedTexture([self.textures['grumpylook']], fps=1)
        grumpylook = TexturedWalkingSprite(
            pos = sportick.pos,
            left = texture,
            right = texture,
            front = texture,
            back = texture,
            speed = 240,
        )
        self.spawn(grumpylook)
        sportick.kill()
        await grumpylook.walk_x(-500)
        self.enemy.name = 'Grumpylook'
        self.enemy.sprite = grumpylook


    async def _move_grumpylook_away(self):
        assert isinstance(self.enemy.sprite, TexturedWalkingSprite)
        await self.enemy.sprite.walk_x(-500)


    async def on_spare(self):
        await display_text(load_text('fight/lyceum/sportick/after_spare/1'))
        await self._become_grumpylook()
        await display_text(load_text('fight/lyceum/sportick/after_spare/2'))
        await self._move_grumpylook_away()
        await super().on_spare()


    async def on_hit(self, killed):
        await super().on_hit(killed)
        if not killed:
            return
        self.enemy.name = 'Grumpylook'
        await display_text(load_text('fight/lyceum/sportick/after_fight'))


async def run(*, enemy_battle, **kwargs):
    global fs
    fs = Script(enemy_battle)
    await fs.run()


async def draw(*, destination, **kwargs):
    global fs
    fs.draw(destination)


async def update(*, time_delta, **kwargs):
    global fs
    fs.update(time_delta)
