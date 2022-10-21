from .doublylinkedlist import DoublyLinkedList, Node

class Cache():
    items = {}
    list = DoublyLinkedList()

    def put(self, key, value):
        '''
            description: this method is used to add element to the cache which is a 
            dictionary and the key is the key for the image and the value is node contains 
            the image in base64 format and we add the node in doubly linkedlist so we can 
            perform the lru 
            input: key -> the image key 
                    value -> the image in base64 format
            output: None 
        '''
        if key in self.items:
            self.list.dropNode(self.items[key])
        n = Node(key = key, value= value)
        self.items[key] = n
        self.list.addFirst(n)

    def get(self, key):
        '''
            description: this method is used to get item from the cache and put it on the
            front of the linkedlist so the minimum used once are at last so we can delete them
            input: key -> the key to the item we want to get
            output: the item we got
        '''
        if key in self.items:
            node = self.items[key]
            value = node.value
            self.list.dropNode(node)
            self.list.addFirst(node= node)
            return value

    def drop(self, key):
        '''
            description: this method is used to delete specific item from the cache
            input: key -> the key to the item we want to delete
            output: the item we deleted
        '''
        if(key in self.items):
            node = self.items[key]
            self.list.dropNode(node)
            return self.items.pop(key)

    def dropRandom(self):
        '''
            description: this method is used to delete random element from the cache
            input: None
            output: the deleted node 
        '''
        key, value = self.items.popitem()
        self.list.dropNode(value)
        return value

    def dropLast(self):
        '''
            description: this method is used to delete the last item of the cache
            which is the least used one
            input: None
            output: the deleted node
        '''
        node = self.list.tail
        self.list.dropNode(node)
        return self.items.pop(node.key)

    def clear(self):
        '''
            description: this method is used to delete all cache data
            input: None
            output: None
        '''
        self.items.clear()
        self.list = DoublyLinkedList()

    def iterate(self):
        h = self.list.head
        while h != None:
            print(h.value)
            h = h.next

    def printD(self):
        '''
            description: this method is used to print the items of cache
            input: None
            output: None
        '''
        print(self.items)

    def count(self):
        '''
            description: this method is used to get the length of items in cache
            input: None
            output: cache items length
        '''
        return len(self.items)
