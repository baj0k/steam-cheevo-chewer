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

# Gets users achievements data for a specific AppID
def getCheevos(appid):
    r1 = session.get('https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?appid=' + appid, params=reqargs)
    
    # Checks if game offers achievements
    try:
        r1.json()['playerstats']['achievements']
    except:
        return 
    r1_df = pd.DataFrame(r1.json()['playerstats']['achievements'])

    r2 = session.get('https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?appid=' + appid, params=reqargs)
    r2_df = pd.DataFrame(r2.json()['game']['availableGameStats']['achievements'])

    # Merge data from two API requests into one dataframe
    r1_df = r1_df.rename(columns = {'apiname':'name'})
    cheevos_df = pd.merge(r1_df, r2_df, how='outer', on='name')

    # Dump csv file
    filename = "C:/tmp/" + re.sub('[:,.!?]', '', r1.json()['playerstats']['gameName'].replace(" ", "_")) + ".csv"
    cheevos_df.to_csv(filename)
    return


if __name__ == '__main__':

    # Create dataframe of AppIDs present in Steam user's library
    session = requests.Session()
    r = session.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1?include_appinfo=1', params=reqargs)
    games_df = pd.DataFrame(r.json()['response']['games'])
    games_df.to_csv('C:/tmp/!games.csv')

    # Generate an achievement data for each AppID
    for appid in games_df['appid']:
        getCheevos(str(appid))