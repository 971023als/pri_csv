import mysql.connector
from getpass import getpass

# 데이터베이스 연결 정보 받기
host = input("Enter database host: ")
database = input("Enter database name: ")
user = input("Enter database user: ")
password = getpass("Enter database password: ")

try:
    conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
    cursor = conn.cursor()

    # 이용 데이터 쿼리
    use_query = """
    UPDATE users SET last_login = NOW() WHERE user_id = %s
    """
    user_id = input("Enter user ID: ")
    cursor.execute(use_query, (user_id,))
    conn.commit()

    print("User data used for login update.")

except mysql.connector.Error as err:
    print("Error: ", err)
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
