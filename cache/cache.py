from .doublylinkedlist import DoublyLinkedList, Node

class Cache():
    items = {}
    list = DoublyLinkedList()

    def put(self, key, value):
        if key in self.items:
            self.list.dropNode(self.items[key])
        n = Node(key = key, value= value)
        self.items[key] = n
        self.list.addFirst(n)

    def get(self, key):
        if key in self.items:
            node = self.items[key]
            value = node.value
            self.list.dropNode(node)
            self.list.addFirst(node= node)
            return value

    def drop(self, key):
        if(key in self.items):
            node = self.items[key]
            self.list.dropNode(node)
            return self.items.pop(key)

    def dropRandom(self):
        key, value = self.items.popitem()
        self.list.dropNode(value)
        return value

    def dropLast(self):
        node = self.list.tail
        self.list.dropNode(node)
        return self.items.pop(node.key)

    def clear(self):
        self.items.clear()
        self.list = DoublyLinkedList()

    def iterate(self):
        h = self.list.head
        while h != None:
            print(h.value)
            h = h.next

    def printD(self):
        print(self.items)

    def count(self):
        return len(self.items)
