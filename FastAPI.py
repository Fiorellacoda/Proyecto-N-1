from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import numpy as np
from pydantic import BaseModel
import uvicorn

# Diccionario para mapear los nombres de los meses en español a números de mes
meses = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8, 
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

# Diccionario para convertir días de la semana en español a números
dias = {
    'lunes': 0, 'martes': 1, 'miércoles': 2, 'jueves': 3, 'viernes': 4, 'sábado': 5, 'domingo': 6
}

# Cargar el CSV una vez
archivo_csv = r'C:\\Users\\Lauta\\Downloads\\movies_dataset_cleaned.csv'
df = pd.read_csv(archivo_csv, parse_dates=['release_date'])

app = FastAPI()

class MesRequest(BaseModel):
    mes: str

class DiaRequest(BaseModel):
    dia: str

class TituloRequest(BaseModel):
    titulo: str

class ActorRequest(BaseModel):
    actor: str

class DirectorRequest(BaseModel):
    director: str

@app.get("/cantidad_filmaciones_mes")
def cantidad_filmaciones_mes(mes: str = Query(..., description="Ingrese un mes en español.")):
    mes = mes.lower()
    if mes not in meses:
        raise HTTPException(status_code=400, detail="Mes no válido. Por favor ingrese un mes en español.")
    mes_numero = meses[mes]
    peliculas_mes = df[df['release_date'].dt.month == mes_numero]
    cantidad = len(peliculas_mes)
    return {"mes": mes, "cantidad": cantidad}

@app.get("/cantidad_filmaciones_dia")
def cantidad_filmaciones_dia(dia: str = Query(..., description="Ingrese un día de la semana en español.")):
    dia_num = dias.get(dia.lower())
    if dia_num is not None:
        count = df[df['release_date'].dt.weekday == dia_num].shape[0]
        return {"dia": dia, "cantidad": count}
    raise HTTPException(status_code=400, detail="Día no válido")

@app.get("/score_titulo")
def score_titulo(titulo: str = Query(..., description="Ingrese el título de la película.")):
    film = df[df['title'].str.lower() == titulo.lower()]
    if not film.empty:
        titulo = film.iloc[0]['title']
        año = film.iloc[0]['release_date'].year
        vote_avarage = film.iloc[0]['score']
        return {"titulo": titulo, "año": año, "score": vote_avarage}
    raise HTTPException(status_code=404, detail="Película no encontrada")

@app.get("/votos_titulo")
def votos_titulo(titulo: str = Query(..., description="Ingrese el título de la película.")):
    film = df[df['title'].str.lower() == titulo.lower()]
    if not film.empty:
        votos = film.iloc[0]['vote_count']
        if votos >= 2000:
            titulo = film.iloc[0]['title']
            año = film.iloc[0]['release_date'].year
            promedio = film.iloc[0]['vote_average']
            return {"titulo": titulo, "año": año, "votos": votos, "promedio": promedio}
        raise HTTPException(status_code=400, detail="La película no cumple con la condición de tener al menos 2000 valoraciones")
    raise HTTPException(status_code=404, detail="Película no encontrada")

@app.get("/get_actor")
def get_actor(actor: str = Query(..., description="Ingrese el nombre del actor o actriz.")):
    actor_films = df[df['cast'].str.contains(actor, case=False, na=False)]
    if not actor_films.empty:
        num_peliculas = actor_films.shape[0]
        retorno_total = actor_films['return'].sum()
        promedio_retorno = actor_films['return'].mean()
        return {"actor": actor, "num_peliculas": num_peliculas, "retorno_total": retorno_total, "promedio_retorno": promedio_retorno}
    raise HTTPException(status_code=404, detail="Actor no encontrado")

@app.get("/get_director")
def get_director(director: str = Query(..., description="Ingrese el nombre del director.")):
    director_films = df[df['director'].str.contains(director, case=False, na=False)]
    if not director_films.empty:
        retorno_total = director_films['return'].sum()
        info_peliculas = director_films[['title', 'release_date', 'return', 'budget', 'revenue']].to_dict('records')
        return {"director": director, "retorno_total": retorno_total, "peliculas": info_peliculas}
    raise HTTPException(status_code=404, detail="Director no encontrado")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)