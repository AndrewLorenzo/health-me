from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__,
            template_folder='.',  # agar bisa akses folder form/ dan profile/
            static_folder='form')  # style.css berada di folder form/

# --- Konfigurasi koneksi ke MySQL (XAMPP/phpMyAdmin) ---
db = mysql.connector.connect(
    host="localhost",
    user="root",           # default user XAMPP
    password="",           # default password kosong
    database="software engineering"  # pastikan DB ini sudah kamu buat di phpMyAdmin
)

# --- Buat tabel jika belum ada ---
# cursor = db.cursor()
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS users (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         nama VARCHAR(100),
#         email VARCHAR(100),
#         umur INT,
#         alamat TEXT
#     )
# """)
# db.commit()

# --- login dan session --- 
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/home')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = db
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user['id']
            cursor.execute("SELECT * FROM profiles WHERE user_id = %s", (user['id'],))
            profile = cursor.fetchone()
            if profile:
                return redirect('/home')
            else:
                return redirect('/form')
        return render_template('login.html', error='Invalid credentials')
    return render_template('login/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = db
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        return redirect('/login')
    return render_template('signup/signup.html')

@app.route('/form', methods=['GET', 'POST'])
def setup_profile():
    if request.method == 'POST':
        age = request.form['age']
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        user_id = session['user_id']
        conn = db
        cursor = conn.cursor()
        cursor.execute("INSERT INTO profiles (user_id, age, weight, height) VALUES (%s, %s, %s, %s)",
                       (user_id, age, weight, height))
        conn.commit()
        return redirect('/home')
    return render_template('setup_profile.html')

@app.route('/home')
def home():
    user_id = session['user_id']
    conn = db
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM profiles WHERE user_id = %s", (user_id,))
    profile = cursor.fetchone()
    bmi = profile['weight'] / ((profile['height'] / 100) ** 2)
    if bmi < 18.5:
        category = "Underweight"
        advice = "Konsumsi makanan tinggi kalori dan protein. Lakukan olahraga ringan seperti yoga."
    elif 18.5 <= bmi < 25:
        category = "Normal"
        advice = "Pertahankan pola makan seimbang dan aktivitas fisik teratur seperti jogging."
    else:
        category = "Overweight"
        advice = "Kurangi makanan berlemak dan lakukan olahraga seperti bersepeda atau berenang."
    return render_template('home/home.html', category=category, advice=advice)


# --- Halaman form ---
@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        firstName = request.form['first-name']
        lastName = request.form['last-name']
        age = request.form['age']
        height = request.form['height']
        weight = request.form['weight']
        sex = request.form['sex']
        bmi = int(weight) / ((int(height) / 100) ** 2)
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (FirstName, LastName, Age, Height, Weight, Sex, BMI) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (firstName, lastName, age, height, weight, sex, bmi))
        db.commit()
        return redirect('/home')
    return render_template('form/form.html')

# --- Submit form ke database ---
# @app.route('/submit', methods=['POST'])
# def submit():
    
#     # user_id = cursor.lastrowid

#     return redirect(url_for('profile', user_id=user_id))

# --- Halaman profil user ---
@app.route('/profile/<int:user_id>')
def profile(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE UserID = %s", (user_id,))
    user = cursor.fetchone()
    return render_template('profile/profile.html', user=user)

# --- Halaman edit data user ---
@app.route('/edit/<int:user_id>')
def edit(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE UserID = %s", (user_id,))
    user = cursor.fetchone()
    return render_template('form/form.html', user=user, edit=True)

# --- Proses update data ---
@app.route('/update/<int:user_id>', methods=['POST'])
def update(user_id):
    firstName = request.form['first-name']
    lastName = request.form['last-name']
    age = request.form['age']
    height = request.form['height']
    weight = request.form['weight']
    sex = request.form['sex']
    bmi = int(weight) / ((int(height) / 100) ** 2)
    # bloodType = request.form['blood-type']

    cursor = db.cursor()
    cursor.execute("""
        UPDATE users SET FirstName = %s, LastName = %s, Age = %s, Height = %s, Weight = %s, Sex = %s, BMI = %s WHERE UserID = %s
    """, (firstName, lastName, age, height, weight, sex, bmi, user_id))
    db.commit()

    return redirect(url_for('profile', user_id=user_id))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# --- Jalankan app ---
if __name__ == '__main__':
    app.run(debug=True)
