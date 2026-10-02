from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()




DB_CONFIG = {
    "host": "wms-postgres-server.postgres.database.azure.com",
    "database": "interlogbd",
    "user": "interlogadminbd",
    "password": os.environ["DB_PASSWORD"],
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

    recipient = order["account"][0]["recipient"]
    location = order["account"][0]["Location"]

    cur.execute("""
        INSERT INTO orders (external_id, status, recipient_name, location)
        VALUES (%s, 'created', %s, %s)
        RETURNING id
    """, (order["external_id"], recipient, location))

    order_id = cur.fetchone()[0]

    for item in order["items"]:
        cur.execute("""
            INSERT INTO order_items (order_id, product_code, quantity)
            VALUES (%s, %s, %s)
        """, (
            order_id,
            item["product_code"],
            item["quantity"]
        ))

    conn.commit()
    cur.close()
    conn.close()

    # crear misión automática
    #create_mission_from_order(order_id, order["recipient"])

    return {"order_id": order_id}



def create_mission_from_order(order_id, recipient):
    conn = get_conn()
    cur = conn.cursor()

    # ubicación fija de picking por ahora
    pickup_location = "STORAGE"

    cur.execute("""
        INSERT INTO robot_missions (
            order_id,
            pickup_location,
            dropoff_location,
            status
        )
        VALUES (%s, %s, %s, 'pending')
    """, (order_id, pickup_location, recipient))

    conn.commit()
    cur.close()
    conn.close()

@app.get("/missions/next")
def next_mission():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, pickup_location, dropoff_location
        FROM missions
        WHERE status = 'pending'
        ORDER BY id
        LIMIT 1
    """)

    mission = cur.fetchone()

    if not mission:
        return {"mission": None}

    mission_id = mission[0]

    cur.execute("""
        UPDATE missions
        SET status = 'assigned'
        WHERE id = %s
    """, (mission_id,))

    conn.commit()
    cur.close()
    conn.close()

    return {
        "mission_id": mission[0],
        "pickup": mission[1],
        "dropoff": mission[2]
    }