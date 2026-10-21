"""Peta tutupan lahan Sarbagita 2020, 2023, 2026 (proyeksi) berdampingan, dengan legend yang sama.

Pakai:  python src/make_figure.py   (butuh rasterio, matplotlib)
Hasil:  images/peta_tutupan_lahan_sarbagita.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from rasterio.enums import Resampling

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "output"
OUT = ROOT / "images" / "peta_tutupan_lahan_sarbagita.png"
OUT.parent.mkdir(exist_ok=True)
NAMES = ["Built-up", "Vegetation", "Agriculture", "Bare Land", "Water Body"]
COLORS = ["#e66101", "#1b7837", "#d9ef8b", "#bf9b7a", "#2166ac"]   # beda terang-gelap, aman buta warna
PANELS = [("2020", "2020"), ("2023", "2023"), ("2026_Proyeksi", "2026 (proyeksi)")]
F = 4   # downsample untuk tampilan, nearest supaya kelas tidak tercampur

fig, axes = plt.subplots(1, 3, figsize=(15, 7.2), dpi=180)
for ax, (key, label) in zip(axes, PANELS):
    with rasterio.open(SRC / f"LC_Sarbagita_{key}.tif") as r:
        full = r.read(1)
        a = r.read(1, out_shape=(r.height // F, r.width // F), resampling=Resampling.nearest)
        b = r.bounds
    land = full[full > 0]
    pct = [100 * (land == k).sum() / land.size for k in range(1, 6)]
    img = np.ma.masked_equal(a, 0)
    lat = (b.top + b.bottom) / 2
    ax.imshow(img, cmap=ListedColormap(COLORS), vmin=1, vmax=5, interpolation="nearest",
              extent=[b.left, b.right, b.bottom, b.top])
    ax.set_aspect(1 / np.cos(np.radians(lat)))
    ax.set_axis_off()
    ax.set_title(label, fontsize=14, fontweight="bold", color="#14232e", loc="left")
    txt = "\n".join(f"{n}: {p:.1f}%" for n, p in zip(NAMES, pct) if p >= 0.05)
    ax.text(0.98, 0.98, txt, transform=ax.transAxes, ha="right", va="top", fontsize=8.5, color="#14232e",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#d6e0e6", lw=0.6))
    # scale bar 10 km
    km = 111.32 * np.cos(np.radians(lat))
    sx, sy = b.left + 0.02, b.bottom + 0.03
    ax.plot([sx, sx + 10 / km], [sy, sy], color="#14232e", lw=2.5, solid_capstyle="butt")
    ax.text(sx + 5 / km, sy + 0.012, "10 km", ha="center", fontsize=8.5, color="#14232e")

fig.legend(handles=[Patch(facecolor=c, edgecolor="#9aa9b4", lw=0.5, label=n) for n, c in zip(NAMES, COLORS)],
           loc="lower center", ncol=5, frameon=False, fontsize=10.5, bbox_to_anchor=(0.5, 0.06))
fig.suptitle("Tutupan Lahan Kawasan Sarbagita, Bali", x=0.02, ha="left", fontsize=17, fontweight="bold",
             color="#14232e", y=0.98)
fig.text(0.02, 0.905, "Klasifikasi Random Forest dari citra Sentinel-2 (2020, 2023) dan proyeksi 2026 dengan "
         "Markov Chain. Persentase dihitung dari luas daratan.", fontsize=10.5, color="#5a6b78")
fig.text(0.02, 0.02, "Sumber: analisis sendiri, github.com/rzkrmadhan/PerubahanTutupanLahan_Sarbagita_ILASPP_"
         "MohamadRizkiRamadhan. CRS WGS 84 (EPSG:4326). Laut di-mask sebagai nodata.", fontsize=8, color="#5a6b78")
plt.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.12, wspace=0.03)
fig.savefig(OUT, facecolor="white")
print("Tersimpan:", OUT)
