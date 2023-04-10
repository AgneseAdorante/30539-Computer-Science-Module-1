class TNode:
    def __init__(self, data, parent = None):
        if not (isinstance(parent, TNode) or parent is None):
            raise TypeError("parent must be another Node or None")
        self.data = data
        self.parent = parent
        if parent is not None:
            parent.children.add(self)
        self.children = set()
    def __repr__(self):
        return f"N[{repr(self.data)}]"
    def __lt__(self, other):
        return self.data < other.data
    def subtree_repr(self):
        s = repr(self)
        if len(self.children) > 0:
            s += ":(" + ", ".join([c.subtree_repr() for c in sorted(self.children)]) + ")"
        return s
    def subtree_size(self):
        return 1 + sum([c.subtree_size() for c in self.children])
    def subtree_find(self, data):
        if self.data == data:
            return self
        for c in self.children:
            try:
                return c.subtree_find(data)
            except ValueError:
                pass
        raise ValueError("data not found")
    def subtree_check(self):
        if self.parent is not None:
            assert self in self.parent.children
        for c in self.children:
            c.subtree_check()
    def subtree_depth(self):
        if len(self.children)==0:
            return 1
        if len(self.children) > 0:
            return 1 + max([c.subtree_depth() for c in self.children])
    def subtree_attach(self,other):
        assert type(other) == TNode
        assert other.parent is None
        self.children.add(other)
        other.parent = self
    def subtree_detach(self,x):
        x.parent = None
        self.children.remove(x)
        
class DTree:
    def __init__(self, max_degree = 3):
        self.root = None
        self.max_degree = max_degree
    def __repr__(self):
        s = "DTree("
        if self.root is not None:
            s += self.root.subtree_repr()
        s += ")"
        return s
    def add(self, data):
        """
        Adds a new node to the tree with the given data and returns it.
        The node is added in the first available slot, breadth-first
        (layer-by-layer). Within each layer, candidate parent nodes are
        scanned in sorted order.
        """
        if self.root is None:
            self.root = TNode(data)
            return self.root
        parent = self._get_available_node(self.max_degree)
        return TNode(data, parent)
    def _get_available_node(self, max_degree):
        assert self.root is not None
        candidates = {self.root}
        while True:
            for c in sorted(candidates):
                if len(c.children) < max_degree:
                    return c
            staged = set()
            for c in candidates:
                staged |= c.children
            candidates = staged
    def __len__(self):
        if self.root is None:
            return 0
        return self.root.subtree_size()
    def _check(self):
        if self.root is None:
            return
        self.root.subtree_check()
    def depth(self):
        if self.root is None:
            return 0
        return self.root.subtree_depth()
    def attach_tree(self,other):
        try:
            type(other) == DTree()
        except:
            raise TypeError
        if self.root is None:
            self.root = other.root
        else:
            parent_free = self._get_available_node(self.max_degree)
            parent_free.subtree_attach(other.root)
        other.root = None
    def _find(self,data):
        try:
            return self.root.subtree_find(data)
        except:
            raise ValueError
    def __contains__(self,x):
        try:
            return self._find(x)
        except ValueError:
            return False
    def cut_subtree(self,x):
        new_tree = DTree()
        if self._find(x) == self.root:
            new_tree.root = self.root
            self.root = None
        else:
            new_tree.root = self._find(x)
            self.root.subtree_detach(self._find(x))
        return new_tree
