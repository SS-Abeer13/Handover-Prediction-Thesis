"""Figure 1 of the journal paper: routes of the four development campaigns.

Plain redraw (no basemap) from the route and handover CSVs in Presentation/matlab.
Usage: python make_fig_routes.py <out.png>
"""
import sys, pathlib
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

SRC = pathlib.Path(__file__).resolve().parents[4] / "Presentation" / "matlab"
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

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
fig, ax = plt.subplots(figsize=(5.6, 6.6), dpi=300)
for c in (1, 2, 3, 4):
    r = R[R.cap == c]
    x, y = km(r.lat.values, r.lon.values)
    ax.plot(x, y, ".", ms=2.2, color=cols[c], alpha=.9, rasterized=True)
x, y = km(H.lat.values, H.lon.values)
ax.plot(x, y, "o", ms=3.4, mfc="none", mec="#222222", mew=.6)
ax.set_aspect("equal")
ax.set_xticks([-5, 0, 5, 10, 15]); ax.set_yticks([-5, 0, 5, 10, 15])
ax.set_xlabel("East of corridor centre (km)")
ax.set_ylabel("North of corridor centre (km)")
ax.grid(True, color="#dddddd", lw=.6)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

n = H.groupby("cap").size()
h = [Line2D([0], [0], color=cols[c], lw=3,
            label=f"Campaign {c}: {drives[c]} drives, {n[c]} HO") for c in (1, 2, 3, 4)]
h.append(Line2D([0], [0], marker="o", ls="", mfc="none", mec="#222222",
                label=f"{len(H)} handover commands (HO)"))
ax.legend(handles=h, loc="lower right", bbox_to_anchor=(1.0, 0.02), frameon=True, framealpha=1, edgecolor="#bbbbbb",
          fontsize=9, borderpad=.7, labelspacing=.5)
fig.tight_layout()
fig.savefig(OUT, dpi=300)
print(OUT, dict(n), len(H))
