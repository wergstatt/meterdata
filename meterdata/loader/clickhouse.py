import time
from multiprocessing import Pool

from clickhouse_driver import Client
from pyarrow import parquet as pq

from meterdata.loader.common import (
    get_data_from_row_group,
    write_execution_time,
)

CH_BASE_TABLE = "meterdata_raw.meter_halfhourly_dataset"


def ch_get_row_count(table: str):
    start = time.perf_counter()

    with Client("localhost") as client:
        n_rows = client.execute(f"select count(*) from {table}")[0][0]

    write_execution_time(
        exec_time=time.perf_counter() - start,
        function_name=ch_get_row_count.__name__,
    )
    return n_rows


def ch_truncate_table(table: str):
    start = time.perf_counter()

    with Client("localhost") as client:
        client.execute(query=f"truncate table {table}")

    write_execution_time(
        exec_time=time.perf_counter() - start,
        function_name=ch_truncate_table.__name__,
    )


def ch_insert_data(data):
    start = time.perf_counter()

    with Client("localhost") as client:
        client.execute(
            query="insert into meterdata_raw.meter_halfhourly_dataset (id, ts, val) values",
            params=data,
            types_check=True,
        )

    write_execution_time(
        exec_time=time.perf_counter() - start,
        function_name=ch_insert_data.__name__,
    )


def ch_insert_row_group(args):
    start = time.perf_counter()

    file_path, year, row_group_index = args
    data = get_data_from_row_group(
        file_path=file_path,
        year=year,
        row_group_index=row_group_index,
    )
    ch_insert_data(data=data)

    write_execution_time(
        exec_time=time.perf_counter() - start,
        function_name=ch_insert_row_group.__name__,
    )


def ch_insert_file_content(table_name: str, year: int):
    start = time.perf_counter()

    file_path = f"data/ready/{table_name}.parquet"
    parquet_file = pq.ParquetFile(file_path)
    with Pool() as pool:
        pool.map(
            ch_insert_row_group,
            [(file_path, year, i) for i in range(parquet_file.num_row_groups)],
        )

    write_execution_time(
        exec_time=time.perf_counter() - start,
        function_name=ch_insert_file_content.__name__,
    )