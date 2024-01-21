## LeaguePred
All files involved in the creation of the LeaguePred website:
- 1 csv of preclean diamond data
- 3 csvs of cleaned data
- `data_collect.py` file for collection of data
- `league_model.py` file for creation of model
- `leaguepred_website` folder for Django web application
- `league_eda.Rmd` file for exploratory data analysis and csv cleanup

Due to the large update Riot Games did with account name changes implemented after the website went live, the website does not work for any user that is not with a name with the default #na1
Check the finished website with http://LeaguePred.net


## Dependencies

- R==4.3.2
- Django==3.0.9
- scikit-learn==1.2.2
- joblib==1.2.0
- requests==2.22.0
- beautifulsoup4==4.11.2
- numpy==1.24.2
- pandas==1.5.3
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
