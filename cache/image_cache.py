from .cache import Cache
import os

class ImageCache():
    cache = Cache()
    size = 0
    requsts = 0
    hits = 0
    miss = 0

    def __init__(self, images_path, maxSizeByte = 2 * 1024 * 1024, lru = True):
        self.maxSizeByte = maxSizeByte
        self.lru = lru
        self.images_path = images_path

    def put(self, key, image):
        imageSize = os.stat(os.path.join(self.images_path, image)).st_size
        while(self.size + imageSize > self.maxSizeByte):
            if(self.count() == 0):
                return
            droped = None
            if(self.lru):
                droped = self.cache.dropLast()
            else:
                droped = self.cache.dropRandom()
            self.size -= os.stat(os.path.join(self.images_path, droped.value)).st_size
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

    def updateConfig(self, maxSizeByte, lru):
        self.maxSizeByte = maxSizeByte
        self.lru = lru

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
