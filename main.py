from fastapi import FastAPI, HTTPException
from sklearn.metrics import mean_squared_error, r2_score
from pydantic import BaseModel
from typing import List
from enum import Enum
import joblib
import pandas as pd
import json

app = FastAPI()

df = []

with open('enpointdf.json') as f: 
    for line in f.readlines():
        df.append(json.loads(line))



df_endpoint = pd.DataFrame(df)

#modelo pred.
modelo_entrenado = joblib.load('modelo_entrenado.pkl')
#label encoder
#label_encoder = joblib.load('label_encoder.pkl')

GENRES_LIST = ['Action','Adventure','Casual','Early Access','Free to Play','Indie','Massively Multiplayer','RPG','Racing','Simulation','Sports','Strategy']

def filter_by_year(year):
    #control de excepciones de Python, importando el manejo de errores de FASTAPI
    try:
        int_year = int(year)
    except ValueError: 
        raise HTTPException(400, "El año debe ser un entero.")
    return df_endpoint[df_endpoint['release_year'] == int_year]

#La función anterior, se encarga de filtrar los valores por año, ya que es algo que se utiliza en todos los endpoints.

#esto lo voy a usar para poder poner una lista de generos
class Item(BaseModel):
    year: str
    genres: List[str]

class ParametroOpciones(str, Enum):
    opcion1 = "valor_opcion1"
    opcion2 = "valor_opcion2"
    opcion3 = "valor_opcion3"


@app.get("/genero/{year}")
def genero(year: str):
    df_filtered = filter_by_year(year)
    all_genres = df_filtered['genres'].tolist()
    all_genres_flat = [genre for sublist in all_genres if isinstance(sublist, list) for genre in sublist]
    genre_counts = pd.Series(all_genres_flat).value_counts(sort=True, ascending=False)

    genre_counts_dict = {genre: count for genre, count in list(genre_counts.items())[:5]}

    return genre_counts_dict

@app.get("/juegos/{year}")
def juegos(year: str):
    df_filtered = filter_by_year(year)

    juegos_lanzados = df_filtered['title'].tolist()

    return juegos_lanzados


@app.get("/specs/{year}")
def specs(year:str):
    df_filtered = filter_by_year(year)

    all_specs = [spec for specs_list in df_filtered['specs'] if isinstance(specs_list, list) for spec in specs_list]
    top_5_specs = pd.Series(all_specs).value_counts(sort=True, ascending=False)

    top_5_specs = {specs: count for specs, count in list(top_5_specs.items())[:5]}
    return top_5_specs

@app.get("/earlyacces/{year}")
def earlyacces(year:str):
    df_filtered = filter_by_year(year)

    num_earlyacces = df_filtered['early_access'].sum()

    return {"earlyacces": str(num_earlyacces)}

@app.get("/sentiment/{year}")
def sentiment(year:str):
    df_filtered = filter_by_year(year)

    sentiment_counts = df_filtered['sentiment'].value_counts()

    sentiments = ['Mixed', 'Mostly Negative', 'Mostly Positive', 'Negative', 'Overwhelmingly Negative',
                  'Overwhelmingly Positive', 'Positive', 'Very Negative', 'Very Positive']
    sentiment_dict = {sentiment: sentiment_counts.get(sentiment, 0) for sentiment in sentiments}
    sentiment_dict = {sentiment: int(count) for sentiment, count in sentiment_dict.items() if count != 0}

    return sentiment_dict

@app.get("/metascore/{year}")
def metascore(year: str):
    df_filtered = filter_by_year(year)
    df_filtered['metascore'] = pd.to_numeric(df_filtered['metascore'], errors='coerce')
    df_sorted = df_filtered.sort_values(by='metascore', ascending=False)
    top_5_juegos = df_sorted.head(5)[['title', 'metascore']].to_dict(orient='records')

    return top_5_juegos


@app.get("/predict/")
def predict_price(year: str, genres: str):
    #obtengo los datos
    genres_dict = extract_genres(genres)
    data = {'release_year': int(year), **genres_dict}
    df = pd.DataFrame(data, index=[0])

    prediction = modelo_entrenado.predict(df)

    return {"prediction": prediction[0], "RMSE": 8.194215961503977, "R2": 0.4053934917647908}

def extract_genres(genres:str):
    genres_splitted = genres.split(",")
    genres_parsed = [genre.strip() for genre in genres_splitted]
    genres_excluded = list(set(GENRES_LIST) - set(genres_parsed))
    genres_included = list(set(GENRES_LIST) - set(genres_excluded))

    result = {}

    for genre in GENRES_LIST:
        if genre in genres_included:
            result[genre] = 1
        else:
            result[genre] = 0

    return result