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
        # Cek apakah email sudah terdaftar
        cursor.execute("SELECT * FROM UsersAccount WHERE Email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return render_template('signup/signup.html', error='Email is already registered')
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
    return render_template('form/form.html', user=None)

@app.route('/home')
def home():
    user_id = session['UserID']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM UsersProfiles WHERE UserID = %s", (user_id,))
    profile = cursor.fetchone()

    bmi = profile['BMI'] if profile else 0
    if bmi < 18.5:
        category = "Underweight"
        message = "Jangan menyerah! Setiap langkah kecil membawa perubahan besar 💪"
    elif 18.5 <= bmi < 25:
        category = "Normal"
        message = "Pertahankan ritmemu! Kamu sedang berada di jalur yang tepat! ✅"
    else:
        category = "Overweight"
        message = "Mulai hari ini, kamu bisa bergerak lebih sehat! Kamu mampu! 🔥"

    tips = []
    if category == "Normal":
        tips = [
            "Konsisten dengan pola makan sehat",
            "Sarapan rutin",
            "Makan 3x + 1–2 snack sehat",
            "Aktif fisik tiap hari minimal 30 menit",
            "Tidur cukup (7–8 jam)",
            "Kelola stres",
            "Pantau berat badan mingguan"
        ]

    return render_template('home/home.html',
                           category=category,
                           message=message,
                           tips=tips)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session['UserID']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
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
        return redirect('/profile')

    return render_template('form/form.html', user=profile, edit=bool(profile))

@app.route('/activity')
def activity():
    user_id = session['UserID']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT BMI FROM UsersProfiles WHERE UserID = %s", (user_id,))
    row = cursor.fetchone()

    bmi = row['BMI']
    if bmi < 18.5:
        category = "Underweight"
        activities = [
            "Latihan kekuatan (3–4x/minggu): angkat beban ringan/sedang",
            "Yoga atau Pilates",
            "Hindari olahraga kardio berlebihan"
        ]
    elif 18.5 <= bmi < 25:
        category = "Normal"
        activities = [
            "Kardio ringan–sedang: jalan cepat, jogging, bersepeda 150 menit/minggu",
            "Latihan kekuatan 2–3x/minggu",
            "Aktivitas harian aktif: naik tangga, jalan kaki"
        ]
    else:
        category = "Overweight"
        activities = [
            "Olahraga aerobik: jalan cepat, berenang, senam low impact (30–60 menit/hari)",
            "Latihan beban 2–3x/minggu untuk meningkatkan metabolisme",
            "Aktif harian: hindari duduk terlalu lama"
        ]

    return render_template('activity/activity.html', category=category, activities=activities)

@app.route('/foods')
def foods():
    user_id = session['UserID']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT BMI FROM UsersProfiles WHERE UserID = %s", (user_id,))
    row = cursor.fetchone()

    bmi = row['BMI']
    if bmi < 18.5:
        category = "Underweight"
        foods = [
            "Makanan tinggi kalori: alpukat, kacang-kacangan, keju",
            "Protein tinggi: telur, dada ayam, susu full cream",
            "Karbo kompleks: nasi merah, kentang, ubi",
            "Snack sehat: smoothie, roti selai kacang"
        ]
    elif 18.5 <= bmi < 25:
        category = "Normal"
        foods = [
            "Porsi seimbang: ½ sayur & buah, ¼ protein, ¼ karbohidrat",
            "Protein sedang: ayam, ikan, telur",
            "Lemak sehat: alpukat, kacang, minyak zaitun",
            "Cukup air putih: 8 – 10 gelas/hari"
        ]
    else:
        category = "Overweight"
        foods = [
            "Kalori terkontrol: makanan tinggi serat, porsi kecil",
            "Perbanyak sayur dan buah",
            "Kurangi gula & gorengan",
            "Protein rendah lemak: putih telur, dada ayam tanpa kulit"
        ]

    return render_template('foods/foods.html', category=category, foods=foods)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/about us')
def about_us():
    return render_template('about us/about us.html')

if __name__ == '__main__':
    app.run(debug=True)