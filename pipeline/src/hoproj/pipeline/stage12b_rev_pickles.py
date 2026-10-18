"""Stage 12b - build the data/rev pickles that stages 22-31 read.

    python -m hoproj.pipeline.stage12b_rev_pickles

Stage 12 writes data/processed_xcal (the row-level frames). Stages 22-31 also
read two signalling pickles, data/rev/signalling.pkl and data/rev/reports_v2.pkl,
which had no builder of their own in src/ until stage 32 added one. This stage
exposes that builder for the four development campaigns, so the reproduction
order is explicit:

    stage12_xcal_prepare -> stage12b_rev_pickles -> stage22_revision --exp all
    -> stage23_signalling_revision -> stage26_rev_extras -> stage30_sensitivity
"""
from __future__ import annotations

import argparse
from pathlib import Path

from . import stage12_xcal_prepare as s12
from .stage32_second_operator import build_pickles


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/rev")
    a = ap.parse_args(argv)
    build_pickles(s12.CAPTURES, Path(a.out))


if __name__ == "__main__":
    main()
