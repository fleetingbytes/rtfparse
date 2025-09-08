#!/usr/bin/env python
from abc import ABC, abstractmethod

class Renderer(ABC):
    @abstractmethod
    def render(self) -> None:
        pass
    pass


if __name__ == "__main__":
    pass
