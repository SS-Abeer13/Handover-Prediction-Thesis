"""Figure 1 of the journal paper: routes of the four development campaigns.

Redraw from the route and handover CSVs and the cached OpenStreetMap basemap in
Presentation/matlab (tiles fetched once at zoom 13; Map data (c) OpenStreetMap contributors, ODbL).
Usage: python make_fig_routes.py <out.png>
"""
import sys, pathlib
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.lines import Line2D

ROOT = pathlib.Path(__file__).resolve().parents[4]
SRC = ROOT / "Presentation" / "matlab"
OUT = sys.argv[1] if len(sys.argv) > 1 else "fig03_map_routes.png"

lat0, lon0 = 23.812500, 90.404213
def km(lat, lon):
    R, k = 6378.137, np.cos(np.deg2rad(lat0))
    merc = lambda p: np.log(np.tan(np.pi / 4 + np.deg2rad(p) / 2))
    return R * np.deg2rad(lon - lon0) * k, R * (merc(lat) - merc(lat0)) * k

R = pd.read_csv(SRC / "map_route_4camp.csv")
H = pd.read_csv(SRC / "map_handovers_4camp.csv")
cols = {1: "#1f4e79", 2: "#e69f00", 3: "#2a8c55", 4: "#c0392b"}
drives = {1: 15, 2: 8, 3: 20, 4: 14}

xw, xe, ys, yn = -5.5020, 15.4772, -7.9731, 19.8306
img = np.asarray(Image.open(SRC / "osm_basemap_4camp.jpg").convert("RGB")).astype(float)
img = (255 - 0.72 * (255 - img)).astype(np.uint8)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
fig, ax = plt.subplots(figsize=(5.6, 6.6), dpi=300)
# the cached 1024-px mosaic (zoom 12) is registered to the route coordinates by
# maximising road coverage under the GPS fixes; 0.03496 km per pixel at this latitude
px = 0.03496
xl0, yt0 = -14.34, 26.03
ax.imshow(img, extent=[xl0, xl0 + 1024 * px, yt0 - 1024 * px, yt0], origin="upper", zorder=0, interpolation="bilinear")
for c in (1, 2, 3, 4):
    r = R[R.cap == c]
    x, y = km(r.lat.values, r.lon.values)
    ax.plot(x, y, ".", ms=2.2, color=cols[c], alpha=.95, rasterized=True, zorder=3)
# operator-B blind capture (9 Oct 2026): GPS track from the one-hertz export
B = pd.read_csv(ROOT / "Drivetest Data" / "oct-9-2026.csv", usecols=["Latitude", "Longitude"],
                low_memory=False).dropna()
bx, by = km(B.Latitude.values, B.Longitude.values)
ax.plot(bx, by, ".", ms=2.2, color="#7b2d8e", alpha=.95, rasterized=True, zorder=3)
x, y = km(H.lat.values, H.lon.values)
ax.plot(x, y, "o", ms=3.4, mfc="none", mec="#222222", mew=.6, zorder=4)
ax.set_aspect("equal"); ax.set_xlim(xw, xe); ax.set_ylim(ys, yn)
ax.set_xticks([-5, 0, 5, 10, 15]); ax.set_yticks([-5, 0, 5, 10, 15])
ax.set_xlabel("East of corridor centre (km)")
ax.set_ylabel("North of corridor centre (km)")
ax.text(xe - .2, ys + .3, "Map data \u00a9 OpenStreetMap contributors", fontsize=7.5, ha="right", va="bottom",
        bbox=dict(fc="white", ec="none", pad=1.5), zorder=6)

n = H.groupby("cap").size()
h = [Line2D([0], [0], color=cols[c], lw=3,
            label=f"Campaign {c}: {drives[c]} drives, {n[c]} HO") for c in (1, 2, 3, 4)]
h.append(Line2D([0], [0], color="#7b2d8e", lw=3, label="Operator B (blind): 87 HO"))
h.append(Line2D([0], [0], marker="o", ls="", mfc="none", mec="#222222",
                label=f"{len(H)} operator-A handovers (HO)"))
ax.legend(handles=h, loc="lower right", bbox_to_anchor=(1.0, 0.045), frameon=True, framealpha=1, edgecolor="#bbbbbb",
          fontsize=8, borderpad=.6, labelspacing=.4, handlelength=1.6)
fig.tight_layout()
fig.savefig(OUT, dpi=300)
print(OUT, dict(n), len(H))
