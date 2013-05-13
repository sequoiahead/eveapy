import os
import pickle
import shelve
import time

class SmartCache(object):
    def __init__(self, path=None):
        if path is None:
            path = os.getenv('XDG_CACHE_HOME', '$HOME/.cache/')
        path = path + 'eveapy/api.cache'
        d = os.path.dirname(path)
        if not os.path.exists(d):
            os.makedirs(d, 0755)
        self.__data = shelve.open(path)
    
    def __extractMeta(self, response):
        timeStr = response.find('cachedUntil').text
        return {'cachedUntil': time.strptime(timeStr, '%Y-%m-%d %H:%M:%S')}
    
    def __extractKey(self, request):
        return str(hash(request.get_full_url() + request.get_data()))
    
    def put(self, request, response):
        key = self.__extractKey(request)
        self.__data[key] = pickle.dumps(response)
        self.__data.sync()
        
    def get(self, request):
        key = self.__extractKey(request)
        if key not in self.__data:
            return None, None
        cached = pickle.loads(self.__data[key])
        meta = self.__extractMeta(cached)
        if time.gmtime() > meta['cachedUntil']:
            del self.__data[key]
            return None, None
        return cached, meta
