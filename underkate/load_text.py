from underkate.text import DisplayedText, TextPage
from underkate.texture import load_texture, BaseTexture
from underkate.font import load_font

from pathlib import Path
from typing import List, Dict, Optional

import yaml


def _load_texture(root: Path, spec: str) -> BaseTexture:
    filename, _, scale_str = spec.partition('//')
    if _ != '':
        scale = int(scale_str)
        return load_texture(root / filename, scale)
    return load_texture(root / filename)


def load_text(name: str, fmt: Optional[Dict[str, str]] = None):
    if fmt is None:
        fmt = {}

    path = Path('.') / 'assets' / 'texts' / name

    with open(path / 'text.yml') as f:
        data = yaml.safe_load(f)

    pictures = {
        picture_name: _load_texture(path, picture_filename)
        for picture_name, picture_filename in data['pictures'].items()
    }

    pages: List[TextPage] = []
    for page in data['pages']:
        font_name = page.get('font', 'default')
        font = load_font(Path('.') / 'assets' / 'fonts' / font_name)
        delay = page.get('delay', 0.05)
        skippable = page.get('skippable', True)
        picture_name = page.get('picture', None)
        auto_advance = page.get('auto_advance', False)
        if picture_name is None:
            picture = None
        else:
            picture = pictures[picture_name]
        text = page['text'].format(**fmt)
        pages.append(
            TextPage(
                text,
                font = font,
                delay = delay,
                skippable = skippable,
                picture = picture,
                auto_advance = auto_advance,
            )
        )
    return DisplayedText(pages)
