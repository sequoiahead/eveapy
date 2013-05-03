from eveapy.impl import ApiImpl

class ApiKey:
    def __init__(self, keyID, verCode):
        self.keyID = keyID
        self.verCode = verCode

class Account:
    def __init__(self, apiKey):
        self._charsList = [];
        self._apiImpl = ApiImpl()
        
        chars = self._apiImpl.charactersList(apiKey)
        
        for char in chars:
            self._charsList.append(Character(**char.attrib))
            
    def getCharacters(self):
        return self._charsList     
    
class Character:
    def __init__(self, characterID, name, corporationName, corporationID):
        self.id = characterID
        self.name = name
        self.corpName = corporationName
        self.corpID = corporationID
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return self.name