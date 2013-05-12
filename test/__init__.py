from apiKeys import apiKeys
from collections import namedtuple
from eveapy.api import Api, Account
from eveapy.cache import SmartCache
import eveapy
import logging
import os

logging.basicConfig(level=logging.DEBUG)

cache = SmartCache()
impl = Api(cache)
acc = Account(impl, apiKeys['full'])

keyInfo = acc.getApiKeyInfo()
print keyInfo

status = acc.getAccountStatus()
print status

chars = acc.getCharacters()
for char in chars:
    print char

logging.shutdown()
