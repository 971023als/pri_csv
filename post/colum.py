import csv
import mysql.connector
from getpass import getpass  # 비밀번호 안전 입력을 위해 사용

# 사용자 입력을 통해 데이터베이스 연결 정보 받기
host = input("Enter database host: ")
database = input("Enter database name: ")
user = input("Enter database user: ")
password = getpass("Enter database password: ")  # 비밀번호는 화면에 표시되지 않도록 입력

# 데이터베이스 연결 설정
try:
    conn = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    # 쿼리 실행하여 필요한 데이터 추출
    cursor.execute("""
        SELECT t.table_name, c.column_name, c.data_type, t.table_comment
        FROM information_schema.tables t
        JOIN information_schema.columns c ON t.table_name = c.table_name
        WHERE t.table_schema = %s
        ORDER BY t.table_name, c.ordinal_position
    """, (database,))
    
    # CSV 파일 저장
    with open('database_flow_chart.csv', 'w', newline='') as csvfile:
        fieldnames = ['Table', 'Column', 'Data Type', 'Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in cursor:
            writer.writerow({
                'Table': row[0],
                'Column': row[1],
                'Data Type': row[2],
                'Description': row[3]
            })

    print("CSV 파일이 생성되었습니다.")

except mysql.connector.Error as err:
    print("Error: ", err)
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
