import psycopg2

def create_login_table():
    conn = psycopg2.connect(
        dbname="user_login_page",
        user="postgres",
        password="jaihind",
        host="127.0.0.1",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS login_page (
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(255) NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("login_page table created successfully.")

if __name__ == "__main__":
    create_login_table()

