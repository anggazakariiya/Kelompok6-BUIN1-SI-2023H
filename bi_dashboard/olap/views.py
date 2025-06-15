import json
from django.shortcuts import render
from collections import defaultdict
from django.db.models import Count, Sum, Avg, F
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models.functions import ExtractHour, ExtractWeekDay
from olap.models import FactPenjualan, FactPerformaProduk, FactPenjualanCabang
import numpy as np
from sklearn.linear_model import LinearRegression


BULAN_TO_ANGKA = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}


# 1. Dashboard Penjualan (Diperbarui dengan Analisis per Hari)
def dashboard_penjualan(request):
    # Query Penjualan per Bulan & Prediksi
    penjualan_per_bulan_query = FactPenjualan.objects.values('tanggal__bulan', 'tanggal__tahun').annotate(total=Sum('total'))
    penjualan_per_bulan = sorted(penjualan_per_bulan_query, key=lambda b: (int(b['tanggal__tahun']), BULAN_TO_ANGKA.get(b['tanggal__bulan'], 0)))
    labels_bulan = [f"{b['tanggal__bulan']}/{b['tanggal__tahun']}" for b in penjualan_per_bulan]
    data_bulan = [float(b['total']) for b in penjualan_per_bulan]
    labels_prediksi, data_prediksi = [], []
    if len(data_bulan) > 1:
        X = np.array(range(len(data_bulan))).reshape(-1, 1)
        y = np.array(data_bulan)
        model = LinearRegression().fit(X, y)
        bulan_prediksi = 3
        indeks_prediksi = np.array(range(len(data_bulan), len(data_bulan) + bulan_prediksi)).reshape(-1, 1)
        hasil_prediksi = model.predict(indeks_prediksi)
        data_prediksi = [round(max(0, val)) for val in hasil_prediksi]
        last_date_str = f"1 {penjualan_per_bulan[-1]['tanggal__bulan']} {penjualan_per_bulan[-1]['tanggal__tahun']}"
        last_date = datetime.strptime(last_date_str, "%d %B %Y")
        for i in range(1, bulan_prediksi + 1):
            next_date = last_date + relativedelta(months=i)
            labels_prediksi.append(next_date.strftime("%B/%Y"))

    # Query Laba Kotor
    laba_per_bulan_query = FactPenjualan.objects.values('tanggal__bulan', 'tanggal__tahun').annotate(total_penjualan=Sum('total'), total_laba=Sum(F('total') - F('cogs')))
    laba_per_bulan_sorted = sorted(laba_per_bulan_query, key=lambda b: (int(b['tanggal__tahun']), BULAN_TO_ANGKA.get(b['tanggal__bulan'], 0)))
    labels_laba = [f"{b['tanggal__bulan']}/{b['tanggal__tahun']}" for b in laba_per_bulan_sorted]
    data_penjualan_untuk_laba = [float(b['total_penjualan']) for b in laba_per_bulan_sorted]
    data_laba_kotor = [float(b['total_laba']) for b in laba_per_bulan_sorted]

    # Query Penjualan per Hari
    penjualan_per_hari_query = FactPenjualan.objects.values('tanggal__hari').annotate(total_penjualan=Sum('total')).order_by('tanggal__hari')
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    penjualan_harian = {day: 0 for day in day_order}
    for item in penjualan_per_hari_query:
        hari = item['tanggal__hari']
        if hari in penjualan_harian:
            penjualan_harian[hari] = float(item['total_penjualan'])
    labels_hari = list(penjualan_harian.keys())
    data_hari = list(penjualan_harian.values())

    # --- DIUBAH: Query untuk Rating per Cabang dengan Nama Lengkap ---
    rating_per_cabang_query = (
        FactPenjualan.objects
        .values('cabang__branch', 'cabang__city') # Tambahkan 'cabang__city'
        .annotate(avg_rating=Avg('rating'))
        .order_by('-avg_rating')
    )
    labels_cabang = [f"{c['cabang__branch']} - {c['cabang__city']}" for c in rating_per_cabang_query]
    data_rating = [float(c['avg_rating']) for c in rating_per_cabang_query]
    # --- AKHIR BAGIAN YANG DIUBAH ---

    # Query Metode Pembayaran
    penjualan_per_pembayaran = FactPenjualan.objects.values('pembayaran__payment_method').annotate(total=Sum('total'))
    labels_pembayaran = [p['pembayaran__payment_method'] for p in penjualan_per_pembayaran]
    data_pembayaran = [float(p['total']) for p in penjualan_per_pembayaran]

    context = {
        'labels_bulan': json.dumps(labels_bulan), 'data_bulan': json.dumps(data_bulan),
        'labels_prediksi': json.dumps(labels_prediksi), 'data_prediksi': json.dumps(data_prediksi),
        'labels_pembayaran': json.dumps(labels_pembayaran), 'data_pembayaran': json.dumps(data_pembayaran),
        'labels_cabang': json.dumps(labels_cabang), 'data_rating': json.dumps(data_rating),
        'labels_laba': json.dumps(labels_laba), 'data_penjualan_untuk_laba': json.dumps(data_penjualan_untuk_laba),
        'data_laba_kotor': json.dumps(data_laba_kotor),
        'labels_hari': json.dumps(labels_hari), 'data_hari': json.dumps(data_hari),
    }
    return render(request, 'olap/dashboard_penjualan.html', context)


# 2. Dashboard Performa Produk (Tidak diubah)
def dashboard_performa_produk(request):
    # Query yang sudah ada
    data_tren = (
        FactPerformaProduk.objects
        .values('produk__product_line', 'tanggal__bulan', 'tanggal__tahun')
        .annotate(total=Sum('total'))
    )
    bulan_set = set((d['tanggal__bulan'], d['tanggal__tahun']) for d in data_tren)
    bulan_sorted = sorted(bulan_set, key=lambda x: (int(x[1]), BULAN_TO_ANGKA.get(x[0], 0)))
    labels_bulan = [f"{b}/{y}" for b, y in bulan_sorted]
    tren_per_produk = defaultdict(lambda: [0] * len(labels_bulan))
    for d in data_tren:
        label = f"{d['tanggal__bulan']}/{d['tanggal__tahun']}"
        index = labels_bulan.index(label)
        tren_per_produk[d['produk__product_line']][index] = float(d['total'])

    weekday_data = (
        FactPerformaProduk.objects
        .annotate(weekday=ExtractWeekDay('tanggal__tanggal'))
        .values('weekday')
        .annotate(total=Sum('total'))
    )
    day_map = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    total_per_day = {day: 0 for day in day_order}
    for d in weekday_data:
        day_name = day_map[d['weekday']]
        total_per_day[day_name] = float(d['total'])
    stacked_labels = list(total_per_day.keys())
    stacked_values = list(total_per_day.values())

    profit_per_produk = (
        FactPerformaProduk.objects
        .values('produk__product_line')
        .annotate(
            total_penjualan=Sum('total'),
            total_laba=Sum(F('total') - F('cogs'))
        )
        .order_by('-total_laba')
    )
    labels_profit = [p['produk__product_line'] for p in profit_per_produk]
    data_profit_penjualan = [float(p['total_penjualan']) for p in profit_per_produk]
    data_profit_laba = [float(p['total_laba']) for p in profit_per_produk]

    data = (
        FactPerformaProduk.objects
        .values('produk__product_line')
        .annotate(total_penjualan=Sum('total'), avg_rating=Avg('rating'))
    )
    labels_produk = [d['produk__product_line'] for d in data]
    data_total_penjualan = [float(d['total_penjualan']) for d in data]
    data_rating = [float(d['avg_rating']) for d in data]

    # --- DIUBAH: Query & Proses Data untuk Performa Produk per Cabang ---
    performa_cabang_query = (
        FactPerformaProduk.objects
        .values('cabang__branch', 'cabang__city', 'produk__product_line') # Tambahkan 'cabang__city'
        .annotate(total_penjualan=Sum('total'))
        .order_by('cabang__branch', 'cabang__city', 'produk__product_line')
    )
    
    # Buat label lengkap (e.g., "A - Jakarta")
    labels_cabang_unik = sorted(list(set(f"{item['cabang__branch']} - {item['cabang__city']}" for item in performa_cabang_query)))
    labels_produk_unik = sorted(list(set(item['produk__product_line'] for item in performa_cabang_query)))

    data_performa_cabang = defaultdict(lambda: [0] * len(labels_cabang_unik))

    for item in performa_cabang_query:
        produk = item['produk__product_line']
        # Gunakan label lengkap untuk mencocokkan
        cabang_label = f"{item['cabang__branch']} - {item['cabang__city']}"
        total = float(item['total_penjualan'])
        
        cabang_index = labels_cabang_unik.index(cabang_label)
        data_performa_cabang[produk][cabang_index] = total

    datasets_performa_cabang = []
    for produk, data in data_performa_cabang.items():
        datasets_performa_cabang.append({
            'label': produk,
            'data': data,
        })
    # --- AKHIR BAGIAN YANG DIUBAH ---

    context = {
        'labels_produk': json.dumps(labels_produk),
        'data_total_penjualan': json.dumps(data_total_penjualan),
        'data_rating': json.dumps(data_rating),
        'labels_bulan': json.dumps(labels_bulan),
        'tren_per_produk': json.dumps(dict(tren_per_produk)),
        'stacked_labels': json.dumps(stacked_labels),
        'stacked_values': json.dumps(stacked_values),
        'labels_profit': json.dumps(labels_profit),
        'data_profit_penjualan': json.dumps(data_profit_penjualan),
        'data_profit_laba': json.dumps(data_profit_laba),
        'labels_performa_cabang': json.dumps(labels_cabang_unik), # Kirim label yang sudah lengkap
        'datasets_performa_cabang': json.dumps(datasets_performa_cabang),
    }
    return render(request, 'olap/dashboard_performa.html', context)



# 3. Dashboard Penjualan Cabang (Tidak diubah)
def dashboard_cabang(request):
    # Query terpadu untuk mendapatkan semua metrik kinerja cabang
    kinerja_cabang = (
        FactPenjualanCabang.objects
        .values('cabang__branch', 'cabang__city')
        .annotate(
            total_penjualan=Sum('total'),
            jumlah_transaksi=Count('id'),
            total_laba=Sum(F('total') - F('cogs'))
        )
        .order_by('-total_penjualan')
    )

    # Memproses data untuk grafik
    labels_cabang = [f"{d['cabang__branch']} - {d['cabang__city']}" for d in kinerja_cabang]
    data_penjualan = [float(d['total_penjualan']) for d in kinerja_cabang]
    data_transaksi = [d['jumlah_transaksi'] for d in kinerja_cabang]
    data_laba = [float(d['total_laba']) for d in kinerja_cabang]
    # Menghitung ATV, hindari pembagian dengan nol dan konversi ke float
    data_atv = [
        float(item['total_penjualan'] / item['jumlah_transaksi']) if item['jumlah_transaksi'] > 0 else 0
        for item in kinerja_cabang
    ]
    
    context = {
        'labels_cabang': json.dumps(labels_cabang),
        'data_penjualan': json.dumps(data_penjualan),
        'data_transaksi': json.dumps(data_transaksi),
        'data_laba_kotor_cabang': json.dumps(data_laba), 
        'data_atv_cabang': json.dumps(data_atv),       
        'year': datetime.now().year
    }
    return render(request, 'olap/dashboard_cabang.html', context)

from django.http import HttpResponse

