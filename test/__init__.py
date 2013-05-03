import eveapy

acc = eveapy.Account(eveapy.ApiKey("none", "none"))
chars = acc.getCharacters()

for char in chars:
    print char
