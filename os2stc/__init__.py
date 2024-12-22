import argparse
import json
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader("os2stc"))


class Vec3:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


class Node:
    def to_json(self) -> Any:
        raise NotImplementedError


class RootNode(Node):
    def __init__(self, children: Iterable[Node] | Node) -> None:
        try:
            self.children = list(children)
        except TypeError:
            self.children = [children]

    def to_json(self) -> Any:
        return {
            "type": "root",
            "children": [child.to_json() for child in self.children],
        }


class ObjectNode(Node):
    def __init__(self, position: Optional[Vec3] = None) -> None:
        if position is None:
            position = Vec3(0, 0, 0)
        self.position = position

    def to_json(self) -> Any:
        return {
            "type": "object",
            "position": {
                "x": self.position.x,
                "y": self.position.y,
                "z": self.position.z,
            },
        }


class CylinderNode(ObjectNode):
    def __init__(
        self,
        h: float = 1,
        r: float = 1,
        position: Optional[Vec3] = None,
        center: bool = False,
    ) -> None:
        super().__init__(position)
        self.h = h
        self.r = r
        self.center = center

    def to_json(self) -> Any:
        return {
            **super().to_json(),
            "type": "cylinder",
            "h": self.h,
            "r": self.r,
            "center": self.center,
        }


class CubeNode(ObjectNode):
    def __init__(
        self,
        size: Optional[Vec3] = None,
        position: Optional[Vec3] = None,
        center: bool = False,
    ) -> None:
        super().__init__(position)

        if size is None:
            size = Vec3(1, 1, 1)
        self.size = size

        self.center = center

    def to_json(self) -> Any:
        return {
            **super().to_json(),
            "type": "cube",
            "size": {
                "x": self.size.x,
                "y": self.size.y,
                "z": self.size.z,
            },
            "center": self.center,
        }


class TransformNode(Node):
    def __init__(self, children: Iterable[Node] | Node) -> None:
        try:
            self.children = list(children)
        except TypeError:
            self.children = [children]

    def to_json(self) -> Any:
        return {
            "type": "transform",
            "children": [child.to_json() for child in self.children],
        }


class TranslateNode(TransformNode):
    def __init__(self, translation: Vec3, children: Iterable[Node]) -> None:
        super().__init__(children)
        self.translation = translation

    def to_json(self) -> Any:
        return {
            **super().to_json(),
            "translation": {
                "x": self.translation.x,
                "y": self.translation.y,
                "z": self.translation.z,
            },
        }


class RotateNode(TransformNode):
    def __init__(self, rotation: Vec3, children: Iterable[Node]) -> None:
        super().__init__(children)
        self.rotation = rotation

    def to_json(self) -> Any:
        return {
            **super().to_json(),
            "rotation": {
                "x": self.rotation.x,
                "y": self.rotation.y,
                "z": self.rotation.z,
            },
        }


def compile(ast: Node, output: Path) -> None:
    template = env.get_template("fragment.glsl")
    with output.open("w") as f:
        f.write(template.render())


def parse(input: Path) -> RootNode:
    with input.open() as f:
        raise NotImplementedError


def main(args: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", default="scene.scad", type=Path, help="Input file"
    )
    parser.add_argument(
        "-o", "--output", default="out.glsl", type=Path, help="Output file"
    )
    args = parser.parse_args(args)

    # ast = parse(args.input)

    ast = RootNode(
        [
            # Car body base
            CubeNode(Vec3(60, 20, 10), center=True),
            # Car body top
            TranslateNode(
                Vec3(5, 0, 10 - 0.001),
                CubeNode(Vec3(30, 20, 10), center=True),
            ),
            # Front left wheel
            TranslateNode(
                Vec3(-20, -15, 0),
                RotateNode(
                    Vec3(90, 0, 0),
                    CylinderNode(h=3, r=8, center=True),
                ),
            ),
            # Front right wheel
            TranslateNode(
                Vec3(-20, 15, 0),
                RotateNode(
                    Vec3(90, 0, 0),
                    CylinderNode(h=3, r=8, center=True),
                ),
            ),
            # Back left wheel
            TranslateNode(
                Vec3(20, -15, 0),
                RotateNode(
                    Vec3(90, 0, 0),
                    CylinderNode(h=3, r=8, center=True),
                ),
            ),
            # Back right wheel
            TranslateNode(
                Vec3(20, 15, 0),
                RotateNode(
                    Vec3(90, 0, 0),
                    CylinderNode(h=3, r=8, center=True),
                ),
            ),
            # Front axle
            TranslateNode(
                Vec3(-20, 0, 0),
                RotateNode(
                    Vec3(90, 0, 0),
                    CylinderNode(h=30, r=2, center=True),
                ),
            ),
            # Back axle
            TranslateNode(
                Vec3(20, 0, 0),
                RotateNode(
                    Vec3(90, 0, 0),
                    CylinderNode(h=30, r=2, center=True),
                ),
            ),
        ]
    )
    # print(json.dumps(ast.to_json(), indent=2))

    compile(ast, args.output)
