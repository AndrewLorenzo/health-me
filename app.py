from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

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

# --- Halaman form ---
@app.route('/')
def form():
    return render_template('form/form.html')

# --- Submit form ke database ---
@app.route('/submit', methods=['POST'])
def submit():
    firstName = request.form['first-name']
    lastName = request.form['last-name']
    age = request.form['age']
    height = request.form['height']
    weight = request.form['weight']
    sex = request.form['sex']
    bmi = int(weight) / ((int(height) / 100) ** 2)
    # bloodType = request.form['blood-type']


    cursor = db.cursor()
    cursor.execute("INSERT INTO users (FirstName, LastName, Age, Height, Weight, Sex, BMI) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (firstName, lastName, age, height, weight, sex, bmi))
    db.commit()
    user_id = cursor.lastrowid

    return redirect(url_for('profile', user_id=user_id))

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

# --- Jalankan app ---
if __name__ == '__main__':
    app.run(debug=True)
