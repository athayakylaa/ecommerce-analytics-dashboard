
# E-Commerce Analytics Dashboard
## Deskripsi Proyek

Proyek ini menganalisis kinerja penjualan dan segmentasi pelanggan pada platform E-Commerce menggunakan Brazilian E-Commerce Public Dataset by Olist.

Analisis difokuskan pada pesanan berstatus delivered selama Januari–Desember 2017.

## Pertanyaan Bisnis

1. Bagaimana perkembangan total nilai penjualan bulanan dan kategori produk apa yang memberikan kontribusi penjualan terbesar selama Januari–Desember 2017?
2. Bagaimana segmentasi pelanggan berdasarkan Recency, Frequency, dan Monetary (RFM), serta segmen mana yang perlu diprioritaskan dalam strategi retensi pelanggan?

## Dataset

Dataset yang digunakan meliputi:
- customers_dataset.csv
- orders_dataset.csv
- order_items_dataset.csv
- products_dataset.csv
- product_category_name_translation.csv

## Metode Analisis

- Data Wrangling
- Exploratory Data Analysis (EDA)
- Visualisasi Kinerja Penjualan
- Analisis Recency, Frequency, Monetary (RFM)
- Segmentasi Pelanggan Berdasarkan Skor RFM

## Hasil Analisis

- Total pesanan delivered tahun 2017: 43.428.
- Total pelanggan unik: 42.136.
- Total item transaksi: 49.556.
- Penjualan tertinggi terjadi pada November 2017.
- Kategori bed_bath_table memiliki kontribusi penjualan terbesar.
- Segmen At Risk High Value menjadi prioritas strategi retensi pelanggan.

## Cara Menjalankan Dashboard

1. Pastikan Python telah terpasang.
2. Buka terminal pada folder proyek.
3. Instal seluruh library:

   pip install -r requirements.txt

4. Jalankan dashboard:

   streamlit run dashboard.py

5. Buka http://localhost:8501 pada browser.

## Struktur Folder

submission-ecommerce/
- data/
  - customers_dataset.csv
  - orders_dataset.csv
  - order_items_dataset.csv
  - products_dataset.csv
  - product_category_name_translation.csv
- dashboard.py
- requirements.txt
- README.md

## Sumber Data

Brazilian E-Commerce Public Dataset by Olist.
