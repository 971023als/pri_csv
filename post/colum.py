import psycopg2
import csv
import getpass  # 비밀번호 입력을 위해 사용

# 사용자 입력을 통해 데이터베이스 연결 정보 받기
host = input("Enter database host: ")
database = input("Enter database name: ")
user = input("Enter database user: ")
password = getpass.getpass("Enter database password: ")  # 비밀번호는 화면에 표시되지 않도록 입력

try:
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    # 업무별 정보를 쿼리하고 CSV로 저장하는 함수
    def query_and_save(task_type, query, filename):
        cursor.execute(query)
        rows = cursor.fetchall()

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['업무', '처리 목적', '처리 개인정보', '주관 부서', '개인정보 건수 (고유식별정보 건수)', '개인정보 영향도']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in rows:
                writer.writerow({
                    '업무': task_type,
                    '처리 목적': row[0],
                    '처리 개인정보': row[1],
                    '주관 부서': row[2],
                    '개인정보 건수 (고유식별정보 건수)': row[3],
                    '개인정보 영향도': row[4]
                })
            print(f"{filename} has been created.")

    # 각 업무별 쿼리 실행 및 CSV 파일 생성
    query_and_save("수집", "SELECT purpose, data_handled, department, data_count, impact FROM personal_info_flow WHERE task='수집'", 'collect_info_flow.csv')
    query_and_save("저장", "SELECT purpose, data_handled, department, data_count, impact FROM personal_info_flow WHERE task='저장'", 'store_info_flow.csv')
    query_and_save("이용", "SELECT purpose, data_handled, department, data_count, impact FROM personal_info_flow WHERE task='이용'", 'use_info_flow.csv')
    query_and_save("파기", "SELECT purpose, data_handled, department, data_count, impact FROM personal_info_flow WHERE task='파기'", 'dispose_info_flow.csv')

except psycopg2.Error as e:
    print(f"An error occurred: {e}")
finally:
    # 연결 종료
    if conn:
        cursor.close()
        conn.close()
