# -*- coding: utf-8 -*-
"""One-off builder for the karhutla work plan."""
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

wb = Workbook()

NAVY = "1B3A4B"
TEAL = "0F6E6B"
INK = "1F2933"
MUTED = "52606D"
LINE = "D9E2EC"
ANCA = "D6E6F5"
FARID = "D9EFE3"
JOSE = "FDE8D0"
BERSAMA = "E6E0F5"
GAGAL = "FDECEC"
WHITE = "FFFFFF"
ZEBRA = "F7F9FB"

thin = Border(
    left=Side(style="thin", color=LINE),
    right=Side(style="thin", color=LINE),
    top=Side(style="thin", color=LINE),
    bottom=Side(style="thin", color=LINE),
)
wrap = Alignment(wrap_text=True, vertical="top", horizontal="left")
center = Alignment(wrap_text=True, vertical="center", horizontal="center")


def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)


owner_fill = {"Anca": ANCA, "Farid": FARID, "Jose": JOSE, "Bersama": BERSAMA}

tasks = [
    ["B1", "Bersama", "Kunci cerita", "Kunci sisa keputusan yang masih terbuka",
     "S0 sudah selesai: repo karhutla-idc ada, ONI dan batas kabupaten sudah terunduh. Rapat ini tidak mengulang pilihan tema. Yang dikunci: 10 provinsi termasuk Kepri dan Babel sampai panitia menjawab; cut-off kerja 31 Oktober 2026 sampai data bulan itu lengkap; satu sensor VIIRS S-NPP 375 m; Trase/MapBiomas sebagai angka luas utama; SiPongi hanya pembanding; tidak ada nama perusahaan. Tulis satu kalimat tesis kerja: jejak api Sumatera 2015–2026 ditinjau dari gambut, fase ENSO, dan sebaran antarprovinsi. Hipotesis H1–H6 tetap harus diuji, bukan dianggap benar.",
     "Catatan keputusan satu halaman di docs/methodology.md bagian keputusan, plus daftar pertanyaan yang Farid kirim ke panitia.",
     "Jawaban panitia bila sudah ada. Jika belum, keputusan default di atas dipakai dan dicatat sebagai default.",
     "Brief bagian 11, AGENTS.md, dan berkas yang sudah ada di data/raw.",
     "—", 1,
     "Tiga orang bisa menyebut sensor, cut-off, dan sumber luas utama yang sama.",
     "Kalau masih ada usul sumber hotspot lain, tidak dicampur ke deret S-NPP. Usul ditunda sampai go/no-go 14 November. Jangan mulai pipeline dengan dua sensor.",
     "Farid menulis keputusan. Anca menolak sumber yang tidak bisa diverifikasi."],
    ["B2", "Bersama", "Go atau berhenti", "Putuskan apakah tiga data inti bisa digabung",
     "Pada 14 November cek tiga syarat sekaligus: arsip hotspot VIIRS S-NPP sudah ada di data/raw, luas terbakar Trase terbaca per kabupaten, dan luas gambut terbakar atau persentase gambut bisa disambungkan ke kabupaten yang sama. Tunjukkan satu kabupaten contoh dengan tiga angka itu berdampingan. Jika salah satu tidak ada, ini belum go.",
     "Keputusan tertulis: lanjut karhutla, atau berhenti dan pindah tema. Keputusan disimpan di docs/methodology.md.",
     "Status email FIRMS, berkas Trase, dan jumlah kabupaten yang gagal dicocokkan.",
     "Log unduhan Farid dan percobaan gabung Anca.",
     "A2, A3, F2, F5", 1,
     "Ada kalimat lanjut atau berhenti, dengan alasan yang menunjuk berkas, bukan perkiraan.",
     "Kalau belum go, 15 November tidak dipakai menambah fitur. Dipakai untuk satu hambatan yang paling dekat selesai, atau untuk memilih tema cadangan. Jangan mengisi hotspot yang belum datang.",
     "Anca yang menyatakan data bisa atau tidak bisa digabung. Farid dan Jose tidak mengganti keputusan itu dengan sumber berita."],
    ["B3", "Bersama", "Tinjau", "Baca kesimpulan H1 sampai H6",
     "Setiap hipotesis dibacakan dengan satu kalimat: didukung, tidak didukung, atau tidak konklusif, plus angka dan tahunnya. Jose menandai kalimat mana yang muat di judul grafik. Farid menandai kalimat mana yang masuk deskripsi karya. Tidak ada hipotesis baru setelah rapat ini.",
     "docs/findings.md versi yang disepakati, dan daftar grafik yang tetap hidup.",
     "Tabel hasil H1–H6 dan catatan metode yang sudah tertulis.",
     "Tahap S4 Anca.",
     "A9", 2,
     "Enam hipotesis punya status. Tidak ada yang dibiarkan kosong.",
     "Kalau datanya tidak mendukung cerita 2026 yang lebih menyebar, judul dashboard mengikuti temuan, bukan judul lama. Jose mengganti judul grafik. Farid mengganti judul bab. Anca tidak melunakkan kalimat supaya cerita tetap dramatis.",
     "Catatan rapat dipegang Farid."],
    ["B4", "Bersama", "Tinjau", "Uji tiga halaman seperti juri",
     "Masing-masing mengoperasikan tautan lihat, tanpa mode edit, selama 20 menit. Ganti tahun, provinsi, dan skenario ENSO. Tutup dengan satu kalimat kesimpulan. Bandingkan dengan findings.md. Kumpulkan paling banyak 12 revisi. Pisahkan salah angka, klaim terlalu kuat, dan chart yang tidak terbaca.",
     "Daftar revisi bernomor. Setelah rapat, tidak ada chart baru.",
     "Tiga halaman Looker tersambung ke CSV final, dan draf deskripsi sudah memakai findings yang sama.",
     "J6, A12, F7.",
     "J6, A12, F7", 2,
     "Satu kalimat kesimpulan disepakati, dan setiap revisi punya pemilik.",
     "Kalau kesimpulan tiga orang berbeda, 25 November hanya merapikan alur dan kalimat. Indikator baru tidak ditambahkan.",
     "Anca menurunkan klaim. Jose menyederhanakan chart. Farid mencoret paragraf yang tidak ada di dashboard."],
    ["B5", "Bersama", "Bekukan", "Checklist ketentuan dan bekukan data",
     "Centang subtema Preservasi Ekosistem Tropis, judul, nomor peserta, sumber data, watermark, 3 halaman, landscape, minimal 1366 piksel, tautan tanpa login, tiga PDF, nama berkas, dan ukuran arsip di bawah 50 MB. Setelah centang lengkap, data di data/processed tidak diubah lagi.",
     "Checklist bertanggal dengan nama pemeriksa tiap butir.",
     "Nomor peserta, template watermark, dan ZIP kandidat.",
     "Panitia dan berkas 25 November.",
     "J8, J9, F8, F10", 1,
     "Semua butir yang dicentang punya bukti. Butir tanpa bukti tetap kosong.",
     "Kalau nomor peserta atau watermark belum ada, jangan membekukan dan jangan mengunggah. Farid menghubungi panitia pada 26 November pagi. Jose menyiapkan posisi tetap agar nomor bisa ditempel tanpa menggeser layout.",
     "Narahubung: Zannuba Arifah Ilman +6285379472612 dan Asri Meilani +6285841622959."],
    ["B6", "Bersama", "Kumpulkan", "Unggah pada 27 November dan simpan bukti",
     "Target kirim 27 November, bukan malam 28 November. Farid mengunggah. Orang lain membuka bukti bahwa berkas masuk. Setelah status berhasil, tidak ada kiriman kedua karena karya pertama yang dinilai.",
     "Tangkapan layar nama berkas, jam, dan status berhasil.",
     "Akun ketua tim dan ZIP beku di bawah 50 MB.",
     "Situs dateraquest.com dan hasil B5.",
     "B5, F10", 1,
     "Bukti unggah tersimpan sebelum pukul 18.00 pada 27 November.",
     "Kalau situs gagal, catat jam percobaan, pindah jaringan, dan hubungi narahubung pada hari yang sama. 28 November hanya untuk mengulang unggah berkas yang sama, bukan untuk mengubah isi.",
     "Pengunggah cadangan adalah Anca, memakai akun ketua tim."],
    ["F1", "Farid", "Data", "Kirim pertanyaan terbuka ke panitia",
     "Kirim satu pesan yang berisi empat hal: subtema Preservasi Ekosistem Tropis tetap sah meski guidebook dan slide berbeda; Kepri dan Babel dihitung sebagai Sumatera; batas ukuran yang dipakai 50 MB; alat yang dipakai Google Looker Studio. Simpan jawaban. Sebelum jawaban datang, kerjakan dengan default yang dikunci di B1.",
     "Pesan terkirim dan tangkapan layarnya ada di folder Kiriman/panitia.",
     "Teks perbedaan guidebook dan slide, plus nomor narahubung.",
     "Guidebook halaman ketentuan dan slide Ketentuan IDC.",
     "B1", 1,
     "Pesan terkirim pada 10 atau 11 November, bukan pada minggu pengiriman.",
     "Kalau tidak ada jawaban sampai 14 November, default tetap dipakai dan dicatat di metodologi. Jangan menghentikan pipeline hanya karena panitia belum membalas.",
     "Anca merumuskan kalimat teknis. Farid yang mengirim."],
    ["F2", "Farid", "Data", "Unduh Trase luas terbakar dan gambut terbakar",
     "Dari halaman Trase, unduh level kabupaten untuk burned area dan fire on peatlands. Jangan mengedit isi berkas. Simpan di folder unduhan dengan nama yang memuat sumber dan tanggal. Catat di docs/sources.md: tanggal unduh, nama berkas, dan apakah unit kolom tertulis di berkas atau tidak. Jika unit tidak tertulis, biarkan kosong. Jangan menganggap hektare sebelum ada bukti di berkas atau dokumentasi yang menyertainya.",
     "Dua berkas mentah Trase plus baris sumber yang diperbarui.",
     "Tombol unduh di dua halaman Trase, dan izin lisensi yang tertulis di halaman atau di dalam berkas.",
     "https://trase.earth/open-data/datasets/spatial-metrics-indonesia-burned-area dan tautan burned peat di brief.",
     "B1", 2,
     "Anca bisa membuka kedua berkas, dan sources.md menyebut tanggal unduh yang benar.",
     "Kalau tombol unduh gagal atau berkas tidak memuat kabupaten, catat pesan galatnya. Jangan mengganti dengan angka dari Databoks atau berita. Bawa bukti ini ke go/no-go.",
     "Anca boleh mencoba unduh yang sama jika Farid terhalang akun, tetapi Farid tetap yang mencatat sumbernya."],
    ["F3", "Farid", "Data", "Cek apakah SiPongi bisa diunduh sebagai pembanding",
     "Buka SiPongi dan panduannya. Cari tabel luas karhutla per provinsi, idealnya per bulan. Jika yang ada hanya gambar atau dasbor yang tidak bisa disalin utuh, tulis tidak tersedia sebagai tabel. Jangan menyalin angka dari tangkapan layar ke pipeline.",
     "Catatan di sources.md: tersedia sebagai tabel, atau tidak.",
     "Alamat situs yang masih aktif. Domain kementerian bisa berpindah.",
     "https://sipongi.menlhk.go.id/ dan panduan PDF yang disebut di brief.",
     "B1", 2,
     "Ada keputusan pakai sebagai pembanding, atau tidak dipakai, dengan alasan yang menunjuk halaman yang dibuka.",
     "Kalau situs tidak bisa dibuka, catat jam dan pesan galat, lalu lanjut tanpa SiPongi. Trase tetap angka utama. Jangan menunda go/no-go hanya karena pembanding ini belum ada.",
     "Anca tidak mencari portal lain secara diam-diam."],
    ["F4", "Farid", "Data", "Lengkapi katalog untuk berkas yang benar-benar diunduh",
     "Untuk setiap berkas di data/raw, pastikan docs/sources.md memuat URL, tanggal akses, versi bila tertulis, lisensi bila tertulis, dan catatan. Kolom yang dipakai diisi hanya setelah Anca menyatakan kolom itu masuk pipeline. Checksum tetap di data/raw/SHA256SUMS. Farid tidak mengubah isi data/raw.",
     "sources.md sesuai dengan isi folder mentah.",
     "Nama kolom yang terlihat di berkas, tanpa menafsirkan unit yang tidak tertulis.",
     "Folder data/raw dan berkas unduhan Trase.",
     "F2, A2", 2,
     "Tidak ada berkas mentah yang tidak punya baris sumber.",
     "Kalau lisensi Trase tidak tertulis, kolom lisensi tetap kosong dan Farid mengirim pertanyaan ke info@trase.earth. Jangan mengisi CC BY hanya karena halaman situs menyebut lisensi itu untuk konten situs.",
     "Anca menunjukkan kolom mana yang akhirnya dipakai, setelah skripnya jalan."],
    ["F5", "Farid", "Data", "Tinjau manual nama kabupaten yang tidak cocok",
     "Anca membuat daftar nama yang gagal bergabung. Farid meninjau satu per satu: ejaan, sisipan kata Kota, dan pemekaran. Ia menulis keputusan di tabel crosswalk: cocok dengan id tertentu, atau memang tidak ada padanan. Tidak ada baris yang dibiarkan tanpa status. Fuzzy match tidak diterima sebagai keputusan final.",
     "Tabel crosswalk dengan status sudah ditinjau untuk semua nama yang gagal.",
     "Daftar gagal dari skrip, nama resmi di geoBoundaries, dan nama di berkas Trase.",
     "Keluaran percobaan gabung Anca.",
     "A7", 4,
     "Nol nama gagal yang belum ditinjau. Itu syarat S2.",
     "Kalau sebuah nama tidak bisa diputuskan, barisnya ditandai belum diputuskan dan angkanya tidak digabung diam-diam. Kabupaten itu keluar dari chart sampai ada keputusan, dan jumlahnya ditulis di metodologi.",
     "Anca tidak menutup baris yang masih bertanda belum ditinjau."],
    ["F6", "Farid", "Naskah", "Susun kerangka deskripsi karya",
     "Urutkan bab seperti tiga halaman dashboard: identitas karya, pertanyaan, data dan metode, 2026 di antara tahun api, di mana dan mengapa, risiko dan prioritas, keterbatasan, sumber. Nomor peserta yang belum ada ditulis [NOMOR PESERTA]. Jangan menulis hasil hipotesis sebelum findings.md ada. Bab metode boleh diisi dari keputusan yang sudah dikunci: satu sensor, cut-off, beda hotspot dan luas terbakar, tidak ada klaim sebab-akibat.",
     "Kerangka deskripsi dengan semua judul bab.",
     "Template panitia bila sudah dibagikan. Ketentuan umum: A4, Times New Roman 12, spasi 1,5, huruf hitam, justify, PDF.",
     "Guidebook bagian deskripsi karya dan keputusan B1.",
     "B1", 1.5,
     "Semua bab wajib sudah punya judul. Identitas ada di halaman pertama.",
     "Kalau template belum turun, isi tetap ditulis di dokumen polos. Format final menyusul. Jangan menunda isi sampai template datang.",
     "Anca mengecek urutan bab. Jose tidak menulis bab analisis."],
    ["F7", "Farid", "Naskah", "Tulis deskripsi dari findings yang sudah dikunci",
     "Setiap angka disebut bersama tahun, satuan, dan sumber. Hotspot dan hektare tidak ditulis sebagai hal yang sama. Gunakan berasosiasi, bukan menyebabkan. Enam hipotesis masuk dengan statusnya, termasuk yang tidak didukung. Tiga provinsi atau kabupaten prioritas harus sama dengan halaman 3. Paragraf yang tidak tampil di dashboard dihapus.",
     "Draf utuh deskripsi karya.",
     "findings.md, paragraf keterbatasan Anca, dan kamus data.",
     "A9, A11, F6.",
     "A9, F6", 5,
     "Anca bisa menunjuk sel atau tabel sumber untuk setiap angka di naskah.",
     "Kalau findings terlambat, Farid menyelesaikan bab data dan metode lebih dulu. Angka temuan tidak ditulis dari berita Katadata atau Mongabay. Angka berita hanya boleh menjadi kalimat konteks yang disebut sebagai berita, bukan sebagai hasil olahan.",
     "Anca mengedit klaim yang terlalu kuat. Farid tetap pemilik naskah."],
    ["F8", "Farid", "Naskah", "Format dan ekspor PDF deskripsi serta surat",
     "Terapkan format panitia pada naskah yang sudah lolos audit angka. Ekspor PDF bernama IDTim_NamaTim_DeskripsiDashboard. Isi surat orisinalitas dari tautan panitia. PDF surat bernama IDTim_NamaTim_SuratOrisinalitas. Placeholder nomor peserta harus sudah hilang.",
     "Dua PDF final.",
     "ID tim, nama tim, nomor peserta, dan cara tanda tangan yang diminta panitia.",
     "Audit A13 dan tautan surat dari panitia.",
     "A13, F7", 2.5,
     "PDF terbuka di komputer Anca dan Jose, tanpa komentar dan tanpa placeholder.",
     "Kalau surat belum dibagikan pada 25 November, Farid menghubungi panitia hari itu. Paket tidak dikirim tanpa surat. PDF deskripsi yang masih berisi placeholder tidak masuk ZIP.",
     "Anca mengekspor PDF dari berkas yang Farid kunci, bila aplikasi Farid bermasalah."],
    ["F9", "Farid", "Kumpulkan", "Rakit ZIP dan unggah",
     "PDF dashboard hanya berisi judul, nomor peserta, nama tim, dan tautan Looker. Gabungkan tiga PDF menjadi ZIP bernama IDTim_NamaTim. Ukuran di bawah 50 MB. Unggah 27 November. Simpan bukti. Jangan mengunggah versi kedua.",
     "ZIP final dan bukti unggah.",
     "Tautan yang sudah diuji di jendela penyamaran, tiga PDF, dan akun ketua tim.",
     "J9, F8, B5.",
     "J9, F8, B5", 2.5,
     "ZIP terbuka di dua komputer lain. Tautan di dalam PDF tidak meminta izin. Ukuran di bawah 50 MB.",
     "Kalau ZIP melebihi 50 MB, penyebab yang biasa adalah PDF dashboard berisi gambar. Ganti PDF itu dengan halaman tautan. Kalau situs down, ikuti B6. Jangan mengirim isi yang berbeda setelah kiriman pertama masuk.",
     "Anca mengunggah bila Farid tidak bisa masuk ke situs. Jose memeriksa izin tautan."],
    ["A1", "Anca", "Data", "Minta arsip FIRMS hari ini",
     "Ajukan Archive Download untuk VIIRS S-NPP 375 m saja, dari 1 Januari 2015 sampai 31 Oktober 2026. Wilayah unduh mencakup 10 provinsi Sumatera; bbox kerja lintang -6,5 sampai 6,5 dan bujur 94,5 sampai 109,5, lalu titik di luar poligon dibuang nanti. Minta CSV. Catat jam pengajuan dan alamat email tujuan. Jangan menambahkan NOAA-20, NOAA-21, atau MODIS ke permintaan yang sama.",
     "Bukti permintaan terkirim, dengan parameter sensor, tanggal, dan wilayah tertulis.",
     "Akun Earthdata atau alur kode email di halaman unduh FIRMS.",
     "https://firms.modaps.eosdis.nasa.gov/download/",
     "B1", 1,
     "Ada bukti permintaan pada 10 November, sebelum tengah malam.",
     "Kalau login gagal, catat pesan galatnya dan coba kode email yang disediakan halaman itu. Jangan beralih ke API atau sensor lain pada hari yang sama. Bawa kegagalan ini ke Farid supaya sources.md mencatatnya.",
     "Farid menyimpan tangkapan layar di folder panitia/data bila Anca sudah mendapat bukti."],
    ["A2", "Anca", "Data", "Simpan arsip FIRMS tanpa mengubah isinya",
     "Saat email arsip datang, simpan berkas apa adanya ke data/raw lewat skrip checksum. Jangan membuka lalu menyimpan ulang dari spreadsheet. Catat jumlah baris mentah. Filter belum dilakukan di langkah ini. Jika email belum datang pada 13 November malam, laporkan statusnya dan siapkan go/no-go tanpa hotspot.",
     "Berkas mentah FIRMS di data/raw dengan baris SHA256SUMS.",
     "Tautan email FIRMS, masa berlaku tautan, dan kolom yang benar-benar ada, terutama confidence dan type.",
     "Email arsip dan FAQ FIRMS.",
     "A1", 1.5,
     "Checksum tercatat dan berkas bisa dibaca skrip tanpa diedit tangan.",
     "Kalau tautan email kedaluwarsa, minta ulang dengan parameter yang sama pada hari tautan itu gagal. Jangan mengunduh NRT harian sebagai pengganti arsip lalu menyambungnya diam-diam.",
     "Farid mencatat tanggal tiba di sources.md. Jose tidak memakai angka dari email."],
    ["A3", "Anca", "Data", "Baca Trase ke tabel kabupaten-tahun",
     "Skrip membaca berkas yang Farid unduh, menyimpan salinan mentah, dan menulis parquet interim. Simpan nama kolom asli. Jangan mengisi unit yang tidak tertulis. Jangan menjumlahkan luas terbakar dengan jumlah hotspot. Hasilkan hitungan: berapa nama kabupaten yang unik, tahun minimum, tahun maksimum.",
     "Parquet interim luas terbakar dan gambut terbakar, plus catatan tahun dan jumlah nama.",
     "Arti kolom bila ada di dokumentasi berkas. Metodologi Fire Koleksi 2 bila sudah dibuka.",
     "Berkas F2 dan metodologi Auriga bila tersedia.",
     "F2", 2.5,
     "Tahun minimum dan maksimum dilaporkan dari berkas, dan satu total contoh bisa dihitung ulang dengan spreadsheet.",
     "Kalau berkas tidak sampai 2025 atau 2026, kosongkan tahun yang tidak ada. Jangan menyalin angka factsheet Auriga ke dalam tabel. Factsheet tetap sanity check di dokumen, terpisah dari kolom pipeline.",
     "Farid menulis tahun yang hilang ke sources.md."],
    ["A4", "Anca", "Data", "Hitung persentase gambut hanya jika petanya ada",
     "Persentase gambut kabupaten dipakai sebagai fitur dan sebagai penjelas. Sumber yang sudah disebut masih harus dipilih dari berkas yang benar-benar bisa diunduh. Jika Global Peatland Map atau alternatifnya belum ada saat panel dibangun, kolom peat_share_pct tetap kosong. Luas gambut terbakar dari Trase tidak dipakai sebagai pengganti persentase tutupan gambut, karena keduanya mengukur hal yang berbeda.",
     "Kolom peat_share_pct terisi, atau catatan bahwa kolom itu sengaja kosong.",
     "Lisensi dan definisi nilai raster. Untuk Global Peatland Map, brief menyebut nilai 1 dan 2. Konfirmasi di berkas sebelum menghitung.",
     "Sumber gambut bagian 4.3 brief, setelah manusia mengunduhnya.",
     "F2", 2,
     "Setiap kabupaten berstatus terhitung atau dikecualikan dengan alasan.",
     "Kalau raster tidak bisa diunduh sampai 16 November, model dan halaman gambut memakai luas terbakar di lahan gambut dari Trase, dan persentase tutupan ditulis tidak tersedia. Jangan mengira-ngira persentase dari berita 60 persen.",
     "Farid mengunduh raster bila halaman Earth Engine atau katalognya membutuhkan klik manusia."],
    ["A5", "Anca", "Analisis", "Susun fase ENSO dari ONI yang sudah terunduh",
     "Berkas ONI sudah ada, dari DJF 1950 sampai ASO 2026, dengan kolom SEAS, YR, TOTAL, dan ANOM. Baca halaman ONI change dan readme sebelum menetapkan ambang El Niño, netral, dan La Niña. Jika ambang resmi tidak berhasil dikonfirmasi, jangan mengarang kategori. Simpan anomali mentahnya, dan tandai enso_phase kosong.",
     "Tabel musim ke fase, atau catatan bahwa fase belum boleh diisi.",
     "Ambang resmi pada halaman CPC yang berhasil dibuka, dan cara CPC menamai musim tiga bulan.",
     "data/raw/oni/oni.ascii.txt dan dua halaman CPC di sources.md.",
     "B1", 1.5,
     "Setiap musim 2015 sampai ASO 2026 punya anomali. Fase terisi hanya bila ambangnya bersumber.",
     "Kalau halaman ambang tidak bisa dibuka, dashboard boleh menampilkan garis ONI tanpa warna fase. Jose tidak mewarnai fase dari ingatan. Anca menulis keterbatasan ini di metodologi.",
     "Farid membantu membuka halaman CPC bila diblokir di jaringan Anca, lalu mengirim berkas yang terlihat, bukan ringkasan dari blog."],
    ["A6", "Anca", "Analisis", "Gabungkan titik panas ke kabupaten",
     "Spatial join pada EPSG:4326 antara titik di dalam bbox dan poligon geoBoundaries. Hitung luas kabupaten pada CRS equal-area untuk area_km2. Buang titik di luar 10 provinsi dan tulis jumlahnya di log, terpisah untuk laut, luar negeri, dan provinsi Indonesia lain. Simpan confidence n dan h. Buang l. Jika kolom type ada, simpan hanya type 0. Jika tidak ada, tulis di metodologi bahwa sumber panas statis belum bisa dibuang dengan kolom itu.",
     "Tabel titik yang sudah punya kab_id, plus log jumlah yang dibuang.",
     "Nama kolom confidence dan type pada berkas FIRMS yang diterima, serta daftar 10 provinsi pada poligon.",
     "A2 dan data/raw/boundaries/idn_adm2.geojson.",
     "A2", 3,
     "Sedikitnya 99 persen titik di dalam bbox Sumatera terhubung ke kabupaten. Sisanya ada di log.",
     "Kalau join di bawah 99 persen, jangan menaikkan toleransi diam-diam. Laporkan kabupaten atau geometri yang bermasalah. Perbaikan ejaan tidak menyelesaikan titik yang jatuh di laut. Titik itu dibuang dan dihitung.",
     "Farid memeriksa daftar kabupaten dengan nol titik pada tahun yang seharusnya ada api, untuk membedakan nol yang sah dan join yang gagal."],
    ["A7", "Anca", "Analisis", "Buat crosswalk nama, lalu serahkan yang gagal",
     "Normalisasi nama secara eksplisit: huruf kecil, spasi, dan urutan kata Kota. Hasil yang tetap gagal ditulis ke CSV untuk Farid, bukan dipaksa dengan fuzzy match. Setelah Farid selesai meninjau, skrip hanya menerima padanan yang statusnya sudah ditinjau.",
     "CSV gagal-gabung dan, setelah tinjauan, crosswalk final.",
     "Nama unik dari Trase, dari poligon, dan keputusan Farid.",
     "A3 dan F5.",
     "A3", 2,
     "Nol kabupaten tanpa padanan yang belum ditinjau.",
     "Kalau Farid belum selesai meninjau, panel kabupaten-tahun tidak dibuat. Lebih baik mundur satu hari daripada menggabungkan nama yang salah.",
     "Jose tidak memperbaiki nama di dalam Looker."],
    ["A8", "Anca", "Analisis", "Bangun panel bulan dan panel tahun",
     "fact sementara di parquet: satu baris per kabupaten per bulan dari 2015-01 sampai cut-off, tanpa duplikat. Bulan tanpa titik diisi nol untuk hitungan hotspot, bukan dikosongkan. Curah hujan yang belum ada tetap NaN. Total hotspot per tahun harus sama dengan agregat berkas mentah setelah filter yang sudah didokumentasikan. Pytest untuk duplikat, cakupan bulan, dan rekonsiliasi total.",
     "Parquet panel dan tes yang lulus.",
     "Cut-off final, filter confidence, dan crosswalk final.",
     "A5, A6, A7.",
     "A5, A6, A7", 3,
     "pytest untuk tiga syarat S3 lulus, dan satu total tahunan bisa dihitung ulang.",
     "Kalau CHIRPS belum masuk, panel tetap dibuat tanpa hujan. Kolom hujan tetap ada dan berisi NaN. Hipotesis H3 yang butuh hujan ditandai tidak konklusif bila data itu tidak datang sebelum 18 November. Jangan mengisi hujan dari rata-rata kira-kira.",
     "Farid menjalankan pytest sekali di komputernya bila Anca sudah mendorong kodenya, supaya tes tidak hanya lulus di satu mesin."],
    ["A9", "Anca", "Analisis", "Uji H1 sampai H6 dan tulis findings.md",
     "Tiap hipotesis menghasilkan satu tabel dan satu kalimat status. H1 memakai indeks konsentrasi per tahun, lalu dibandingkan 2026 dengan 2019 pada bulan yang sama-sama tersedia. H2 membandingkan porsi gambut dan mineral antarprovinsi dan antarbulan, hanya dari kolom yang memang terpisah. H3 menghubungkan ONI dan anomali hujan dengan lag 0–3 bila hujannya ada. H4 menghitung share kumulatif kabupaten. H5 menetapkan N sebelum melihat daftar, lalu baru menghitung kabupaten yang memenuhi N. H6 membandingkan bulan puncak provinsi utara dan selatan. Jika bukti tidak cukup, statusnya tidak konklusif.",
     "docs/findings.md dengan enam status.",
     "Panel final dan definisi N yang ditulis sebelum tabel H5 dihasilkan.",
     "A8.",
     "A8", 3.5,
     "Setiap hipotesis punya tabel, kalimat, dan status. Tidak ada angka dari artikel berita di dalam tabel.",
     "Kalau cut-off membuat 2026 hanya terisi sebagian tahun, H1 membandingkan Januari sampai bulan cut-off pada 2019 dan 2026, bukan setahun penuh lawan sebagian tahun. Tuliskan jendela bulan itu di kalimatnya.",
     "Jose hanya mengambil kalimat yang statusnya didukung atau tidak didukung. Yang tidak konklusif masuk catatan, bukan judul utama."],
    ["A10", "Anca", "Model", "Latih model dan bandingkan dengan baseline",
     "Targetnya hitungan hotspot confidence minimal nominal pada horizon 1, 2, dan 3 bulan. Validasi hanya berurutan waktu. Baseline wajib: persistence dan klimatologi musiman. Metrik MAE dan Poisson deviance untuk regresi. Jangan memakai random split. Jika model tidak mengalahkan klimatologi, tulis itu di model_metrics dan jangan menampilkan skor model sebagai perkiraan utama.",
     "model_metrics terisi dengan angka model dan kedua baseline.",
     "Panel bulan yang lulus tes, dan daftar fitur yang kolomnya benar-benar terisi.",
     "A8 dan bagian 7 brief.",
     "A8", 2.5,
     "Setiap metrik model punya angka baseline di sampingnya.",
     "Kalau model kalah, halaman 3 beralih ke risiko klimatologi bersyarat fase ENSO. Jose tidak membuat grafik feature importance untuk model yang tidak dipakai. Anca menulis alasannya dalam satu paragraf.",
     "Farid menyalin paragraf itu ke bab keterbatasan, tanpa menambah klaim akurasi."],
    ["A11", "Anca", "Model", "Buat tiga skenario ENSO, bukan satu prediksi",
     "Keluarkan ml_risk_forecast untuk skenario netral, El Niño, dan La Niña pada jendela musim kering yang sudah ditulis di temuan. Skor 0–1, peringkat, dan kelas hanya boleh diisi setelah aturan kelasnya tertulis. Jika yang dipakai adalah klimatologi karena model kalah, kolom skenario tetap ada dan top_driver menjelaskan bahwa pendorongnya adalah klimatologi plus fase, bukan importance model.",
     "CSV prakiraan yang lolos skema Pandera.",
     "Hasil A10 dan ambang kelas yang ditulis dulu di metodologi.",
     "A10, A5.",
     "A10", 1.5,
     "Tiga skenario lengkap untuk kabupaten yang masuk panel, atau satu catatan bahwa skenario tidak dibuat plus alasannya.",
     "Kalau fase ENSO belum sah, jangan membuat tiga skenario. Ekspor satu peta klimatologi dan tulis bahwa skenario ditunda. Lebih baik halaman 3 jujur daripada tiga peta dengan fase yang dikarang.",
     "Jose menyiapkan tiga kontrol skenario, dan menyembunyikannya bila CSV skenario tidak jadi."],
    ["A12", "Anca", "Ekspor", "Validasi dan tulis CSV untuk Looker",
     "Jalankan validasi Pandera sebelum menulis data/processed. CSV memakai UTF-8, header snake_case, tanggal ISO, dan desimal titik. Sertakan kolom turunan yang sudah ada di skema supaya Jose tidak membuat banyak blend. model_metrics dan feature_importance tidak ditulis dengan kolom dadakan. Tambahkan kolomnya ke skema dulu, di PR yang sama, berdasarkan isi yang benar-benar dihitung.",
     "CSV di data/processed yang lolos skema, plus kamus data yang menyebut kolom terisi dan kolom yang sengaja kosong.",
     "Skema src/export/schemas.py dan temuan final.",
     "A8, A9, A11.",
     "A9, A11", 1.5,
     "Perintah ekspor bisa diulang dari data/raw dan menghasilkan checksum CSV yang sama.",
     "Kalau validasi gagal, CSV tidak ditulis. Jose tetap memakai parquet atau cuplikan yang diberi tanda belum final. Jangan mengunggah CSV yang gagal skema ke Looker lalu memperbaikinya di dalam Looker.",
     "Farid menyalin catatan kolom kosong ke bab metode."],
    ["A13", "Anca", "Tinjau", "Audit angka dashboard dan naskah",
     "Cocokkan scorecard, peta provinsi, dan tiga kabupaten prioritas dengan CSV. Pisahkan audit hotspot dan audit hektare. Tandai klaim menyebabkan, terbukti, dan nama pihak yang tidak boleh ada. Hasilnya ditulis di tabel audit: nama chart, nilai Looker, nilai CSV, lulus atau tidak.",
     "Tabel audit tanpa baris gagal yang masih terbuka, lalu satu kali baca ulang pada PDF.",
     "Tautan Looker versi lihat dan CSV final.",
     "J4, J5, J6, F7.",
     "J6, F7", 1.5,
     "Tidak ada angka publik yang gagal audit.",
     "Chart yang gagal disembunyikan sampai lulus. Anca tidak mengubah layout. Jose tidak mengubah angka di calculated field untuk memaksa cocok.",
     "Farid mengulang audit empat angka utama sebagai pemeriksa kedua."],
    ["J1", "Jose", "Desain", "Uji peta Looker pada report percobaan",
     "Buat report percobaan, terpisah dari report lomba. Uji apakah kode ISO 3166-2 mengisi peta provinsi untuk ID-AC, ID-SU, ID-SB, ID-RI, ID-KR, ID-JA, ID-SS, ID-BE, ID-LA, dan ID-BB. Uji apakah Looker mengenal poligon kabupaten. Jika tidak, putuskan cadangan: peta isian untuk provinsi dan peta gelembung dari field latlon untuk kabupaten. Catat hasilnya di satu halaman, karena keputusan ini mengubah data yang Anca ekspor.",
     "Catatan uji peta: provinsi berhasil atau gagal, kabupaten berhasil atau gagal, dan cadangan yang dipilih.",
     "Akun Google yang memiliki Looker Studio, dan contoh 10 kode ISO.",
     "Brief bagian 6, catatan Looker.",
     "B1", 2,
     "Ada keputusan tertulis sebelum 12 November, sehingga Anca tidak mengekspor geometri yang tidak akan terpakai.",
     "Kalau peta provinsi pun gagal, jangan mengganti alat ke Tableau. Pakai peta gelembung untuk keduanya dan tulis keterbatasannya. Farid memasukkannya ke bab metode.",
     "Anca menyediakan satu CSV contoh berlabel CONTOH, dengan 10 baris provinsi, bukan data lomba."],
    ["J2", "Jose", "Desain", "Storyboard tiga halaman",
     "Halaman 1: 2026 di antara tahun-tahun api. Halaman 2: di mana dan mengapa. Halaman 3: risiko dan prioritas. Tiap halaman punya satu kalimat yang harus terbaca dalam 10 detik, tempat filter, tempat sumber, dan tempat nomor peserta. Grafik yang tidak menjawab H1–H6 tidak masuk. Hotspot dan luas terbakar tidak digabung dalam satu sumbu.",
     "Storyboard tiga halaman.",
     "Hasil uji peta J1 dan daftar hipotesis.",
     "J1 dan brief bagian 3.",
     "J1", 2.5,
     "Orang lain bisa menunjuk di storyboard tempat juri melihat jawaban tiap hipotesis yang mungkin tampil.",
     "Kalau storyboard butuh halaman keempat, potong sebelum membangun. Yang dipotong adalah grafik dampak kesehatan, karena datanya masih berupa kutipan berita.",
     "Anca berhak mengeluarkan grafik yang menyamakan hotspot dengan hektare. Jose berhak menolak grafik yang tidak terbaca."],
    ["J3", "Jose", "Desain", "Kunci warna dan hierarki",
     "Pakai warna yang tetap untuk hotspot, luas terbakar, gambut, dan rata-rata pembanding. Jangan mengandalkan merah-hijau saja. Judul karya, nomor peserta, dan sumber berada di tempat yang sama pada tiga halaman. Gaya ini tidak diganti setelah 19 November kecuali uji juri menunjukkan teks tidak terbaca.",
     "Satu kartu angka dan satu chart contoh dengan gaya terkunci.",
     "Judul kerja. Nomor peserta bila sudah ada.",
     "Storyboard J2.",
     "J2", 1.5,
     "Tiga halaman nanti terlihat seperti satu laporan.",
     "Kalau gaya diubah di tengah pembangunan, waktu habis untuk merapikan. Setelah halaman 1 terisi data sungguhan, perubahan gaya harus disetujui di rapat, bukan di chat malam.",
     "Farid memeriksa apakah sumber masih terbaca setelah warna final."],
    ["J4", "Jose", "Bangun dashboard", "Bangun halaman 1 dari CSV final",
     "Sambungkan CSV processed, bukan ketikan tangan. Halaman 1 memuat KPI 2026 dibanding rata-rata 2015–2025 pada jendela bulan yang sama, deret bulanan, dan peta provinsi. Filter tahun dan provinsi. Label harus membedakan jumlah hotspot dan luas hektare. Default tahun adalah tahun terakhir yang lengkap menurut metodologi.",
     "Halaman 1 dengan data final dan filter yang hidup.",
     "CSV prov_summary dan fact yang sudah lolos skema, plus kalimat temuan halaman 1.",
     "A12 dan J2.",
     "A12, J3", 4,
     "Mengganti tahun mengubah seluruh chart halaman 1, dan satu angka cocok dengan CSV.",
     "Kalau CSV final belum ada, halaman ini tetap berupa kerangka pada report percobaan. Jangan menyalin angka findings ke dalam scorecard secara manual.",
     "Anca mengaudit angka halaman ini di A13."],
    ["J5", "Jose", "Bangun dashboard", "Bangun halaman 2",
     "Tampilkan gambut dan mineral secara terpisah, konsentrasi sebaran antarprovinsi, heatmap bulan kali tahun, dan kabupaten yang memenuhi aturan kronis dari findings. Filter provinsi menggerakkan chart kabupaten di dalam provinsi itu. Jika H1 tidak didukung, judul halaman mengatakan apa yang ditemukan, bukan mengulang klaim 2026 lebih menyebar.",
     "Halaman 2 interaktif.",
     "Status H1, H2, H4, H5, H6 dan kolom yang tersedia.",
     "A9 dan J4.",
     "A9, J4", 4,
     "Setiap chart halaman 2 punya satu hipotesis induk yang tertulis di catatan Jose.",
     "Kalau kolom hujan kosong, scatter anomali hujan tidak dipasang. Jangan menggantinya dengan grafik hiasan. Ruang itu dipakai untuk kalimat tidak konklusif yang ditulis Anca.",
     "Farid memastikan istilah di chart sama dengan istilah di naskah."],
    ["J6", "Jose", "Bangun dashboard", "Bangun halaman 3",
     "Tampilkan peringkat kabupaten sesuai CSV risiko. Jika ada tiga skenario, kontrol skenario harus terlihat dan nilai defaultnya netral. Jika model kalah dari baseline, halaman ini menampilkan klimatologi bersyarat dan paragraf yang mengatakan hal itu. Sumber data dan keterbatasan harus terbaca pada lebar 1366 tanpa menggulir panjang.",
     "Halaman 3 lengkap secara isi.",
     "ml_risk_forecast atau keputusan bahwa prakiraan model tidak dipakai.",
     "A11 dan A10.",
     "A11", 3,
     "Nama kabupaten prioritas sama dengan findings dan dengan naskah.",
     "Kalau CSV risiko belum lolos skema, halaman 3 hanya memuat kerangka dan catatan belum final. Jangan mengetik peringkat dari memori hasil model.",
     "Anca memberi urutan kabupaten. Jose tidak memilih kabupaten prioritas sendiri."],
    ["J7", "Jose", "Bangun dashboard", "Samakan filter pada tiga halaman",
     "Kontrol tahun, provinsi, dan skenario berada di tempat yang sama, dengan nilai default yang sama. Pada lebar 1366, kontrol tidak menutupi angka. Chart yang tidak mengikuti filter diperbaiki atau dihapus sebelum uji juri.",
     "Tiga halaman dengan kontrol yang perilakunya sama.",
     "Nilai default dari metodologi.",
     "J4, J5, J6.",
     "J4, J5, J6", 2,
     "Orang baru menemukan filter yang sama di halaman 2 tanpa dijelaskan.",
     "Chart yang diam saat filter diganti terlihat seperti data yang bertentangan. Chart itu tidak boleh ikut saat B4.",
     "Anca menguji filter saat audit."],
    ["J8", "Jose", "Patuh ketentuan", "Pasang identitas karya dan cek kanvas",
     "Pasang judul, nomor peserta, watermark bila template sudah ada, dan sumber di setiap halaman. Orientasi landscape. Tepat tiga halaman. Cek pada lebar 1366 bahwa teks tidak terpotong.",
     "Tangkapan 1366 untuk tiga halaman.",
     "Template watermark dan nomor peserta.",
     "Panitia dan J7.",
     "J7", 2,
     "Identitas dan sumber terlihat di ketiga halaman.",
     "Kalau template belum ada, sisakan posisi yang sama di tiga halaman dan jangan menggeser layout pada 26 November hanya untuk menempel nomor.",
     "Farid memeriksa ejaan judul terhadap keputusan B1."],
    ["J9", "Jose", "Patuh ketentuan", "Buka tautan untuk siapa saja yang memegang link",
     "Ubah izin report lomba menjadi siapa saja dengan tautan dapat melihat. Uji di jendela penyamaran. Berikan tautan ke Farid untuk PDF. Jangan mengubah izin menjadi pribadi setelah unggah.",
     "Tautan publik yang sudah diuji.",
     "Report yang sudah lolos audit angka.",
     "A13 dan J8.",
     "A13, J8", 1.5,
     "Anca dan Farid membuka tautan dari akun yang bukan pemilik report, tanpa permintaan akses.",
     "Kalau tautan masih minta izin, juri tidak bisa menilai interaktivitas. Perbaiki izin sebelum ZIP dibuat. Jangan mengganti dashboard dengan tangkapan layar.",
     "Report juga disimpan di akun ketua tim, supaya tautan tidak bergantung pada satu akun pribadi."],
]

days = [
    ["2026-11-10", "Selasa", "Kunci cerita", "B1, A1, F1, F2, J1",
     "Sore, 45 menit. S0 sudah selesai, jadi rapat hanya mengunci default: 10 provinsi, cut-off Oktober 2026, satu sensor, Trase sebagai luas utama. Bagi sisa hari ini.",
     "Kirim permintaan arsip FIRMS sebelum tengah malam. VIIRS S-NPP 375 m, 1 Januari 2015 sampai 31 Oktober 2026, bbox Sumatera. Simpan bukti parameter.",
     "Kirim pertanyaan ke panitia. Unduh dua berkas Trase level kabupaten. Jangan mengedit isinya. Simpan dengan tanggal di nama berkas.",
     "Buka report percobaan. Uji peta ISO 10 provinsi dan cek apakah kabupaten bisa jadi peta isian. Tulis hasilnya, walaupun masih kasar.",
     "Bukti permintaan FIRMS, dua berkas Trase atau catatan gagal unduh, dan catatan uji peta versi awal.",
     "Repo S0 dan akun Earthdata atau jalur kode email.",
     "Kalau FIRMS tidak bisa diminta karena akun ditolak, catat pesannya dan coba kode email di halaman yang sama. Jangan ganti sensor malam ini.",
     "Tinggi"],
    ["2026-11-11", "Rabu", "Data", "A5, F3, F4, J1, J2",
     "Tidak ada rapat panjang. Sore 15 menit hanya untuk status email FIRMS dan hasil uji peta.",
     "Cek email pagi dan sore. Jika arsip belum datang, kerjakan ONI: baca readme dan halaman ONI change. Jangan mengisi fase sebelum ambangnya ketemu.",
     "Cek SiPongi. Perbarui sources.md untuk Trase: tanggal, nama berkas, lisensi yang benar-benar tertulis, tahun yang terlihat. Unit yang tidak tertulis dibiarkan kosong.",
     "Selesaikan catatan uji peta dan gambar storyboard tiga halaman. Pisahkan hotspot dan hektare sejak di sketsa.",
     "Keputusan peta tertulis. sources.md untuk Trase terbarui. Storyboard tiga halaman.",
     "Unduhan 10 November dan ONI yang sudah ada di data/raw.",
     "Kalau Trase tidak memuat kabupaten, Farid membawa tangkapan layar ke Anca. Jangan mengunduh tabel nasional sebagai pengganti.",
     "Tinggi"],
    ["2026-11-12", "Kamis", "Data", "A3, F4, J2, J3",
     "Chat singkat bila Jose sudah bisa menunjukkan storyboard. Anca hanya memeriksa sumbu yang menyamakan dua satuan.",
     "Buat skrip baca Trase ke interim. Laporkan tahun minimum, tahun maksimum, dan jumlah nama kabupaten. Jangan mengisi unit yang tidak ada.",
     "Lengkapi katalog sumber untuk berkas yang sudah masuk raw. Kirim pertanyaan lisensi ke info@trase.earth bila lisensi berkas kosong.",
     "Kunci storyboard bila B1 dan uji peta sudah cukup. Buat satu contoh gaya kartu angka pada report percobaan.",
     "Catatan cakupan tahun Trase. Gaya visual contoh. Storyboard dikunci.",
     "Berkas Trase yang tidak diedit.",
     "Kalau skrip gagal membaca berkas, Anca berhenti dan menanyakan struktur berkasnya. Jangan mengubah berkas mentah supaya mudah dibaca.",
     "Tinggi"],
    ["2026-11-13", "Jumat", "Data", "A2, A7, F5, J3",
     "Malam, 15 menit: status arsip FIRMS saja.",
     "Jika email sudah datang, simpan mentah plus checksum dan hitung jumlah baris. Jika belum, siapkan daftar nama Trase yang gagal cocok dengan geoBoundaries dan kirim ke Farid.",
     "Mulai meninjau nama yang gagal. Setiap baris punya status. Yang belum yakin ditandai belum diputuskan, bukan dipaksa cocok.",
     "Rapikan report percobaan agar filternya tidak menutupi angka pada lebar 1366. Jangan membangun report lomba dengan angka sungguhan sebelum CSV final.",
     "Arsip FIRMS tersimpan, atau status belum datang tertulis. Daftar nama gagal sudah mulai ditinjau.",
     "Email FIRMS atau daftar nama dari Trase.",
     "Kalau tautan email mati, minta ulang dengan parameter yang sama besok pagi. Crosswalk tetap jalan karena tidak bergantung pada hotspot.",
     "Tinggi"],
    ["2026-11-14", "Sabtu", "Go atau berhenti", "B2, A4, A6, F5",
     "Rapat go/no-go, 1 jam. Syarat lanjut: hotspot, luas terbakar, dan gambut bisa ditunjuk pada kabupaten yang sama. Jika tidak, putuskan hambatan yang dikejar atau tema cadangan.",
     "Jika hotspot sudah ada, hitung uji kecil spatial join untuk satu bulan. Jika belum, kerjakan persentase gambut hanya bila rasternya sudah diunduh. Jangan mengisi yang kosong.",
     "Selesaikan tinjauan nama yang menggantung. Bawa jumlah baris belum diputuskan ke rapat.",
     "Hadir di go/no-go. Siapkan konsekuensi tampilan: halaman mana yang hilang bila hotspot atau gambut tidak ada. Jangan mendesain ulang seluruh storyboard pada hari yang sama.",
     "Keputusan tertulis lanjut atau berhenti.",
     "Status tiga sumber inti pada pagi 14 November.",
     "Kalau belum go, 15 November tidak menambah chart dan tidak menambah sensor. Satu hambatan saja yang dikerjakan, lalu keputusan diulang sehari.",
     "Tinggi"],
    ["2026-11-15", "Minggu", "Gabung wilayah", "A6, A7, F5",
     "Tidak ada rapat. Hari kerja karena batas S2 adalah 16 November. Tidak ada fitur baru di luar join dan crosswalk.",
     "Jalankan spatial join penuh bila hotspot sudah ada. Tulis log titik yang dibuang. Terapkan crosswalk yang sudah ditinjau Farid.",
     "Tutup sisa nama. Nol baris belum ditinjau adalah syarat selesai hari ini.",
     "Istirahat dari pembangunan halaman. Baca log jumlah titik yang dibuang supaya tahu apa yang harus dijelaskan di catatan peta. Jangan mengubah storyboard.",
     "Log join dan crosswalk final, atau daftar hambatan yang masih tersisa.",
     "Keputusan lanjut pada 14 November.",
     "Kalau join di bawah 99 persen, Anca tidak menaikkan toleransi. Farid memeriksa apakah yang gagal adalah nama atau titik di luar poligon. Jose menunggu.",
     "Sedang"],
    ["2026-11-16", "Senin", "Panel", "A8, F6, J4",
     "Sore 15 menit: Anca menyebut cut-off final dan kolom yang masih NaN.",
     "Bangun panel bulan dan tahun. Isi nol hanya untuk hitungan hotspot yang benar-benar tidak ada titiknya. Hujan yang belum ada tetap kosong. Jalankan tes duplikat dan cakupan bulan.",
     "Susun kerangka deskripsi dari keputusan metode yang sudah ada. Jangan menulis hasil hipotesis.",
     "Siapkan kerangka halaman 1 pada report lomba tanpa angka manual: posisi KPI, peta, deret, filter, sumber.",
     "Panel lulus tes struktur. Kerangka naskah punya semua bab. Kerangka halaman 1 ada.",
     "Crosswalk final dan log join.",
     "Kalau CHIRPS belum ada, panel tetap ditutup tanpa hujan. H3 disiapkan sebagai tidak konklusif bila hujan tidak datang sampai 18 November.",
     "Tinggi"],
    ["2026-11-17", "Selasa", "Panel", "A8, F4, J4",
     "Tidak ada rapat. Anca mengumumkan di chat bila total tahunan sudah cocok dengan mentah.",
     "Selesaikan rekonsiliasi total hotspot per tahun terhadap berkas mentah setelah filter. Perbaiki skrip bila selisih. Jangan memperbaiki dengan mengedit CSV.",
     "Perbarui sources.md dengan kolom yang Anca nyatakan dipakai. Tambahkan catatan filter confidence dan type.",
     "Sambungkan cuplikan yang diberi label belum final hanya bila Anca memberikannya. Jika belum, tetap pada kerangka.",
     "Total tahunan cocok, atau selisihnya tertulis beserta penyebabnya.",
     "Panel 16 November.",
     "Selisih total berarti filter atau join masih salah. Halaman Looker tidak diisi sampai selisihnya dijelaskan.",
     "Tinggi"],
    ["2026-11-18", "Rabu", "Hipotesis", "A9, F6, J5",
     "Malam 20 menit: Anca membacakan definisi N untuk kabupaten kronis sebelum tabelnya dibuat.",
     "Tulis findings untuk hipotesis yang datanya sudah cukup. Mulai dari H4, H5, dan H6 karena tidak menunggu model. Bandingkan 2026 dan 2019 pada jendela bulan yang sama.",
     "Isi bab data dan metode di kerangka naskah dari metodologi, termasuk apa yang sengaja kosong.",
     "Bangun struktur halaman 2 tanpa angka manual. Siapkan tempat untuk kalimat tidak konklusif.",
     "Definisi N tercatat sebelum hasil H5. Kerangka dua halaman ada.",
     "Panel yang totalnya sudah direkonsiliasi.",
     "Kalau 2026 tidak setahun penuh, jangan membandingkannya dengan setahun 2019. Tulis jendela bulannya di findings pada hari yang sama.",
     "Tinggi"],
    ["2026-11-19", "Kamis", "Hipotesis", "A9, A10, J5",
     "Tidak ada rapat. Model dimulai hanya setelah panel tidak berubah lagi hari ini.",
     "Selesaikan H1 sampai H3. Lalu mulai baseline persistence dan klimatologi. Jangan melatih model sebelum baseline itu ada angkanya.",
     "Salin definisi dan batasan dari findings yang sudah berstatus ke draf, tanpa menambah tafsir.",
     "Isi halaman 2 hanya dari findings yang statusnya sudah ada. Chart untuk hipotesis tidak konklusif tidak dipaksakan.",
     "Enam hipotesis punya status, atau yang tertahan punya alasan data. Baseline model punya angka.",
     "Findings yang selesai pada 18 November.",
     "Kalau H2 tidak bisa dihitung karena kolom mineral dan gambut tidak terpisah, statusnya tidak konklusif. Jose mengosongkan chart itu, bukan mengira dari persentase berita.",
     "Tinggi"],
    ["2026-11-20", "Jumat", "Model", "A10, F7, J6",
     "Sore 15 menit: Anca menyatakan model mengalahkan baseline atau tidak.",
     "Selesaikan metrik versus baseline. Jika kalah, tulis paragraf keterbatasan dan hentikan penjualan skor model.",
     "Lanjutkan draf deskripsi pada bab yang angkanya sudah ada di findings. Tandai bab risiko sebagai menunggu keputusan model.",
     "Siapkan halaman 3 dalam dua versi kerangka: tiga skenario, atau klimatologi bila model kalah. Jangan mengisi angka.",
     "model_metrics memuat baseline. Ada keputusan halaman 3 yang mengikuti hasil itu.",
     "Baseline 19 November.",
     "Kalau pelatihan gagal karena kolom fitur kosong, buang fitur itu dan catat. Jangan mengisi lag yang hilang dengan nol tanpa menulis alasannya.",
     "Tinggi"],
    ["2026-11-21", "Sabtu", "Tinjau", "B3, A11, F7",
     "Rapat 2 jam. Baca enam status hipotesis. Kunci kalimat yang masuk dashboard. Tidak ada hipotesis baru sesudahnya.",
     "Setelah rapat, buat CSV skenario hanya bila keputusannya memang membuat skenario. Validasi dengan Pandera.",
     "Tandai paragraf naskah yang tidak punya padanan di daftar chart yang disepakati. Paragraf itu dihapus, bukan ditambahkan chart baru.",
     "Hadir dan menandai judul chart yang harus diganti agar mengikuti temuan, bukan mengikuti judul kerja lama.",
     "findings disepakati. Daftar chart final tidak bertambah lagi.",
     "Findings lengkap dan keputusan model 20 November.",
     "Kalau tiga orang tidak sepakat pada satu hipotesis, status tetap mengikuti tabel Anca. Yang dibahas adalah kalimatnya, bukan penghitungan ulang di dalam rapat.",
     "Sedang"],
    ["2026-11-22", "Minggu", "Buffer", "A12, J5, F7",
     "Hari ringan. Hanya menutup temuan yang gagal ditulis rapi. Tidak ada model baru dan tidak ada sumber baru.",
     "Rapikan ekspor bila skema gagal pada CSV yang sudah ada. Jangan menambah fitur.",
     "Selaraskan istilah naskah dengan daftar chart 21 November.",
     "Perbaiki judul dan label yang salah dari daftar rapat. Tidak menambah chart.",
     "Tidak ada butir rapat 21 November yang masih menggantung tanpa alasan.",
     "Daftar rapat 21 November.",
     "Kalau CSV masih gagal skema, biarkan gagal dan tulis penyebabnya. Jangan melemahkan skema supaya lulus.",
     "Ringan"],
    ["2026-11-23", "Senin", "Ekspor", "A12, F7, J4",
     "Sore 20 menit: Anca menyerahkan daftar CSV yang lolos dan daftar kolom yang sengaja kosong.",
     "Tulis CSV final ke data/processed. Ulangi perintah dari raw bila perlu supaya bisa diulang. Perbarui kamus data.",
     "Selesaikan draf deskripsi dari findings dan keterbatasan. Angka yang belum ada di CSV tidak ditulis.",
     "Sambungkan halaman 1 ke CSV final. Cek satu KPI terhadap berkas.",
     "CSV final tersimpan. Halaman 1 tersambung. Draf naskah utuh.",
     "Skema dan findings yang sudah dikunci.",
     "Kalau satu CSV gagal, halaman yang bergantung padanya tetap kerangka. Jangan menempel angka dari findings ke Looker.",
     "Tinggi"],
    ["2026-11-24", "Selasa", "Tinjau", "B4, A13, J5, J6",
     "Rapat uji juri 2 jam pada tautan lihat. Maksimal 12 revisi. Tidak ada chart baru.",
     "Audit angka yang dipakai di halaman yang sudah tersambung. Chart gagal dicatat untuk disembunyikan, bukan diperbaiki angkanya di Looker.",
     "Catat revisi naskah dari rapat. Jangan menulis ulang bab yang tidak disebut.",
     "Isi halaman 2 dan 3 dari CSV final sebelum rapat bila sempat. Setelah rapat, kerjakan hanya butir daftar.",
     "Daftar revisi bernomor dengan pemilik.",
     "Tautan lihat dan draf naskah.",
     "Kalau halaman 3 belum berisi karena model baru selesai, rapat menguji halaman 1 dan 2 saja. Halaman 3 tidak diisi semalam dengan angka sementara.",
     "Sedang"],
    ["2026-11-25", "Rabu", "Patuh ketentuan", "A13, F8, J7, J8",
     "Malam 30 menit: buka PDF dan tautan dari komputer yang bukan milik pembuatnya.",
     "Baca ulang PDF deskripsi terhadap CSV. Pastikan tidak ada klaim sebab-akibat yang tersisa.",
     "Format A4, Times New Roman 12, spasi 1,5, justify, huruf hitam. Ekspor PDF deskripsi. Isi surat bila tautannya ada.",
     "Samakan filter, pasang identitas, cek 1366, lalu ubah izin tautan menjadi siapa saja dengan link dapat melihat. Uji di jendela penyamaran.",
     "Dua PDF naskah dan surat, atau catatan surat belum ada. Tautan publik lulus uji.",
     "Daftar revisi 24 November yang bertipe angka dan label sudah ditutup.",
     "Kalau surat belum ada, Farid menghubungi panitia hari ini. ZIP tidak dibuat dengan surat kosong.",
     "Tinggi"],
    ["2026-11-26", "Kamis", "Bekukan", "B5, F9, J9",
     "Rapat checklist. Setelah lengkap, data processed dan report tidak diubah lagi kecuali salah ketik atau salah izin tautan.",
     "Periksa tiga nama atau angka prioritas pada versi beku. Jika ada salah angka, perbaiki sumber CSV lalu ekspor ulang, jangan memperbaiki di Looker saja.",
     "Susun ZIP kandidat, cek ukuran di bawah 50 MB, simpan terpisah dari ZIP percobaan. Isi checklist bagian berkas.",
     "Pastikan izin tautan masih publik setelah halaman dibekukan. Jangan menggeser layout.",
     "Checklist lengkap dan satu ZIP beku.",
     "PDF 25 November dan tautan yang sudah diuji.",
     "Kalau nomor peserta belum turun, checklist butir itu tetap kosong dan unggah 27 November ditahan sampai nomor terpasang. Hubungi panitia pagi ini.",
     "Sedang"],
    ["2026-11-27", "Jumat", "Kumpulkan", "B6, F9",
     "Pagi hari pengumpulan. Target selesai sebelum pukul 18.00. Setelah status berhasil, tidak ada revisi.",
     "Berjaga sebagai pengunggah cadangan. Setelah unggah, buka tautan sekali lagi dari PDF yang benar-benar terkirim bila situs mengizinkan melihat berkas.",
     "Unggah ZIP beku ke dateraquest.com. Simpan tangkapan nama berkas, jam, dan status. Jangan mengunggah versi kedua.",
     "Berjaga pagi hari hanya bila izin tautan bermasalah. Setelah berhasil, jangan mengubah sharing.",
     "Bukti unggah di folder Kiriman.",
     "ZIP beku 26 November dan akun ketua tim.",
     "Kalau situs gagal, catat jam, ganti jaringan, dan hubungi narahubung. Isi berkas tidak diubah. Percobaan ulang memakai ZIP yang sama pada 28 November.",
     "Tenggat"],
    ["2026-11-28", "Sabtu", "Cadangan", "B6",
     "Hari ini tidak dipakai untuk analisis, desain, atau naskah. Hanya untuk mengunggah ZIP beku yang sama bila 27 November gagal karena situs atau nomor peserta yang baru turun pagi itu.",
     "Tidak membuka model. Hanya membantu unggah bila kemarin gagal.",
     "Jika kemarin sudah berhasil, tidak melakukan apa pun pada berkas. Jika belum, unggah ZIP yang sama dan simpan bukti sebelum pukul 20.00, jauh dari batas 23.59.",
     "Tidak mengubah report. Jika nomor peserta baru tiba dan belum terunggah, tempel nomor di posisi yang sudah disiapkan, tanpa menggeser chart lain, lalu beritahu Farid bahwa PDF tautan perlu diganti hanya untuk nomor itu.",
     "Bukti unggah, atau konfirmasi bahwa unggah 27 November sudah cukup.",
     "Satu ZIP beku. Bukan hasil revisi semalam.",
     "Kalau isi ingin diubah pada hari ini, tidak dilakukan. Kiriman pertama yang dinilai, dan perubahan setelah terkirim tidak diterima.",
     "Cadangan"],
]


def style_header(ws, row, start, end, bg=NAVY):
    for col in range(start, end + 1):
        cell = ws.cell(row, col)
        cell.font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
        cell.fill = fill(bg)
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = thin


def apply_body(cell, owner=None):
    cell.font = Font(name="Calibri", size=10, color=INK)
    cell.alignment = wrap
    cell.border = thin
    if owner:
        cell.fill = fill(owner_fill.get(owner, WHITE))


def set_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def paint_title(ws, last_col, title, subtitle):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    c = ws.cell(1, 1, title)
    c.font = Font(name="Calibri", bold=True, size=16, color="FFFFFF")
    c.fill = fill(NAVY)
    c.alignment = Alignment(vertical="center", horizontal="left", indent=1)
    ws.row_dimensions[1].height = 28
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
    s = ws.cell(2, 1, subtitle)
    s.font = Font(name="Calibri", size=10, color=INK)
    s.fill = fill("E8EEF2")
    s.alignment = Alignment(wrap_text=True, vertical="center", indent=1)
    ws.row_dimensions[2].height = 48


def height_for(texts, widths):
    lines = 1
    for text, width in zip(texts, widths):
        lines = max(lines, (len(str(text)) // max(18, int(width * 0.95))) + 1)
    return min(210, max(64, lines * 14))


ws1 = wb.active
ws1.title = "Pembagian Tugas"
headers1 = [
    "ID", "Pemilik", "Fase", "Tugas", "Detail pekerjaan", "Output",
    "Informasi yang dibutuhkan", "Dari mana informasi didapat", "Bergantung pada",
    "Jam", "Selesai jika", "Kalau gagal, yang dilakukan", "Cadangan",
]
paint_title(
    ws1, len(headers1),
    "IDC Dateraquest 2.0  ·  Pembagian tugas karhutla Sumatera",
    "Subtema Preservasi Ekosistem Tropis. Anca pegang pipeline, uji hipotesis, dan model. Farid pegang berkas sumber, tinjauan nama kabupaten, deskripsi karya, dan unggah. Jose pegang tiga halaman Looker Studio. "
    "Jam rapat dihitung untuk setiap orang yang hadir. Ukuran arsip di bawah 50 MB. Target unggah 27 November 2026, batas panitia 28 November 23.59 WIB. S0 pada 10 November sudah selesai.",
)
ws1.row_dimensions[3].height = 8
for col, h in enumerate(headers1, 1):
    ws1.cell(4, col, h)
style_header(ws1, 4, 1, len(headers1))
ws1.freeze_panes = "A5"
ws1.sheet_properties.tabColor = NAVY
for i, t in enumerate(tasks):
    r = 5 + i
    owner = t[1]
    for c, val in enumerate(t, 1):
        cell = ws1.cell(r, c, val)
        apply_body(cell, owner)
        if c in (1, 2, 10):
            cell.alignment = center
        if c == 12:
            cell.fill = fill(GAGAL)
            cell.font = Font(name="Calibri", size=10, color="5C1A1B")
    ws1.row_dimensions[r].height = height_for(
        [t[4], t[6], t[11], t[12]],
        [62, 40, 55, 36],
    )
last_data = 4 + len(tasks)
ws1.auto_filter.ref = f"A4:M{last_data}"
set_widths(ws1, [6, 12, 18, 42, 62, 38, 40, 36, 16, 8, 36, 55, 36])
ws1.page_setup.orientation = "landscape"
ws1.page_setup.fitToPage = True
ws1.page_setup.fitToWidth = 1
ws1.page_setup.fitToHeight = 0
ws1.page_setup.paperSize = ws1.PAPERSIZE_A3
ws1.page_setup.horizontalCentered = True
ws1.sheet_properties.pageSetUpPr.fitToPage = True
ws1.print_title_rows = "1:4"
ws1.sheet_view.showGridLines = False
ws1.sheet_view.zoomScale = 110
ws1.page_setup.paperSize = ws1.PAPERSIZE_A3

sum_row = last_data + 2
ws1.cell(sum_row, 1, "Ringkasan beban").font = Font(name="Calibri", bold=True, size=13, color=NAVY)
ws1.merge_cells(start_row=sum_row, start_column=1, end_row=sum_row, end_column=4)
sum_headers = ["Orang", "Hasil yang dipegang", "Jam tugas sendiri", "Jam rapat bersama", "Jam total", "Catatan"]
for c, h in enumerate(sum_headers, 1):
    ws1.cell(sum_row + 1, c, h)
style_header(ws1, sum_row + 1, 1, 6, TEAL)
summaries = [
    ("Anca", "Arsip FIRMS, panel kabupaten, uji H1–H6, model versus baseline, dan CSV final.",
     "Jamnya lebih besar karena pipeline ada di jalur kritis. Model yang kalah dari baseline tetap dilaporkan, bukan dipaksa menang."),
    ("Farid", "Berkas Trase dan katalog sumber, tinjauan nama kabupaten, deskripsi karya, serta ZIP yang diunggah.",
     "Unduhan dan unggah tidak bisa dikerjakan skrip. Tinjauan nama yang gagal digabung juga ada di sini."),
    ("Jose", "Uji peta Looker, storyboard, dan tiga halaman yang membaca CSV final.",
     "Report percobaan terpisah dari report lomba. Angka lomba tidak diketik langsung ke Looker."),
]
for i, (name, hasil, catatan) in enumerate(summaries):
    r = sum_row + 2 + i
    ws1.cell(r, 1, name)
    ws1.cell(r, 2, hasil)
    ws1.cell(r, 3, f'=SUMIF($B$5:$B${last_data},A{r},$J$5:$J${last_data})')
    ws1.cell(r, 4, f'=SUMIF($B$5:$B${last_data},"Bersama",$J$5:$J${last_data})')
    ws1.cell(r, 5, f"=C{r}+D{r}")
    ws1.cell(r, 6, catatan)
    for c in range(1, 7):
        apply_body(ws1.cell(r, c), name)
        if c in (3, 4, 5):
            ws1.cell(r, c).alignment = center
            ws1.cell(r, c).number_format = "0.0"
    ws1.row_dimensions[r].height = 48
note_r = sum_row + 6
ws1.merge_cells(start_row=note_r, start_column=1, end_row=note_r, end_column=6)
note = ws1.cell(
    note_r, 1,
    "Filter header untuk melihat satu orang. Warna baris mengikuti pemilik. Kolom gagal berwarna tetap. "
    "Spreadsheet rencana pangan yang lama tidak dipakai untuk pengerjaan ini.",
)
note.font = Font(name="Calibri", size=10, italic=True, color=MUTED)
note.alignment = wrap
ws1.row_dimensions[note_r].height = 32
ws1.print_area = f"A1:M{note_r}"

ws2 = wb.create_sheet("Pipeline Harian")
headers2 = [
    "Tanggal", "Hari", "Fase", "ID tugas", "Kerja bersama",
    "Anca", "Farid", "Jose", "Output di akhir hari",
    "Syarat dari hari sebelumnya", "Kalau hari ini gagal", "Intensitas",
]
paint_title(
    ws2, len(headers2),
    "IDC Dateraquest 2.0  ·  Pipeline harian karhutla 10–28 November 2026",
    "10 November adalah sisa hari setelah S0. Go/no-go ada pada 14 November. Target unggah 27 November. "
    "28 November hanya untuk mengirim berkas yang sama bila unggah sebelumnya gagal. ID tugas merujuk ke tab Pembagian Tugas.",
)
ws2.row_dimensions[3].height = 8
for col, h in enumerate(headers2, 1):
    ws2.cell(4, col, h)
style_header(ws2, 4, 1, len(headers2))
ws2.freeze_panes = "A5"
ws2.sheet_properties.tabColor = TEAL
intensity_fill = {
    "Tinggi": "F8D3C6",
    "Sedang": "FFF3C4",
    "Ringan": "D8F3DC",
    "Tenggat": "F4C7CE",
    "Cadangan": "E6E0F5",
}
for i, d in enumerate(days):
    r = 5 + i
    y, m, dd = [int(x) for x in d[0].split("-")]
    values = [date(y, m, dd), *d[1:]]
    for c, val in enumerate(values, 1):
        cell = ws2.cell(r, c, val)
        cell.font = Font(name="Calibri", size=10, color=INK)
        cell.alignment = wrap
        cell.border = thin
        cell.fill = fill(WHITE if i % 2 == 0 else ZEBRA)
    ws2.cell(r, 1).number_format = "DD MMM YYYY"
    ws2.cell(r, 1).alignment = center
    ws2.cell(r, 2).alignment = center
    ws2.cell(r, 3).alignment = center
    ws2.cell(r, 4).alignment = center
    ws2.cell(r, 12).alignment = center
    ws2.cell(r, 12).fill = fill(intensity_fill[d[-1]])
    ws2.cell(r, 12).font = Font(name="Calibri", size=10, bold=True, color=INK)
    ws2.cell(r, 6).fill = fill(ANCA)
    ws2.cell(r, 7).fill = fill(FARID)
    ws2.cell(r, 8).fill = fill(JOSE)
    ws2.cell(r, 11).fill = fill(GAGAL)
    ws2.row_dimensions[r].height = height_for(
        [d[4], d[5], d[6], d[7], d[10]],
        [42, 42, 42, 42, 48],
    )
last2 = 4 + len(days)
ws2.auto_filter.ref = f"A4:L{last2}"
set_widths(ws2, [16, 12, 18, 22, 42, 42, 42, 42, 40, 36, 48, 14])
ws2.page_setup.orientation = "landscape"
ws2.page_setup.fitToPage = True
ws2.page_setup.fitToWidth = 1
ws2.page_setup.fitToHeight = 0
ws2.page_setup.paperSize = ws2.PAPERSIZE_A3
ws2.page_setup.horizontalCentered = True
ws2.sheet_properties.pageSetUpPr.fitToPage = True
ws2.print_title_rows = "1:4"
ws2.sheet_view.showGridLines = False
ws2.sheet_view.zoomScale = 110
leg = last2 + 2
ws2.cell(leg, 1, "Intensitas").font = Font(name="Calibri", bold=True, size=12, color=NAVY)
labels = [
    ("Tinggi", "Hari isi utama. Outputnya menahan orang lain."),
    ("Sedang", "Hari membangun atau meninjau."),
    ("Ringan", "Hanya menutup hutang. Tidak ada sumber, hipotesis, atau chart baru."),
    ("Tenggat", "Hari unggah yang ditargetkan."),
    ("Cadangan", "Hanya mengulang unggah berkas yang sama bila 27 November gagal."),
]
for i, (name, desc) in enumerate(labels):
    cell = ws2.cell(leg + 1, 1 + i, f"{name}: {desc}")
    cell.fill = fill(intensity_fill[name])
    cell.font = Font(name="Calibri", size=9, color=INK)
    cell.alignment = wrap
    cell.border = thin
ws2.row_dimensions[leg + 1].height = 36
foot = leg + 3
ws2.merge_cells(start_row=foot, start_column=1, end_row=foot, end_column=8)
fcell = ws2.cell(
    foot, 1,
    "Urutan yang tidak dibalik: permintaan FIRMS dan unduh Trase, simpan mentah, crosswalk yang ditinjau, spatial join, panel, hipotesis, model versus baseline, CSV, Looker, PDF, ZIP, unggah. "
    "Hotspot dan luas terbakar tidak dijumlahkan. 14 November adalah keputusan lanjut atau berhenti.",
)
fcell.font = Font(name="Calibri", size=10, italic=True, color=MUTED)
fcell.alignment = wrap
ws2.row_dimensions[foot].height = 32
ws2.print_area = f"A1:L{foot}"

out = r"d:\Coolyeah\SEM5\IDC\karhutla-idc\Rencana_Kerja_Karhutla.xlsx"
wb.save(out)
print(out, "tasks", len(tasks), "days", len(days))
