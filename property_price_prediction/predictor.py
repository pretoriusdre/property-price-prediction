from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from typing import Dict, Any, Optional

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PropertyPricePredictor:
    
    EPOCH_DATE = datetime(2000, 1, 1)  # Used to convert dates into integer number of days since
    FEATURES_TO_USE = ['bed', 'bath', 'car', 'land', 'days_since_epoch', 'desirability']

    def __init__(self, data_path: Optional[str] = None) -> None:
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
    def get_days_since_epoch(date: str | datetime) -> int:
        return (pd.to_datetime(date) - PropertyPricePredictor.EPOCH_DATE).days


    def load_data(self) -> pd.DataFrame:

        try:
            self.df = pd.read_excel(self.data_path)
        except FileNotFoundError as e:
            logger.error(e)
            raise e

        self.df['days_since_epoch'] = self.df['date'].apply(self.get_days_since_epoch)
        return self.df


    def build_models(self) -> Dict[str, LinearRegression]:
        
        for model_name in self.df['data_model'].unique():

            logger.info(f'Starting on {model_name}')

            df_subset = self.df[self.df['data_model'] == model_name].copy()

            missing_features = df_subset[self.FEATURES_TO_USE].isnull().sum()
            
            if missing_features.any():
                logger.warning(f'Missing values detected in feature columns for model "{model_name}":')
                logger.warning(f"Number of missing values in each column: {dict(missing_features[missing_features > 0])}")

                for feature in self.FEATURES_TO_USE:
                    if df_subset[feature].isnull().any():
                        mode_value = df_subset[feature].mode()[0]
                        df_subset[feature] = df_subset[feature].fillna(mode_value)
                        logger.warning(f'Filled missing values in feature "{feature}" with the most common value. Accuracy is affected.')
                                    

            x = df_subset[self.FEATURES_TO_USE]
            y = df_subset['price']

            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

            model = LinearRegression()
            model.fit(x_train, y_train)

            y_pred = model.predict(x_test)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))

            
            
            logger.info(f'Number of datapoints used for training: {len(df_subset)}')
            logger.info(f'R² score: {r2:.4f}')
            logger.info(f'RMS error: ${rmse:,.0f}')
            print('------------')

            self.models[model_name] = model

        return self.models


    def predict(self, parameters: Dict[str, Any]) -> int:
        model_name = parameters['data_model']
        if model_name not in self.models:
            raise ValueError(f'No model found for "{model_name}". Did you include the model in the sample data?')

        test_house = pd.DataFrame([parameters])
        test_house['days_since_epoch'] = test_house['date'].apply(self.get_days_since_epoch)

        prediction = self.models[model_name].predict(test_house[self.FEATURES_TO_USE])
        logger.info(f'Predicted price for the house with parameters {parameters}:\n${prediction[0]:,.0f}')
        return int(round(prediction[0], 0))



    def get_sensitivities(self, model_name: str) -> None:

        model = self.models[model_name]
        bed_coef = model.coef_[self.FEATURES_TO_USE.index('bed')]
        bath_coef = model.coef_[self.FEATURES_TO_USE.index('bath')]
        car_coef = model.coef_[self.FEATURES_TO_USE.index('car')]
        land_coef = model.coef_[self.FEATURES_TO_USE.index('land')]
        date_coef = model.coef_[self.FEATURES_TO_USE.index('days_since_epoch')]
        desirability_coef = model.coef_[self.FEATURES_TO_USE.index('desirability')]

        impact_bed = bed_coef * 1 # Impact of 1 more bedroom
        impact_car = car_coef
        impact_bath = bath_coef
        impact_land = land_coef * 100  # 100 sqm increase
        impact_date = date_coef * 30  # 1 month
        impact_desirability = desirability_coef

        logger.info(f'Sensitivities for {model_name}:')
        logger.info(f'Impact of ± 1 bedroom: ${impact_bed:,.0f}')
        logger.info(f'Impact of ± 1 bathroom: ${impact_bath:,.0f}')
        logger.info(f'Impact of ± 1 car bay: ${impact_car:,.0f}')
        logger.info(f'Impact of ± 100 sqm land: ${impact_land:,.0f}')
        logger.info(f'Impact of ± 1 month: ${impact_date:,.0f}')
        logger.info(f'Impact of ± 1 desirability point: ${impact_desirability:,.0f}')

