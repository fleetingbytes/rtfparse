#!/usr/bin/env python


# Own modules
from rtfparse import entities
from rtfparse.renderers import Renderer
import logging
# Typing
import io


# Setup logging
logger = logging.getLogger(__name__)


class Encapsulated_HTML(Renderer):
    def __init__(self) -> None:
        super().__init__()
        self.render_func = dict((
            ("par", lambda x: "\n"),
            ))
    def render(self, parsed: entities.Group, file: io.TextIOWrapper) -> None:
        for item in parsed.structure:
            if isinstance(item, entities.Group):
                self.render(item, file)
            elif isinstance(item, entities.Control_Word):
                try:
                    file.write(self.render_func[item.control_name](item))
                except KeyError:
                    pass
            else:
                pass


if __name__ == "__main__":
    pass
