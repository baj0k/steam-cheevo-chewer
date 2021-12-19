from optparse import OptionParser
import requests
import json

# Argument parsing
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



# Get a list of AppIDs of games added to Steam user's library
def getAppids():
    r = requests.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1?include_appinfo=1', params=reqargs)
    r_dict= r.json()
    appids = []

    for i in r_dict['response']['games']:
        appids.append(i['name'] + ", " + str(i['appid']))
    return appids

# Get achievement list for an AppID
def getCheevos(appid):
    r = requests.get('https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?appid=' + appid, params=reqargs)
    r_dict= r.json()
    cheevos = []

    for i in r_dict['playerstats']['achievements']:
        # cheevos.append(i['apiname'])
        cheevos.append(i)
    return cheevos

# Main execution
appids = getAppids()
cheevos = getCheevos("440")
# print(appids)
# print(cheevos)

# Write AppID list to a file
f = open("C:/tmp/appids.txt", "w")
for line in appids:
    f.write(line + "\n")
f.close()

# Write achievement list to a file
f = open("C:/tmp/cheevos.txt", "w")
for line in cheevos:
    f.write(str(line) + "\n")
f.close()

#open and read the file after the appending:
# f = open("demofile3.txt", "r")
# print(f.read()) 








# for i in appids:
#     getCheevos(str(i))
