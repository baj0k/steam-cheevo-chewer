from optparse import OptionParser
import pandas as pd
import requests
import json
import re
import os

# Argument parsing
parser = OptionParser(usage = "usage: %prog -i ID -k KEY -o DEST")
parser.add_option("-i", "--id",
                action="store", dest="id", help="64-bit Steam ID")
parser.add_option("-k", "--key",
                action="store", dest="key", help="Steam Web API Key (https://steamcommunity.com/dev/apikey)")
parser.add_option("-o", "--output",
                action="store", dest="destination", help="Write output files to the folder specified. The default is /tmp")
(options, args) = parser.parse_args()

if not (options.id and options.key):
    parser.error("You need to specify both the Steam Web API key and Steam user 64-bit ID")

if not (options.destination):
    options.destination = "/tmp"

reqargs = {
'steamid':options.id,
'key':options.key
}

# Get user's achievements data for a specific AppID
def getCheevos(appid):
    r1 = session.get('https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?appid=' + appid, params=reqargs)
    
    # Check if game offers achievements
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
    filename = os.path.abspath(options.destination + '/' + re.sub('[:,.!?]', '', r1.json()['playerstats']['gameName'].replace(" ", "_")) + ".csv")
    print("Processing: " + filename)
    cheevos_df.to_csv(filename)
    return cheevos_df


if __name__ == '__main__':

    # Create dataframe of AppIDs present in Steam user's library
    session = requests.Session()
    r = session.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1?include_appinfo=1', params=reqargs)
    games_df = pd.DataFrame(r.json()['response']['games'])
    games_df.to_csv(options.destination + '/' + 'games.csv')

    # Generate an achievement data for each AppID
    # for appid in games_df['appid']:
    #     cheevos_df = getCheevos(str(appid))



    full_cheevos_df = getCheevos(str("10180"))
    # partfull_cheevos_df = getCheevos(str("311690"))
    # empty_cheevos_df = getCheevos(str("507490"))

    full_achieved_df = full_cheevos_df.loc[full_cheevos_df['achieved'] == 1]
    # partfull_achieved_df = partfull_cheevos_df.loc[partfull_cheevos_df['achieved'] == 1]
    # empty_achieved_df = empty_cheevos_df.loc[empty_cheevos_df['achieved'] == 1]

    
    # print(full_achieved_df)
    # print(partfull_achieved_df)
    # print(empty_achieved_df)

    # print(achieved_df.duplicated(subset=['unlocktime']).to_csv(index=False))

    full_test_df = full_achieved_df.duplicated(subset=['unlocktime']).to_csv(index=False)
    # partfull_test_df = partfull_achieved_df.duplicated(subset=['unlocktime'])
    # empty_test_df = empty_achieved_df.duplicated(subset=['unlocktime']).to_csv(index=False)

    print(full_test_df)
    # print(partfull_test_df)
    # print(empty_test_df)
    


    # for row in cheevos_df:
    #     if (cheevos_df)
    #     print(row)
        
    #     if (row['achieved'])
    # print(cheevos_df['achieved'].to_csv(index=False))

