from collections import namedtuple
from eveapy import fqcn
from eveapy.cache import SmartCache
import logging
import time
import urllib
import urllib2
import xml.etree.ElementTree as et

ApiKey = namedtuple('ApiKey', ('keyID', 'vCode'))
Character = namedtuple('Character', ('characterID', 'name', 'corporationName', 'corporationID'))
AccountStatus = namedtuple('AccountStatus', ('paidUntil', 'createDate', 'logonCount', 'logonMinutes'))

class Api(object):
    def __init__(self, cache, apiKey=None, urlBase='https://api.eveonline.com'):
        self.urlBase = urlBase;
        if apiKey is not None and not isinstance(apiKey, ApiKey):
            raise TypeError("apiKey object must be of type %s", fqcn(ApiKey))
        self.apiKey = apiKey
        if not isinstance(cache, SmartCache):
            raise TypeError("cache object must be of type %s.%s", fqcn(SmartCache))
        self.__cache = cache
        self.__logger = logging.getLogger(fqcn(self))
        
    def getResponse(self, urlApi, reqData=None, bypassCache=False):
        req = self.__prepareRequest(urlApi, reqData)
        self.__logger.debug("URL: %s, data: %s", req.get_full_url(), req.get_data())
     
        if not bypassCache:
            cached, meta = self.__cache.get(req)
        if cached is not None:
            self.__logger.debug("Cache hit, cached until: %s", time.strftime("%Y-%m-%d %H:%M:%S UTC", meta['cachedUntil']))
            return cached
        self.__logger.debug("Cache miss (bypass = %s)", bypassCache)
        
        rawResponse = urllib2.urlopen(req).read()
        self.__logger.debug("Raw response:\n%s", rawResponse)
        response = et.fromstring(rawResponse)
        
        self.__handleError(response)
        
        self.__cache.put(req, response) 
        return response
    
    def __handleError(self, response):
        error = response.find('error')
        if(error is not None):
            raise ApiException(error.attrib['code'], error.text)
        
    def __prepareRequest(self, urlApi, reqData=None):
        reqDataFull = self.apiKey._asdict() if self.apiKey is not None else dict()
        if reqData is not None:
            reqData = reqData._asdict() if isinstance(reqData, ApiKey) else reqData
            reqDataFull = dict(sorted(reqDataFull.items() + reqData.items()))
        req = urllib2.Request('%s/%s' % (self.urlBase, urlApi))
        req.add_data(urllib.urlencode(reqDataFull))
        return req
        
class Account(object):
    def __init__(self, api, apiKey):
        self.__api = api
        self.__apiKey = apiKey
    
    def getCharacters(self):
        response = self.__api.getResponse('account/characters.xml.aspx', self.__apiKey)
        
        charsList = []
        for char in list(response.find('result/rowset')):
            charsList.append(Character(**char.attrib))
        return charsList
    
    def getAccountStatus(self):
        response = self.__api.getResponse('account/AccountStatus.xml.aspx', self.__apiKey)
        status = response.find('result')
        return AccountStatus(**dict((x.tag, x.text) for x in list(status)))
    
class ApiException(Exception):
    def __init__(self, code, message):
        self.__code = code
        self.__message = message

    def __str__(self):
        return '#%s %s' % (self.__code, self.__message) 
