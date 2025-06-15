from django.db import models

# ==================== DIMENSI ====================

class DimWaktu(models.Model):
    tanggal_id = models.IntegerField(primary_key=True)
    tanggal = models.DateField()
    hari = models.CharField(max_length=10)
    bulan = models.CharField(max_length=10)
    tahun = models.IntegerField()

    def __str__(self):
        return f"{self.tanggal} ({self.hari})"


class DimProduk(models.Model):
    produk_id = models.IntegerField(primary_key=True)
    product_line = models.CharField(max_length=50)

    def __str__(self):
        return self.product_line


class DimCabang(models.Model):
    cabang_id = models.IntegerField(primary_key=True)
    branch = models.CharField(max_length=10)
    city = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.branch} - {self.city}"


class DimPelanggan(models.Model):
    pelanggan_id = models.IntegerField(primary_key=True)
    customer_type = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.customer_type} - {self.gender}"


class DimPembayaran(models.Model):
    pembayaran_id = models.IntegerField(primary_key=True)
    payment_method = models.CharField(max_length=20)

    def __str__(self):
        return self.payment_method

# ==================== FAKTA ====================

class FactPenjualan(models.Model):
    tanggal = models.ForeignKey(DimWaktu, on_delete=models.CASCADE)
    produk = models.ForeignKey(DimProduk, on_delete=models.CASCADE)
    cabang = models.ForeignKey(DimCabang, on_delete=models.CASCADE)
    pelanggan = models.ForeignKey(DimPelanggan, on_delete=models.CASCADE)
    pembayaran = models.ForeignKey(DimPembayaran, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cogs = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1)


class FactPerformaProduk(models.Model):
    produk = models.ForeignKey(DimProduk, on_delete=models.CASCADE)
    tanggal = models.ForeignKey(DimWaktu, on_delete=models.CASCADE)
    cabang = models.ForeignKey(DimCabang, on_delete=models.CASCADE)
    pelanggan = models.ForeignKey(DimPelanggan, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cogs = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1)


class FactPenjualanCabang(models.Model):
    cabang = models.ForeignKey(DimCabang, on_delete=models.CASCADE)
    tanggal = models.ForeignKey(DimWaktu, on_delete=models.CASCADE)
    pembayaran = models.ForeignKey(DimPembayaran, on_delete=models.CASCADE)
    produk = models.ForeignKey(DimProduk, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cogs = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
