from flask import Flask, render_template, request, redirect, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'secret_key'

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='software engineering',  # ganti sesuai nama database Anda
        user='root',
        password=''  # ganti sesuai konfigurasi MySQL Anda
    )

@app.route('/')
def index():
    if 'UserID' in session:
        return redirect('/home')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM UsersAccount WHERE Email=%s AND Pass=%s", (email, password))
        user = cursor.fetchone()
        if user:
            session['UserID'] = user['UserID']
            cursor.execute("SELECT * FROM UsersProfiles WHERE UserID = %s", (user['UserID'],))
            profile = cursor.fetchone()
            if profile:
                return redirect('/home')
            else:
                return redirect('/setup_profile')
        return render_template('login/login.html', error='Account or password error')
    return render_template('login/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return render_template('signup/signup.html', error='Passwords do not match')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO UsersAccount (Email, Pass) VALUES (%s, %s)", (email, password))
        conn.commit()
        # Ambil UserID dari user yang baru dibuat
        cursor.execute("SELECT UserID FROM UsersAccount WHERE Email=%s", (email,))
        user = cursor.fetchone()
        session['UserID'] = user[0]  # simpan UserID ke session
        return redirect('/login')
    return render_template('signup/signup.html')

@app.route('/setup_profile', methods=['GET', 'POST'])
def setup_profile():
    if request.method == 'POST':
        firstName = request.form['first-name']
        lastName = request.form['last-name']
        age = request.form['age']
        height = request.form['height']
        weight = request.form['weight']
        sex = request.form['sex']
        bmi:float = float(weight) / ((float(height) / 100) ** 2)
        user_id = session['UserID']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO UsersProfiles (UserID, FirstName, LastName, Age, Height, Weight, Sex, BMI) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (user_id, firstName, lastName, age, height, weight, sex, bmi))
        conn.commit()
        return redirect('/home')
    return render_template('form/form.html')

@app.route('/home')
def home():
    user_id = session['UserID']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM UsersProfiles WHERE UserID = %s", (user_id, ))
    profile = cursor.fetchone()
    bmi = profile['BMI'] if profile else 0
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal"
    else:
        category = "Overweight"

    # Semua konten saran & tips disimpan di dictionary
    advice_data = {
        "Underweight": {
            "goals": "Meningkatkan massa otot dan berat badan secara sehat",
            "activity": [
                "Latihan kekuatan 3–4x/minggu: angkat beban ringan/sedang, resistance band",
                "Yoga atau Pilates",
                "Hindari olahraga kardio berlebihan"
            ],
            "food": [
                "Alpukat, kacang-kacangan, keju, minyak zaitun",
                "Protein tinggi: telur, ayam, tempe, susu full cream",
                "Karbo kompleks: nasi merah, ubi, roti gandum",
                "Snack: smoothie, roti selai kacang"
            ]
        },
        "Normal": {
            "goals": "Mempertahankan berat badan ideal dan menjaga kebugaran",
            "activity": [
                "Kardio ringan–sedang: jalan cepat, bersepeda 150 menit/minggu",
                "Latihan kekuatan 2–3x/minggu",
                "Aktivitas harian aktif: jalan kaki, naik tangga"
            ],
            "food": [
                "Porsi seimbang: ½ sayur & buah, ¼ protein, ¼ karbo",
                "Protein sedang: ayam, ikan, telur",
                "Lemak sehat: alpukat, kacang",
                "Cukup air putih: 8–10 gelas/hari"
            ],
            "tips": [
                "Konsisten dengan pola makan sehat",
                "Sarapan rutin",
                "Makan 3x + 1–2 snack sehat",
                "Aktif fisik tiap hari minimal 30 menit",
                "Tidur cukup (7–8 jam)",
                "Kelola stres",
                "Pantau berat badan mingguan"
            ]
        },
        "Overweight": {
            "goals": "Mengurangi berat badan dan lemak tubuh secara bertahap",
            "activity": [
                "Olahraga aerobik: jalan cepat, senam 30–60 menit/hari",
                "Latihan beban 2–3x/minggu",
                "Aktif sepanjang hari: kurangi duduk lama"
            ],
            "food": [
                "Kalori terkontrol: porsi kecil, makanan tinggi serat",
                "Sayur & buah lebih banyak",
                "Kurangi gula & gorengan",
                "Protein tinggi & rendah lemak: dada ayam, ikan kukus"
            ]
        }
    }

    return render_template(
        'home page/home.html',
        category=category,
        advice=advice_data[category],
        show_tips=(category == "Normal")
    )

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session['UserID']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # if request.method == 'POST':
    #     firstName = request.form['first-name']
    #     lastName = request.form['last-name']
    #     age = request.form['age']
    #     height = request.form['height']
    #     weight = request.form['weight']
    #     sex = request.form['sex']
    #     bmi:float = float(weight) / ((float(height) / 100) ** 2)
    #     cursor.execute("""
    #         UPDATE users SET FirstName = %s, LastName = %s, Age = %s, Height = %s, Weight = %s, Sex = %s, BMI = %s WHERE UserID = %s
    #     """, (firstName, lastName, age, height, weight, sex, bmi, user_id))
    #     conn.commit()
    cursor.execute("SELECT * FROM UsersProfiles WHERE UserID = %s", (user_id,))
    user = cursor.fetchone()
    return render_template('profile/profile.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session['UserID']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Cek apakah profil sudah ada
    cursor.execute("SELECT * FROM UsersProfiles WHERE UserID = %s", (user_id,))
    profile = cursor.fetchone()

    if request.method == 'POST':
        firstName = request.form['first-name']
        lastName = request.form['last-name']
        age = int(request.form['age'])
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        sex = request.form['sex']
        bmi = weight / ((height / 100) ** 2)
        cursor.execute("""
            UPDATE UsersProfiles SET FirstName=%s, LastName=%s, Age=%s, Height=%s, Weight=%s, Sex=%s, BMI=%s WHERE UserID=%s
        """, (firstName, lastName, age, height, weight, sex, bmi, user_id))
        conn.commit()
        return redirect('/home')

    return render_template('form/form.html', user=profile, edit=bool(profile))


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)