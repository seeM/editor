from dataclasses import dataclass, field, replace
from uuid import uuid4

from pyrsistent import pmap


@dataclass(frozen=True)
class Block:
    string: object = ""
    id: object = field(default_factory=uuid4)

    def print(self, level=0, indent=2, bullet="-"):
        indent = level * indent * " "
        string = indent + bullet + " " + self.string + "\n"
        for c in self.children:
            string += c.print(level + 1)
        return string

    def __str__(self):
        return self.print().strip()

    def __hash__(self):
        return hash(self.id)

#     def add_child(self, block):
#         if block.parent:
#             raise ValueError("Block already has a parent")
#         block = replace(block, parent=self)
#         return replace(self, children=self.children + [block]), block

#     def remove_child(self, block):
#         b
#         pass


@dataclass(frozen=True)
class Page:
    name: object
    # children: object
    # parent: object

    def __str__(self):
        return "\n".join((self.name, len(self.name)*"-", *(str(c) for c in self.children)))


@dataclass(frozen=True)
class Outliner:
    page: object
    _children: object
    _parent: object

    @classmethod
    def make(cls, page, children):
        blocks = set(children.keys()) | set(children.values())
        parent = pmap({c: b for b in blocks for c in children.get(b, [])})
        return cls(page, children, parent)

    def index(self, block):
        p = self.parent(block)
        return self.children(p).index(block) if p else None

    def add_child(self, block, child):
        children = self.children.copy()
        children[block] = children[block].copy()
        children[block].append(block)
        return Page(self.name, children=children)

    def remove_child(self, parent, block):
        children = self.children.copy()
        children[parent] = children[parent].copy()
        children[parent].remove(block)
        return Page(self.name, children=children)

    def parent(self, block):
        return self._parent.get(block, None)

    def children(self, block):
        return self._children.get(block, [])

    def siblings(self, block):
        p = self.parent(block)
        return [c for c in self.children[p] if c.id != block.id] if p else []

    # TODO: Staying immutable feels shit... Think that needs to be at a lower level of abstraction
    # TODO: Handle error cases
    def indent(self, block):
        # Add block to its _previous_ sibling
        # TODO: Should siblings & child_index exist on block?
        s = self.siblings(block)[self.index(block) - 1]
        self.add_child(s, b)

        # Remove block from its parent
        p = self.parent[block]
        page = remove_child(page, p, b)

        return page
