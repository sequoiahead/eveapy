from apiKeys import apiKeys
from collections import namedtuple
from eveapy.api import Api, AccountApi, CharacterApi
from eveapy.cache import SmartCache
import eveapy
import logging
import os

logging.basicConfig(level=logging.DEBUG)

cache = SmartCache('./resources/.cache')
impl = Api(cache)
acc = AccountApi(impl, apiKeys['full'])
chrApi = CharacterApi(impl, apiKeys['full'])

keyInfo = acc.getApiKeyInfo()
print keyInfo

status = acc.getAccountStatus()
print status

chars = acc.getCharacters()
for char in chars:
    print char


sit = chrApi.getSkillInTraining(1851172576)
print sit
sit = chrApi.getSkillInTraining(93315844)
print sit

queue = chrApi.getSkillQueue(1851172576)
print queue
queue = chrApi.getSkillQueue(93315844)
print queue

logging.shutdown()
