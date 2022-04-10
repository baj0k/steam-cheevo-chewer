# Steam-cheevo-chewer
Detects steam achievements that might have been unlocked by cheating (e.g. with Steam Achievement Manager).

How to obtain the Steam Web API Key:
https://steamcommunity.com/dev/apikey

## Usage
```
python3 chewer.py -i ID -k API_KEY [-o DEST -a APPID]
```

## TODO
- add option to specify url to user's profile instead of 64-bit steamID (If user is using a custom profile url it needs to be extracted from the source of the page because it is not present in the uri anymore)
