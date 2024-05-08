import psycopg2
from graphviz import Digraph
import getpass  # 비밀번호 입력을 위해 사용

# 사용자 입력을 통해 데이터베이스 연결 정보 받기
host = input("Enter database host: ")
database = input("Enter database name: ")
user = input("Enter database user: ")
password = getpass.getpass("Enter database password: ")  # 비밀번호는 화면에 표시되지 않도록 입력

# 데이터베이스 연결 설정
try:
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    # SQL 쿼리 실행
    cursor.execute("SELECT task, purpose, data_handled, department, data_count, impact FROM personal_info_flow")
    rows = cursor.fetchall()

    dot = Digraph(comment='개인정보 처리 흐름도', format='png')

    # 동적으로 노드 생성
    for idx, row in enumerate(rows):
        label = f"{row[0]}\n목적: {row[1]}\n데이터: {row[2]}\n부서: {row[3]}\n데이터 건수: {row[4]}\n영향도: {row[5]}"
        dot.node(str(idx), label)

    # 동적으로 엣지 생성
    for idx in range(len(rows) - 1):
        dot.edge(str(idx), str(idx + 1))

    # 그래프 출력 및 파일 저장
    dot.render('output/dynamic_personal_info_flow', view=True)
    print("흐름도가 생성되었습니다.")

except psycopg2.Error as e:
    print(f"An error occurred: {e}")
finally:
    # 연결 종료
    if conn:
        cursor.close()
        conn.close()
