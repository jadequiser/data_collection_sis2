import sqlite3
import pandas as pd
import os

def run_loader():
    
    #files
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'data', 'cleaned_data.csv')
    db_path = os.path.join(base_dir, 'data', 'output.db')

    if not os.path.exists(csv_path):
        print(f"File is not found {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    #define columns
    df.columns = df.columns.str.strip().str.lower()
    print(f"Columns {list(df.columns)}")

    #renaming 
    if 'price' in df.columns:
        df = df.rename(columns={'price': 'price_original'})
 
    if 'price_original' not in df.columns:
        print("price_original not found")
        #creating empty
        df['price_original'] = "0"

    #define needed columns 
    target_columns = ['title', 'price_original', 'link', 'price_cleaned']
    final_cols = [c for c in target_columns if c in df.columns]
    df = df[final_cols]

    #save to db
    print(f"Connecting to our db {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS listings")
    
    create_table_query = """
    CREATE TABLE listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        price_original TEXT,
        link TEXT,
        price_cleaned INTEGER
    );
    """
    cursor.execute(create_table_query)

    try:
        df.to_sql('listings', conn, if_exists='append', index=False)
        
        count = cursor.execute("SELECT count(*) FROM listings").fetchone()[0]
        print(f" {count} rows are successfully load")
        
    except Exception as e:
        print(f"Error {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_loader()