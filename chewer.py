#!/usr/bin/env python

from optparse import OptionParser
import pandas as pd
import requests
import json
import re
import os
import glob
import multiprocessing

# Argument parsing
parser = OptionParser(usage = "usage: %prog -i USER_ID -k API_KEY [-o DEST -a APPID]")
parser.add_option("-a", "--appid",
                action="store", dest="appid", type="string", help="Run the script against only a specific AppID instead of entire library")
parser.add_option("-i", "--id",
                action="store", dest="id", type="string", help="64-bit Steam ID")
parser.add_option("-k", "--key",
                action="store", dest="key", type="string", help="Steam Web API Key (https://steamcommunity.com/dev/apikey)")
(options, args) = parser.parse_args()

if not (options.key):
    parser.error("--key missing")

if not (options.id or options.appid):
    parser.error("--appid or --id missing. Both arguments are mandatory")

datadir = "data/" + options.id
if not (os.path.exists(datadir)):
   os.makedirs(datadir)
   os.makedirs(datadir + "/Full")
   os.makedirs(datadir + "/Sus")

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

    # Save full achievement data
    print("Processing: " + gameName)
    cheevos_df.to_csv(os.path.abspath(datadir + "/Full/" + fileName.replace(" ", "_") + ".csv"))
    cheevos_df = cheevos_df.loc[cheevos_df['achieved'] == 1]

    # Check for duplicated unlocktime values
    suspicious_df = cheevos_df[cheevos_df.duplicated(['unlocktime'], keep=False)].sort_values(by=['unlocktime', 'displayName'])
    #suspicious_df = cheevos_df[cheevos_df.duplicated(['unlocktime'], keep=False)].sort_values(by=['unlocktime'])

    if 'description' in suspicious_df.columns: 
        suspicious_df = suspicious_df[['displayName', 'unlocktime', 'description']]
    else:
        suspicious_df = suspicious_df[['displayName', 'unlocktime']]

    

    # timestamp = 1642445213
    # value = datetime.datetime.fromtimestamp(timestamp)
    # print(f"{value:%Y-%m-%d %H:%M:%S}")


    if not (suspicious_df.empty):
        suspicious_df.to_csv(os.path.abspath(datadir + "/Sus/" + fileName.replace(" ", "_") + ".csv"), header=None)

    return cheevos_df

def mergeCsv(src, dst):
    df_csv_concat = pd.concat([pd.read_csv(file) for file in glob.glob(src + '*.{}'.format('csv'))], ignore_index=True)
    df_csv_concat.to_csv(os.path.abspath(dst + "/total.csv"))
 
if __name__ == '__main__':

    # Create dataframe of AppIDs present in Steam user's library
    reqargs = {
    'steamid':options.id,
    'key':options.key
    }

    session = requests.Session()
    r = session.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1?include_appinfo=1&include_played_free_games=1', params=reqargs)
    games_df = pd.DataFrame(r.json()['response']['games']).sort_values(by=['name'])
    games_df.to_csv(datadir + '/games.csv')

    # Generate an achievement data for each AppID
    if (options.appid):
        cheevos_df = getCheevos(str(options.appid))
    else:
        with multiprocessing.Pool() as pool:
            for appid in games_df['appid']:
                cheevos_df = getCheevos(str(appid))

    mergeCsv(datadir + "/Sus/", datadir)