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
        self.maxSizeByte = maxSizeByte
        self.lru = lru

    def put(self, key, image):
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
        self.requsts += 1
        value = self.cache.get(key)
        if(value != None):
            self.hits += 1
        return value

    def clear(self):
        self.cache.clear()
        self.size = 0

    def drop(self, key):
        image = self.cache.drop(key = key)
        self.size -= os.stat(os.path.join(self.images_path, image.value)).st_size

    def updateMaxSizeByte(self, max):
        self.maxSizeByte = max *1024 *1024

    def updateLru(self):
        if self.lru:
            self.lru = False
        else:
            self.lru = True

    def missRate(self):
        if(self.requsts == 0):
            return 0
        return (self.requsts - self.hits) / self.requsts

    def hitRate(self):
        if(self.requsts == 0):
            return 0
        return self.hits / self.requsts

    def resetStats(self):
        self.request = 0
        self.hits = 0
        self.miss = 0

    def getStats(self):
        return (self.count(), self.requsts, self.size, self.missRate(), self.hitRate())

    def count(self):
        return len(self.cache.items)

    def sizeMB(self):
        return self.size /(1024 * 1024)
