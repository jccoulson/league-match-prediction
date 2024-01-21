import requests
import time
from bs4 import BeautifulSoup
from urllib.request import urlopen
import csv
from pathlib import Path
from urllib.parse import quote
from urllib.error import HTTPError, URLError
import sys
import re


logfile = open('riot_log.txt', 'a')

#write to logfile
def log(*content):
    for item in content:
        logfile.write(str(item) + ' ')
    logfile.write('\n')
    logfile.flush()

#put your api key here
api_key = ""

headers = {
    "X-Riot-Token": api_key
}


region = "na1"  # Replace with the appropriate region

#to limit the number of requests to riot's 100 per 2 minutes
count = 0
num_rows = 0

#keep track of matchid to not have duplicate matches
matchid_list = []
page = 1

#get three pages per rank
for i in range(40):


    random_url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/GOLD/I?page={page}"

    page = page+1

    random_response = requests.get(random_url, headers=headers)
    count = count + 1
    if random_response.status_code == 200:
        random_response = random_response.json()
    else:
        # Handle the error
        print("Error:", random_response.status_code)
        log("Error on first random match lookup:", random_response.status_code)
        time.sleep(60) #just in case disconnection sleep then move on
        continue

    for player in random_response:
        skip_flag = 0
        summoner_name = player['summonerName']
        #keep track of which summoner is printing
        print(f"writing info from {summoner_name}'s game...")
        log(f"writing info from {summoner_name}'s game...")

        #use summoner name to get puuid for later api calls
        name_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"


        # Send the GET request to the API
        name_response = requests.get(name_url, headers=headers)
        count = count + 1

        # Process the name_response
        if name_response.status_code == 200:
            name_response = name_response.json()
        elif name_response.status_code == 404:
        #    print("User no longer exists in api, moving to next user")
            log("User no longer exists in api, moving to next user")
            continue
        else:
            #print("Error:", name_response.status_code)
            log("Error:", name_response.status_code)
            time.sleep(60)
            continue


        puuid = name_response['puuid']

        #different region name for next api request
        if region == 'na1':
            general_region = 'americas'

        #get list of match ids
        id_url = f"https://{general_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked"

        id_response = requests.get(id_url, headers=headers)
        count = count+1

        # Process the name_response
        if id_response.status_code == 200:
            id_response = id_response.json()
        else:
            # Handle the error
            print("Error:", id_response.status_code)
            log("Error:", id_response.status_code)
            time.sleep(60)
            continue

        match_id = id_response[0]

        duplicate_found = 0

        #make sure no match duplicates in data
        for matchid in matchid_list:
            if matchid == match_id:
                print("Game is duplicate, moving to next")
                log("Game is duplicate, moving to next")
                duplicate_found = 1

        if duplicate_found == 1:
            continue

        matchid_list.append(match_id)

        match_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
        match_response = requests.get(match_url, headers=headers)
        count = count+1

        #add this if reaching rate limit
    #    if count > 90:
    #        print("Taking break, too many api calls...")
    #        time.sleep(20)
    #        count = 0


        # Process the name_response
        if match_response.status_code == 200:
            match_response = match_response.json()
        else:
            #print("Error:", match_response.status_code)
            log("Error:", match_response.status_code)
            time.sleep(60)
            continue


        #make list of summoner name and champ name from each team
        team1 = []
        team2 = []

        #the team we will web scrape for
        lookup_team = []

        if len(match_response["info"]["participants"]) != 10:
            #uncommon error
            #print("There was not 10 people in the api query, someone probably got banned, skipping game...")
            log("There was not 10 people in the api query, someone probably got banned, skipping game...")
            continue

        for i in range(10):

            #gets  summoner name, champ name, and team
            match_summoner = match_response["info"]["participants"][i]["summonerName"]
            match_champ = match_response["info"]["participants"][i]["championName"]
            match_team = match_response["info"]["participants"][i]["teamId"]


            #if match's summoner name is the same as original summoner assign it to original team
            if match_summoner == summoner_name:
                original_team = match_team
                game_outcome = match_response["info"]["participants"][i]["win"]


            summoner_tuple = (match_summoner,match_champ)
            if match_team == 100:
                team1.append(summoner_tuple)
            else:
                team2.append(summoner_tuple)


        if original_team == 100:
            for z in range(5):
                lookup_team.append(team1[z])
            for z in range(5):
                lookup_team.append(team2[z])
        else:
            for z in range(5):
                lookup_team.append(team2[z])
            for z in range(5):
                lookup_team.append(team1[z])



        #create csv with header if  file not created
        csv_header =['Win/Loss', 'Player1 name', 'Player1 champ name','Player1 overall wr', 'Player1 total games',
        'Player1 champ games', 'Player1 champ wr', 'Player1 kda', 'Player1 cs', 'Player1 mastery', 'Player2 name', 'Player2 champ name',
        'Player2 overall wr', 'Player2 total games','Player2 champ games','Player2 champ wr', 'Player2 kda', 'Player2 cs','Player2 mastery','Player3 name', 'Player3 champ name','Player3 overall wr', 'Player3 total games',
        'Player3 champ games','Player3 champ wr', 'Player3 kda','Player3 cs','Player3 mastery','Player4 name', 'Player4 champ name',
        'Player4 overall wr', 'Player4 total games','Player4 champ games','Player4 champ wr',
        'Player4 kda','Player4 cs','Player4 mastery','Player5 name', 'Player5 champ name', 'Player5 overall wr', 'Player5 total games',
        'Player5 champ games','Player5 champ wr', 'Player5 kda','Player5 cs','Player5 mastery', 'Player6 name', 'Player6 champ name','Player6 overall wr', 'Player6 total games',
        'Player6 champ games', 'Player6 champ wr', 'Player6 kda', 'Player6 cs', 'Player6 mastery','Player7 name', 'Player7 champ name',
        'Player7 overall wr', 'Player7 total games','Player7 champ games','Player7 champ wr',
        'Player7 kda', 'Player7 cs', 'Player7 mastery','Player8 name', 'Player8 champ name','Player8 overall wr', 'Player8 total games',
        'Player8 champ games','Player8 champ wr', 'Player8 kda','Player8 cs','Player8 mastery','Player9 name', 'Player9 champ name',
        'Player9 overall wr', 'Player9 total games','Player9 champ games','Player9 champ wr',
        'Player9 kda','Player9 cs','Player9 mastery','Player10 name', 'Player10 champ name', 'Player10 overall wr', 'Player10 total games',
        'Player10 champ games','Player10 champ wr', 'Player10 kda', 'Player10 cs', 'Player10 mastery']



        if not Path('new_gold.csv').exists():
            with open('new_gold.csv', 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(csv_header)

        #contains data for a row for the csv, store summoner name and outcome
        csv_row = []

        #if you still want whose game we are getting everyone from add back and put in header
        if game_outcome:
            game_outcome = "win"
        else:
            game_outcome = "loss"
        csv_row.append(game_outcome)

        #use beautiful soup to get info from op.gg
        for summoner in lookup_team:
            temp_sum_name = summoner[0]

            #normalize champ names
            temp_champ_name = summoner[1].replace(",", "")
            temp_champ_name = temp_champ_name.lower()
            if temp_champ_name == "monkeyking":
                temp_champ_name = "wukong"

            if temp_champ_name == "nunu":
                temp_champ_name = "nunu&willump"

            #protect against non ascii chars in url, deals with spaces too
            safe_sum_name = quote(temp_sum_name)
            site = f'https://www.u.gg/lol/profile/na1/{safe_sum_name}/champion-stats'

            #error 404 occurs when theres been a namechange recently
            try:
                html = urlopen(site)
            except HTTPError as e:
                log(f"Site won't open at {site} for {safe_sum_name}, skipping game")
                skip_flag = 1
                break
            except URLError as e:#url error
                log(f"URLerror at {site}, skipping game")
                skip_flag =1
                break

            soup = BeautifulSoup(html, 'lxml')

            #find info needed in soup
            op_wr = soup.find_all(class_= "champion-rates")
            op_names = soup.find_all(class_= "champion-name")
            op_kda = soup.find_all(class_="kda")
            op_cs = soup.find_all(class_="cs-cell")


            #find out what index champ is in list to get more data from later
            champ_index = 0
            #bool to see if they are first timing
            champ_found = 0
            cs = 0
            champ_mastery = 0
            #find location of their statistics on champ
            for op_champ_name in op_names:
                #put opgg champ names in same form
                op_champ_name = op_champ_name.text.replace("'", "")
                op_champ_name = op_champ_name.replace(" ","")
                op_champ_name = op_champ_name.replace(".","")
                op_champ_name = op_champ_name.lower()

                if(op_champ_name == "nunu&willump"):
                    op_champ_name == "nunu"
                if op_champ_name == temp_champ_name:
                    champ_found = 1
                    break

                champ_index = champ_index + 1

            if champ_found == 1:
                #finding winrate of champ
                winrate_text = op_wr[champ_index].text

                #extract wr
                winrate_match = re.search(r'(\d+)%', winrate_text)
                champ_winrate = winrate_match.group(1)

                #extract total games
                games_match = re.search(r'(\d+)W (\d+)L', winrate_text)
                champ_wins = games_match.group(1)
                champ_losses = games_match.group(2)
                total_champ_games = int(champ_wins) + int(champ_losses)

                #find kda of champ
                kda_text = op_kda[champ_index].text
                index = kda_text.find(" ")
                kda = kda_text[:index]

                #getting cs of champ
                #need to index by one because first output is "CS"
                cs = op_cs[champ_index+1].text

                #look for overall winrate
                site = f'https://u.gg/lol/profile/na1/{safe_sum_name}/overview'
                try:
                    html = urlopen(site)
                except HTTPError as e:
                    log(f"Site won't open at {site} for {safe_sum_name}, skipping game")
                    skip_flag = 1
                    break
                except URLError as e:#url error
                    log(f"URL error, Site won't open at {site} for {safe_sum_name}, skipping game")
                    skip_flag = 1
                    break
                soup = BeautifulSoup(html, 'lxml')
                op_totals = soup.find(class_= "rank-wins")


                if op_totals is not None:
                    total_text = op_totals.text
                    #find total games
                    total_games = re.findall(r'\d+', total_text)
                    total_games = int(total_games[0]) + int(total_games[1])

                    #extract wr
                    total_wr = re.findall(r'\d+%', total_text)
                    total_wr = int(total_wr[0].strip('%'))
                else:
                    total_games = "None_unranked"
                    total_wr = "None_unranked"
            elif champ_found == 0:
                total_wr = "None"
                total_games = "None"
                total_champ_games= "None"
                champ_winrate = "None"
                kda = "None"
##Mastery code goes here if using

            #if first timing champ store as none_champname
            #'Player1 name', 'Player1 champ name','Player1 overall wr', 'Player1 total games',
            #'Player1 champ games', 'Player1 wr', 'Player1 cs', 'Player1 kda', 'Player1 mastery'
            #add to list for row
            csv_row.append(temp_sum_name)
            csv_row.append(temp_champ_name)
            csv_row.append(total_wr)
            csv_row.append(total_games)
            csv_row.append(total_champ_games)
            csv_row.append(champ_winrate)
            csv_row.append(kda)
            csv_row.append(cs)
            csv_row.append("ng")

        if skip_flag == 1:
            continue

        num_rows = num_rows +1;
        if num_rows%10 == 0:
            log(f"There are {num_rows} rows in csv")

        log(f"Current page of ranked league is {page-1}")

        #write data to csv
        with open('new_gold.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(csv_row)
