class Node:
    def __init__(self, key = None ,value = None, previous = None ,next = None):
        self.value = value
        self.key = key
        self.next = next
        self.previous = previous


class DoublyLinkedList:
    head = None;
    tail = None;
    def __init__(self):
        self.head = None;
        self.tail = None

    def addFirst(self, value):
        if(self.head != None):
            newNode = Node(value = value)
            newNode.next = self.head
            self.head.previous = newNode
            self.head = newNode
        else:
            self.head = Node(value= value);
            self.tail = self.head

    def addFirst(self, node):
        if(self.head != None):
            node.next = self.head
            self.head.previous = node
            self.head = node
        else:
            self.head = node
            self.tail = self.head

    def dropNode(self, node):
        if(node == self.head):
            self.head = self.head.next
        elif(node == self.tail):
            self.tail = self.tail.previous
            if(self.tail != None):
                self.tail.next = None
        else:
            node.previous.next = node.next
            node.next.previous = node.previous
            node.next = None
            node.previous = None
