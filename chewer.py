#!/usr/bin/env python

from optparse import OptionParser
import pandas as pd
import requests
import json
import re
import os

# Argument parsing
parser = OptionParser(usage = "usage: %prog -i ID -k KEY -o DEST")
parser.add_option("-a", "--appid",
                action="store", dest="appid", type="string", help="Run the script against only a specific AppID instead of entire library")
parser.add_option("-i", "--id",
                action="store", dest="id", type="string", help="64-bit Steam ID")
parser.add_option("-k", "--key",
                action="store", dest="key", type="string", help="Steam Web API Key (https://steamcommunity.com/dev/apikey)")
parser.add_option("-o", "--output",
                action="store", dest="destination", type="string", help="Write output files to the folder specified. The default is /tmp")
(options, args) = parser.parse_args()

if not (options.key):
    parser.error("--key missing")

if not (options.id or options.appid):
    parser.error("--appid or --id missing. You need to specify either of these")

if not (options.destination):
   options.destination = "/tmp/cheevos"

if not (os.path.exists(options.destination + "/cache/")):
   os.makedirs(options.destination + "/cache/")

# Get user's achievements data for a specific AppID
def getCheevos(appid):
    r1 = session.get('https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?appid=' + appid, params=reqargs)
    
    # Check if game offers achievements
    try:
        r1.json()['playerstats']['achievements']
    except:
        return 

    gameName = re.sub('[^a-zA-Z0-9 \n]', '', r1.json()['playerstats']['gameName'])
    fileName = gameName + "-" + appid

    r1_df = pd.DataFrame(r1.json()['playerstats']['achievements'])
    r2 = session.get('https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?appid=' + appid, params=reqargs)
    r2_df = pd.DataFrame(r2.json()['game']['availableGameStats']['achievements'])

    # Merge data from two API requests into one dataframe
    r1_df = r1_df.rename(columns = {'apiname':'name'})
    cheevos_df = pd.merge(r1_df, r2_df, how='outer', on='name')

    # Cache all achievement data
    print("Processing: " + gameName)
    cheevos_df.to_csv(os.path.abspath(options.destination + '/cache/' + "Full_" + fileName.replace(" ", "_") + ".csv"))
    cheevos_df = cheevos_df.loc[cheevos_df['achieved'] == 1]

    # Check for duplicated unlocktime values
    suspicious_df = cheevos_df[cheevos_df.duplicated(['unlocktime'], keep=False)].sort_values(by=['unlocktime', 'displayName'])
    #suspicious_df = cheevos_df[cheevos_df.duplicated(['unlocktime'], keep=False)].sort_values(by=['unlocktime'])

    if 'description' in suspicious_df.columns: 
        suspicious_df = suspicious_df[['displayName', 'unlocktime', 'description']]
    else:
        suspicious_df = suspicious_df[['displayName', 'unlocktime']]

    if not (suspicious_df.empty):
        suspicious_df.to_csv(os.path.abspath(options.destination + "/" + fileName.replace(" ", "_") + ".csv"), header=None)

    return cheevos_df

if __name__ == '__main__':

    # Create dataframe of AppIDs present in Steam user's library
    reqargs = {
    'steamid':options.id,
    'key':options.key
    }

    session = requests.Session()
    r = session.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1?include_appinfo=1&include_played_free_games=1', params=reqargs)
    games_df = pd.DataFrame(r.json()['response']['games']).sort_values(by=['name'])
    games_df.to_csv(options.destination + '/' + '!games.csv')

    # Generate an achievement data for each AppID
    if (options.appid):
        cheevos_df = getCheevos(str(options.appid))
    else:
        for appid in games_df['appid']:
            cheevos_df = getCheevos(str(appid))
