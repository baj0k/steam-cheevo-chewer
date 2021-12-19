from optparse import OptionParser
import requests
import json

parser = OptionParser(usage = "usage: %prog -i ID -k KEY")
parser.add_option("-i", "--id",
                action="store", dest="id", help="64-bit Steam ID")
parser.add_option("-k", "--key",
                action="store", dest="key", help="Steam Web API Key (https://steamcommunity.com/dev/apikey)")
(options, args) = parser.parse_args()

if not ( options.id and options.key):
    parser.error("Both arguments are mandatory")

reqargs = {
'steamid':options.id,
'key':options.key
}

def getAppids():
    r = requests.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001?include_appinfo=1', params=reqargs)
    r_dict= r.json()
    appids = []

    for i in r_dict['response']['games']:
        appids.append(i['appid'])
    return appids

def getCheevos(appid):
    r = requests.get('https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid=' + appid, params=reqargs)
    r_dict= r.json()
    cheevos = []

    for i in r_dict['playerstats']['achievements']:
        # cheevos.append(i['apiname'])
        cheevos.append(i)
    return cheevos

appids = getAppids()
# print(appids)

cheevos = getCheevos("440")

print(cheevos)

# print(cheevos)


# for i in appids:
#     getCheevos(str(i))
