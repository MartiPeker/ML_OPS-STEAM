from fastapi import FastAPI
import pandas as pd
import json

app = FastAPI()

df = []

with open('enpointdf.json') as f: 
    for line in f.readlines():
        df.append(json.loads(line))

df_endpoint = pd.DataFrame(df)

def filter_by_year(year):
    return df_endpoint[df_endpoint['release_year'] == year]


@app.get("/genero/{year}")
def genero(year: int):
    df_filtered = filter_by_year(year)

    all_genres = df_filtered['genres'].tolist()
    all_genres_flat = [genre for sublist in all_genres if isinstance(sublist, list) for genre in sublist]
    genre_counts = pd.Series(all_genres_flat).value_counts(sort=True, ascending=False)
    genres_repeat = genre_counts.index[:5]

    return {genre for genre in genres_repeat}

@app.get("/juegos/{year}")
def juegos(year: int):
    df_filtered = filter_by_year(year)

    juegos_lanzados = df_filtered['title'].tolist()

    return juegos_lanzados


@app.get("/specs/{year}")
def specs(year:int):
    df_filtered = filter_by_year(year)

    all_specs = [spec for specs_list in df_filtered['specs'] if isinstance(specs_list, list) for spec in specs_list]
    spec_counts = pd.Series(all_specs).value_counts(sort=True, ascending=False)
    top_5_specs = spec_counts.index[:5].tolist()

    return top_5_specs

@app.get("/earlyacces/{year}")
def earlyacces(year:int):
    df_filtered = filter_by_year(year)

    num_earlyacces = df_filtered['early_access'].sum()

    return {"earlyacces": int(num_earlyacces)}

@app.get("/sentiment/{year}")
def sentiment(year:int):
    df_filtered = filter_by_year(year)

    sentiment_counts = df_filtered['sentiment'].value_counts()

    sentiments = ['Mixed', 'Mostly Negative', 'Mostly Positive', 'Negative', 'Overwhelmingly Negative',
                  'Overwhelmingly Positive', 'Positive', 'Very Negative', 'Very Positive']
    sentiment_dict = {sentiment: sentiment_counts.get(sentiment, 0) for sentiment in sentiments}
    sentiment_dict = {sentiment: int(count) for sentiment, count in sentiment_dict.items() if count != 0}

    return sentiment_dict

@app.get("/metascore/{year}")
def metascore(year:int):
    df_filtered = filter_by_year(year)
    df_sorted = df_filtered.sort_values(by='metascore', ascending=False)
    
    top_5_juegos = df_sorted.head(5)['title'].tolist()

    return top_5_juegos
    
