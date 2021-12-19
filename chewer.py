from optparse import OptionParser
import requests
import json
import pandas as pd

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

class Achievement:
    def __init__(self, displayname, description, unlocktime ):
        self.displayname = displayname
        self.description = description
        self.unlocktime = unlocktime
    
    def createCheevo(self):
        print("test")

class Game:
    def __init__(self, appid, name, achievements):
        self.appid = appid
        self.name = name
        self.achievements = achievements

# cheevo1 = Achievement("", "")
# print(cheevo1.id)
# print(cheevo1.name) 

# Get a list of AppIDs of games added to Steam user's library
def getAppids():
    r = requests.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1?include_appinfo=1', params=reqargs)
    r_dict= r.json()
    r_df = pd.DataFrame(r_dict['response']['games'])
    return r_df

# Get list of users achievements for an AppID
def getCheevos(appid):
    r = requests.get('https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?appid=' + appid, params=reqargs)
    r_dict= r.json()
    r_df = pd.DataFrame(r_dict['playerstats']['achievements'])
    return r_df

# Get list of achievements metadata for an AppID
def getCheevosData(appid):
    r = requests.get('https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?appid=' + appid, params=reqargs)
    r_dict = r.json()
    r_df = pd.DataFrame(r_dict['game']['availableGameStats']['achievements'])
    return r_df

# Merge achievements metadata with users achievements stats
def mergeCheevosFrames(cheevos_df, cheevosData_df):
    cheevos_df = cheevos_df.rename(columns = {'apiname':'name'})
    cheevos_df = pd.merge(cheevos_df, cheevosData_df, how='outer', on='name')
    print(cheevos_df)
    return cheevos_df


# Main execution
appids_df = getAppids()
cheevosList_df = getCheevos("10180")
cheevosData_df = getCheevosData("10180")
# print(appids_df)
# print(cheevosList_df)
# print(cheevosData_df)

# cheevosList_df.rename(columns = {'apiname':'name'})
# print(cheevosList_df)

mergeCheevosFrames(cheevosList_df, cheevosData_df)

# Write AppID list to a file
f = open("C:/tmp/appids.txt", "w")
for line in appids_df:
    f.write(line + "\n")
f.close()

# Write achievement list to a file
f = open("C:/tmp/cheevos.txt", "w")
for line in cheevosList_df:
    f.write(str(line) + "\n")
f.close()

# Write achievement data to a file
f = open("C:/tmp/cheevosData.txt", "w")
for line in cheevosData_df:
    f.write(str(line) + "\n")
f.close()

#open and read the file after the appending:
# f = open("demofile3.txt", "r")
# print(f.read()) 








# for i in appids:
#     getCheevos(str(i))
