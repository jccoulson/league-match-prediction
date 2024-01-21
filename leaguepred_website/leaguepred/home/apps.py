from django.apps import AppConfig
import joblib
import os

class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'
    model = None

    def ready(self):
        #modelfile path
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources/league_rf_model.joblib')
        #load model
        HomeConfig.model = joblib.load(model_path)
