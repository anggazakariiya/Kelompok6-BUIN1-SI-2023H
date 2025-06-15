from airflow import DAG
from airflow.operators.python import PythonOperator  # type: ignore
from datetime import datetime
import pandas as pd
import os

dag_path = os.path.dirname(__file__)
raw_data_path = os.path.join(dag_path, 'supermarket_sales.csv')

# extract
def extract():
    df = pd.read_csv(raw_data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df.to_csv('/tmp/extracted_sales.csv', index=False)

# transform
def transform():
    df = pd.read_csv('/tmp/extracted_sales.csv')

    # Dimensi

    # Produk
    dim_produk = df[['Product line']].drop_duplicates().reset_index(drop=True)
    dim_produk['produk_id'] = dim_produk.index + 1
    dim_produk.rename(columns={'Product line': 'product_line'}, inplace=True)

    # Waktu
    dim_waktu = df[['Date']].drop_duplicates().reset_index(drop=True)
    dim_waktu['tanggal_id'] = dim_waktu.index + 1
    dim_waktu['tanggal'] = pd.to_datetime(dim_waktu['Date']).dt.date
    dim_waktu['hari'] = pd.to_datetime(dim_waktu['Date']).dt.day_name()
    dim_waktu['bulan'] = pd.to_datetime(dim_waktu['Date']).dt.month_name()
    dim_waktu['tahun'] = pd.to_datetime(dim_waktu['Date']).dt.year

    # Cabang
    dim_cabang = df[['Branch', 'City']].drop_duplicates().reset_index(drop=True)
    dim_cabang['cabang_id'] = dim_cabang.index + 1

    # Pelanggan
    dim_pelanggan = df[['Customer type', 'Gender']].drop_duplicates().reset_index(drop=True)
    dim_pelanggan['pelanggan_id'] = dim_pelanggan.index + 1

    # Pembayaran
    dim_pembayaran = df[['Payment']].drop_duplicates().reset_index(drop=True)
    dim_pembayaran['pembayaran_id'] = dim_pembayaran.index + 1
    dim_pembayaran.rename(columns={'Payment': 'payment_method'}, inplace=True)

    # Merge Foreign Key

    df = df.merge(dim_produk, left_on='Product line', right_on='product_line')
    df = df.merge(dim_waktu[['tanggal_id', 'Date']], on='Date')
    df = df.merge(dim_cabang, on=['Branch', 'City'])
    df = df.merge(dim_pelanggan, on=['Customer type', 'Gender'])
    df = df.merge(dim_pembayaran, left_on='Payment', right_on='payment_method')

    df['cogs'] = df['Total'] / 1.05  # Asumsi tax 5%

    # Fakta

    # fact_penjualan
    fact_penjualan = df[['tanggal_id', 'produk_id', 'cabang_id', 'pelanggan_id', 'pembayaran_id',
                         'Quantity', 'Total', 'cogs', 'Rating']].copy()
    fact_penjualan.columns = ['tanggal_id', 'produk_id', 'cabang_id', 'pelanggan_id', 'pembayaran_id',
                              'quantity', 'total', 'cogs', 'rating']

    # fact_performa_produk
    fact_performa_produk = df[['produk_id', 'tanggal_id', 'cabang_id', 'pelanggan_id',
                               'Quantity', 'Total', 'cogs', 'Rating']].copy()
    fact_performa_produk.columns = ['produk_id', 'tanggal_id', 'cabang_id', 'pelanggan_id',
                                    'quantity', 'total', 'cogs', 'rating']

    # fact_penjualan_cabang
    fact_penjualan_cabang = df[['cabang_id', 'tanggal_id', 'pembayaran_id', 'produk_id',
                                'Quantity', 'Total', 'cogs', 'Rating']].copy()
    fact_penjualan_cabang.columns = ['cabang_id', 'tanggal_id', 'pembayaran_id', 'produk_id',
                                     'quantity', 'total', 'cogs', 'rating']

    # simpan csv /tmp 

    dim_produk.to_csv('/tmp/dim_produk.csv', index=False)
    dim_waktu[['tanggal_id', 'tanggal', 'hari', 'bulan', 'tahun']].to_csv('/tmp/dim_waktu.csv', index=False)
    dim_cabang.to_csv('/tmp/dim_cabang.csv', index=False)
    dim_pelanggan.to_csv('/tmp/dim_pelanggan.csv', index=False)
    dim_pembayaran.to_csv('/tmp/dim_pembayaran.csv', index=False)

    fact_penjualan.to_csv('/tmp/fact_penjualan.csv', index=False)
    fact_performa_produk.to_csv('/tmp/fact_performa_produk.csv', index=False)
    fact_penjualan_cabang.to_csv('/tmp/fact_penjualan_cabang.csv', index=False)

# Load
def load():
    output_path = os.path.join(dag_path, 'output')
    os.makedirs(output_path, exist_ok=True)

    for file in ['dim_produk.csv', 'dim_waktu.csv', 'dim_cabang.csv',
                 'dim_pelanggan.csv', 'dim_pembayaran.csv',
                 'fact_penjualan.csv', 'fact_performa_produk.csv', 'fact_penjualan_cabang.csv']:
        tmp_path = os.path.join('/tmp', file)
        final_path = os.path.join(output_path, file)
        df = pd.read_csv(tmp_path)
        df.to_csv(final_path, index=False)

# Dag
with DAG(
    dag_id='etl_supermarket_sales',
    start_date=datetime(2023, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['etl', 'supermarket']
) as dag:

    t1 = PythonOperator(
        task_id='extract',
        python_callable=extract
    )

    t2 = PythonOperator(
        task_id='transform',
        python_callable=transform
    )

    t3 = PythonOperator(
        task_id='load',
        python_callable=load
    )

    # Urutan eksekusi
    t1 >> t2 >> t3
