import sqlite3
import pandas as pd
import os
import math

# --- CONFIGURAÇÃO ---
DB_NAME = "DisneyDB.db"
DATA_FILE = "DisneyPlus.xlsx" 
SCHEMA_FILE = "schema.sql"

# --- FUNÇÃO UTILITÁRIA: CACHING & INSERT ---
def get_or_create_id(cursor, table_name, col_name, value, cache_dict):
    """
    Retorna o ID de um valor. Se não existir, cria.
    Usa cache para evitar milhares de SELECTs repetidos.
    """
    if value is None or str(value).strip() == "":
        return None
    
    value = str(value).strip()
    
    if value in cache_dict:
        return cache_dict[value]
    
    try:
        query = f"INSERT OR IGNORE INTO {table_name} ({col_name}) VALUES (?)"
        cursor.execute(query, (value,))
        
        query_select = f"SELECT {table_name}_id FROM {table_name} WHERE {col_name} = ?"
        cursor.execute(query_select, (value,))
        result = cursor.fetchone()
        
        if result:
            new_id = result[0]
            cache_dict[value] = new_id
            return new_id
            
    except sqlite3.Error as e:
        print(f"Erro ao processar {table_name} ('{value}'): {e}")
        return None

def main():
    # 1. PREPARAÇÃO DA BASE DE DADOS
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Base de dados antiga removida para reiniciar.")
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    print("A criar tabelas a partir do schema.sql...")
    try:
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())
    except FileNotFoundError:
        print(f"ERRO: Não encontrei o ficheiro {SCHEMA_FILE}. Verifica a pasta.")
        return

    # 2. LEITURA DO DATASET
    print(f"A ler o ficheiro {DATA_FILE}...")
    try:
        df = pd.read_excel(DATA_FILE)
    except FileNotFoundError:
        # Tenta caminho relativo alternativo
        df = pd.read_excel(f"../{DATA_FILE}")
    
    # Substituir NaN por None
    df = df.where(pd.notnull(df), None)
    
    # Forçamos o formato '%m/%d/%Y' para garantir que 11/26/2021 é lido corretamente
    # errors='coerce' transforma datas inválidas em NaT (None) sem parar o script
    df['date_added_clean'] = pd.to_datetime(df['date_added'], format='%m/%d/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    
    # 3. INICIALIZAR CACHES
    cache_rating = {}
    cache_genre = {}
    cache_country = {}
    cache_person = {}

    print("A iniciar inserção de dados...")
    count = 0
    
    # 4. LOOP PRINCIPAL
    for index, row in df.iterrows():
        
        # A. RATING
        rating_id = get_or_create_id(cursor, "Rating", "code", row['rating'], cache_rating)
        
        # B. DURAÇÃO ("90 min" ou "1 Season")
        duration_val = None
        duration_unit = None
        raw_duration = row['duration']
        
        if raw_duration:
            try:
                parts = str(raw_duration).strip().split(' ', 1)
                if len(parts) == 2:
                    duration_val = int(parts[0]) # Converte "90" para inteiro
                    duration_unit = parts[1].strip() # "min"
            except (ValueError, AttributeError):
                pass 

        # C. TRATAMENTO DO ANO DE LANÇAMENTO (1998)
        # Garante que tratamos 1998, "1998" ou 1998.0 da mesma forma
        release_date_fmt = None
        if row['release_year']:
            try:
                # float() primeiro para apanhar casos como 1998.0, depois int()
                year_int = int(float(row['release_year']))
                release_date_fmt = f"{year_int}-01-01"
            except ValueError:
                release_date_fmt = None

        # D. INSERIR SHOW
        insert_show_sql = """
        INSERT INTO Show (title, description, show_type, release_date, date_added, duration_value, duration_unit, rating_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            row['title'], 
            row['description'], 
            row['type'],           
            release_date_fmt,        # Data fictícia baseada no ano (ex: 1998-01-01)
            row['date_added_clean'], # Data real formatada (ex: 2021-11-26)
            duration_val,          
            duration_unit,         
            rating_id
        )
        
        cursor.execute(insert_show_sql, params)
        show_id = cursor.lastrowid
        
        # E. PROCESSAR LISTAS (Separadas por vírgula)
        
        # Géneros
        if row['listed_in']:
            genres = [g.strip() for g in str(row['listed_in']).split(',')]
            for genre_name in genres:
                g_id = get_or_create_id(cursor, "Genre", "name", genre_name, cache_genre)
                if g_id:
                    cursor.execute("INSERT OR IGNORE INTO Show_Genre (show_id, genre_id) VALUES (?, ?)", (show_id, g_id))

        # Países
        if row['country']:
            countries = [c.strip() for c in str(row['country']).split(',')]
            for country_name in countries:
                if country_name: 
                    c_id = get_or_create_id(cursor, "Country", "name", country_name, cache_country)
                    if c_id:
                        cursor.execute("INSERT OR IGNORE INTO Show_Country (show_id, country_id) VALUES (?, ?)", (show_id, c_id))
            
        # Elenco (Cast)
        if row['cast']:
            actors = [a.strip() for a in str(row['cast']).split(',')]
            for actor_name in actors:
                if actor_name:
                    p_id = get_or_create_id(cursor, "Person", "name", actor_name, cache_person)
                    if p_id:
                        cursor.execute("INSERT OR IGNORE INTO Credit (show_id, person_id, role) VALUES (?, ?, 'Actor')", (show_id, p_id))
            
        # Diretores
        if row['director']:
            directors = [d.strip() for d in str(row['director']).split(',')]
            for director_name in directors:
                if director_name:
                    p_id = get_or_create_id(cursor, "Person", "name", director_name, cache_person)
                    if p_id:
                        cursor.execute("INSERT OR IGNORE INTO Credit (show_id, person_id, role) VALUES (?, ?, 'Director')", (show_id, p_id))

        count += 1
        if count % 100 == 0:
            print(f"Processados: {count}...", end='\r')

    conn.commit()
    conn.close()
    print(f"\n\nSUCESSO! Base de dados '{DB_NAME}' criada com {count} filmes/séries.")

if __name__ == "__main__":
    main()