from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2

app = Flask(__name__)
app.secret_key = "your_secret_key"


def get_db_connection():
    return psycopg2.connect(
        dbname="user_login_page",
        user="postgres",
        password="jaihind",
        host="127.0.0.1",
        port="5432",
    )


def create_student_module_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS student_module (
            studentID VARCHAR(100) PRIMARY KEY,
            student_name VARCHAR(100),
            student_branch VARCHAR(100),
            student_batch INT CHECK (
                student_batch >= 1947
                AND student_batch <= 2200
            ) DEFAULT 1947,
            student_graduating_year INT GENERATED ALWAYS AS (student_batch + 4) STORED,
            student_backlog INT DEFAULT 0,
            student_backlog_history INT DEFAULT 0,
            student_cgpa DECIMAL(10, 2) CHECK (
                student_cgpa >= 0
                AND student_cgpa <= 10
            ) DEFAULT 0,
            student_status VARCHAR(50) GENERATED ALWAYS AS (
                CASE
                    WHEN student_cgpa >= 6.0
                    AND student_backlog = 0 THEN 'Eligible'
                    WHEN student_cgpa >= 6.0
                    AND student_backlog > 0 THEN 'Conditionally Eligible'
                    WHEN student_cgpa < 6.0
                    AND student_backlog >= 0 THEN 'Not Eligible'
                END
            ) STORED,
            placement_status VARCHAR(50) DEFAULT 'Not Placed'
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


create_student_module_table()


def insert_student(data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO student_module (
            studentID, student_name, student_branch, student_batch,
            student_backlog, student_backlog_history, student_cgpa, placement_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (studentID) DO NOTHING
        """,
        (
            data["studentID"].upper(),
            data["student_name"].title(),
            data["student_branch"],
            int(data["student_batch"]),
            int(data["student_backlog"]),
            int(data["student_backlog_history"]),
            float(data["student_cgpa"]),
            data.get("placement_status", "Not Placed"),
        ),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_students():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            studentID,
            student_name,
            student_branch,
            student_batch,
            student_graduating_year,
            student_backlog,
            student_backlog_history,
            student_cgpa,
            student_status,
            placement_status
        FROM student_module
        ORDER BY studentID
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM login_page WHERE username = %s", (username,))
        result = cur.fetchone()
        print(
            f"Entered username: '{username}' | Entered password: '{password}' | DB result: {result}"
        )
        cur.close()
        conn.close()
        if not result:
            flash("Invalid username.", "danger")
        elif result[0].strip() == password.strip():
            session["username"] = username
            if username.startswith("admin"):
                session["user_type"] = "admin"
                return redirect(url_for("hr_eligible"))
            elif username.startswith("C"):
                session["user_type"] = "company"
                return redirect(url_for("company_dashboard"))
            elif username.startswith("4MT"):
                session["user_type"] = "student"
                return redirect(url_for("student_dashboard"))
            else:
                flash("Unknown user type.", "danger")
        else:
            flash("Invalid password.", "danger")
    return render_template("Login_Page.html")


@app.route("/hr/eligible", methods=["GET", "POST"])
def hr_eligible():
    if session.get("user_type") != "admin":
        return redirect(url_for("login"))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT company_name FROM company_module ORDER BY company_name;")
    company_names = [row[0] for row in cur.fetchall()]

    company_name = ""
    if request.method == "POST":
        company_name = request.form.get(
            "company_name", company_names[0] if company_names else ""
        )
    elif company_names:
        company_name = company_names[0]

    students = []
    columns = []
    if company_name:
        cur.execute(
            """
            SELECT s.studentID, 
                   s.student_name, 
                   s.student_branch, 
                   s.student_batch, 
                   s.student_graduating_year, 
                   s.student_backlog, 
                   s.student_backlog_history, 
                   s.student_cgpa, 
                   s.student_status, 
                   s.placement_status
            FROM company_module c
            JOIN company_module_branch cb ON c.companyID = cb.companyID
            JOIN student_module s ON s.student_branch = cb.student_branch
                AND s.student_graduating_year = c.student_graduating_year
                AND s.student_backlog <= c.student_backlog
                AND s.student_backlog_history <= c.student_backlog_history
                AND s.student_cgpa >= c.student_cgpa
            WHERE s.placement_status = 'Not Placed'
              AND c.company_name = %s
            """,
            (company_name,),
        )
        students = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        columns.append("Contact Email")
        students = [list(row) + [f"{row[0].lower()}@mite.ac.in"] for row in students]
    cur.close()
    conn.close()
    return render_template(
        "Human_Resource.html",
        students=students,
        columns=columns,
        company_name=company_name,
        company_names=company_names,
    )


@app.route("/mark_placed", methods=["POST"])
def mark_placed():
    if session.get("user_type") != "admin":
        return redirect(url_for("login"))
    student_id = request.form.get("student_id")
    if student_id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE student_module SET placement_status = 'Placed' WHERE studentID = %s",
            (student_id,),
        )
        conn.commit()
        cur.close()
        conn.close()
    return redirect(request.referrer or url_for("hr_eligible"))


@app.route("/update_students", methods=["GET"])
def update_students():
    if session.get("user_type") != "admin":
        return redirect(url_for("login"))
    student_id = request.args.get("student_id", "").strip()
    branch = request.args.get("branch", "").strip()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT DISTINCT student_branch FROM student_module ORDER BY student_branch;"
    )
    branches = [row[0] for row in cur.fetchall()]

    query = """
        SELECT studentID, student_name, student_branch, student_batch, student_backlog,
               student_backlog_history, student_cgpa, student_status, placement_status
        FROM student_module
        WHERE placement_status != 'Placed'
    """
    params = []
    if branch:
        query += " AND student_branch = %s"
        params.append(branch)
    if student_id:
        query += " AND studentID ILIKE %s"
        params.append(f"%{student_id}%")
    query += " ORDER BY student_branch, studentID"

    cur.execute(query, tuple(params))
    students = [
        dict(
            studentID=row[0],
            student_name=row[1],
            student_branch=row[2],
            student_batch=row[3],
            student_backlog=row[4],
            student_backlog_history=row[5],
            student_cgpa=row[6],
            student_status=row[7],
            placement_status=row[8],
        )
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return render_template(
        "Update_student.html",
        students=students,
        branches=branches,
        selected_branch=branch,
        branch_name=branch if branch else None,
    )


def create_company_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_module (
            companyID VARCHAR(100) PRIMARY KEY,
            company_name VARCHAR(100) NOT NULL,
            company_package DECIMAL(10, 2) NOT NULL,
            company_package_category VARCHAR(100) GENERATED ALWAYS AS (
                CASE
                    WHEN company_package >= 20 THEN 'L4'
                    WHEN company_package >= 10 THEN 'L3'
                    WHEN company_package >= 6 THEN 'L2'
                    ELSE 'L1'
                END
            ) STORED,
            student_graduating_year INT NOT NULL,
            student_backlog INT DEFAULT NULL,
            student_backlog_history INT DEFAULT NULL,
            student_cgpa DECIMAL(10, 2) CHECK (
                student_cgpa >= 0
                AND student_cgpa <= 10
            ) NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_module_branch (
            companyID VARCHAR(100),
            student_branch VARCHAR(100) NOT NULL,
            FOREIGN KEY (companyID) REFERENCES company_module (companyID) ON DELETE CASCADE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/company", methods=["GET", "POST"])
def company_entry():
    create_company_tables()  
    if request.method == "POST":
        companyID = request.form["companyID"]
        company_name = request.form["company_name"]
        company_package = request.form["company_package"]
        student_graduating_year = request.form["student_graduating_year"]
        student_backlog = request.form["student_backlog"]
        student_backlog_history = request.form["student_backlog_history"]
        student_cgpa = request.form["student_cgpa"]
        student_branches = request.form.getlist("student_branch")  

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO company_module (
                    companyID, company_name, company_package, student_graduating_year,
                    student_backlog, student_backlog_history, student_cgpa
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (companyID) DO NOTHING
            """,
                (
                    companyID,
                    company_name,
                    company_package,
                    student_graduating_year,
                    student_backlog,
                    student_backlog_history,
                    student_cgpa,
                ),
            )

            for branch in student_branches:
                cur.execute(
                    """
                    INSERT INTO company_module_branch (companyID, student_branch)
                    VALUES (%s, %s)
                """,
                    (companyID, branch),
                )

            conn.commit()
        finally:
            cur.close()
            conn.close()
        flash(
            "Company record submitted successfully!", "success"
        )
        return redirect(url_for("company_entry"))

    return render_template("Company.html")


@app.route("/company", methods=["GET", "POST"])
def company_dashboard():
    if session.get("user_type") != "company":
        return redirect(url_for("login"))
    if request.method == "POST":
        flash("Company record submitted successfully!", "success")
        return redirect(url_for("company_dashboard"))
    return render_template("Company.html")


@app.route("/student", methods=["GET", "POST"])
def student_dashboard():
    if session.get("user_type") != "student":
        return redirect(url_for("login"))
    if request.method == "POST":
        insert_student(request.form)
        flash("Student record submitted successfully!", "success")
        return redirect(url_for("student_dashboard"))
    rows = get_students()
    return render_template("Student_Form.html", rows=rows)


@app.route("/student/display")
def display_table():
    if session.get("user_type") != "student":
        return redirect(url_for("login"))
    rows = get_students()
    return render_template("Student_Display.html", rows=rows)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/delete_student", methods=["POST"])
def delete_student():
    if session.get("user_type") != "admin":
        return redirect(url_for("login"))
    student_id = request.form.get("student_id")
    if student_id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM student_module WHERE studentID = %s", (student_id,))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(request.referrer or url_for("update_students"))


@app.route("/student_form", methods=["GET", "POST"])
def student_form():
    if request.method == "POST":
        flash("Student details submitted successfully!", "success")
        return redirect(url_for("student_form"))
    return render_template("Student_Form.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
