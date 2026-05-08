"""
insert.py - PostgreSQL performance test virtual data generator

All data produced by this script, including schema names, columns, and values,
is generic dummy data for learning and performance testing.
It is not related to any company or customer production data or schema.
"""
import psycopg2
import csv
import random
import time
from io import StringIO
from datetime import datetime, timezone

# PostgreSQL ?곌껐 ?ㅼ젙
DB_PARAMS = {
    "dbname": "sample_db",
    "user": "sample_user",
    "password": "sample_password",
    "host": "localhost",
    "port": "5432"
}

TABLE_NAME = "sample_long_method_metrics"
BATCH_SIZE = 100000  # 10留?媛쒖뵫 諛곗튂濡?INSERT
TOTAL_ROWS = 10_000_000  # 1000留?媛??곗씠??

# ?쒖닔 ?곗씠???앹꽦 ?⑥닔
def generate_data():
    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')  # TIMESTAMP ???
    start_time = int(time.time())  # BIGINT ???

    return [
        current_time,  # time (TIMESTAMP)
        random.randint(1, 1000),  # was_id
        random.randint(1, 100000),  # tid
        random.randint(1, 1000000),  # method_id
        random.randint(1, 100),  # method_seq
        random.randint(1000, 9999),  # crc
        random.randint(1, 1000000),  # calling_method_id
        random.randint(1000, 9999),  # calling_crc
        random.randint(0, 10),  # error_count
        random.randint(1, 1000),  # exec_count
        int(random.uniform(1, 100)),  # elapse_time (BIGINT ???
        int(random.uniform(1, 50)),  # cpu_time (BIGINT ???
        random.randint(1000, 1000000),  # memory
        start_time,  # start_time (BIGINT)
        random.randint(1, 20),  # method_depth
        int(random.uniform(1, 10))  # gap_time (BIGINT ???
    ]

# ????곗씠???쎌엯 ?⑥닔
def bulk_insert():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    start = time.time()
    
    for batch in range(TOTAL_ROWS // BATCH_SIZE):
        buffer = StringIO()
        writer = csv.writer(buffer, delimiter='\t')

        for _ in range(BATCH_SIZE):
            writer.writerow(generate_data())

        buffer.seek(0)

        # COPY 紐낅졊?대줈 鍮좊Ⅴ寃??쎌엯
        cursor.copy_from(buffer, TABLE_NAME, sep='\t', columns=[
            "time", "was_id", "tid", "method_id", "method_seq", "crc", "calling_method_id",
            "calling_crc", "error_count", "exec_count", "elapse_time", "cpu_time",
            "memory", "start_time", "method_depth", "gap_time"
        ])
        
        conn.commit()
        print(f"Inserted batch {batch + 1}/{TOTAL_ROWS // BATCH_SIZE}")

    cursor.close()
    conn.close()
    
    print(f"Total time: {time.time() - start:.2f} seconds")

if __name__ == "__main__":
    bulk_insert()
