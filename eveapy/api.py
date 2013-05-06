import urllib2, urllib, time
import xml.etree.ElementTree as et

from eveapy import data

class Base(object):
    def __init__(self, apiKey, urlPath='', urlBase='https://api.eveonline.com'):
        self.urlBase = urlBase; 
        self.urlPath = urlPath; 
        self.apiKey = apiKey
        self.__cache = SmartCache()
        
    def _getResponse(self, urlApi, reqData=None):
        req = self.__prepareRequest(urlApi, reqData)
        
        cacheKey = req.get_full_url() + req.get_data()
        cachedReponse = self.__cache.get(cacheKey) 
        
        if cachedReponse != None:
            return cachedReponse
        
        rawResponse = urllib2.urlopen(req).read()
        response = et.fromstring(rawResponse)
        self.__cache.put(cacheKey, response) 
        return response
    
    def __prepareRequest(self, urlApi, reqData=None):
        reqDataFull = self.apiKey
        if reqData != None:
            reqDataFull = dict(reqDataFull.items() + reqData.items())
             
        req = urllib2.Request('%s/%s/%s' % (self.urlBase, self.urlPath, urlApi)) 
        req.add_data(urllib.urlencode(reqDataFull))
        return req
        
class Account(Base):
    def __init__(self, apiKey, urlPath='account'):
        Base.__init__(self, apiKey, urlPath)
    
    def getCharacters(self):
        response = self._getResponse('characters.xml.aspx')
        
        charsList = []
        for char in list(response.find('result/rowset')):
            charsList.append(data.Character(**char.attrib))
        return charsList
            

class SmartCache(object):
    def __init__(self):
        self.__data = dict()
        self.__meta = dict()
    
    def __extractMeta(self, response):
        timeStr = response.find('cachedUntil').text
        cachedUntil = time.strptime(timeStr, '%Y-%m-%d %H:%M:%S')
        return {'cachedUntil':cachedUntil}
        
    def put(self, key, value):
        self.__data[key] = value
        self.__meta[key] = self.__extractMeta(value)
        
    def get(self, key):
        if key not in self.__data:
            return None
        if time.gmtime() > self.__meta[key]['cachedUntil']:
            self.remove(key)
            return None
        return self.__data[key]
    
    def remove(self, key):
        del self.__data[key]
        del self.__meta[key]
