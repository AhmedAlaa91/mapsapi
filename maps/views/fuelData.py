import pandas as pd
from django.shortcuts import render
import os

FILE_PATH = os.path.join(os.path.dirname(__file__),  'fuel-prices-for-be-assessment.csv')

def load_fuel_data():
    df = pd.read_csv(FILE_PATH)
    return df.to_dict(orient='records')