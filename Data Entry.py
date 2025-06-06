# Login Page Login Id and password Credential 

import psycopg2

def main():
    conn = psycopg2.connect(
        dbname="user_login_page",
        user="postgres",
        password="jaihind",
        host="127.0.0.1",
        port="5432"
    )
    cur = conn.cursor()

    # HR users
    cur.execute("""
        INSERT INTO login_page (username, password) VALUES
            ('admin01', 'admin01'),
            ('admin02', 'admin02'),
            ('admin03', 'admin03'),
            ('admin04', 'admin04'),
            ('admin05', 'admin05'),
            ('admin06', 'admin06'),
            ('admin07', 'admin07'),
            ('admin08', 'admin08'),
            ('admin09', 'admin09'),
            ('admin10', 'admin10')
        ON CONFLICT (username) DO NOTHING;
    """)

    # Student users
    cur.execute("""
        INSERT INTO login_page (username, password) VALUES
            ('4MT21AI001', '4MT21AI001'),
            ('4MT21AI002', '4MT21AI002'),
            ('4MT21AI003', '4MT21AI003'),
            ('4MT21AI004', '4MT21AI004'),
            ('4MT21AI005', '4MT21AI005'),
            ('4MT21AI006', '4MT21AI006'),
            ('4MT21AI007', '4MT21AI007'),
            ('4MT21AI008', '4MT21AI008'),
            ('4MT21AI009', '4MT21AI009'),
            ('4MT21AI010', '4MT21AI010')
        ON CONFLICT (username) DO NOTHING;
    """)

    # Company users
    cur.execute("""
        INSERT INTO login_page (username, password) VALUES
            ('C01', 'C01'),
            ('C02', 'C02'),
            ('C03', 'C03'),
            ('C04', 'C04'),
            ('C05', 'C05'),
            ('C06', 'C06'),
            ('C07', 'C07'),
            ('C08', 'C08'),
            ('C09', 'C09'),
            ('C10', 'C10')
        ON CONFLICT (username) DO NOTHING;
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("All login data inserted successfully.")

if __name__ == "__main__":
    main()