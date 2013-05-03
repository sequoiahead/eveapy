import urllib2, urllib
import xml.etree.ElementTree as et

class ApiImpl:    
    def charactersList(self, apiKey):
        req = urllib2.Request('https://api.eveonline.com/account/characters.xml.aspx')
        req.add_data(urllib.urlencode({'keyID':apiKey.keyID, 'vCode':apiKey.verCode}))
        
        rawResponse = urllib2.urlopen(req).read()
        
        response = et.fromstring(rawResponse)        
        return list(response.find('result/rowset'))