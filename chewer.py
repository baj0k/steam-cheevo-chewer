from optparse import OptionParser
import requests
import json
import re
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
    r1 = session.get('https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?appid=' + appid, params=reqargs)
    r1_dict= r1.json()
    
    # Checks if game offers achievements
    try:
        r1_dict['playerstats']['achievements']
    except:
        return 

    r1_df = pd.DataFrame(r1_dict['playerstats']['achievements'])
    filename = "C:/tmp/" + re.sub('[:,.!?]', '', r1_dict['playerstats']['gameName'].replace(" ", "_")) + ".csv"

    r2 = session.get('https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?appid=' + appid, params=reqargs)
    r2_dict = r2.json()
    r2_df = pd.DataFrame(r2_dict['game']['availableGameStats']['achievements'])

    # Merge data from two API requests into one dataframe
    r1_df = r1_df.rename(columns = {'apiname':'name'})
    cheevos_df = pd.merge(r1_df, r2_df, how='outer', on='name')
    cheevos_df.to_csv(filename)
    return

if __name__ == '__main__':

    # Create dataframe of AppIDs present in Steam user's library
    session = requests.Session()
    r = session.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1?include_appinfo=1', params=reqargs)
    r_dict= r.json()
    games_df = pd.DataFrame(r_dict['response']['games'])
    # tmp dump csv
    games_df.to_csv('C:/tmp/games.csv')

    # Create list of AppIDs and create achievement csv for each AppID
    appids = []
    for i in r_dict['response']['games']:
        print("Processing: " + i['name'])
        getCheevos(str(i['appid']))
        appids.append(str(i['appid']))

    
    # DEBUG
    # test = ['15080', '20900', '29800', '10190', '46560', '207490', '234740', '256410', '3910', '237530', '242550', '254000', '221100', '301480', '303390', '352130', '357290', '370510', '371670', '322330', '306040', '355150', '391070', '391420', '416080', '418070', '438180', '440760', '448780', '469730', '485330', '493700', '497050', '499420', '521230', '1058650', '1160220', '833040']
    # for line in appids:
    #     r1 = session.get('https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?appid=' + line, params=reqargs)
    #     r1_dict= r1.json()
    #     if not (r1_dict['playerstats']['success']):
    #         test.append(line)

    # print(test)

    # for line in test:
    #     df2 = (games_df[games_df['appid'] == int(line)])
    #     print(df2.name.to_string(index=False))

        
    # new_df.append(games_df[games_df['appid'] == int(test[1])])
    # new_df.to_csv('C:/tmp/nocheevos.csv')