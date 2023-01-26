from operator import xor
from .cache import Cache
import os

class ImageCache():
    cache = Cache()
    size = 0
    requsts = 0
    hits = 0
    miss = 0

    def __init__(self, maxSizeByte = 2 * 1024 * 1024, lru = True):
        '''
            description: this method is used to initalize the image cache 
            object which will contain the cache and its properties 
            input: maxSizeByte -> the maximum size of the cache and it should not exceed it
                    lru -> if the deleting policy is least recently used or random
            output: None
        '''
        self.maxSizeByte = maxSizeByte
        self.lru = lru

    def put(self, key, image):
        '''
            description: this method is used to add elements to the cache
            and calculate its size and delete elements if the size exceeds the maximum 
            size
            input: key -> the image key, image -> the image in base64 format
            output: None
        '''
        imageSize = len(image) * 3/4
        while(self.size + imageSize > self.maxSizeByte):
            if(self.count() == 0):
                return
            droped = None
            if(self.lru):
                droped = self.cache.dropLast()
            else:
                droped = self.cache.dropRandom()
            self.size -= (len(droped.value) * 3/4)
        self.cache.put(key= key, value= image)
        self.size += imageSize

    def get(self, key):
        '''
            description: this method is used to get the item from its key
            input: key -> the key to the image we want to get
            output: the image we wanted and none if it doesn't exist
        '''
        self.requsts += 1
        value = self.cache.get(key)
        if(value != None):
            self.hits += 1
        return value

    def clear(self):
        '''
            description: this method is used to delete all cache elements
            input: None
            output: None
        '''
        self.cache.clear()
        self.size = 0

    def drop(self, key):
        '''
            description: this method is used to delete item for given key and 
            decrease the size of the used cache
            input: key to element we want to delete
            output: None
        '''
        image = self.cache.get(key)
        self.cache.drop(key = key)
        imagesize = len(image) * 3/4
        self.size -= imagesize

    def updateMaxSizeByte(self, max):
        '''
            description: this method is used to update the maximum size of cache
            input: None
            output: None
        '''
        self.maxSizeByte = max *1024 *1024

    def updateLru(self):
        '''
            description: this method is used to change the policy of deleting items on cache
            input: None
            output: None
        '''
        if self.lru:
            self.lru = False
        else:
            self.lru = True

    def missRate(self):
        '''
            description: this method is used to get miss rate when we get items,
            if the item is not in the cache its a miss so we substract the number of hits
            from the total number of requests and divide it by the total requests
            input: None
            output: miss rate
        '''
        if(self.requsts == 0):
            return 0
        return (self.requsts - self.hits) / self.requsts

    def hitRate(self):
        '''
            description: this method is used to get hit rate when we get items,
            if the item is in the cache its a hit so we divide it by the total requests
            input: None
            output: hit rate
        '''
        if(self.requsts == 0):
            return 0
        return self.hits / self.requsts

    def resetStats(self):
        '''
            description: this method is used to reset status of hit and miss rates
            input: None
            output: None
        '''
        self.request = 0
        self.hits = 0
        self.miss = 0

    def getStats(self):
        '''
            description: this method is used to get the current status of hit rate,
            miss rate, the request number and the size of the cache to store them in database
            input: None
            output: requsts -> number of requests happened, size -> the cache current size,
            missRate -> miss hitting rate, hitRate -> the hit rate
        '''
        return (self.count(), self.requsts, self.size, self.missRate(), self.hitRate())

    def count(self):
        '''
            description: this method is used to get number of items in cache
            input: None
            output: number of items in cache
        '''
        return len(self.cache.items)

    def sizeMB(self):
        '''
            description: this method is used to get the size of cache in mega bytes
            input: None
            output: the size in megabytes
        '''
        return self.size /(1024 * 1024)
        
