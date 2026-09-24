"""Stage R1 - is this capture measured data, or generated?

The proposal's R1 gate says: audit the existing dataset before treating any of
its numbers as authoritative. This module is that audit, expressed as physics
and protocol checks that measured LTE data passes and a generator usually does
not. Each check returns a verdict and the evidence behind it, so the audit is
reproducible rather than an opinion.

The checks, and why each one is hard to fake:

``path_loss``        Signal strength must fall with distance from the cell.
                     Urban LTE sits near -30 to -40 dB per decade of distance.
                     A generator that draws RSRP without geometry has no slope.
``target_is_neighbour`` The cell you hand over to is nearly always one the phone
                     just reported as strong. Real networks: 70-95%. Independent
                     random draws: at or below chance.
``neighbour_identity`` A neighbour today is a serving cell tomorrow. The two ID
                     sets should overlap almost completely.
``rsrq_identity``    RSRQ = 10log10(N_RB) + RSRP - RSSI. The residual must be
                     close to constant, because all three are views of one
                     measurement.
``gps_kinematics``   A vehicle does not reverse direction between consecutive
                     seconds, and reported speed tracks GPS displacement.
``sampling_jitter``  Real logging equipment jitters and drops samples. A perfect
                     grid is a red flag.
``value_quantisation`` Instruments report on quantised steps; uniform last digits
                     indicate a random draw on a decimal grid.
``handover_gain``    Real handover gains are widely spread and often negative.
                     A tight distribution around one value indicates a constant
                     offset plus noise.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.authenticity")

PASS, WARN, FAIL, SKIP = "pass", "warn", "FAIL", "n/a"


@dataclass
class Check:
    name: str
    verdict: str
    statistic: str
    expected: str
    note: str = ""


def _m(lat):
    return 111320.0, 111320.0 * np.cos(np.radians(np.nanmean(lat)))


def path_loss(df: pd.DataFrame) -> Check:
    need = {"lat", "lon", "serving_rsrp", "serving_pci"}
    if not need <= set(df.columns) or df["lat"].isna().all():
        return Check("path_loss", SKIP, "-", "-30..-40 dB/decade", "missing GPS or PCI")
    cent = df.groupby("serving_pci")[["lat", "lon"]].mean().rename(
        columns={"lat": "clat", "lon": "clon"})
    j = df.join(cent, on="serving_pci")
    ky, kx = _m(j["lat"])
    dist = np.hypot((j["lat"] - j["clat"]) * ky, (j["lon"] - j["clon"]) * kx)
    ok = (dist > 20) & np.isfinite(j["serving_rsrp"]) & np.isfinite(dist)
    if ok.sum() < 500:
        return Check("path_loss", SKIP, "-", "-30..-40 dB/decade", "too few samples")
    x, y = np.log10(dist[ok]), j["serving_rsrp"][ok]
    slope = float(np.polyfit(x, y, 1)[0])
    r = float(np.corrcoef(x, y)[0, 1])
    # A physical cell ID is reused across a city, so its sample centroid is only a
    # rough proxy for the antenna. This check is therefore INFORMATIONAL: a real
    # capture can score near zero simply from PCI reuse. It carries weight only
    # alongside the identity and consistency checks below.
    verdict = PASS if slope < -12 else WARN
    return Check("path_loss (informational)", verdict, f"{slope:+.1f} dB/decade (r={r:+.2f})",
                 "negative, but PCI reuse weakens this test", "")


def event_sample_pairing(df: pd.DataFrame, ho: pd.DataFrame) -> Check:
    """Do the event table and the sample table describe the same cells?

    A regenerated sample export paired with an old event log looks exactly like
    fabricated data on every cross-file test, so this runs first and gates the
    interpretation of everything that compares the two.
    """
    if not len(ho) or "to_pci" not in ho or "serving_pci" not in df:
        return Check("event/sample pairing", SKIP, "-", ">60% shared cells", "no event table")
    serv = set(pd.to_numeric(df["serving_pci"], errors="coerce").dropna().astype(int))
    tgt = set(pd.to_numeric(ho["to_pci"], errors="coerce").dropna().astype(int))
    if not tgt:
        return Check("event/sample pairing", SKIP, "-", ">60% shared cells", "no targets")
    ov = len(serv & tgt) / len(tgt)
    verdict = PASS if ov > 0.6 else (WARN if ov > 0.3 else FAIL)
    return Check("event/sample pairing", verdict,
                 f"{ov:.0%} of {len(tgt)} handover targets appear as a serving cell "
                 f"({len(serv)} serving cells in the samples)",
                 ">60%",
                 "the event log and the sample log describe different cells - they are "
                 "almost certainly from different exports; regenerate the event log"
                 if verdict == FAIL else "")


def target_is_neighbour(df: pd.DataFrame, ho: pd.DataFrame, k: int = 3) -> Check:
    cols = [f"nbr{i}_id" for i in range(1, k + 1) if f"nbr{i}_id" in df]
    if not cols or not len(ho) or "to_pci" not in ho:
        return Check("target_is_neighbour", SKIP, "-", "70-95%", "no neighbour columns")
    # Meaningless if the two tables are not the same capture - say so instead of
    # reporting a near-zero hit rate as evidence of fabrication.
    pairing = event_sample_pairing(df, ho)
    if pairing.verdict == FAIL:
        return Check("target_is_neighbour", SKIP, "-", "70-95%",
                     "skipped: event log and sample log are not the same capture")
    s = df.set_index("t").sort_index()
    hit1 = hitk = n = 0
    for t, target in zip(ho["t"], ho["to_pci"]):
        try:
            row = s.loc[:t - pd.Timedelta(seconds=1)].iloc[-1]
        except Exception:
            continue
        # some exports repeat the serving cell in the neighbour list; it cannot
        # be a handover target, so it is not a candidate
        serving = row.get("serving_pci")
        cands = [row.get(c) for c in cols if not (pd.notna(serving) and row.get(c) == serving)]
        if not cands or all(pd.isna(c) for c in cands):
            continue
        n += 1
        hit1 += bool(cands[0] == target)
        hitk += bool(target in cands)
    if n < 20:
        return Check("target_is_neighbour", SKIP, "-", "70-95%", "too few matched events")
    p1, pk = hit1 / n, hitk / n
    chance = min(1.0, len(cols) / max(df[cols[0]].nunique(), 1))
    verdict = PASS if pk > 0.5 else (WARN if pk > 0.2 else FAIL)
    return Check("target_is_neighbour", verdict,
                 f"top-1 {p1:.1%}, top-{len(cols)} {pk:.1%} (chance {chance:.1%}, n={n})",
                 "top-3 above 70%",
                 "handover targets are unrelated to the measured neighbours"
                 if verdict == FAIL else "")


def neighbour_identity(df: pd.DataFrame, k: int = 3) -> Check:
    cols = [f"nbr{i}_id" for i in range(1, k + 1) if f"nbr{i}_id" in df]
    if not cols or "serving_pci" not in df:
        return Check("neighbour_identity", SKIP, "-", ">80% overlap", "no neighbour columns")
    serv = set(pd.to_numeric(df["serving_pci"], errors="coerce").dropna().astype(int))
    nb: set[int] = set()
    for c in cols:
        nb |= set(pd.to_numeric(df[c], errors="coerce").dropna().astype(int))
    if not nb:
        return Check("neighbour_identity", SKIP, "-", ">80% overlap", "neighbour columns empty")
    ov = len(serv & nb) / len(nb)
    verdict = PASS if ov > 0.6 else (WARN if ov > 0.3 else FAIL)
    return Check("neighbour_identity", verdict,
                 f"{ov:.1%} of {len(nb)} neighbour IDs are also a serving cell",
                 ">60%", "serving and neighbour cell identities come from different pools"
                 if verdict == FAIL else "")


def rsrq_identity(df: pd.DataFrame) -> Check:
    if not {"serving_rsrp", "serving_rsrq", "serving_rssi"} <= set(df.columns):
        return Check("rsrq_identity", SKIP, "-", "residual std < 3 dB", "missing RSSI")
    res = (df["serving_rsrq"] - (df["serving_rsrp"] - df["serving_rssi"])).dropna()
    if len(res) < 500:
        return Check("rsrq_identity", SKIP, "-", "residual std < 3 dB", "too few samples")
    sd = float(res.std())
    verdict = PASS if sd < 3 else (WARN if sd < 5 else FAIL)
    return Check("rsrq_identity", verdict,
                 f"std {sd:.1f} dB, range {res.min():.0f}..{res.max():.0f}",
                 "near-constant (std < 3 dB)",
                 "RSRP, RSRQ and RSSI are not three views of one measurement"
                 if verdict == FAIL else "")


def gps_kinematics(df: pd.DataFrame, gap_s: float = 5.0) -> Check:
    if "lat" not in df or df["lat"].isna().all():
        return Check("gps_kinematics", SKIP, "-", "<2% reversals", "no GPS")
    dt = df["t"].diff().dt.total_seconds().fillna(gap_s + 1)
    blk = (dt > gap_s).cumsum()
    rev, tot, corrs = 0, 0, []
    for _, g in df.groupby(blk):
        if len(g) < 50:
            continue
        lat, lon = g["lat"].to_numpy(float), g["lon"].to_numpy(float)
        ky, kx = _m(lat)
        step_m = np.hypot(np.diff(lat) * ky, np.diff(lon) * kx)
        brg = np.degrees(np.arctan2(np.diff(lon), np.diff(lat)))
        turn = np.abs((np.diff(brg) + 180) % 360 - 180)
        # GPS noise makes a stationary receiver appear to spin. Only count
        # reversals over steps long enough to be real movement (> ~15 km/h).
        moving = (step_m[:-1] > 4.0) & (step_m[1:] > 4.0)
        rev += int((turn[moving] > 90).sum())
        tot += int(moving.sum())
        if "speed_kmh" in g:
            ky, kx = _m(lat)
            step = np.hypot(np.diff(lat) * ky, np.diff(lon) * kx) * 3.6
            v = g["speed_kmh"].to_numpy(float)[1:]
            m = np.isfinite(step) & np.isfinite(v)
            m &= (step > 4.0 * 3.6) | (v > 15)
            if m.sum() > 100:
                corrs.append(float(np.corrcoef(step[m], v[m])[0, 1]))
    if tot == 0:
        return Check("gps_kinematics", SKIP, "-", "<2% reversals", "no usable track")
    frac = rev / tot
    corr = float(np.mean(corrs)) if corrs else np.nan
    verdict = PASS if frac < 0.05 else (WARN if frac < 0.15 else FAIL)
    return Check("gps_kinematics", verdict,
                 f"{frac:.1%} direction reversals/s while moving "
                 f"(n={tot}), speed-vs-GPS r={corr:.2f}",
                 "<5% reversals while moving",
                 "the track reverses direction faster than a vehicle can"
                 if verdict == FAIL else "")


def sampling_jitter(df: pd.DataFrame, raw_times: pd.Series | None = None) -> Check:
    """Must be given the RAW timestamps. The pipeline resamples onto a regular
    grid, so running this on processed samples measures our own preprocessing."""
    if raw_times is None:
        return Check("sampling_jitter", SKIP, "-", "some jitter",
                     "raw timestamps not supplied; grid is imposed by the pipeline")
    dt = pd.Series(pd.to_datetime(raw_times)).sort_values().diff().dt.total_seconds().dropna()
    if len(dt) < 100:
        return Check("sampling_jitter", SKIP, "-", "some jitter", "too few samples")
    within = dt[dt < 5]
    exact = float((within == within.round(3)).mean())
    uniq = int(within.round(3).nunique())
    # INFORMATIONAL: XCAL itself exports on a fixed grid, so a regular clock is
    # normal here and says nothing about authenticity. Kept because it tells you
    # the export rate, which is what limits the shortest labelable horizon.
    verdict = PASS if uniq > 5 else WARN
    return Check("sampling_jitter (informational)", verdict,
                 f"{uniq} distinct inter-sample gaps, {exact:.3%} on an exact grid",
                 "export rate, not an authenticity signal", "")


def value_quantisation(df: pd.DataFrame, cols=("serving_rsrp", "serving_rsrq")) -> Check:
    spreads = []
    for c in cols:
        if c not in df:
            continue
        v = df[c].dropna()
        if len(v) < 1000:
            continue
        # Instruments quantise. XCAL reports RSRP/RSRQ as whole dBm, so a single
        # last-digit value is the *expected* signature; a flat spread across all
        # ten digits is what indicates round(uniform(), 1).
        digits = ((v * 10).round().astype(int) % 10).value_counts(normalize=True)
        spreads.append(1.0 if len(digits) == 1 else float(digits.std()))
    if not spreads:
        return Check("value_quantisation", SKIP, "-", "uneven digits", "no columns")
    sd = float(np.mean(spreads))
    verdict = PASS if sd > 0.02 else (WARN if sd > 0.01 else FAIL)
    return Check("value_quantisation", verdict,
                 f"last-decimal-digit spread {sd:.4f}",
                 "uneven (instruments quantise); 0.000 means uniform random",
                 "values look drawn uniformly on a 0.1 grid" if verdict == FAIL else "")


def handover_gain(df: pd.DataFrame, ho: pd.DataFrame) -> Check:
    if not len(ho) or "serving_rsrp" not in df:
        return Check("handover_gain", SKIP, "-", "wide spread", "no events")
    s = df.set_index("t").sort_index()
    gains = []
    for t in ho["t"]:
        try:
            b = s.loc[:t - pd.Timedelta(seconds=1)].iloc[-1]["serving_rsrp"]
            a = s.loc[t + pd.Timedelta(seconds=1):].iloc[0]["serving_rsrp"]
        except Exception:
            continue
        if np.isfinite(b) and np.isfinite(a):
            gains.append(a - b)
    if len(gains) < 20:
        return Check("handover_gain", SKIP, "-", "wide spread", "too few events")
    g = np.array(gains)
    ratio = abs(float(np.mean(g) - np.median(g)))
    improved = float((g > 0).mean())
    verdict = PASS if (g.std() > 4 and improved < 0.95) else WARN
    return Check("handover_gain", verdict,
                 f"mean {g.mean():+.1f} dB, median {np.median(g):+.1f}, std {g.std():.1f}, "
                 f"{improved:.0%} improve",
                 "wide spread, some handovers lose signal",
                 "gain is a near-constant offset" if ratio < 0.2 and g.std() < 4 else "")


DECISIVE = {"switch_physics", "target_is_neighbour", "neighbour_identity",
            "rsrq_identity", "value_quantisation"}


def switch_physics(df: pd.DataFrame, k: int = 3) -> Check:
    """When the serving cell changes, was a neighbour actually stronger first?

    This is the strongest authenticity signal available, because it needs only
    the sample file: it asks whether the file agrees with itself. A generator
    that draws serving-cell changes independently of the neighbour columns
    cannot produce it.
    """
    ncols = [f"nbr{i}_rsrp" for i in range(1, k + 1) if f"nbr{i}_rsrp" in df]
    if "serving_pci" not in df or "serving_rsrp" not in df or not ncols:
        return Check("switch_physics", SKIP, "-", ">70% neighbour stronger", "missing columns")
    p = pd.to_numeric(df["serving_pci"], errors="coerce").to_numpy()
    chg = np.flatnonzero((p[1:] != p[:-1]) & np.isfinite(p[1:]) & np.isfinite(p[:-1])) + 1
    if len(chg) < 20:
        return Check("switch_physics", SKIP, "-", ">70% neighbour stronger", "too few changes")
    srv = df["serving_rsrp"].to_numpy(float)
    with np.errstate(invalid="ignore"):
        nb = df[ncols].to_numpy(float)
        best = np.where(np.isnan(nb).all(axis=1), np.nan, np.nanmax(np.nan_to_num(nb, nan=-1e9), axis=1))
        best[best < -1e8] = np.nan
    gap = srv[chg - 1] - best[chg - 1]
    coverage = float(np.isfinite(gap).mean())
    gap = gap[np.isfinite(gap)]
    if len(gap) < 20:
        return Check("switch_physics", SKIP, "-", ">70% neighbour stronger", "no neighbour data")
    # Only meaningful when a neighbour reading actually exists at the moment of
    # the switch. Event-triggered reporting (real XCAL) leaves most switches with
    # no fresh neighbour value, which would look like a failure but is not.
    if coverage < 0.6:
        return Check("switch_physics", SKIP,
                     f"only {coverage:.0%} of cell changes have a neighbour reading",
                     ">70% neighbour stronger",
                     "neighbour coverage too sparse for this test")
    frac = float((gap <= 0).mean())
    verdict = PASS if frac > 0.7 else (WARN if frac > 0.4 else FAIL)
    return Check("switch_physics", verdict,
                 f"{frac:.0%} of {len(gap)} cell changes had a stronger neighbour first "
                 f"(median gap {np.median(gap):+.1f} dB)",
                 ">70%", "cell changes are unrelated to the measured neighbours"
                 if verdict == FAIL else "")


def audit(df: pd.DataFrame, ho: pd.DataFrame | None = None, k: int = 3,
          raw_times: pd.Series | None = None) -> pd.DataFrame:
    ho = ho if ho is not None else pd.DataFrame()
    checks = [
        switch_physics(df, k), target_is_neighbour(df, ho, k), neighbour_identity(df, k),
        rsrq_identity(df), value_quantisation(df), event_sample_pairing(df, ho),
        gps_kinematics(df), sampling_jitter(df, raw_times), handover_gain(df, ho),
        path_loss(df),
    ]
    out = pd.DataFrame([c.__dict__ for c in checks])
    fails = int((out["verdict"] == FAIL).sum())
    LOG.info("authenticity audit: %d fail, %d warn, %d pass, %d skipped",
             fails, int((out["verdict"] == WARN).sum()),
             int((out["verdict"] == PASS).sum()), int((out["verdict"] == SKIP).sum()))
    return out


def overall_verdict(table: pd.DataFrame) -> str:
    """Weighted on the four checks that cleanly separate measured from generated
    data. The others are context: they can fail on a genuine capture for benign
    reasons (PCI reuse, GPS noise, a resampled export)."""
    dec = table[table["name"].isin(DECISIVE)]
    dec_fail = int((dec["verdict"] == FAIL).sum())
    fails = int((table["verdict"] == FAIL).sum())
    warns = int((table["verdict"] == WARN).sum())
    if dec_fail >= 3:
        return ("SYNTHETIC - fails the checks that separate measured from generated "
                "data. Do not use it for any reported result.")
    if dec_fail >= 1:
        return ("SUSPECT - a decisive check has failed. Establish the provenance of "
                "this file before using it.")
    if fails >= 3:
        return ("SYNTHETIC - this capture fails physical and protocol checks that "
                "measured data passes. Do not use it for any reported result.")
    if fails >= 1:
        return ("SUSPECT - at least one check that measured data should pass has failed. "
                "Establish the provenance of this file before using it.")
    if warns >= 3:
        return "INCONCLUSIVE - several checks are borderline; inspect them individually."
    return "CONSISTENT WITH MEASURED DATA on the checks available for this capture."
