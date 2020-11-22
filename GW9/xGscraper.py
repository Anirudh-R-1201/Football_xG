import numpy as np 
import pandas as pd 
import requests 
import json
from bs4 import BeautifulSoup

base_url = 'https://understat.com/league' 
leagues = ['La_liga', 'EPL', 'Bundesliga', 'Serie_A', 'Ligue_1', 'RFPL'] 
seasons = ['2014', '2015', '2016', '2017', '2018', '2019']

#Starting with 2017/18 data for the Prem, cuz I'm a Man Utd fan 
url = base_url+'/'+leagues[1]+'/'+seasons[3] 
res = requests.get(url) 

soup = BeautifulSoup(res.content, "lxml")
scripts = soup.find_all('script')

#get only JSON data 
ind_start = string_with_json_obj.index("('")+2 
ind_end = string_with_json_obj.index("')") 
json_data = string_with_json_obj[ind_start:ind_end] 
json_data = json_data.encode('utf8').decode('unicode_escape')

#3 dictionaries present in data: id, title and history

# Get teams and their relevant ids  
teams = {} 
for id in data.keys(): 
    teams[id] = data[id]['title']


values = [] 
for id in data.keys(): 
    columns = list(data[id]['history'][0].keys()) 
    values = list(data[id]['history'][0].values()) 
    break

dataframes = {} 
for id, team in teams.items(): 
    teams_data = [] 
    for row in data[id]['history']:
        teams_data.append(list(row.values())) 
    df = pd.DataFrame(teams_data, columns=columns) 
    dataframes[team] = df 
    print('Added data for{}.'.format(team))


#for ppda and oppda coeff removal
for team, df in dataframes.items(): 
    dataframes[team]['ppda_coef'] = dataframes[team]['ppda'].apply(lambda x: x['att']/x['def'] if x['def'] != 0 else 0)
    dataframes[team]['oppda_coef'] = dataframes[team]['ppda_allowed'].apply(lambda x: x['att']/x['def'] if x['def'] != 0 else 0)


cols_to_sum = ['xG', 'xGA', 'npxG', 'npxGA', 'deep', 'deep_allowed', 'scored', 'missed', 'xpts', 'wins', 'draws', 'loses', 'pts', 'npxGD'] 
cols_to_mean = ['ppda_coef', 'oppda_coef']


frames = [] 
for team, df in dataframes.items(): 
    sum_data = pd.DataFrame(df[cols_to_sum].sum()).transpose()
    mean_data = pd.DataFrame(df[cols_to_mean].mean()).transpose()
    final_df = sum_data.join(mean_data) 
    final_df['team'] = team
    final_df['matches'] = len(df) 
    frames.append(final_df) full_stat = pd.concat(frames)


#reorder table
full_stat = full_stat[['team', 'matches', 'wins', 'draws', 'loses', 'scored', 'missed', 'pts', 'xG', 'npxG', 'xGA', 'npxGA', 'npxGD', 'ppda_coef', 'oppda_coef', 'deep', 'deep_allowed', 'xpts']]
full_stat.sort_values('pts', ascending=False, inplace=True)
full_stat.reset_index(inplace=True, drop=True)
full_stat['position'] = range(1,len(full_stat)+1)
full_stat['xG_diff'] = full_stat['xG'] - full_stat['scored'] 
full_stat['xGA_diff'] = full_stat['xGA'] - full_stat['missed'] 
full_stat['xpts_diff'] = full_stat['xpts'] - full_stat['pts']

cols_to_int = ['wins', 'draws', 'loses', 'scored', 'missed', 'pts', 'deep', 'deep_allowed'] 
full_stat[cols_to_int] = full_stat[cols_to_int].astype(int)

col_order = ['position','team', 'matches', 'wins', 'draws', 'loses', 'scored', 'missed', 'pts', 'xG', 'xG_diff', 'npxG', 'xGA', 'xGA_diff', 'npxGA', 'npxGD', 'ppda_coef', 'oppda_coef', 'deep', 'deep_allowed', 'xpts', 'xpts_diff'] 
full_stat = full_stat[col_order] 
full_stat.columns = ['#', 'team', 'M', 'W', 'D', 'L', 'G', 'GA', 'PTS', 'xG', 'xG_diff', 'NPxG', 'xGA', 'xGA_diff', 'NPxGA', 'NPxGD', 'PPDA', 'OPPDA', 'DC', 'ODC', 'xPTS', 'xPTS_diff'] 
pd.options.display.float_format = '{:,.2f}'.format full_stat.head(10)