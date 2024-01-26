# LeaguePred
This project predicts the outcome of a League of Legends game by analyzing player statistics. The steps involved in the project are data collection with RIOT API and web scraping, data cleaning, exploratory data analysis, and machine learning with random forest to predict outcome of games. The model is integrated into a Django web application making it possible look up live game participants and display odds on their chance of winning.

## Project Components
- 1 csv of preclean diamond data
- 3 csvs of cleaned data
- Data Collection(`data_collection.py`)
  - Uses the RIOT API and web scraping via Python's Beautiful Soup, collects random game statistics and player data in those games and saves as csv
- Data Cleaning and Exploratory Data Analysis(`league_eda.Rmd`)
  - Processes and cleans the collected data. Fills out missing values and does exploratory data analysis with visualizations. Outputs cleaned data to csv
- Prediction Model (`league_model.py`)
  - Uses scikit-learn Random Forest algorithm and predicts outcome based on player statistics and features from the cleaned data
- Web Application (`/leaguepred_website`)
  - web applciation built with Django, integrates the prediction model and allows users to look up a player and displays odds of winning and basic game information

Due to the large update Riot Games did with account name changes implemented after the website went live, the website does not work for any user that is not with a name with the default #na1
Check the finished website with http://LeaguePred.net


## Dependencies

- R>=4.3.2
- Django>=3.0.9
- scikit-learn>=1.2.2
- joblib>=1.2.0
- requests>=2.22.0
- beautifulsoup4>=4.11.2
- numpy>=1.24.2
- pandas>=1.5.3
- gunicorn
- whitenoise
- lxml
- Rstudio


## Running Django project locally
To run locally add api key in views.py

- Run server locally `python manage.py runserver`
- Access at `http://127.0.0.1:8000/`

## Run data collection script
Add api key to be able to run
- `python data_collection.py`

## Run model creation

- `python capstone_model.py`
