# LeaguePred
This project predicts the outcome of a League of Legends game by analyzing player statistics. The steps involved in the project are data collection with RIOT API and web scraping, data cleaning, exploratory data analysis, and machine learning with random forest to predict outcome of games. The model is integrated into a Django web application making it possible look up live game participants and display odds on their chance of winning.

## Project Components
- 1 csv of preclean diamond data
- 1 csv of diamond team statistics data
- 3 csvs of cleaned data
- Data Collection(`data_collection.py`)
  - Uses the RIOT API and web scraping via Python's Beautiful Soup, collects random game statistics and player data in those games and saves as csv
- Data Cleaning and Exploratory Data Analysis(`league_eda.Rmd`)
  - Processes and cleans the collected data. Fills out missing values and does exploratory data analysis with visualizations. Outputs cleaned data to csv
- Prediction Model (`league_model.py`)
  - Uses scikit-learn Random Forest algorithm and predicts outcome based on player statistics and features from the cleaned data
- Web Application (`/leaguepred_website`)
  - web applciation built with Django, integrates the prediction model and allows users to look up a player and displays odds of winning and basic game information

The LeaguePred web application http://LeaguePred.net is now deprecated. Riot has made changes drastic to their naming conventions and the website has been taken down and has to be updated to be deployed again.

## Images
### Density plot of all champion winrates
![image](https://github.com/jccoulson/match-prediction/assets/28967794/b82002b2-a6e1-4aae-b682-48458d0f4209)

### t-SNE plot to visualize high dimensional feature space to predict win or loss in 2 dimensions
![image](https://github.com/jccoulson/match-prediction/assets/28967794/fa74fad2-9bd7-47c1-bd38-7a07cb25081e)

### Web application predicting game outcome for user
![image](https://github.com/jccoulson/match-prediction/assets/28967794/638060a7-005c-48c2-abd3-311e8d14354c)


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

## Images

