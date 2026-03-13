import psycopg2
from psycopg2 import OperationalError
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def tao_ket_noi():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def kiem_tra_ket_noi():
    try:
        conn = tao_ket_noi()
        conn.close()
        return True, "Kết nối thành công"
    except OperationalError as e:
        return False, str(e)