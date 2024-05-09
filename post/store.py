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

    # 저장 관련 데이터 조회 쿼리
    storage_related_query = """
    SELECT table_name, column_name, data_type, is_nullable, column_comment
    FROM information_schema.columns
    WHERE table_schema = %s AND (column_name LIKE '%store%' OR column_name LIKE '%save%' OR column_name LIKE '%keep%')
    ORDER BY table_name, ordinal_position;
    """
    cursor.execute(storage_related_query, (database,))
    results = cursor.fetchall()

    # 결과 출력
    print("저장 관련 데이터:")
    for row in results:
        print("테이블: {}, 컬럼: {}, 데이터 타입: {}, NULL 허용: {}, 설명: {}".format(
            row[0], row[1], row[2], row[3], row[4]
        ))

except mysql.connector.Error as err:
    print("Error: ", err)
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
