from flask import Flask, render_template, request, redirect, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'secret_key'

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='healthme',  # ganti sesuai nama database Anda
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
        message = "Don't give up! Every small step brings big changes 💪"
    elif 18.5 <= bmi < 25:
        category = "Normal"
        message = "Keep up the pace! You are on the right track! ✅"
    else:
        category = "Overweight"
        message = "Starting today, you can move towards a healthier you! You can do it! 🔥"

    return render_template('home/home.html',
                           category=category,
                           message=message)

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
        age = request.form['age']
        height = request.form['height']
        weight = request.form['weight']
        sex = request.form['sex']
        error = None
        try:
            age = int(age)
            height = float(height)
            weight = float(weight)
            if height <= 0 or weight <= 0 or age <= 0:
                error = "Age, height, and weight must be numbers greater than 0."
        except ValueError:
            error = "Age must be an integer, and height and weight must be decimal numbers."
        if error:
            return render_template('form/form.html', user=profile, edit=True, error=error)
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
            {
                "image": "assets/dumbbell.png",
                "title": "Strength training",
                "desc": "(3–4 times/week) light to moderate weight lifting, resistance bands, bodyweight training."
            },
            {
                "image": "assets/yoga.png",
                "title": "Yoga or Pilates:",
                "desc": "help build muscle and flexibility."
            },
            {
                "image": "assets/running.png",
                "title": "Avoid excessive cardio exercise",
                "desc": "that burns a lot of calories."
            }
        ]
    elif 18.5 <= bmi < 25:
        category = "Normal"
        activities = [
            {
                "image": "assets/dumbbell.png",
                "title": "Strength training",
                "desc": "(2-3 times/week) light to moderate weight lifting, resistance bands, bodyweight training."
            },
            {
                "image": "assets/stairs.png",
                "title": "Active daily activities",
                "desc": "stair climbing, walking, regular stretching"
            },
            {
                "image": "assets/running.png",
                "title": "Light-moderate cardio",
                "desc": "brisk walking, jogging, cycling (150 minutes per week)."
            }
        ]
    else:
        category = "Overweight"
        activities = [
            {
                "image": "assets/dumbbell.png",
                "title": "Weight training",
                "desc": "2–3 times/week to increase metabolism."
            },
            {
                "image": "assets/stairs.png",
                "title": "Active daily activities",
                "desc": "Brisk walking, swimming, low-impact gymnastics (30–60 minutes/day)."
            },
            {
                "image": "assets/couch.png",
                "title": "Cardio exercise",
                "desc": " Please avoid sitting too long, move more."
            }
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
            {
                "image": "assets/underweight1.png",
                "title1": "Rich in healthy calories",
                "title2": "High protein sources",
                "desc1": "avocado, nuts, seeds, cheese, olive oil.",
                "desc2": "eggs, chicken breast, tempeh, tofu, full cream milk, Greek yogurt."
            },
            {
                "image": "assets/underweight2.png",
                "title1": "Complex carbohydrates",
                "title2": "Healthy high energy snacks",
                "desc1": "brown rice, potatoes, sweet potatoes, whole wheat bread.",
                "desc2": "smoothies, bread with peanut butter, granola."
            }
        ]
    elif 18.5 <= bmi < 25:
        category = "Normal"
        foods = [
            {
                "image": "assets/normal1.png",
                "title1": "Balanced portion",
                "title2": "Medium protein",
                "desc1": "½ vegetables and fruits, ¼ protein, ¼ complex carbohydrates.",
                "desc2": "chicken, fish, eggs, tofu, tempeh."
            },
            {
                "image": "assets/normal2.png",
                "title1": "Healthy fats",
                "title2": "Adequate water intake",
                "desc1": "avocado, nuts, olive oil.",
                "desc2": "8–10 glasses per day."
            }
        ]
    else:
        category = "Overweight"
        foods = [
            {
                "image": "assets/overweight1.png",
                "title1": "Controlled calories",
                "title2": "Increase vegetables and fruits",
                "desc1": "reduce portion sizes, choose low-calorie but high-fiber foods.",
                "desc2": "helps you feel full longer."
            },
            {
                "image": "assets/overweight2.png",
                "title1": "Reduce sugar and fried foods",
                "title2": "High-protein and low-fat",
                "desc1": "replace with boiled or grilled options.",
                "desc2": "egg whites, skinless chicken breast, steamed fish."
            }
        ]

    return render_template('foods/foods.html', category=category, foods=foods)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/about us')
def about_us():
    return render_template('about us/about us.html')


@app.route('/schedule')
def schedule():
    user_id = session['UserID']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT BMI FROM UsersProfiles WHERE UserID = %s", (user_id,))
    row = cursor.fetchone()

    meal_plans = {
        "Underweight": [
            {
                "Breakfast": "Oatmeal with whole milk, banana, honey, peanut butter",
                "WorkoutMorning": "Light strength training or yoga (20 mins)",
                "Lunch": "Grilled chicken breast, brown rice, avocado, sautéed vegetables",
                "WorkoutAfternoon": "Short walk or stretching (15 mins)",
                "Dinner": "Salmon, mashed sweet potatoes, broccoli with butter",
                "WorkoutEvening": "Pilates or light bodyweight training (15–20 mins)"
            },
            {
                "Breakfast": "Scrambled eggs, toast, yogurt with berries",
                "WorkoutMorning": "Yoga or resistance band exercises",
                "Lunch": "Beef stir-fry with rice and vegetables",
                "WorkoutAfternoon": "Light cycling or brisk walking",
                "Dinner": "Chicken curry with rice and green beans",
                "WorkoutEvening": "Stretching + meditation"
            },
            {
                "Breakfast": "Pancakes with syrup, butter, and a glass of milk",
                "WorkoutMorning": "Bodyweight squats and light dumbbell curls",
                "Lunch": "Tuna sandwich, eggs, avocado, fruit",
                "WorkoutAfternoon": "Leisure walk or low-impact cardio",
                "Dinner": "Baked chicken thighs, couscous, roasted carrots",
                "WorkoutEvening": "Light yoga for flexibility"
            },
            {
                "Breakfast": "Cereal with whole milk, banana, boiled eggs",
                "WorkoutMorning": "Upper body dumbbell workout (light)",
                "Lunch": "Pasta with meatballs, side salad, parmesan",
                "WorkoutAfternoon": "Short stairs or walking indoors",
                "Dinner": "Grilled steak, baked potatoes, spinach",
                "WorkoutEvening": "Foam rolling and stretching"
            },
            {
                "Breakfast": "French toast, banana slices, milk",
                "WorkoutMorning": "Core workout and breathing exercises",
                "Lunch": "Chicken wrap with cheese and veggies",
                "WorkoutAfternoon": "Walk to nearby park or store",
                "Dinner": "Baked salmon, rice pilaf, roasted asparagus",
                "WorkoutEvening": "Pilates or posture training"
            },
            {
                "Breakfast": "Omelet with cheese, mushrooms, toast",
                "WorkoutMorning": "Morning yoga flow (15 mins)",
                "Lunch": "Turkey sandwich, cheese, potato salad",
                "WorkoutAfternoon": "Stretching or light mobility routine",
                "Dinner": "Creamy pasta with shrimp, garlic bread",
                "WorkoutEvening": "Calm walk or dance workout"
            },
            {
                "Breakfast": "Smoothie bowl with granola",
                "WorkoutMorning": "Strength training full body (light)",
                "Lunch": "Fried rice with egg, chicken, vegetables",
                "WorkoutAfternoon": "Outdoor activity or sports",
                "Dinner": "Lamb stew with potatoes and carrots",
                "WorkoutEvening": "Meditation and stretches"
            }
        ],
        "Normal": [
            {
                "Breakfast": "Boiled egg, toast, and fruit",
                "WorkoutMorning": "Jogging or light cardio (20 mins)",
                "Lunch": "Grilled chicken, quinoa, mixed veggies",
                "WorkoutAfternoon": "Walk or mobility stretch",
                "Dinner": "Baked salmon, mashed potatoes, broccoli",
                "WorkoutEvening": "Stretching or home workout"
            },
            {
                "Breakfast": "Smoothie with banana, yogurt, peanut butter",
                "WorkoutMorning": "Full-body circuit (moderate)",
                "Lunch": "Turkey sandwich with salad",
                "WorkoutAfternoon": "Walking while listening to music",
                "Dinner": "Stir-fried tofu with brown rice",
                "WorkoutEvening": "Dance session (20 mins)"
            },
            {
                "Breakfast": "Scrambled eggs and toast",
                "WorkoutMorning": "Cycling (15–30 mins)",
                "Lunch": "Chicken Caesar salad with bread",
                "WorkoutAfternoon": "Light jog or walk",
                "Dinner": "Tilapia with couscous and spinach",
                "WorkoutEvening": "Stretch, foam roll"
            },
            {
                "Breakfast": "Overnight oats with fruit",
                "WorkoutMorning": "Core and stability exercises",
                "Lunch": "Beef wrap with veggies and hummus",
                "WorkoutAfternoon": "Mobility work or casual walk",
                "Dinner": "Grilled chicken, vegetables, sweet potato",
                "WorkoutEvening": "Yoga or light pilates"
            },
            {
                "Breakfast": "Whole grain cereal with milk",
                "WorkoutMorning": "Brisk walk or jump rope",
                "Lunch": "Shrimp fried rice",
                "WorkoutAfternoon": "Dance or Zumba",
                "Dinner": "Vegetable lasagna, side salad",
                "WorkoutEvening": "Relaxing movement session"
            },
            {
                "Breakfast": "Omelet with tomato and cheese",
                "WorkoutMorning": "Full-body dumbbell workout",
                "Lunch": "Pasta with chicken and spinach",
                "WorkoutAfternoon": "House chores actively",
                "Dinner": "Sautéed tofu, brown rice, vegetables",
                "WorkoutEvening": "Gentle yoga and cool down"
            },
            {
                "Breakfast": "Granola with yogurt and berries",
                "WorkoutMorning": "Jog in nature",
                "Lunch": "Chicken burrito bowl",
                "WorkoutAfternoon": "Outdoor walk",
                "Dinner": "Steamed fish with vegetables",
                "WorkoutEvening": "Stretch or short bike ride"
            }
        ],
        "Overweight": [
            {
                "Breakfast": "Boiled eggs and apple slices",
                "WorkoutMorning": "Morning walk (20–30 mins)",
                "Lunch": "Grilled chicken salad",
                "WorkoutAfternoon": "Chair yoga",
                "Dinner": "Baked fish, steamed broccoli",
                "WorkoutEvening": "Stretch and meditation"
            },
            {
                "Breakfast": "Smoothie with spinach, banana, almond milk",
                "WorkoutMorning": "Seated strength routine",
                "Lunch": "Turkey lettuce wraps",
                "WorkoutAfternoon": "Short walk indoors",
                "Dinner": "Grilled tofu, brown rice",
                "WorkoutEvening": "Gentle stretching"
            },
            {
                "Breakfast": "Oatmeal with berries",
                "WorkoutMorning": "Low-impact cardio video",
                "Lunch": "Vegetable stir-fry with tofu",
                "WorkoutAfternoon": "Standing stretches",
                "Dinner": "Chicken soup with vegetables",
                "WorkoutEvening": "Breathing and stretch"
            },
            {
                "Breakfast": "Greek yogurt with nuts",
                "WorkoutMorning": "Chair cardio workout",
                "Lunch": "Tuna salad with greens",
                "WorkoutAfternoon": "Walking around house",
                "Dinner": "Grilled salmon with asparagus",
                "WorkoutEvening": "Foam roll or massage"
            },
            {
                "Breakfast": "Avocado toast (1 slice bread)",
                "WorkoutMorning": "Gentle yoga flow",
                "Lunch": "Zucchini noodles with turkey meatballs",
                "WorkoutAfternoon": "Walk with breaks",
                "Dinner": "Grilled chicken, brown rice",
                "WorkoutEvening": "Neck and back stretch"
            },
            {
                "Breakfast": "Chia pudding with fruit",
                "WorkoutMorning": "Dance follow-along (easy)",
                "Lunch": "Vegetable soup, multigrain toast",
                "WorkoutAfternoon": "Breathwork + mobility",
                "Dinner": "Steamed fish, veggie mix",
                "WorkoutEvening": "Relaxation routine"
            },
            {
                "Breakfast": "Scrambled egg whites, orange",
                "WorkoutMorning": "Walk to local store",
                "Lunch": "Chicken wrap with greens",
                "WorkoutAfternoon": "Chair tai-chi",
                "Dinner": "Vegetarian chili",
                "WorkoutEvening": "Mindful stretching"
            }
        ]
    }
    bmi = row['BMI']
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal"
    else:
        category = "Overweight"
    return render_template('schedule/schedule.html', category=category, meals=meal_plans[category])

if __name__ == '__main__':
    app.run(debug=True)