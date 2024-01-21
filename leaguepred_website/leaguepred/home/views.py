from django.shortcuts import render
from .apps import HomeConfig
import joblib
from urllib.parse import quote
from urllib.error import HTTPError, URLError
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from .champids import champ_dict #mapping ids to champ name
import numpy as np
import re
import pandas as pd


def replace_second_dot(s):
    s = s[::-1]
    s = s.replace('.', '', 1)
    return s[::-1]

def get_team_info(team_champ_wr, team_champ_kda, team_champs, team_names, region):
    for i in range(5):
        #convert champid to champ name
        temp_champ_name = champ_dict[team_champs[i]][0]
        temp_champ_name = temp_champ_name.replace(",", "")
        temp_champ_name = temp_champ_name.lower()

        #wukong and nunu have mismatch names from riot api to u.gg
        if temp_champ_name == "monkeyking":
            temp_champ_name = "wukong"
        if temp_champ_name == "nunu":
            temp_champ_name = "nunu&willump"


        safe_sum_name = quote(team_names[i])
        #open u.gg for individual statistics
        site = f'https://www.u.gg/lol/profile/{region}/{safe_sum_name}/champion-stats'
        try:
            html = urlopen(site)
        except HTTPError as e: #maybe display something on page if someone has to be skipped
            continue
        except URLError as e:
            continue
        except Exception as e:
            continue

        soup = BeautifulSoup(html, 'lxml')

        #find info needed in soup
        gg_wr = soup.find_all(class_= "champion-rates")
        gg_names = soup.find_all(class_= "champion-name")
        gg_kda = soup.find_all(class_="kda")


        champ_index = 0
        champ_found = 0

        #find index of their statistics on champ
        for gg_champ_name in gg_names:
            #put ugg champ names in same form
            gg_champ_name = gg_champ_name.text.replace("'", "")
            gg_champ_name = gg_champ_name.replace(" ","")
            gg_champ_name = gg_champ_name.lower()

            if gg_champ_name == temp_champ_name:
                champ_found = 1
                break
            champ_index = champ_index + 1

        if champ_found == 1:
            #get champ winrate
            winrate_text = gg_wr[champ_index].text
            winrate_match = re.search(r'(\d+)%', winrate_text)
            champ_winrate = winrate_match.group(1)

            #get champ kda
            kda_text = gg_kda[champ_index].text
            index = kda_text.find(" ")
            champ_kda = kda_text[:index]

            team_champ_wr[i] = champ_winrate
            team_champ_kda[i] = champ_kda


def home(request):
    return render(request, 'home/home.html')

def search_results(request):
    ##Put api key here
    api_key = ""

    #get rid of leading and trailing whitespace
    summoner_name = request.GET.get('q', '').strip()

    #make sure they entered something into search
    if not summoner_name:
        return render(request, 'home/home.html', {'error': 'Please enter a user to search'})

    region = request.GET.get('region', '').strip()

    #make sure they entered region
    if not region:
        return render(request, 'home/home.html', {'error': 'Please enter a region to search'})

    headers = {
        "X-Riot-Token": api_key
    }

    #make it safe with special chars and other things
    safe_summoner_name = quote(summoner_name)

    #search for more summoner info based on name
    summoner_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{safe_summoner_name}"
    summoner_response = requests.get(summoner_url, headers=headers)

    #Render different webpage if they cant be found
    if summoner_response.status_code == 200:
        summoner_response = summoner_response.json()
    elif summoner_response.status_code == 404:
        return render(request,  'home/home.html', {'error': 'Cannot find user'})
    else:
        return render(request,  'home/home.html', {'error': 'Cannot find user'})

    #grab id from json object
    encrypted_id = summoner_response['id']

    #lookup live game based on id
    live_url = f"https://{region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{encrypted_id}"
    live_response = requests.get(live_url, headers=headers)


    #Render different webpage if they cant be found
    #there is error when user exists but not currently in a game
    if live_response.status_code == 200:
        live_response = live_response.json()
    elif live_response.status_code == 404:
        return render(request, 'home/home.html', {'error' : "User is not in live game"})
    else: #THEIR GAME CANT BE FOUND BECAUSE NOT IN LIVE GAME
        return render(request,  'home/home.html', {'error' : "User is not in live game"})

    #initialse vars for data on game
    enemy_names = []
    enemy_champs = []
    team_names = []
    team_champs = []
    team_images = []
    enemy_images = []
    team_id = None

    summoner_name = summoner_name.lower()

    #find out which team the user looked up is on
    for i in range(10):
        check_name = live_response["participants"][i]["summonerName"].lower()
        if check_name == summoner_name:
            team_id = live_response["participants"][i]["teamId"]

    #star assigning to ally or enemy arrays based on which team original player was on
    for i in range(10):
        champ_id = live_response["participants"][i]["championId"]
        if team_id == live_response["participants"][i]["teamId"]:
            team_names.append(live_response["participants"][i]["summonerName"])
            team_champs.append(champ_id)
            team_images.append(champ_dict[champ_id][1])
        else:
            enemy_names.append(live_response["participants"][i]["summonerName"])
            enemy_champs.append(champ_id)
            enemy_images.append(champ_dict[champ_id][1])

    #set defaults for if no info
    team_champ_wr = [50]*5
    enemy_champ_wr = [50]*5

    #need to be string because kda is given in string form from ugg
    team_champ_kda = ['0']*5
    enemy_champ_kda = ['0']*5

    #get ugg statistics with function call
    get_team_info(team_champ_wr, team_champ_kda, team_champs, team_names, region)
    get_team_info(enemy_champ_wr, enemy_champ_kda, enemy_champs, enemy_names, region)

    ##clean up ally player data
    #kda from website has two dots, need to remove second one for array
    team_champ_kda = [replace_second_dot(s) for s in team_champ_kda]

    #exact kda's have Perfect in front
    team_champ_kda = [s.replace('Perfect', '') for s in team_champ_kda]
    np_team_champ_wr = np.array(team_champ_wr)
    np_team_champ_kda = np.array(team_champ_kda)

    np_team_champ_wr = np_team_champ_wr.astype(int)
    np_team_champ_kda = np_team_champ_kda.astype(float)

    ##clean up enemy player data
    enemy_champ_kda = [replace_second_dot(s) for s in enemy_champ_kda]

    #exact kda's have Perfect in front
    enemy_champ_kda = [s.replace('Perfect', '') for s in enemy_champ_kda]
    np_enemy_champ_wr = np.array(enemy_champ_wr)
    np_enemy_champ_kda = np.array(enemy_champ_kda)

    #change from to int and float
    np_enemy_champ_wr = np_enemy_champ_wr.astype(int)
    np_enemy_champ_kda = np_enemy_champ_kda.astype(float)


    #calculate mean and std of kda and champ wr
    team_champ_wr_mean = np.mean(np_team_champ_wr)
    team_champ_kda_mean = np.mean(np_team_champ_kda)
    team_champ_wr_std = np.std(np_team_champ_wr)
    team_champ_kda_std = np.std(np_team_champ_kda)

    #calculate mean and std of kda and champ wr
    enemy_champ_wr_mean = np.mean(np_enemy_champ_wr)
    enemy_champ_kda_mean = np.mean(np_enemy_champ_kda)
    enemy_champ_wr_std = np.std(np_enemy_champ_wr)
    enemy_champ_kda_std = np.std(np_enemy_champ_kda)


    #convert to dataframe to match original model
    #need to match exact names and order of original model
    X_df = pd.DataFrame({
        'avg_ally_champ_wr': [team_champ_wr_mean],
        'avg_ally_kda': [team_champ_kda_mean],
        'avg_enemy_champ_wr': [enemy_champ_wr_mean],
        'avg_enemy_kda': [enemy_champ_kda_mean],
        'std_ally_champ_wr': [team_champ_wr_std],
        'std_ally_kda': [team_champ_kda_std],
        'std_enemy_champ_wr': [enemy_champ_wr_std],
        'std_enemy_kda': [enemy_champ_kda_std]
    })

    #load in model from resources
    rf_model = HomeConfig.model

    # Use the model to predict the outcome
    game_outcome = rf_model.predict(X_df)
    outcome_probability = rf_model.predict_proba(X_df)


    #[0][0] contains odds to lose, [0][1] contains odds to win
    if game_outcome == 'win':
        outcome_odds = outcome_probability[0][1]
    else:
        outcome_odds = outcome_probability[0][0]

    #turn from decimal to % format e.g. 75%
    outcome_odds = int(round(float(outcome_odds), 2) * 100)

    #store whether was win or loss
    game_outcome = game_outcome[0]

    #round champion winrates
    rounded_team_wr_array = np.round(np_team_champ_wr, 2)
    rounded_enemy_wr_array = np.round(np_enemy_champ_wr, 2)

    context = {
        'outcome_odds': outcome_odds,
        'game_outcome': game_outcome,
        'player1_wr': rounded_team_wr_array[0],
        'player2_wr': rounded_team_wr_array[1],
        'player3_wr': rounded_team_wr_array[2],
        'player4_wr': rounded_team_wr_array[3],
        'player5_wr': rounded_team_wr_array[4],
        'player6_wr': rounded_enemy_wr_array[0],
        'player7_wr': rounded_enemy_wr_array[1],
        'player8_wr': rounded_enemy_wr_array[2],
        'player9_wr': rounded_enemy_wr_array[3],
        'player10_wr': rounded_enemy_wr_array[4],
        'player1_name': team_names[0],
        'player2_name': team_names[1],
        'player3_name': team_names[2],
        'player4_name': team_names[3],
        'player5_name': team_names[4],
        'player6_name': enemy_names[0],
        'player7_name': enemy_names[1],
        'player8_name': enemy_names[2],
        'player9_name': enemy_names[3],
        'player10_name': enemy_names[4],
        'player1_image': "images/"+team_images[0],
        'player2_image': "images/"+team_images[1],
        'player3_image': "images/"+team_images[2],
        'player4_image': "images/"+team_images[3],
        'player5_image': "images/"+team_images[4],
        'player6_image': "images/"+enemy_images[0],
        'player7_image': "images/"+enemy_images[1],
        'player8_image': "images/"+enemy_images[2],
        'player9_image': "images/"+enemy_images[3],
        'player10_image': "images/"+enemy_images[4],
    }
    return render(request, 'home/results.html', context)
