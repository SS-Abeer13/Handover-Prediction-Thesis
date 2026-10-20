"""Figure 1 of the journal paper: routes of the four development campaigns.

Redraw from the route and handover CSVs and the cached OpenStreetMap basemap in
Presentation/matlab (tiles fetched once at zoom 13; Map data (c) OpenStreetMap contributors, ODbL).
Usage:
  python make_fig_routes.py <out.png>                 cached OSM basemap (Bengali labels)
  python make_fig_routes.py <out.png> --tiles esri    English labels: downloads Esri World Street Map
        tiles once (zoom 13, ~35 tiles, cached in Presentation/matlab/tiles_esri). Needs internet.
        LOOK AT THE RESULT: a provider that has started requiring a key returns watermarked tiles.
  python make_fig_routes.py <out.png> --tiles mock    offline self-test of the stitching
"""
import sys, pathlib, math, io, time, argparse, urllib.request
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.lines import Line2D

ROOT = pathlib.Path(__file__).resolve().parents[4]
SRC = ROOT / "Presentation" / "matlab"
ap = argparse.ArgumentParser()
ap.add_argument("out", nargs="?", default="fig03_map_routes.png")
ap.add_argument("--tiles", choices=["cached", "esri", "mock"], default="cached")
ap.add_argument("--zoom", type=int, default=13)
args = ap.parse_args()
OUT = args.out

lat0, lon0 = 23.812500, 90.404213
def km(lat, lon):
    R, k = 6378.137, np.cos(np.deg2rad(lat0))
    merc = lambda p: np.log(np.tan(np.pi / 4 + np.deg2rad(p) / 2))
    return R * np.deg2rad(lon - lon0) * k, R * (merc(lat) - merc(lat0)) * k

R = pd.read_csv(SRC / "map_route_4camp.csv")
H = pd.read_csv(SRC / "map_handovers_4camp.csv")
cols = {1: "#1f4e79", 2: "#e69f00", 3: "#2a8c55", 4: "#c0392b"}
drives = {1: 15, 2: 8, 3: 20, 4: 14}

xw, xe, ys, yn = -5.5020, 15.4772, -7.9731, 19.8306   # plotted window (km)
_R, _K = 6378.137, math.cos(math.radians(lat0))
_merc = lambda p: math.log(math.tan(math.pi / 4 + math.radians(p) / 2))
_X = lambda lon: _R * math.radians(lon - lon0) * _K
_Y = lambda lat: _R * (_merc(lat) - _merc(lat0)) * _K
_tlon = lambda n, z: n / 2 ** z * 360 - 180
_tlat = lambda m, z: math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * m / 2 ** z))))
_tx = lambda lon, z: int((lon + 180) / 360 * 2 ** z)
_ty = lambda lat, z: int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 2 ** z)


def _lon_of(xkm):
    return lon0 + math.degrees(xkm / (_R * _K))


def _lat_of(ykm):
    m = ykm / (_R * _K) + _merc(lat0)
    return math.degrees(2 * math.atan(math.exp(m)) - math.pi / 2)


def stitched_basemap(source, z):
    """Web-Mercator tiles covering the plotted window -> (image, extent in km)."""
    n_w, n_e = _tx(_lon_of(xw), z), _tx(_lon_of(xe), z)
    m_n, m_s = _ty(_lat_of(yn), z), _ty(_lat_of(ys), z)
    cache = SRC / ("tiles_esri" if source == "esri" else "tiles_mock")
    cache.mkdir(exist_ok=True)
    mosaic = Image.new("RGB", ((n_e - n_w + 1) * 256, (m_s - m_n + 1) * 256), "white")
    for n in range(n_w, n_e + 1):
        for m in range(m_n, m_s + 1):
            f = cache / f"{z}_{n}_{m}.img"
            if source == "mock":                      # crop from the cached z12 mosaic
                mos = Image.open(SRC / "osm_basemap_4camp.jpg").convert("RGB")
                n0, m0 = 3075, 1766                   # tile index of the mosaic's top-left
                tile = mos.crop(((n - n0) * 256, (m - m0) * 256, (n - n0 + 1) * 256, (m - m0 + 1) * 256))
            else:
                if not f.exists():
                    url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{m}/{n}"
                    req = urllib.request.Request(url, headers={"User-Agent": "handover-figure/1.0 (academic; one-time fetch)"})
                    f.write_bytes(urllib.request.urlopen(req, timeout=30).read())
                    time.sleep(0.2)
                tile = Image.open(f).convert("RGB")
            mosaic.paste(tile, ((n - n_w) * 256, (m - m_n) * 256))
    ext = [_X(_tlon(n_w, z)), _X(_tlon(n_e + 1, z)), _Y(_tlat(m_s + 1, z)), _Y(_tlat(m_n, z))]
    return np.asarray(mosaic).astype(float), ext


if args.tiles == "cached":
    img = np.asarray(Image.open(SRC / "osm_basemap_4camp.jpg").convert("RGB")).astype(float)
    # cached zoom-12 mosaic: top-left tile corner at (-14.313, 26.068) km, 0.03496 km/px
    px = 0.03496
    ext = [-14.313, -14.313 + 1024 * px, 26.068 - 1024 * px, 26.068]
    credit = "Map data \u00a9 OpenStreetMap contributors"
else:
    z = 12 if args.tiles == "mock" else args.zoom
    img, ext = stitched_basemap(args.tiles, z)
    credit = ("Map data \u00a9 OpenStreetMap contributors" if args.tiles == "mock"
              else "Esri, HERE, Garmin, \u00a9 OpenStreetMap contributors")
img = (255 - 0.72 * (255 - img)).astype(np.uint8) if args.tiles != "esri" else img.astype(np.uint8)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
fig, ax = plt.subplots(figsize=(5.6, 6.6), dpi=300)
ax.imshow(img, extent=ext, origin="upper", zorder=0, interpolation="bilinear")
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
ax.text(xe - .2, ys + .3, credit, fontsize=7.5, ha="right", va="bottom",
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
