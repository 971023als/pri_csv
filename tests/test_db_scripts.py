"""post/ DB 스크립트의 오류 처리 및 정리(cleanup) 동작 테스트.

외부 DB·패키지 설치 없이 표준 라이브러리만 사용한다.
가짜 mysql.connector / psycopg2 / graphviz 모듈을 임시 디렉터리에 만들어
PYTHONPATH로 주입하고, 시나리오별로 스크립트를 서브프로세스로 실행해 검증한다.

실행: python3 -m unittest tests/test_db_scripts.py (저장소 루트에서)
"""
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POST_DIR = os.path.join(REPO_ROOT, "post")

MYSQL_CONNECTOR = '''
import os
class Error(Exception): pass
class _Cur:
    def execute(self, q, p=None):
        if os.environ.get("STUB_MODE") == "query_fail":
            raise Error("simulated query failure")
    def fetchall(self): return []
    def __iter__(self): return iter([])
    def close(self): print("STUB_CURSOR_CLOSED")
class _Conn:
    def cursor(self):
        if os.environ.get("STUB_MODE") == "cursor_fail":
            raise Error("simulated cursor failure")
        return _Cur()
    def is_connected(self): return True
    def commit(self): pass
    def close(self): print("STUB_CONN_CLOSED")
def connect(**kw):
    if os.environ.get("STUB_MODE") == "connect_fail":
        raise Error("simulated connect failure")
    return _Conn()
'''

PSYCOPG2 = '''
import os
class Error(Exception): pass
class _Cur:
    def execute(self, q, p=None):
        if os.environ.get("STUB_MODE") == "query_fail":
            raise Error("simulated query failure")
    def fetchall(self): return []
    def close(self): print("STUB_CURSOR_CLOSED")
class _Conn:
    def cursor(self):
        if os.environ.get("STUB_MODE") == "cursor_fail":
            raise Error("simulated cursor failure")
        return _Cur()
    def close(self): print("STUB_CONN_CLOSED")
def connect(**kw):
    if os.environ.get("STUB_MODE") == "connect_fail":
        raise Error("simulated connect failure")
    return _Conn()
'''

GRAPHVIZ = '''
class Digraph:
    def __init__(self, **kw): pass
    def node(self, *a): pass
    def edge(self, *a): pass
    def render(self, *a, **kw): pass
'''

MYSQL_SCRIPTS = ["collect.py", "Dispose.py", "store.py", "use.py", "colum.py"]
ALL_SCRIPTS = MYSQL_SCRIPTS + ["draw.py"]
STDIN_DATA = "host\ndb\nuser\npw\n42\n"


def _write_stubs(tmp):
    pkgs = {
        "mysql/__init__.py": "",
        "mysql/connector.py": MYSQL_CONNECTOR,
        "psycopg2/__init__.py": PSYCOPG2,
        "graphviz/__init__.py": GRAPHVIZ,
    }
    for rel, content in pkgs.items():
        path = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


def _run_script(tmp, script, mode):
    env = dict(os.environ)
    env["PYTHONPATH"] = tmp
    env["STUB_MODE"] = mode
    return subprocess.run(
        [sys.executable, os.path.join(POST_DIR, script)],
        input=STDIN_DATA, capture_output=True, text=True,
        env=env, cwd=tmp,
    )


class TestDbScripts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp_obj = tempfile.TemporaryDirectory()
        cls.tmp = cls._tmp_obj.name
        _write_stubs(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        cls._tmp_obj.cleanup()

    def _assert_clean_error_exit(self, r, script, mode):
        combined = r.stdout + r.stderr
        self.assertNotIn("Traceback", combined,
                         f"{script}/{mode}: unexpected traceback\n{combined}")
        self.assertNotIn("NameError", combined,
                         f"{script}/{mode}: unbound variable\n{combined}")
        self.assertEqual(r.returncode, 1,
                         f"{script}/{mode}: DB failure must exit nonzero, got {r.returncode}")

    def test_connect_failure_exits_cleanly(self):
        for script in ALL_SCRIPTS:
            with self.subTest(script=script):
                self._assert_clean_error_exit(
                    _run_script(self.tmp, script, "connect_fail"), script, "connect_fail")

    def test_cursor_failure_exits_cleanly(self):
        for script in ALL_SCRIPTS:
            with self.subTest(script=script):
                r = _run_script(self.tmp, script, "cursor_fail")
                self._assert_clean_error_exit(r, script, "cursor_fail")
                # conn은 생성되었으므로 close가 호출되어야 한다
                self.assertIn("STUB_CONN_CLOSED", r.stdout,
                              f"{script}: connection was not closed\n{r.stdout}")

    def test_query_failure_exits_cleanly(self):
        for script in ALL_SCRIPTS:
            with self.subTest(script=script):
                r = _run_script(self.tmp, script, "query_fail")
                self._assert_clean_error_exit(r, script, "query_fail")
                self.assertIn("STUB_CURSOR_CLOSED", r.stdout,
                              f"{script}: cursor was not closed\n{r.stdout}")
                self.assertIn("STUB_CONN_CLOSED", r.stdout,
                              f"{script}: connection was not closed\n{r.stdout}")

    def test_success_path_completes_and_closes(self):
        for script in ALL_SCRIPTS:
            with self.subTest(script=script):
                r = _run_script(self.tmp, script, "success")
                combined = r.stdout + r.stderr
                self.assertNotIn("Traceback", combined,
                                 f"{script}/success: unexpected traceback\n{combined}")
                self.assertEqual(r.returncode, 0,
                                 f"{script}/success: expected exit 0, got {r.returncode}\n{combined}")
                self.assertIn("STUB_CURSOR_CLOSED", r.stdout,
                              f"{script}/success: cursor was not closed\n{r.stdout}")
                self.assertIn("STUB_CONN_CLOSED", r.stdout,
                              f"{script}/success: connection was not closed\n{r.stdout}")

    def test_draw_script_compiles(self):
        import py_compile
        py_compile.compile(os.path.join(POST_DIR, "draw.py"), doraise=True)


if __name__ == "__main__":
    unittest.main()
