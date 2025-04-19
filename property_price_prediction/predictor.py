from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score



class PropertyPricePredictor:
    
    EPOCH_DATE = datetime(2000, 1, 1)  # Used to convert dates into integer number of days since
    FEATURES_TO_USE = ['bed', 'bath', 'car', 'land', 'days_since_epoch', 'desirability']

    def __init__(self, data_path=None):
        if not data_path:
            try:
                data_path = 'data/similar_sales_private.xlsx'
                assert Path(data_path).exists()
            except AssertionError:
                data_path = 'data/similar_sales.xlsx'

        self.data_path = Path(data_path)
        self.df = None
        self.models = {}

        self.load_data()
        self.build_models()


    @staticmethod
    def get_days_since_epoch(date):
        return (pd.to_datetime(date) - PropertyPricePredictor.EPOCH_DATE).days


    def load_data(self):
        self.df = pd.read_excel(self.data_path)
        self.df['days_since_epoch'] = self.df['date'].apply(self.get_days_since_epoch)
        return self.df


    def build_models(self):
        
        for model_name in self.df['data_model'].unique():
            df_subset = self.df[self.df['data_model'] == model_name]
            x = df_subset[self.FEATURES_TO_USE]
            y = df_subset['price']

            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

            model = LinearRegression()
            model.fit(x_train, y_train)

            y_pred = model.predict(x_test)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))

            print(model_name)
            print(f'Number of datapoints used for training: {len(df_subset)}')
            print(f'R² score: {r2:.4f}')
            print(f'RMS error: ${rmse:,.0f}')
            print('------------')

            self.models[model_name] = model

        return self.models


    def predict(self, parameters: dict):
        model_name = parameters['data_model']
        if model_name not in self.models:
            raise ValueError(f"No model found for '{model_name}'. Did you train the models?")

        test_house = pd.DataFrame([parameters])
        test_house['days_since_epoch'] = test_house['date'].apply(self.get_days_since_epoch)

        prediction = self.models[model_name].predict(test_house[self.FEATURES_TO_USE])
        print(f'Predicted price for the house with parameters {parameters}:\n${prediction[0]:,.0f}')
        return int(round(prediction[0], 0))
