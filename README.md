# Supermarket Sales Data Dashboard Monitoring

Proyek ini mengembangkan pipeline ETL (Extract, Transform, Load) untuk data penjualan supermarket dan dashboard Business Intelligence (BI) terkait. Tujuannya adalah untuk mengubah data transaksi mentah menjadi format yang siap untuk analisis, serta menyajikan insight bisnis melalui visualisasi interaktif.


## Proyek ini merupakan bagian dari tugas akhir (UAS):
-   **Mata Kuliah:** Business Intelligence
-   **Program Studi:** Sistem Informasi 
-   **Universitas:** Universitas Negeri Surabaya
-   **Dosen Pembimbing/Kolaborator:** Cendra Devayana Putra, S.Kom., M.IM.


## Repositori ini terdiri dari dua komponen utama:

-   `etl_pipeline/`: Berisi kode untuk proses ETL data.
-   `bi_dashboard/`: Berisi file-file untuk visualisasi dan dashboard BI.


## Tugas utama proyek ini adalah membangun sebuah sistem data warehouse sederhana yang mampu mengolah data penjualan supermarket dari sumber mentah hingga siap untuk dianalisis. Proses ini melibatkan:

1.  **Ekstraksi Data:** Mengambil data transaksi penjualan dari file CSV mentah.
2.  **Transformasi Data:** Mengubah dan menata ulang data ke dalam struktur dimensional Star Schema. Tiga tabel fakta utama yang dibuat adalah:
    * `fact_penjualan`: Untuk analisis penjualan umum berdasarkan waktu, produk, cabang, pelanggan, dan metode pembayaran. 
    * `fact_performa_produk`: Untuk menganalisis kinerja produk berdasarkan penjualan, biaya pokok, dan rating. 
    * `fact_penjualan_cabang`: Untuk menganalisis penjualan spesifik per cabang, waktu, metode pembayaran, dan produk. 
    Tabel-tabel dimensi yang mendukung meliputi `dim_produk` , `dim_waktu` , `dim_cabang` , `dim_pelanggan` , dan `dim_pembayaran`.
3.  **Pemuatan Data:** Menyimpan data yang sudah ditransformasi ke dalam format CSV yang terstruktur.
4.  **Visualisasi Data:** Mengembangkan dashboard interaktif untuk menyajikan insight penting dari data yang sudah diolah.

## Tujuan utama dari proyek ini adalah untuk **memahami dan mengimplementasikan konsep data warehouse dan dimensional modeling** (khususnya Star Schema) serta **membangun pipeline ETL fungsional** yang dapat digunakan untuk analisis bisnis.


## Proyek ini menggunakan data penjualan supermarket yang tersedia dalam format CSV.

-   **`etl_pipeline/supermarket_sales.csv`**: Ini adalah file data mentah yang digunakan sebagai sumber data untuk proses ETL. File ini berisi catatan transaksi penjualan individual dari sebuah supermarket, dengan berbagai kolom seperti tanggal, jenis produk, cabang, tipe pelanggan, metode pembayaran, kuantitas, total, dan rating.



## **Anggota Kelompok**:
1. Fahmi Hasan Firdaus         (23051214262) 
2. Angga Zakariya              (23051214267)
3. Muhammad Fahril Syahputra   (23051214279)
4. Muchammad Abdulloh ‘Ubaid   (23051214283)

---
