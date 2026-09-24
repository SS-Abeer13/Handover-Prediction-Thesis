# -*- coding: utf-8 -*-
"""Revised manuscript text, part C: Section 5.10 (ping-pong and arrivals) and the
remaining paragraphs whose numbers come from stage 26."""


def part_c(N):
    return {
500: "Table 5.14 reports where the phenomenon concentrates.",
495: ("Table 5.13 reports the same fixed set of "
     f"{N['ho_all']} handover commands under three definitions that differ only in choices the "
     "literature routinely leaves unstated, and Figure 5.15 extends that ladder to the full grid of "
     "window lengths."),
497: ("The rate moves by "
     f"{100 * (N['pp_any'] - N['pp_strict']):.0f} percentage points — from {N['pp_strict']:.1%} to "
     f"{N['pp_any']:.1%} — without a single change to the underlying measurement. This is the "
     "quantitative form of the observation in Section 2.4, and it is why this thesis quotes the "
     "strictest of the three and states the alternatives alongside it. It also explains how Amirova "
     f"et al. [{N['ref_amirova']}] arrive at 0.13 % on comparable data: dividing by measurement "
     "records rather than by handovers changes the denominator by two orders of magnitude."),
498: ("The window length is a fourth choice, and Figure 5.15 reports the full grid rather than the "
     "single row of Table 5.13. Across three window lengths and three identity-and-return conventions "
     f"the same {N['ho_all']} commands yield nine defensible ping-pong rates between "
     f"{N['pp_grid_min']:.1%} and {N['pp_grid_max']:.1%}. No cell in that grid is wrong; what is "
     "wrong is publishing one of them without saying which."),
# NB: a list value means "replace this paragraph, then insert the rest after it".
503: [("Figure 5.16 separates the strata, and Table 5.14 gives the counts as well as the rates so "
     "that the two stratifications can be seen to partition the same "
     f"{N['pp_n_total']} returns. Both are computed by flagging each command once on the full "
     "sequence and then partitioning the flags. Flagging inside a stratum instead — which an earlier "
     "version of this analysis did, and which is the natural way to write the loop — redefines "
     "“the immediately previous cell” as the previous cell *within the stratum*, and made the "
     "carrier rows and the regime rows disagree by 34 returns on one fixed command set."),
    ("One contrast is large and one is not what it appears to be. Ping-pong concentrates in "
     f"intra-frequency handovers, at {N['pp_intra']:.1%} against {N['pp_inter']:.1%} across carriers, "
     "a factor of roughly three: a return to the cell just left is overwhelmingly a return within the "
     "same carrier, which is what the A3 entry condition on a single frequency makes easy. The speed "
     "contrast points the other way from the intuitive account and cannot be resolved here. The "
     f"highway campaign, at roughly twice the urban mean speed, returns at {N['pp_highway']:.1%} "
     f"against {N['pp_urban']:.1%} on the urban campaigns — higher, not lower. With one campaign per "
     "regime, speed is completely confounded with route, cell density, carrier mix and time of day, "
     "so this thesis does not claim that speed drives ping-pong and does not claim to have ruled it "
     "out; it reports that the fastest campaign is also the most return-prone, which is the opposite "
     "of what a speed-protective account would predict. Importantly, a rapid return to the previous "
     "cell identifies an oscillatory transfer under cellular operational rules, but does not by itself "
     "prove that the initial handover was counterfactually unnecessary: without observing link quality "
     "had the handset remained on the serving cell (which may have suffered severe fading or link failure), "
     "a rapid return reflects sensitive boundary triggering rather than established service degradation."),
    ("An earlier version of this section named the time-to-trigger and offset of the dominant "
     "configuration profile as the lever available to an operator. That claim is withdrawn. Section "
     "3.5 establishes that the configuration set is stable across all four campaigns: there is no "
     "time-to-trigger or offset variation anywhere in this data, so neither parameter can be "
     "associated with the return rate from these measurements at all, in either direction. The "
     "time-to-trigger remains the most plausible lever on theoretical grounds and the obvious "
     "candidate for the controlled experiment proposed in Section 7.3, but nothing measured here "
     "bears on it.")],
504: ("Modelling the arrival stream as a self-exciting process characterises the clustering from a "
     f"different direction. The fitted Hawkes branching ratio is {N['hawkes_pooled']:.3f} on the "
     f"pooled stream, with per-campaign estimates from {N['hawkes_min']:.3f} to {N['hawkes_max']:.3f}. "
     "The physical reading of that quantity — the expected number of direct offspring per event — "
     "belongs to the exponential-kernel model, and the Ogata residual test of Section 4.11 rejects "
     f"that kernel on this data: rescaling the time axis by the fitted compensator gives "
     f"{N['ogata_n']} residuals whose Kolmogorov\u2013Smirnov distance from a unit-rate exponential "
     f"is D = {N['ogata_D']:.3f} at p = {N['ogata_p']:.4f}. Their mean is "
     f"{N['ogata_mean_resid']:.3f}, indicating that while the average rate is well-matched, the "
     "stationary exponential Hawkes model as a whole is rejected by the data. Such a rejection may "
     "reflect non-exponential decay dynamics, a time-varying background rate \u03bc(t) driven by "
     "corridor transitions and junctions, or unobserved network covariates. The rejection and its "
     "statistic are reported rather than suppressed, and together they limit what "
     "the number may be used for: the branching ratio is taken here as a comparable summary statistic "
     "of how strongly arrivals cluster, not as a count of triggered handovers. The clustering itself "
     "is not in doubt, and it is the reason Section 5.8 separates quiet rows from rows inside a "
     "burst."),
}
