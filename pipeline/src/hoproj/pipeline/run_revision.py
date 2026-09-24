"""Run the revision pipeline end to end: stages 22 to 31.

    python -m hoproj.pipeline.run_revision            # everything
    python -m hoproj.pipeline.run_revision --only 22 26 30
    python -m hoproj.pipeline.run_revision --skip 28  # 28 needs network access

WHY THIS FILE EXISTS.  ``run_all.py``, the Makefile and both notebooks stop at stage
21.  Everything after the 17 September review -- the alignment audit, the one-row
feature lag, leave-one-campaign-out as the primary protocol, and every number in
Chapter 5 of the revised manuscript -- lives in stages 22 to 31 and had no entry
point at all.  A reader who cloned this repository and ran ``make all`` or the
notebook would reproduce the *pre-audit* study, whose headline result the thesis
retracts.  That is the single worst reproducibility failure this project could
ship, so the revision now has a runner of its own.

The v1 pipeline (stages 1 to 21) is deliberately left in place and untouched: the
manuscript quotes its numbers as the thing the audit overturned, so deleting it
would remove the evidence.  It is simply no longer the pipeline that produces the
results.  See ``notebooks/README.md``.

Order matters in two places only: stage 29 writes the per-handover geometry that
stage 31 reads, and the figures of stage 25 consume tables written by everything
before them, so they run last.
"""
from __future__ import annotations

import argparse
import time
import traceback

from ..utils import get_logger

LOG = get_logger("hoproj.run_revision")

# (number, module, callable, one-line description, needs_network)
STAGES = [
    (22, "stage22_revision", "main",
     "alignment audit, protocol ladder, main LOCO, coherence, CRC, ablation", False),
    (23, "stage23_signalling_revision", "main",
     "A3 episodes matched one-to-one to commands; handover completion", False),
    (24, "stage24_external_revision", "main",
     "transfer to the public dataset, both domains from L3 signalling", False),
    (26, "stage26_rev_extras", None,
     "feature-block counts, v2 timeline counters, ping-pong ladder, Hawkes + Ogata", False),
    (27, "stage27_external_alignment", "main",
     "the Raca control: an instantaneous-sampling log, for contrast", False),
    (28, "stage28_nuwins_audit", "main",
     "NUWiNS replication of the alignment defect (downloads ~1 GB)", True),
    (29, "stage29_alignment_mechanism", "main",
     "intra-second geometry, the falsification test, three-dataset table", False),
    (30, "stage30_sensitivity", None,
     "sensitivity of the four post-hoc windows", False),
    (31, "stage31_case_studies", None,
     "unsifted TP/FP/FN case studies; per-handover residual evidence", False),
    (25, "stage25_rev_figures", None,
     "every figure in Chapter 5 (runs last: it consumes the tables above)", False),
]

# stages whose module has no main(); call these in order instead
ENTRY_POINTS = {
    26: ("timeline_counters", "feature_blocks", "single_feature_lag0", "pingpong", "hawkes"),
    30: ("block_length", "purge_length", "burst_cutoff", "blank_window"),
    31: ("case_studies", "residual_evidence"),
    25: None,   # module-level __main__ loop; handled specially
}


def _run_stage(num: int, mod_name: str, entry: str | None) -> None:
    import importlib
    mod = importlib.import_module(f"hoproj.pipeline.{mod_name}")
    if num == 25:
        import matplotlib.pyplot as plt
        names = [n for n in dir(mod) if n.startswith("fig_")]
        for n in names:
            try:
                getattr(mod, n)()
                LOG.info("  %s ok", n)
            except FileNotFoundError as exc:
                LOG.warning("  %s skipped, missing table: %s", n, exc)
            plt.close("all")
        return
    for fn in (ENTRY_POINTS.get(num) or (entry,)):
        LOG.info("  -> %s()", fn)
        getattr(mod, fn)()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", nargs="*", type=int, help="run just these stage numbers")
    ap.add_argument("--skip", nargs="*", type=int, default=[], help="skip these stage numbers")
    ap.add_argument("--offline", action="store_true",
                    help="skip every stage that needs to download data (stage 28)")
    ap.add_argument("--list", action="store_true", help="print the stages and exit")
    a = ap.parse_args(argv)

    if a.list:
        for n, m, _, desc, net in STAGES:
            print(f"  {n:>2}  {m:<28} {'[network] ' if net else '':<10}{desc}")
        return 0

    todo = [s for s in STAGES
            if (not a.only or s[0] in a.only)
            and s[0] not in a.skip
            and not (a.offline and s[4])]
    LOG.info("running %d stage(s): %s", len(todo), ", ".join(str(s[0]) for s in todo))

    failed = []
    for num, mod_name, entry, desc, _ in todo:
        LOG.info("=" * 70)
        LOG.info("stage %d - %s", num, desc)
        t0 = time.time()
        try:
            _run_stage(num, mod_name, entry)
            LOG.info("stage %d done in %.0f s", num, time.time() - t0)
        except Exception:                                        # noqa: BLE001
            LOG.error("stage %d FAILED:\n%s", num, traceback.format_exc())
            failed.append(num)

    LOG.info("=" * 70)
    if failed:
        LOG.error("failed stages: %s", failed)
        return 1
    LOG.info("all stages completed; tables in reports_rev/tables, figures in reports_rev/figures")
    LOG.info("now rebuild the manuscript: Docs/manuscript-src/revision/build_revised.py, "
             "then verify.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
