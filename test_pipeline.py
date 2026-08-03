import os
import re
import sqlite3
import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "http://books.toscrape.com/"
DB_NAME = "books_data.db"
EXCHANGE_RATE_GBP_TO_INR  = 105.0

RATING_MAP = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
}

def scrape_books_data():
    print("---1. Scraping Books Data---")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    category_tags = soup.select("ul.nav-list > li > ul > li > a")
    scraped_data = []

    for cat in category_tags:
        cat_name = cat.get_text(strip=True)
        cat_url = BASE_URL + cat['href']
        cat_res = requests.get(cat_url)
        cat_res.raise_for_status()
        cat_soup = BeautifulSoup(cat_res.content, "html.parser")

        articles = cat_soup.find_all("article", class_="product_pod")
        for article in articles:
            title = article.h3.a["title"]
            price_text = article.find( "p", class_="price_color" ).text
            rating_classes = article.find("p", class_="star-rating")["class"]
            rating_text = [c for c in rating_classes if c != "star-rating" ][0]
            avail_text = article.find("p", class_="instock availability" ).text.strip()
            scraped_data.append({
                "title": title, 
                "price_raw": price_text,
                "rating_raw": rating_text, 
                "availability_raw": avail_text,
                "category": cat_name
            })
        print(f"Scraped {len(articles)} books from: {cat_name}")
        if len(scraped_data) >= 60:
            break
    print("Scraped count:", len(scraped_data))
    return pd.DataFrame(scraped_data)
def parse_price(val):
    if pd.isna(val):
        return 0.0
    try:
        clean_val = re.sub(r'[^0-9.]','',str(val))
        return float(clean_val) if clean_val else 0.0
    except Exception:
        return 0.0
    
def clean_and_transform(df):
    print("\n--- 2. Cleaning & Currency Conversion --- ")
    df_clean = df.copy() 

    df_clean['price_gbp'] = df_clean['price_raw'].apply(parse_price).fillna(0).astype(int)
    if df_clean['price_gbp'].isnull().any():
        df_clean['price_gbp']= df_clean['price_gbp'].fillna(df_clean['price_gbp'].median())
    df_clean['rating'] = df_clean['rating_raw'].str.lower().map(RATING_MAP).fillna(0).astype(int)
    df_clean['in_stock'] = df_clean['availability_raw'].str.contains("In stock", case=False, na=False).astype(int)
    df_clean['price_inr'] = (df_clean['price_gbp'] * EXCHANGE_RATE_GBP_TO_INR).round(2)

    return df_clean[['title', 'price_gbp', 'price_inr', 'rating', 'in_stock', 'category']]

def setup_sqlite_db(df):
    print("\n--- 3. Setting Up SQLite Schema ---")

    if os.path.exists(DB_NAME):
        try:
            os.remove(DB_NAME)
        except Exception:
            pass

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, 
        price_gbp REAL NOT NULL,
        price_inr REAL NOT NULL, 
        rating INTEGER NOT NULL,
        in_stock INTEGER NOT NULL, 
        category_id INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories (category_id)
    );
    """)

    categories = df['category'].unique()
    cat_map = {}
    for cat in categories:
        cursor.execute("INSERT INTO  categories (category_name) VALUES  (?)", (cat,))
        cat_map[cat] = cursor.lastrowid
    conn.commit()

    df_db = df.copy()
    df_db['category_id'] = df_db['category'].map(cat_map)

    df_db[['title','price_gbp', 'price_inr', 'rating', 'in_stock', 'category_id']].to_sql(
        'books', conn, if_exists='append', index=False
    )
    return conn

def execute_sql_queries(conn):
    print("\n--- 4. Executing SQL Queries ---")
    queries = {
        "Q1 (SELECT/WHERE)": "SELECT title, price_gbp FROM books WHERE in_stock = 1 ORDER BY price_gbp DESC LIMIT 5;",
        "Q2 (DISTINCT)": "SELECT DISTINCT category_name FROM categories;",
        "Q3 (IN)": "SELECT title, rating FROM books WHERE rating IN (4,5) LIMIT 5;",
        "Q4 (BETWEEN)": "SELECT title, price_inr FROM books WHERE price_inr BETWEEN 2000 AND 5000 LIMIT 5;",
        "Q5 (JOIN)": "SELECT b.title, c.category_name, b.price_inr FROM books b JOIN categories c ON b.category_id = c.category_id LIMIT 5;",
    } 
    for label, q in queries.items():
        print(f"/n[{label}]")
        print(pd.read_sql_query(q, conn))

def compare_joins(conn):
    print("/n--- 5. SQL JOIN vs Pandas pd.merge ---")
    sql_df = pd.read_sql_query(
        "SELECT b.title, c.category_name FROM books b JOIN categories c ON b.category_id = c.category_id", 
        conn
    )
    books_df = pd.read_sql_query("SELECT * FROM books", conn)
    categories_df = pd.read_sql_query("SELECT * FROM categories", conn)

    pd_df = pd.merge(books_df, categories_df, on="category_id")
    pd_df = pd_df[['title', 'category_name']]
    print("Are SQL JOIN and Pandas pd.merge identical?", sql_df.equals(pd_df))

if __name__ == "__main__":
    df_raw = scrape_books_data()
    df_clean = clean_and_transform(df_raw)
    conn = setup_sqlite_db(df_clean)
    execute_sql_queries(conn)
    compare_joins(conn)
    conn.close()
    print("/nModule 1 complete!")