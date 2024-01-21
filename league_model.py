import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score, GridSearchCV
import joblib
import numpy as np

def calculate_team_data(calc_df):
    calc_df['avg_ally_champ_wr'] = calc_df[[f'Player{i}.champ.wr.adjusted' for i in range(1, 6)]].mean(axis=1)
    calc_df['avg_ally_champ_games'] = calc_df[[f'Player{i}.champ.games' for i in range(1, 6)]].mean(axis=1)
    calc_df['avg_ally_total_games'] = calc_df[[f'Player{i}.total.games' for i in range(1, 6)]].mean(axis=1)
    calc_df['avg_ally_overall_wr'] = calc_df[[f'Player{i}.overall.wr.adjusted' for i in range(1, 6)]].mean(axis=1)
    calc_df['avg_ally_champ_games'] = calc_df[[f'Player{i}.champ.games' for i in range(1, 6)]].mean(axis=1)
    calc_df['avg_ally_champ_mastery'] = calc_df[[f'Player{i}.mastery' for i in range(1, 6)]].mean(axis=1)
    calc_df['avg_ally_cs'] = calc_df[[f'Player{i}.cs' for i in range(1, 6)]].mean(axis=1)
    calc_df['avg_ally_kda'] = calc_df[[f'Player{i}.kda' for i in range(1, 6)]].mean(axis=1)
    calc_df['avg_ally_total_games'] = calc_df[[f'Player{i}.total.games' for i in range(1, 6)]].mean(axis=1)

    calc_df['std_ally_overall_wr'] = calc_df[[f'Player{i}.overall.wr.adjusted' for i in range(1, 6)]].std(axis=1)
    calc_df['std_ally_champ_wr'] = calc_df[[f'Player{i}.champ.wr.adjusted' for i in range(1, 6)]].std(axis=1)
    calc_df['std_ally_champ_games'] = calc_df[[f'Player{i}.champ.games' for i in range(1, 6)]].std(axis=1)
    calc_df['std_ally_champ_mastery'] = calc_df[[f'Player{i}.mastery' for i in range(1, 6)]].std(axis=1)
    calc_df['std_ally_cs'] = calc_df[[f'Player{i}.cs' for i in range(1, 6)]].std(axis=1)
    calc_df['std_ally_kda'] = calc_df[[f'Player{i}.kda' for i in range(1, 6)]].std(axis=1)
    calc_df['std_ally_total_games'] = calc_df[[f'Player{i}.total.games' for i in range(1, 6)]].std(axis=1)

    calc_df['avg_enemy_overall_wr'] = calc_df[[f'Player{i}.overall.wr.adjusted' for i in range(6, 11)]].mean(axis=1)
    calc_df['avg_enemy_champ_wr'] = calc_df[[f'Player{i}.champ.wr.adjusted' for i in range(6, 11)]].mean(axis=1)
    calc_df['avg_enemy_champ_games'] = calc_df[[f'Player{i}.champ.games' for i in range(6, 11)]].mean(axis=1)
    calc_df['avg_enemy_champ_mastery'] = calc_df[[f'Player{i}.mastery' for i in range(6, 11)]].mean(axis=1)
    calc_df['avg_enemy_cs'] = calc_df[[f'Player{i}.cs' for i in range(6, 11)]].mean(axis=1)
    calc_df['avg_enemy_kda'] = calc_df[[f'Player{i}.kda' for i in range(6, 11)]].mean(axis=1)
    calc_df['avg_enemy_total_games'] = calc_df[[f'Player{i}.total.games' for i in range(6, 11)]].mean(axis=1)

    calc_df['std_enemy_overall_wr'] = calc_df[[f'Player{i}.overall.wr.adjusted' for i in range(6, 11)]].std(axis=1)
    calc_df['std_enemy_champ_wr'] = calc_df[[f'Player{i}.champ.wr.adjusted' for i in range(6, 11)]].std(axis=1)
    calc_df['std_enemy_champ_games'] = calc_df[[f'Player{i}.champ.games' for i in range(6, 11)]].std(axis=1)
    calc_df['std_enemy_champ_mastery'] = calc_df[[f'Player{i}.mastery' for i in range(6, 11)]].std(axis=1)
    calc_df['std_enemy_cs'] = calc_df[[f'Player{i}.cs' for i in range(6, 11)]].std(axis=1)
    calc_df['std_enemy_kda'] = calc_df[[f'Player{i}.kda' for i in range(6, 11)]].std(axis=1)
    calc_df['std_enemy_total_games'] = calc_df[[f'Player{i}.total.games' for i in range(6, 11)]].std(axis=1)

def adjust_lookahead_bias(adjust_df):
    #this is loop to reduce lookahead bias for ally team
    for i in range(1, 6):
        #create a check for if a game is 0 or 1. This is needed because can only calculate
        #new adjusted winrate if they have over
        champ_game_min_check = adjust_df[f'Player{i}.champ.games'] > 1
        total_game_min_check = (adjust_df[f'Player{i}.total.games'] != 0) & (adjust_df[f'Player{i}.champ.games'] != 1)

        #to reduce lookahead bias in non winrate and game variables filling the low sample size games
        #with the averages of that column from this dataset found from R
        game_check = adjust_df[f'Player{i}.champ.games'] < 2

        adjust_df[f'Player{i}.kda'] = np.where(game_check, 2.6, adjust_df[f'Player{i}.kda'])
        adjust_df[f'Player{i}.cs'] = np.where(game_check, 140, adjust_df[f'Player{i}.cs'])


        #calculate how many wins and losses they had based on win% and total games
        adjust_df[f'Player{i}.champ.wins'] = np.where(champ_game_min_check, adjust_df[f'Player{i}.champ.wr']*.01 * adjust_df[f'Player{i}.champ.games'], adjust_df[f'Player{i}.champ.wins'])
        adjust_df[f'Player{i}.champ.losses'] = np.where(champ_game_min_check, adjust_df[f'Player{i}.champ.games'] - adjust_df[f'Player{i}.champ.wins'], adjust_df[f'Player{i}.champ.losses'])

        adjust_df[f'Player{i}.total.wins'] = np.where(total_game_min_check, adjust_df[f'Player{i}.overall.wr']*.01 * adjust_df[f'Player{i}.total.games'], adjust_df[f'Player{i}.total.wins'])
        adjust_df[f'Player{i}.total.losses'] = np.where(total_game_min_check, adjust_df[f'Player{i}.total.games'] - adjust_df[f'Player{i}.total.wins'], adjust_df[f'Player{i}.total.losses'])

        #remove one game from total to account for taking out current game
        adjust_df[f'Player{i}.champ.games'] = np.where(champ_game_min_check, adjust_df[f'Player{i}.champ.games'] - 1, adjust_df[f'Player{i}.champ.games'])
        adjust_df[f'Player{i}.total.games'] = np.where(total_game_min_check, adjust_df[f'Player{i}.total.games'] - 1, adjust_df[f'Player{i}.total.games'])

        #adjust win or loss total based on outcome
        win_condition = adjust_df['Win.Loss'] == 'win'
        adjust_df.loc[win_condition & champ_game_min_check, f'Player{i}.champ.wins'] -= 1
        adjust_df.loc[~win_condition & champ_game_min_check, f'Player{i}.champ.losses'] -= 1

        adjust_df.loc[win_condition & total_game_min_check, f'Player{i}.total.wins'] -= 1
        adjust_df.loc[~win_condition & total_game_min_check, f'Player{i}.total.losses'] -= 1

        #calculate the new winratre based on the win loss totals
        adjust_df[f'Player{i}.overall.wr.adjusted'] = np.where(total_game_min_check,(adjust_df[f'Player{i}.total.wins'] /  adjust_df[f'Player{i}.total.games']) * 100,adjust_df[f'Player{i}.overall.wr.adjusted'])
        adjust_df[f'Player{i}.champ.wr.adjusted'] = np.where(champ_game_min_check,(adjust_df[f'Player{i}.champ.wins'] / adjust_df[f'Player{i}.champ.games']) * 100,adjust_df[f'Player{i}.champ.wr.adjusted'])

    #loop to reduce lookahead bias for enemy team
    for i in range(6, 11):
        #create a check for if a game is 0 or 1. This is needed because can only calculate
        #new adjusted winrate if they have over
        champ_game_min_check = adjust_df[f'Player{i}.champ.games'] > 1
        total_game_min_check = (adjust_df[f'Player{i}.total.games'] != 0) & (adjust_df[f'Player{i}.champ.games'] != 1)

        #to reduce lookahead bias in non winrate and game variables filling the low sample size games
        #with the averages of that column from this dataset found from R
        game_check = adjust_df[f'Player{i}.champ.games'] < 2

        adjust_df[f'Player{i}.kda'] = np.where(game_check, 2.6, adjust_df[f'Player{i}.kda'])
        adjust_df[f'Player{i}.cs'] = np.where(game_check, 140, adjust_df[f'Player{i}.cs'])


        #calculate how many wins and losses they had based on win% and total games
        adjust_df[f'Player{i}.champ.wins'] = np.where(champ_game_min_check, adjust_df[f'Player{i}.champ.wr']*.01 * adjust_df[f'Player{i}.champ.games'], adjust_df[f'Player{i}.champ.wins'])
        adjust_df[f'Player{i}.champ.losses'] = np.where(champ_game_min_check, adjust_df[f'Player{i}.champ.games'] - adjust_df[f'Player{i}.champ.wins'], adjust_df[f'Player{i}.champ.losses'])

        adjust_df[f'Player{i}.total.wins'] = np.where(total_game_min_check, adjust_df[f'Player{i}.overall.wr']*.01 * adjust_df[f'Player{i}.total.games'], adjust_df[f'Player{i}.total.wins'])
        adjust_df[f'Player{i}.total.losses'] = np.where(total_game_min_check, adjust_df[f'Player{i}.total.games'] - adjust_df[f'Player{i}.total.wins'], adjust_df[f'Player{i}.total.losses'])

        #remove one game from total to account for taking out current game
        adjust_df[f'Player{i}.champ.games'] = np.where(champ_game_min_check, adjust_df[f'Player{i}.champ.games'] - 1, adjust_df[f'Player{i}.champ.games'])
        adjust_df[f'Player{i}.total.games'] = np.where(total_game_min_check, adjust_df[f'Player{i}.total.games'] - 1, adjust_df[f'Player{i}.total.games'])

        #adjust win or loss total based on outcome
        #has opposite condition of ally team because a win on the row means a loss for enemy team
        win_condition = adjust_df['Win.Loss'] == 'win'
        adjust_df.loc[~win_condition & champ_game_min_check, f'Player{i}.champ.wins'] -= 1
        adjust_df.loc[win_condition & champ_game_min_check, f'Player{i}.champ.losses'] -= 1

        adjust_df.loc[~win_condition & total_game_min_check, f'Player{i}.total.wins'] -= 1
        adjust_df.loc[win_condition & total_game_min_check, f'Player{i}.total.losses'] -= 1

        #calculate the new winrate based on the win loss totals
        adjust_df[f'Player{i}.overall.wr.adjusted'] = np.where(total_game_min_check,(adjust_df[f'Player{i}.total.wins'] /  adjust_df[f'Player{i}.total.games']) * 100,adjust_df[f'Player{i}.overall.wr.adjusted'])
        adjust_df[f'Player{i}.champ.wr.adjusted'] = np.where(champ_game_min_check,(adjust_df[f'Player{i}.champ.wins'] / adjust_df[f'Player{i}.champ.games']) * 100,adjust_df[f'Player{i}.champ.wr.adjusted'])


#read csvs into 3 differnt datasets for each csv
df = pd.read_csv('cleaned_gold.csv')
df2 = pd.read_csv('cleaned_diamond.csv')
df3 = pd.read_csv('cleaned_bronze.csv')



#creating new columns used to remove previous game to reduce lookahead bias
for i in range(1, 11):
    df[f'Player{i}.overall.wr.adjusted'] = 50
    df[f'Player{i}.champ.wr.adjusted'] = 50
    df[f'Player{i}.champ.wins'] = 0
    df[f'Player{i}.champ.losses'] = 0
    df[f'Player{i}.total.wins']  = 0
    df[f'Player{i}.total.losses'] = 0

    df2[f'Player{i}.overall.wr.adjusted'] = 50
    df2[f'Player{i}.champ.wr.adjusted'] = 50
    df2[f'Player{i}.champ.wins'] = 0
    df2[f'Player{i}.champ.losses'] = 0
    df2[f'Player{i}.total.wins']  = 0
    df2[f'Player{i}.total.losses'] = 0

    df3[f'Player{i}.overall.wr.adjusted'] = 50
    df3[f'Player{i}.champ.wr.adjusted'] = 50
    df3[f'Player{i}.champ.wins'] = 0
    df3[f'Player{i}.champ.losses'] = 0
    df3[f'Player{i}.total.wins']  = 0
    df3[f'Player{i}.total.losses'] = 0


adjust_lookahead_bias(df)
adjust_lookahead_bias(df2)
adjust_lookahead_bias(df3)

calculate_team_data(df)
calculate_team_data(df2)
calculate_team_data(df3)




feature_columns = ['avg_ally_overall_wr', 'avg_ally_champ_wr', 'avg_ally_champ_games',
                    'avg_ally_cs',  'avg_ally_total_games', 'avg_ally_kda',
                    'std_ally_overall_wr', 'std_ally_champ_wr', 'std_ally_champ_games',
                    'std_ally_cs',  'std_ally_total_games', 'std_ally_kda',
                    'avg_enemy_overall_wr',  'avg_enemy_champ_wr', 'avg_enemy_champ_games',
                    'avg_enemy_cs',  'avg_enemy_total_games', 'avg_enemy_kda',
                    'std_enemy_overall_wr',  'std_enemy_champ_wr', 'std_enemy_champ_games',
                    'std_enemy_cs',  'std_enemy_total_games', 'std_enemy_kda'
]


# Target outcome
target_column = 'Win.Loss'

#Make training and testing set
#gold
X = df[feature_columns]
y = df[target_column]

#diamond
X2 = df2[feature_columns]
y2 = df2[target_column]

#bronze
X3 = df3[feature_columns]
y3 = df3[target_column]

#split data into 80 20
X, X_test_sep, y, y_test_sep = train_test_split(X, y, test_size=0.2, random_state=42)
X2, X_test_sep2, y2, y_test_sep2 = train_test_split(X2, y2, test_size=0.2, random_state=42)
X3, X_test_sep3, y3, y_test_sep3 = train_test_split(X3, y3, test_size=0.2, random_state=42)

##Grid search for optimal hyper params of final model, takes many hours to run
"""
param_grid = {
    'n_estimators': [50, 100, 200, 400],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 4, 8],
    'min_samples_leaf': [1, 2, 4],
    'bootstrap' : [True, False],
    'max_features': ['sqrt', 'log2', None]
}

#5 folds with random forest model
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=5, scoring='accuracy')

grid_search.fit(X, y)

#best model from grid search
best_rf = grid_search.best_estimator_

#best params
print("Best hyperparams:")
print(grid_search.best_params_)
"""

#random forest with optimal hyperparameters from grid search, appears to be half a percent better than default or negligble
rf = RandomForestClassifier(bootstrap = True, max_depth = None, max_features = 'log2',
min_samples_leaf = 1, min_samples_split = 8, n_estimators = 100)

#kfold with 5 folds on gold dataset df2
nfolds = 5
scores = cross_val_score(rf, X, y, cv=nfolds)

print("Random Forest model trained on gold data")

#accuracy of each fold
for fold, score in enumerate(scores, start=1):
    fold = round(fold, 4)
    score = round(score, 4)
    print(f"Fold #{fold}: accuracy = {score}")

# Calculate and print the mean accuracy across all folds
mean_accuracy = scores.mean()
mean_accuracy = round(mean_accuracy, 4)

print(f"Mean Accuracy: {mean_accuracy}")




#fit model on 80% data
rf.fit(X, y)

y_pred_orig = rf.predict(X_test_sep)
accuracy_orig = accuracy_score(y_test_sep, y_pred_orig)
accuracy_orig = round(accuracy_orig, 4)
print("\nTest data accuracy:", accuracy_orig)


pred_dia = rf.predict(X2)
accuracy_dia = accuracy_score(y2, pred_dia)
accuracy_dia = round(accuracy_dia, 4)
print("Diamond test data accuracy:", accuracy_dia)

pred_bronze = rf.predict(X3)
accuracy_bronze = accuracy_score(y3, pred_bronze)
accuracy_bronze = round(accuracy_bronze, 4)
print("Bronze test data accuracy:", accuracy_bronze)


#save model for website usage
#joblib.dump(rf, 'league_rf_model.joblib')
