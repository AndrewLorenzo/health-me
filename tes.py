import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    # password="passwordmu",
    database="software engineering"
)

print("Koneksi berhasil!" if db.is_connected() else "Gagal terkoneksi.")
