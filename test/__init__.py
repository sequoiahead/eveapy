from apiKeys import apiKeys
from eveapy import api

acc = api.Account(apiKeys['full'])
chars = acc.getCharacters()

for char in chars:
    print char
