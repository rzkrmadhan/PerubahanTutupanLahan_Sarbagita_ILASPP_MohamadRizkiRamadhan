# Proyeksi Perubahan Tutupan Lahan Kawasan Sarbagita (2020-2026)

Analisis ini disusun untuk penugasan seleksi Tenaga Ahli GIS Analyst di ILASPP, dengan fokus pada penyusunan peta tematik derivatif proyeksi perubahan tutupan lahan di Kawasan Aglomerasi Sarbagita (Denpasar, Badung, Gianyar, Tabanan), Provinsi Bali.

## 1. Ringkasan

Analisis ini mengklasifikasikan tutupan lahan Kawasan Sarbagita pada tahun 2020 dan 2023 menggunakan citra Sentinel-2A RGB dan algoritma Random Forest, dengan Overall Accuracy 93,52% dan Cohen's Kappa 0,8601 (kategori Almost Perfect). Hasil klasifikasi menunjukkan tren peningkatan lahan terbangun yang konsisten, dari 19,6% (2020) menjadi 25,3% (2023), diiringi penurunan tutupan vegetasi dari 48,1% menjadi 40,5%. Proyeksi ke tahun 2026 menggunakan model Markov Chain yang dimodifikasi dengan driving factor dan restricting factor menghasilkan estimasi lahan terbangun mencapai 43,7%, dengan validasi hindcast menunjukkan Overall Accuracy 67,49% dan Cohen's Kappa 0,5106 (kategori Moderate). Analisis ini memiliki sejumlah keterbatasan metodologis yang dijelaskan pada bagian 6.

## 2. Data

### 2.1 Citra Satelit

- Sumber: Sentinel-2A composite, diakses dari penyedia data penugasan
- Tahun: 2020 dan 2023
- Band: 3 band (RGB true color, 8 bit, rentang nilai 0-255)
- Resolusi spasial: sekitar 10 meter
- CRS: EPSG:4326 (WGS 84)
- Dimensi: 5075 x 6789 piksel
- Cakupan: area daratan Kawasan Sarbagita, area laut di-clip menjadi nodata (RGB 0,0,0)
- Tutupan awan: diperkirakan kurang dari 10% dari total area, tersebar, tidak dilakukan cloud masking khusus mengingat proporsinya kecil. Area yang tertutup awan berpotensi mengalami misklasifikasi.

**Catatan keterbatasan:** citra yang tersedia hanya RGB tanpa band Near Infrared (NIR), sehingga indeks vegetasi standar seperti NDVI tidak dapat dihitung. Klasifikasi sepenuhnya mengandalkan informasi spektral RGB.

### 2.2 Data Pendukung (Driving dan Restricting Factor)

Driving factor dan restricting factor pada analisis ini diturunkan langsung dari hasil klasifikasi 2023, tanpa data eksternal tambahan. DEM dan data jaringan jalan sempat dipertimbangkan sebagai faktor yang secara teori lebih representatif, namun tidak digunakan karena keterbatasan waktu pengerjaan (lihat bagian 6). Detail faktor yang digunakan dijelaskan pada bagian 4.5.

### 2.3 Training Sample

Training sample terdiri dari 47 polygon, didigitasi manual di QGIS berdasarkan interpretasi visual citra 2020, dengan distribusi sebagai berikut:

| Kelas | Jumlah Polygon | Jumlah Piksel |
|---|---|---|
| Built-up | 13 | 206.257 |
| Vegetation | 8 | 1.111.711 |
| Agriculture | 12 | 204.337 |
| Bare Land | 5 | 7.083 |
| Water Body | 9 | 45.601 |

Total piksel training: 1.574.989, dengan pembagian 70% untuk training model (1.102.492 piksel) dan 30% untuk pengujian akurasi (472.497 piksel).

**Catatan keterbatasan:** jumlah polygon untuk kelas Bare Land relatif sedikit (5 polygon, 7.083 piksel) dibandingkan kelas lain. Ini berkontribusi pada akurasi kelas ini yang lebih rendah dibandingkan kelas lainnya (lihat bagian 5.2).

Training sample awalnya didigitasi menggunakan CRS proyek EPSG:32750 (UTM Zona 50S), kemudian direproyeksi ke EPSG:4326 agar sesuai dengan CRS citra sebelum digunakan dalam analisis.

## 3. Skema Klasifikasi Tutupan Lahan

| id_kelas | Kelas | Deskripsi |
|---|---|---|
| 1 | Built-up | Permukiman, jalan, hotel, area komersial |
| 2 | Vegetation | Kebun, tegalan, hutan, vegetasi non-sawah |
| 3 | Agriculture | Sawah aktif maupun bera |
| 4 | Bare Land | Tanah kosong, lahan konstruksi, area gundul |
| 5 | Water Body | Sungai besar, waduk, danau (laut tidak termasuk, sudah di-clip sebagai nodata) |

## 4. Metodologi

### 4.1 Praproses dan QA/QC

Sebelum analisis dimulai, dilakukan pemeriksaan CRS, dimensi, resolusi, dan bounds kedua citra untuk memastikan keduanya identik dan sudah teralign secara piksel, sehingga tidak diperlukan resampling atau reprojection tambahan. Piksel nodata (area laut, RGB bernilai 0,0,0) diidentifikasi mencakup sekitar 48,6% dari total piksel citra, dan di-mask secara eksplisit setelah proses klasifikasi untuk mencegah piksel ini ikut dihitung sebagai kelas tutupan lahan tertentu.

### 4.2 Klasifikasi Tutupan Lahan

Training sample dirasterisasi mengikuti grid citra menggunakan fungsi rasterize dari rasterio, kemudian nilai piksel RGB pada lokasi training diekstraksi sebagai fitur. Model klasifikasi menggunakan Random Forest (scikit-learn) dengan parameter n_estimators=200, max_depth=20, random_state=42. Data dibagi 70% training dan 30% testing dengan stratifikasi berdasarkan kelas. Model dilatih hanya menggunakan training sample dari citra 2020, kemudian digunakan untuk mengklasifikasikan citra 2020 dan 2023 secara terpisah. Pendekatan ini dipilih karena pola spektral tiap kelas relatif konsisten antar waktu, sehingga tidak diperlukan training sample terpisah per tahun.

Feature importance hasil training menunjukkan band Red sebagai yang paling berpengaruh (0,459), diikuti Blue (0,279) dan Green (0,262).

### 4.3 Uji Akurasi

Uji akurasi dilakukan menggunakan 30% data testing yang tidak dilibatkan dalam training. Metrik yang dihitung meliputi confusion matrix, Overall Accuracy, Cohen's Kappa, Producer's Accuracy, dan User's Accuracy per kelas, menggunakan scikit-learn.

### 4.4 Analisis Perubahan (2020-2023)

Matriks transisi dihitung dari perbandingan piksel demi piksel antara hasil klasifikasi 2020 dan 2023 pada area yang valid di kedua tahun (bukan nodata), menghasilkan matriks probabilitas transisi antar kelas yang menjadi dasar model proyeksi.

### 4.5 Faktor Pendorong dan Pembatas

Mengingat keterbatasan waktu pengerjaan, driving factor dan restricting factor dipilih dari variabel yang dapat dihitung langsung dari data yang sudah tersedia, tanpa dependency ke data eksternal:

- **Driving factor:** jarak Euclidean setiap piksel ke piksel Built-up terdekat pada citra 2023, dihitung menggunakan distance_transform_edt (scipy). Logikanya mengikuti prinsip spatial contagion atau neighborhood effect, area yang lebih dekat dengan lahan terbangun eksisting cenderung lebih mudah berubah menjadi lahan terbangun juga, karena infrastruktur pendukung biasanya sudah lebih tersedia di sekitarnya. Jarak rata-rata ke Built-up terdekat adalah 293,5 piksel (sekitar 2,9 km), dengan jarak maksimum 2198,4 piksel (sekitar 22 km) di area yang diperkirakan merupakan wilayah pegunungan utara Tabanan.
- **Restricting factor:** mask badan air pada citra 2023 (49.190 piksel). Piksel yang teridentifikasi sebagai badan air dikunci untuk tetap menjadi badan air pada hasil proyeksi, mengikuti prinsip bahwa badan air secara fisik jarang berubah kelas dalam rentang waktu proyeksi yang pendek (3 tahun).

DEM (elevasi dan kemiringan lereng) serta data jaringan jalan diidentifikasi sebagai faktor yang secara teori lebih representatif, namun tidak digunakan karena keterbatasan waktu untuk mengunduh, mereproyeksi, dan menyelaraskan data eksternal tersebut dengan grid citra.

### 4.6 Model Proyeksi (2026)

Proyeksi menggunakan pendekatan Markov Chain, dipilih dengan pertimbangan berikut:

- Cocok untuk data dua titik waktu (2020 dan 2023), karena hanya membutuhkan minimal dua titik waktu untuk menghitung matriks probabilitas transisi.
- Merupakan metode standar dalam literatur perubahan tutupan lahan, sering dikombinasikan dengan Cellular Automata (CA-Markov), sehingga hasilnya dapat dibandingkan dengan studi sejenis.
- Asumsi utamanya adalah pola perubahan pada periode sebelumnya (2020 ke 2023) akan berlanjut dengan pola serupa pada periode berikutnya (2023 ke 2026). Asumsi ini merupakan salah satu keterbatasan utama model, karena tidak dapat menangkap perubahan kebijakan, bencana, atau intervensi lain yang tidak tercermin pada data historis.

Setiap piksel pada tahun dasar diberi probabilitas berubah kelas berdasarkan matriks transisi, dengan probabilitas menjadi Built-up dimodifikasi (ditingkatkan) berdasarkan driving factor, dan piksel Water Body dikunci sesuai restricting factor. Untuk mengurangi noise spasial hasil sampling per piksel (efek salt and pepper), diterapkan majority filter berbasis one-hot encoding dan uniform_filter, dipilih karena secara metodologis lebih tepat untuk data kategorikal dibandingkan median filter konvensional yang sempat dicoba sebelumnya (median filter menghitung median numerik dari kode kelas, yang tidak bermakna untuk data kategorikal dan sempat menghasilkan distorsi pada distribusi kelas hasil proyeksi).

Sebelum digunakan untuk proyeksi 2026, model divalidasi melalui hindcast, yaitu mensimulasikan kondisi 2023 menggunakan data dasar 2020 dan model yang sama, kemudian membandingkan hasilnya dengan hasil klasifikasi 2023 yang sebenarnya.

## 5. Hasil

### 5.1 Peta Klasifikasi 2020 dan 2023

Distribusi kelas tutupan lahan (dihitung dari piksel valid, tidak termasuk nodata):

| Kelas | 2020 | 2023 |
|---|---|---|
| Built-up | 19,6% | 25,3% |
| Vegetation | 48,1% | 40,5% |
| Agriculture | 31,3% | 33,2% |
| Bare Land | 0,5% | 0,7% |
| Water Body | 0,5% | 0,3% |

Lahan terbangun menunjukkan peningkatan sebesar 5,7 poin persen dalam periode tiga tahun, diiringi penurunan vegetasi sebesar 7,6 poin persen, konsisten dengan tren urbanisasi di kawasan Bali selatan.

### 5.2 Hasil Uji Akurasi

Overall Accuracy: 93,52%
Cohen's Kappa: 0,8601 (kategori Almost Perfect, mengacu pada Landis dan Koch, 1977)

| Kelas | User's Accuracy | Producer's Accuracy |
|---|---|---|
| Built-up | 88,76% | 83,33% |
| Vegetation | 97,30% | 98,04% |
| Agriculture | 78,89% | 82,67% |
| Bare Land | 76,72% | 69,18% |
| Water Body | 91,73% | 81,82% |

Kelas Vegetation menunjukkan akurasi tertinggi, konsisten dengan jumlah training sample yang paling banyak. Kelas Bare Land menunjukkan akurasi terendah, konsisten dengan jumlah training sample yang paling sedikit. Kesalahan klasifikasi paling sering terjadi antara kelas Built-up dan Agriculture, kemungkinan karena kemiripan warna RGB antara lahan pertanian kering atau bera dengan area terbangun.

Tabel lengkap tersedia pada file Uji_Akurasi_Sarbagita.xlsx.

### 5.3 Perubahan Tutupan Lahan 2020-2023

Matriks transisi menunjukkan sebagian besar piksel tetap berada pada kelas yang sama (diagonal dominan) untuk kelas Built-up (75,79%), Vegetation (77,47%), dan Agriculture (66,84%). Kelas Water Body dan Bare Land menunjukkan proporsi piksel tetap yang lebih rendah (37,71% dan 31,78%), dengan sejumlah transisi yang secara fisik kurang wajar, misalnya Water Body ke Vegetation atau Agriculture. Pola ini diperkirakan merupakan noise dari akurasi klasifikasi yang lebih rendah pada kedua kelas tersebut, bukan perubahan tutupan lahan yang sesungguhnya. Hal ini menjadi salah satu pertimbangan pemilihan Water Body sebagai restricting factor pada model proyeksi.

### 5.4 Proyeksi Tutupan Lahan 2026

**Validasi hindcast:** simulasi kondisi 2023 dari data dasar 2020 menggunakan model yang sama menghasilkan Overall Accuracy 67,49% dan Cohen's Kappa 0,5106 (kategori Moderate) setelah penerapan majority filter. Hasil ini menunjukkan model memiliki kemampuan prediksi di atas tebakan acak, namun belum sangat presisi.

**Hasil proyeksi 2026:**

| Kelas | 2023 | 2026 (proyeksi) |
|---|---|---|
| Built-up | 25,3% | 43,7% |
| Vegetation | 40,5% | 38,7% |
| Agriculture | 33,2% | 17,3% |
| Bare Land | 0,7% | 0,0% |
| Water Body | 0,3% | 0,2% |

Proyeksi menunjukkan kelanjutan tren peningkatan lahan terbangun dan penurunan lahan pertanian yang cukup signifikan. Peningkatan Built-up yang tajam pada hasil proyeksi ini sebagian merupakan konsekuensi dari desain driving factor yang secara sengaja meningkatkan probabilitas piksel dekat area terbangun eksisting untuk berubah menjadi Built-up. Hasil ini sebaiknya dibaca sebagai skenario berbasis tren historis dan asumsi model, bukan sebagai prediksi pasti.

## 6. Keterbatasan

- Citra yang digunakan hanya memiliki 3 band RGB tanpa band Near Infrared, sehingga indeks vegetasi standar seperti NDVI tidak dapat dihitung, dan klasifikasi sepenuhnya bergantung pada informasi warna.
- Jumlah training sample untuk kelas Bare Land relatif sedikit (5 polygon), berkontribusi pada akurasi kelas ini yang lebih rendah.
- Data yang tersedia hanya mencakup dua titik waktu (2020 dan 2023), membatasi kemampuan model Markov Chain untuk menangkap pola perubahan yang lebih kompleks atau non linear.
- Model proyeksi mengasumsikan pola perubahan historis akan berlanjut dengan pola serupa, dan tidak dapat menangkap perubahan kebijakan, bencana, atau intervensi tata ruang yang tidak tercermin pada data historis.
- Driving factor dan restricting factor yang digunakan bersifat sederhana (jarak ke Built-up dan mask Water Body), diturunkan dari data yang sudah tersedia karena keterbatasan waktu pengerjaan. Faktor yang secara teori lebih representatif, seperti elevasi, kemiringan lereng dari DEM, dan jarak ke jaringan jalan, tidak digunakan karena keterbatasan waktu untuk memperoleh dan menyelaraskan data eksternal tersebut.
- Validasi hindcast menunjukkan akurasi proyeksi (Kappa 0,5106, kategori Moderate) yang jauh lebih rendah dibandingkan akurasi klasifikasi (Kappa 0,8601, kategori Almost Perfect), mengindikasikan bahwa tahap pemodelan perubahan memiliki ketidakpastian yang jauh lebih besar dibandingkan tahap klasifikasi citra.
- Tutupan awan pada citra (diperkirakan kurang dari 10% dari total area) tidak ditangani dengan cloud masking khusus, sehingga area yang tertutup awan berpotensi mengalami misklasifikasi.

## 7. Struktur Repository

```
PerubahanTutupanLahan_Sarbagita_ILASPP/
├── data/          # citra dan data pendukung (atau catatan sumber jika file besar)
├── training/      # training sample (.shp beserta file pendukungnya)
├── src/           # script python
├── output/        # hasil klasifikasi dan proyeksi (.tif)
├── accuracy/      # tabel uji akurasi (.xlsx)
└── README.md
```

## 8. Cara Menjalankan

1. Siapkan environment Python dengan library numpy, pandas, geopandas, rasterio, scikit-learn, dan scipy.
2. Letakkan citra Sarbagita_2020.tif dan Sarbagita_2023.tif pada folder data/.
3. Letakkan training sample (format shapefile, CRS EPSG:4326) pada folder training/.
4. Jalankan script pada folder src/ secara berurutan, mulai dari praproses, klasifikasi, uji akurasi, analisis perubahan, hingga proyeksi.
5. Hasil raster akan tersimpan pada folder output/, dan tabel uji akurasi pada folder accuracy/.

## 9. Referensi

- Landis, J. R., dan Koch, G. G. (1977). The Measurement of Observer Agreement for Categorical Data. Biometrics.
- Dokumentasi rasterio: https://rasterio.readthedocs.io
- Dokumentasi geopandas: https://geopandas.org
- Dokumentasi scikit-learn: https://scikit-learn.org
- Dokumentasi scipy: https://docs.scipy.org
