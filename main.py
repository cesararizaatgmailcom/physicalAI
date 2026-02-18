from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()

DB_CONFIG = {
    "host": "TU_SERVIDOR.postgres.database.azure.com",
    "database": "wms_db",
    "user": "usuario@servidor",
    "password": "PASSWORD",
    "sslmode": "require"
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

@app.get("/")
def health():
    return {"status": "API running"}

@app.post("/orders")
def create_order(order: dict):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orders (external_id,status,recipient_name)
        VALUES (%s,'created',%s)
        RETURNING id
    """, (order["external_id"], order["recipient"]))

    order_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()

    return {"order_id": order_id}
