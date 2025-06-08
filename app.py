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
    nama = request.form['nama']
    email = request.form['email']
    umur = request.form['umur']
    alamat = request.form['alamat']

    cursor = db.cursor()
    cursor.execute("INSERT INTO users (name, email, age, address) VALUES (%s, %s, %s, %s)",
                   (nama, email, umur, alamat))
    db.commit()
    user_id = cursor.lastrowid

    return redirect(url_for('profile', user_id=user_id))

# --- Halaman profil user ---
@app.route('/profile/<int:user_id>')
def profile(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    return render_template('profile/profile.html', user=user)

# --- Halaman edit data user ---
@app.route('/edit/<int:user_id>')
def edit(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    return render_template('form/form.html', user=user, edit=True)

# --- Proses update data ---
@app.route('/update/<int:user_id>', methods=['POST'])
def update(user_id):
    nama = request.form['nama']
    email = request.form['email']
    umur = request.form['umur']
    alamat = request.form['alamat']

    cursor = db.cursor()
    cursor.execute("""
        UPDATE users SET name = %s, email = %s, age = %s, address = %s WHERE id = %s
    """, (nama, email, umur, alamat, user_id))
    db.commit()

    return redirect(url_for('profile', user_id=user_id))

# --- Jalankan app ---
if __name__ == '__main__':
    app.run(debug=True)
