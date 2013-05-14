from collections import namedtuple
from eveapy import fqcn
from eveapy.cache import SmartCache
import logging
import time
import urllib
import urllib2
import xml.etree.ElementTree as et

ApiKey = namedtuple('ApiKey', ('keyID', 'vCode'))
CharacterInfo = namedtuple('CharacterInfo', ('characterID', 'name', 'corporationName', 'corporationID'))
AccountStatusInfo = namedtuple('AccountStatusInfo', ('paidUntil', 'createDate', 'logonCount', 'logonMinutes'))
ApiKeyInfo = namedtuple('ApiKeyInfo', ('accessMask', 'type', 'expires', 'characters'))
SkillInTrainingInfo = namedtuple('SkillInTrainingInfo', ('skillInTraining', 'currentTQTime', 'trainingEndTime', 'trainingStartTime',
                                                 'trainingTypeID', 'trainingStartSP', 'trainingDestinationSP', 'trainingToLevel'))
SkillQueueItem = namedtuple('SkillQueueItem', ('queuePosition', 'typeID', 'level', 'startSP', 'endSP', 'startTime', 'endTime'))

def nodesListToDict(response, tagName='result'):
    return dict((x.tag, x.text) for x in list(response.find(tagName)))

class Api(object):
    def __init__(self, cache, apiKey=None, urlBase='https://api.eveonline.com'):
        self.__logger = logging.getLogger(fqcn(self))
        self.urlBase = urlBase;
        if apiKey is not None and not isinstance(apiKey, ApiKey):
            raise TypeError("apiKey object must be of type %s", fqcn(ApiKey))
        self.apiKey = apiKey
        if cache is None:
            self.__cache = SmartCache()
        if not isinstance(cache, SmartCache):
            raise TypeError("cache object must be of type %s.%s", fqcn(SmartCache))
        self.__cache = cache
        
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
        
class AccountApi(object):
    def __init__(self, api, apiKey):
        self.__api = api
        self.__apiKey = apiKey
    
    def getCharacters(self):
        response = self.__api.getResponse('account/Characters.xml.aspx', self.__apiKey)
        
        charsList = []
        for char in list(response.find('result/rowset')):
            charsList.append(CharacterInfo(**char.attrib))
        return charsList
    
    def getAccountStatus(self):
        response = self.__api.getResponse('account/AccountStatus.xml.aspx', self.__apiKey)
        return AccountStatusInfo(**nodesListToDict(response))
    
    def getApiKeyInfo(self):
        response = self.__api.getResponse('account/APIKeyInfo.xml.aspx ', self.__apiKey)
        chars = []
        for char in list(response.find('result/key/rowset')):
            char.attrib['name'] = char.attrib.pop('characterName') 
            chars.append(CharacterInfo(**char.attrib))
        info = dict(response.find('result/key').attrib)
        info['characters'] = chars
        return ApiKeyInfo(**info)
    
class CharacterApi(object):
    def __init__(self, api, apiKey):
        self.__api = api
        self.__apiKey = apiKey
        
    def getSkillInTraining(self, characterID):
        reqData = self.__apiKey._asdict()
        reqData['characterID'] = characterID
        response = self.__api.getResponse('char/SkillInTraining.xml.aspx', reqData)
        try:
            isTraining = int(response.find('result/skillInTraining').text)
        except ValueError:
            raise ApiException(2000, "Unexpected value")
        return SkillInTrainingInfo(**nodesListToDict(response)) if isTraining > 0 else None
    
    def getSkillQueue(self, characterID):
        reqData = self.__apiKey._asdict()
        reqData['characterID'] = characterID
        response = self.__api.getResponse('char/SkillQueue.xml.aspx', reqData)
        queue = []
        for item in list(response.find('result/rowset')):
            queue.append(SkillQueueItem(**item.attrib))
        return sorted(queue, lambda x, y: cmp(int(x.queuePosition), int(y.queuePosition)))
    
class ApiException(Exception):
    def __init__(self, code, message):
        self.__code = code
        self.__message = message

    def __str__(self):
        return '#%s %s' % (self.__code, self.__message) 
