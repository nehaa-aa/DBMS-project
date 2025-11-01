from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = Config.SECRET_KEY


# -------------------- DB & Helper Functions --------------------

def db():
    return mysql.connector.connect(
        host=Config.DB_HOST, database=Config.DB_NAME,
        user=Config.DB_USER, password=Config.DB_PASSWORD
    )

def query_db(query, args=(), fetchone=False, commit=False):
    """Utility function to handle DB queries safely and cleanly."""
    con = db()
    cur = con.cursor(dictionary=True)
    cur.execute(query, args)
    data = cur.fetchone() if fetchone else cur.fetchall()
    if commit:
        con.commit()
    cur.close()
    con.close()
    return data

def logged_in():
    return 'user_id' in session


# -------------------- ROUTES --------------------

@app.get('/')
def index():
    return render_template('index.html')


# ---- Signup ----
@app.get('/signup')
def signup_page():
    return render_template('signup.html')

@app.post('/signup')
def signup():
    name = request.form['name']
    email = request.form['email']
    age = request.form.get('age') or None
    gender = request.form.get('gender') or 'Other'
    pw = generate_password_hash(request.form['password'])

    query_db(
        "INSERT INTO Users (name, email, age, gender, password_hash) VALUES (%s, %s, %s, %s, %s)",
        (name, email, age, gender, pw),
        commit=True
    )
    return redirect(url_for('login_page'))


# ---- Login ----
@app.get('/login')
def login_page():
    return render_template('login.html')

@app.post('/login')
def login():
    email = request.form['email']
    password = request.form['password']

    row = query_db("SELECT id, name, password_hash FROM Users WHERE email=%s", (email,), fetchone=True)
    if not row or not check_password_hash(row['password_hash'], password):
        return render_template('login.html', error="Invalid credentials")

    session['user_id'] = row['id']
    session['user_name'] = row['name']
    return redirect(url_for('dashboard'))


# ---- Logout ----
@app.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ---- Dashboard ----
@app.get('/dashboard')
def dashboard():
    if not logged_in():
        return redirect(url_for('login_page'))
    return render_template('dashboard.html', user=session.get('user_name'))


# ---- Biometrics ----
@app.get('/biometrics')
def biometrics_page():
    if not logged_in():
        return redirect(url_for('login_page'))
    return render_template('biometrics.html')

@app.post('/biometrics')
def biometrics_save():
    if not logged_in():
        return redirect(url_for('login_page'))

    h = float(request.form['height_cm'])
    w = float(request.form['weight_kg'])
    goal = request.form.get('goal', 'maintain')

    existing = query_db("SELECT id FROM Biometrics WHERE user_id=%s", (session['user_id'],), fetchone=True)
    if existing:
        query_db(
            "UPDATE Biometrics SET height_cm=%s, weight_kg=%s, goal=%s WHERE user_id=%s",
            (h, w, goal, session['user_id']),
            commit=True
        )
    else:
        query_db(
            "INSERT INTO Biometrics (user_id, height_cm, weight_kg, goal) VALUES (%s, %s, %s, %s)",
            (session['user_id'], h, w, goal),
            commit=True
        )

    return redirect(url_for('reports'))


# ---- Meal Logging ----
@app.get('/meal')
def meal_page():
    if not logged_in():
        return redirect(url_for('login_page'))
    foods = query_db("SELECT id, name FROM Food_Items ORDER BY name")
    return render_template('meal.html', foods=foods)

@app.post('/meal')
def meal_save():
    if not logged_in():
        return redirect(url_for('login_page'))

    food_id = int(request.form['food_id'])
    qty = float(request.form['quantity_g'])
    when = request.form.get('eaten_at') or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    query_db(
        "INSERT INTO Meal_Logs (user_id, food_id, eaten_at, quantity_g) VALUES (%s, %s, %s, %s)",
        (session['user_id'], food_id, when, qty),
        commit=True
    )

    return redirect(url_for('reports'))


# ---- Reports ----
@app.get('/reports')
def reports():
    if not logged_in():
        return redirect(url_for('login_page'))

    bio = query_db(
        "SELECT bmi, height_cm, weight_kg, goal FROM Biometrics WHERE user_id=%s",
        (session['user_id'],),
        fetchone=True
    )
    meals = query_db(
        """SELECT ml.id, fi.name, ml.eaten_at, ml.quantity_g, ml.calories
           FROM Meal_Logs ml 
           JOIN Food_Items fi ON fi.id = ml.food_id
           WHERE ml.user_id=%s
           ORDER BY ml.eaten_at DESC
           LIMIT 5""",
        (session['user_id'],)
    )

    return render_template('reports.html', bio=bio, meals=meals)


# ---- Delete Meal ----
@app.post('/meal/delete/<int:meal_id>')
def meal_delete(meal_id):
    if not logged_in():
        return redirect(url_for('login_page'))
    query_db(
        "DELETE FROM Meal_Logs WHERE id=%s AND user_id=%s",
        (meal_id, session['user_id']),
        commit=True
    )
    return redirect(url_for('reports'))


# -------------------- Run --------------------
if __name__ == '__main__':
    app.run(debug=True, port=5001)
