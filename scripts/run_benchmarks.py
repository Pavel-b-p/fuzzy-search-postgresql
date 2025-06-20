import psycopg2
import time
import uuid
import re
import os

class FuzzySearchBenchmark:
    def __init__(self, conn_params):
        self.conn = psycopg2.connect(**conn_params)
        self.test_run_id = str(uuid.uuid4())

    def benchmark_method(self, method_name, query, search_term, dataset_size):
        cursor = self.conn.cursor()

        cursor.execute(f"""
            CREATE OR REPLACE TEMP VIEW products_subset AS 
            SELECT * FROM products LIMIT {dataset_size};
        """)

        start_time = time.time()
        cursor.execute(query.replace('{term}', search_term))
        results = cursor.fetchall()
        exec_time = (time.time() - start_time) * 1000

        print(f"{method_name:<25} | {search_term:<15} | time: {exec_time:.2f} ms | results: {len(results)}")

        return {
            'method': method_name,
            'term': search_term,
            'time_ms': exec_time,
            'count': len(results)
        }

    def close(self):
        self.conn.close()


def load_sql_queries(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'--\s*(\w+)', content)
    queries = {}
    for i in range(1, len(blocks), 2):
        method = blocks[i].strip()
        sql_block = blocks[i + 1].strip()
        sql_statements = [stmt.strip() for stmt in sql_block.split(';') if stmt.strip()]
        for stmt in sql_statements:
            if '{term}' in stmt:
                queries.setdefault(method, []).append(stmt + ';')
    return queries


if __name__ == "__main__":
    conn_params = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }

    search_terms = ['latpop', 'kompyuter', 'LaPtOp', 'Dell', 'monittor']
    dataset_size = 10000

    benchmark = FuzzySearchBenchmark(conn_params)
    queries = load_sql_queries('../sql/04_benchmarks.sql')

    for method, statements in queries.items():
        for term in search_terms:
            for query in statements:
                benchmark.benchmark_method(method, query, term, dataset_size)

    benchmark.close()
