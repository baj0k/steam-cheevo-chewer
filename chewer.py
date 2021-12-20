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

# # Achievement class constructor
# class Achievement:
#     def __init__(self, displayname, description, unlocktime ):
#         self.displayname = displayname
#         self.description = description
#         self.unlocktime = unlocktime
    
#     def createCheevo(self):
#         print("test")

# # Game class constructor
# class Game:
#     def __init__(self, appid, name, achievement_df):
#         self.appid = appid
#         self.name = name
#         self.achievement_df = achievement_df

#     def initCheevo(self, appid):
#         print("test")

# Gets users achievements data for a specific AppID
def getCheevos(appid):
    r1 = requests.get('https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?appid=' + appid, params=reqargs)
    r1_dict= r1.json()
    r1_df = pd.DataFrame(r1_dict['playerstats']['achievements'])
    filename = "C:/tmp/" + r1_dict['playerstats']['gameName'].replace(":", "").replace(" ", "_") + ".csv"

    r2 = requests.get('https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?appid=' + appid, params=reqargs)
    r2_dict = r2.json()
    r2_df = pd.DataFrame(r2_dict['game']['availableGameStats']['achievements'])

    # Merge data from two API requests into one dataframe
    r1_df = r1_df.rename(columns = {'apiname':'name'})
    cheevos_df = pd.merge(r1_df, r2_df, how='outer', on='name')
    cheevos_df.to_csv(filename)
    return cheevos_df

# Gets list of AppIDs present in Steam user's library
r = requests.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1?include_appinfo=1', params=reqargs)
r_dict= r.json()
r_df = pd.DataFrame(r_dict['response']['games'])

appids = []
for i in r_dict['response']['games']:
    appids.append(i['name'])

# tmp dump
# appids_df = getAppids() 
# appids_df.to_csv("C:/tmp/appids.csv")

# cheevos_df = getCheevos("10180")
# cheevos_df.to_csv("C:/tmp/cheevos.csv")