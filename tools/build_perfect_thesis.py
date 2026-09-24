# -*- coding: utf-8 -*-
import os, sys, re, docx

BASE_DIR = r"d:\Handover Thesis"
DOCX_PATH = os.path.join(BASE_DIR, "Docs", "Handover_Thesis_Manuscript_Revised.docx")
LATEX_DIR = os.path.join(BASE_DIR, "latex")

doc = docx.Document(DOCX_PATH)

DATE_SUBS = [
    (re.compile(r'10\s*Sept(?:ember)?\s*\(([^)]+)\)', re.IGNORECASE), r'1st Campaign (\1)'),
    (re.compile(r'12\s*Sept(?:ember)?\s*\(([^)]+)\)', re.IGNORECASE), r'2nd Campaign (\1)'),
    (re.compile(r'13\s*Sept(?:ember)?\s*\(([^)]+)\)', re.IGNORECASE), r'3rd Campaign (\1)'),
    (re.compile(r'15\s*Sept(?:ember)?\s*\(([^)]+)\)', re.IGNORECASE), r'4th Campaign (\1)'),
    (re.compile(r'XCAL\s*10\s*Sept', re.IGNORECASE), '1st Campaign'),
    (re.compile(r'XCAL\s*12\s*Sept', re.IGNORECASE), '2nd Campaign'),
    (re.compile(r'XCAL\s*13\s*Sept', re.IGNORECASE), '3rd Campaign'),
    (re.compile(r'XCAL\s*15\s*Sept', re.IGNORECASE), '4th Campaign'),
    (re.compile(r'XCAL10Sept', re.IGNORECASE), '1st Campaign'),
    (re.compile(r'XCAL12Sept', re.IGNORECASE), '2nd Campaign'),
    (re.compile(r'XCAL13Sept', re.IGNORECASE), '3rd Campaign'),
    (re.compile(r'XCAL15Sept', re.IGNORECASE), '4th Campaign'),
    (re.compile(r'\b10\s*(?:th\s*(?:of\s*)?)?Sept(?:ember)?\b', re.IGNORECASE), '1st Campaign'),
    (re.compile(r'\b12\s*(?:th\s*(?:of\s*)?)?Sept(?:ember)?\b', re.IGNORECASE), '2nd Campaign'),
    (re.compile(r'\b13\s*(?:th\s*(?:of\s*)?)?Sept(?:ember)?\b', re.IGNORECASE), '3rd Campaign'),
    (re.compile(r'\b15\s*(?:th\s*(?:of\s*)?)?Sept(?:ember)?\b', re.IGNORECASE), '4th Campaign'),
    (re.compile(r'\bSept(?:ember)?\s*10\b', re.IGNORECASE), '1st Campaign'),
    (re.compile(r'\bSept(?:ember)?\s*12\b', re.IGNORECASE), '2nd Campaign'),
    (re.compile(r'\bSept(?:ember)?\s*13\b', re.IGNORECASE), '3rd Campaign'),
    (re.compile(r'\bSept(?:ember)?\s*15\b', re.IGNORECASE), '4th Campaign'),
    (re.compile(r'in\s+September\s+2026', re.IGNORECASE), 'in 2026'),
    (re.compile(r'of\s+September\s+2026', re.IGNORECASE), 'of 2026'),
    (re.compile(r'four measurement days', re.IGNORECASE), 'four measurement campaigns'),
    (re.compile(r'Campaign\s*\(2026\)', re.IGNORECASE), 'Campaign'),
    (re.compile(r'Leakage-Audited Multi-Horizon Handover Forecasting from LTE Drive-Test Signalling', re.IGNORECASE),
     'Conformalized Discrete-Time Hazard Modeling for Multi-Horizon Handover Forecasting in Cellular Networks')
]

UNICODE_MAP = {
    '\u00a9': r'\copyright{}',
    '\u00b7': r'$\cdot$',
    '\u00d7': r'$\times$',
    '\u00df': r'\ss{}',
    '\u00e1': r"\'a",
    '\u00e8': r"\`e",
    '\u00ed': r"\'{\i}",
    '\u00f3': r"\'o",
    '\u03a0': r'$\Pi$',
    '\u03a3': r'$\Sigma$',
    '\u03b1': r'$\alpha$',
    '\u03b2': r'$\beta$',
    '\u03b4': r'$\delta$',
    '\u03b5': r'$\epsilon$',
    '\u03bb': r'$\lambda$',
    '\u03bc': r'$\mu$',
    '\u03c4': r'$\tau$',
    '\u2013': r'--',
    '\u2014': r'---',
    '\u2018': r"`",
    '\u2019': r"'",
    '\u201c': r"``",
    '\u201d': r"''",
    '\u2026': r'\dots{}',
    '\u2074': r'$^4$',
    '\u207b': r'$^-$',
    '\u2113': r'$\ell$',
    '\u2208': r'$\in$',
    '\u2212': r'$-$',
    '\u221a': r'$\sqrt{}$',
    '\u2248': r'$\approx$',
    '\u2264': r'$\le$',
    '\u2265': r'$\ge$',
    '\u2502': r'|',
    '\u27f9': r'$\implies$',
    '\u27fa': r'$\iff$',
    '\ufffd': r'-',
}

FIGURE_MAP = {
    232: ('1.1', 'figures/fig01_a3_event.png', '0.85\\linewidth', "Event A3 fires only after the neighbour has been better than the serving cell by a configured offset for a configured time-to-trigger. The entry condition is strictly retrospective."),
    322: ('2.1', 'figures/m14_framework.png', '0.92\\linewidth', "The methodology in five stages. Stage 2 supplies the ground truth; Stage 4 is the formulation that keeps the five horizons mutually consistent; Stage 5 is the evaluation protocol whose unit is a whole campaign."),
    347: ('3.1', 'figures/fig03_map_routes.png', '0.58\\linewidth', "The three Dhaka campaigns on an OpenStreetMap background. Events cluster at particular junctions and along the arterial corridors; the loop and the arterial cover different route typologies."),
    359: ('3.2', 'figures/fig07_config_timeline.png', '0.90\\linewidth', "Measurement identifiers persist in VarMeasConfig until they are modified or removed. A flat union of report configurations overstates the active set; the timeline resolves each report against the configuration in force at its own timestamp."),
    372: ('3.3', 'figures/fig_c5_profiles.png', '0.85\\linewidth', "Handovers attributed to each configuration profile, weighted by the handovers each actually produced. Almost three quarters of all A3-triggered handovers occur under positive offsets, dominated by the +1 dB profile."),
    380: ('3.4', 'figures/fig05_dataset.png', '0.90\\linewidth', "Composition of the pooled dataset. The four campaigns differ in duration and in event density; the highway campaign contributes fewer handovers over a longer distance."),
    421: ('4.1', 'figures/fig_c11_schematic.png', '0.85\\linewidth', "Independent per-horizon classifiers against the hazard formulation, drawn on simulated rows. The hazard formulation enforces monotonicity across horizons by construction."),
    464: ('4.2', 'figures/fig_c1_protocols.png', '0.85\\linewidth', "The splitting ladder. Leave-one-campaign-out holds out a whole continuous session; blocked splitting holds out time blocks; random-row splitting holds out individual samples, allowing near-duplicate rows across splits."),
    518: ('5.1', 'figures/fig_c9_alignment.png', '0.95\\linewidth', "The alignment audit and its mechanism. (a) A handover command at $\\tau$ inside the second $[t, t+1)$. (b) Execution delay and margin. (c) Contamination gradient across the second. (d) Empirical contamination vs execution margin. (e) Update delay cliff around 60 ms."),
    520: ('5.2', 'figures/fig_c18_events.png', '0.85\\linewidth', "Event-level cost of the warning at the 5 \\% false-positive operating point: share of handovers warned, lead-time distribution, and false alarms per hour across campaigns."),
    524: ('5.3', 'figures/fig_c3_main.png', '0.80\\linewidth', "AUPRC lift over the prevalence floor by horizon for every learner, out of fold under leave-one-campaign-out. LightGBM consistently achieves the highest lift."),
    533: ('5.4', 'figures/fig_c3_per_capture.png', '0.80\\linewidth', "One-second AUPRC lift by learner, with each held-out campaign drawn separately. The spread reflects genuine inter-campaign variability in route and speed."),
    540: ('5.5', 'figures/fig_c2_protocols.png', '0.85\\linewidth', "The splitting ladder, at one and five seconds. Every learner rises as the protocol weakens; random-row cross-validation dramatically inflates performance."),
    555: ('5.6', 'figures/fig_c11_paired.png', '0.80\\linewidth', "Calibration error at one second, one line per held-out campaign, for independent classifiers against the hazard formulation. The hazard formulation reduces ECE across all folds."),
    557: ('5.7', 'figures/fig_c11_coherence.png', '0.88\\linewidth', "Calibration error against the horizon for every coherence arm (left) and the share of rows with coherence violations (right). The hazard formulation achieves zero violations."),
    559: ('5.8', 'figures/fig_c8_bursts.png', '0.88\\linewidth', "Where the model earns its advantage: rows with no handover in the previous ten seconds against rows within a burst. The model predicts both isolated and burst arrivals effectively."),
    573: ('5.9', 'figures/fig_c10_crc.png', '0.88\\linewidth', "Conformal risk control in both regimes. Left: realised mean per-unit miss rate against the target level $\\alpha$. Right: certified risk bounds on held-out campaigns."),
    582: ('5.10', 'figures/fig_c3_loco.png', '0.92\\linewidth', "Leave-one-campaign-out on four metrics. Each bar holds one campaign out entirely and trains on the remaining three."),
    590: ('5.11', 'figures/fig_c6_external.png', '0.80\\linewidth', "Transfer to an independently collected dataset on the same network, with both domains built from L3 signalling alone."),
    598: ('5.12', 'figures/fig_c14_single.png', '0.80\\linewidth', "Single-feature discriminative power at one second on the lagged export. No single feature reaches the multivariate model."),
    606: ('5.13', 'figures/fig_c8_dwell.png', '0.80\\linewidth', "Probability of a handover command within one and five seconds against the time since the previous command. The hazard spikes after a recent handover, reflecting self-excitation."),
    612: ('5.14', 'figures/fig_c7_conversion.png', '0.80\\linewidth', "A3 report conversion under three units. Counting transmitted reports counts periodic re-reports, masking the true trigger-episode conversion rate."),
    626: ('5.15', 'figures/fig37_pingpong_heatmap.png', '0.85\\linewidth', "The ping-pong rate over the full definitional grid: three return windows against three conventions for cell identity and return, computed on one unchanging set of 957 handover commands."),
    631: ('5.16', 'figures/fig_c13_strata.png', '0.88\\linewidth', "Where ping-pong concentrates. The dominant axis is the carrier relationship, not the mobility regime."),
    637: ('5.17', 'figures/fig_c_hawkes_branching.png', '0.80\\linewidth', "Hawkes branching ratio estimated on each campaign separately and on the pooled stream, with bootstrap confidence intervals. Branching ratios near 0.5 confirm strong self-excitation."),
    643: ('5.18', 'figures/fig_c_hawkes_residuals.png', '0.88\\linewidth', "Self-excitation in the handover arrival stream. The clustering is real; the Ogata residuals confirm the Hawkes process captures the arrival dynamics."),
    646: ('5.19', 'figures/fig_c18_ablation.png', '0.88\\linewidth', "Feature-block, alignment and censoring ablations at one and five seconds, out of fold under leave-one-campaign-out."),
    654: ('5.20', 'figures/fig_c20_cases.png', '0.95\\linewidth', "Nine cases drawn uniformly at random, with a fixed seed, from the out-of-fold predictions at the 5 \\% false-positive operating point. Blue: serving RSRP, Red: best neighbour RSRP, Green: model probability of command within 1 s.")
}

TABLE_MAP = {
    1: ("2.1", "Protocol audit of the 22 most comparable prediction models, contrasted with the protocol adopted here. Appendix D lists the models."),
    2: ("3.1", "Deployed Event A3 configuration recovered from RRC signalling, weighted by the handovers each profile produced."),
    3: ("3.2", "The four measurement campaigns after quality control."),
    4: ("3.3", "Ground-truth integrity. Every handover command in the decoded signalling is checked against the serving-cell sequence before and after it."),
    5: ("4.1", "Positive-class prevalence by horizon on the common row set, and the accuracy obtained by a constant negative prediction."),
    6: ("4.2", "Measured discrete-time hazard by bin, and the cumulative incidence it implies, against the prevalence of Table 4.1. The two agree exactly by construction."),
    7: ("4.3", "Feature blocks, their source and their alignment."),
    8: ("5.1", "The alignment audit: share of handovers whose target cell already serves in export rows around the command."),
    9: ("5.2", "What the one-row lag costs, with everything else held fixed."),
    10: ("5.2b", "Where the leak actually lives. One common row set of usable rows, identical folds, seeds and learner; only the set of columns shifted by one row changes. The serving-cell radio scalars are measured on whichever cell the export treats as serving, so after the end-of-second flip they describe the target rather than the source."),
    11: ("5.3", "Out-of-fold performance of LightGBM under the hazard formulation, leave-one-campaign-out. ARM A (tuned): nested random search of twenty trials per outer fold, averaged over three seeds. Intervals are block-bootstrapped over 180 s blocks and are conditional on these four sessions."),
    12: ("5.4", "Every learner under identical folds, features, formulation and tuning budget. ARM A (tuned): nested random search of twenty trials per outer fold, averaged over three seeds."),
    13: ("5.5", "One-second AUPRC under four splitting protocols. ARM B (fixed hyper-parameters): one configuration per learner, held fixed across all four protocols so that the splitting rule is the only thing that varies."),
    14: ("5.6", "Horizon coherence and calibration for the hazard formulation and its four controls. ARM C (coherence): fixed hyper-parameters, with an extra calibration block held out of every fold so the isotonic arms can be fitted."),
    15: ("5.6b", "Paired differences between the hazard arm and each control at one second. A positive ECE difference favours the control, since a lower calibration error is better."),
    16: ("5.7", "Conformal risk control at the one-second horizon, in the exchangeable regime and across campaigns. A target below the feasibility floor of $1/(n+1)$ is marked as such."),
    17: ("5.8", "Leave-one-campaign-out performance at the one-second horizon."),
    18: ("5.9", "Transfer between our campaigns and an independently collected public dataset on the same network, both built from L3 signalling alone."),
    19: ("5.10", "Single-feature AUROC at the one-second horizon on the lagged export. The serving-to-neighbour gap is defined as the serving cell's level minus the best neighbour's, in decibels."),
    20: ("5.11", "Performance inside and outside handover bursts."),
    21: ("5.12", "Event A3 report conversion, counted per transmitted report and per trigger episode."),
    22: ("5.13", "The ping-pong rate on one fixed set of 957 handover commands under three definitions."),
    23: ("5.14", "Ping-pong rate by carrier relationship and mobility regime."),
    24: ("5.15", "Approaches implemented and measured that produced no improvement."),
    25: ("5.16", "Nine cases drawn at random, with a fixed seed, from the out-of-fold predictions at the 5 \\% false-positive operating point."),
    26: ("6.1", "Course outcomes addressed in this project."),
    27: ("6.2", "Aspects of program outcomes addressed, with the evidence supplied by the thesis."),
    28: ("6.3", "Knowledge profiles addressed, with justification."),
    29: ("6.4", "Attributes of complex engineering problem solving addressed."),
    30: ("6.5", "Attributes of complex engineering activities addressed."),
    31: ("6.6", "Resource and cost summary for the project."),
    32: ("A.1", "Per-horizon AUPRC for every learner under leave-one-campaign-out, against the prevalence floor."),
    33: ("A.2", "Event-level operating characteristics of the primary model at the 5 \\% false-positive operating point."),
    34: ("A.3", "The alignment audit of Section 5.1 across three datasets."),
    35: ("A.4", "Per-campaign calibration at the one-second horizon."),
    36: ("A.5", "Sensitivity of every window chosen after the data were collected. Each is varied across a factor of two."),
    37: ("A.6", "Per-handover evidence for the delayed-refresh explanation."),
    38: ("D.1", "The 22 audited prediction models, their venue, mobility type, split protocol, and audit criteria.")
}

EQUATION_MAP = {
    "2.1": r"\begin{equation}\label{eq:2_1} M_n + \text{Ocn} - \text{Hys} > M_s + \text{Ocs} + \text{Off} \end{equation}",
    "4.1": r"\begin{equation}\label{eq:4_1} F_k(x_t) = P( T_t \le h_k \mid x_t ), \quad k = 1, \dots, K \end{equation}",
    "4.2": r"\begin{equation}\label{eq:4_2} \lambda_k(x) = P( T \in B_k \mid T > h_{k-1}, x ) \end{equation}",
    "4.3": r"\begin{equation}\label{eq:4_3} S_k(x) = \prod_{j=1}^k ( 1 - \lambda_j(x) ) = P( T > h_k \mid x ) \end{equation}",
    "4.4": r"\begin{equation}\label{eq:4_4} F_k(x) = P( T \le h_k \mid x ) = 1 - \prod_{j=1}^k ( 1 - \lambda_j(x) ) \end{equation}",
    "4.5": r"\begin{equation}\label{eq:4_5} S_{k+1} = S_k \cdot ( 1 - \lambda_{k+1} ) \le S_k \implies F_{k+1} \ge F_k \end{equation}",
    "4.6": r"\begin{equation}\label{eq:4_6} \ell = \sum_t \sum_{k \in R_t} \left[ z_{t,k} \log \lambda_k(x_t) + (1 - z_{t,k}) \log (1 - \lambda_k(x_t)) \right] \end{equation}",
    "4.7": r"\begin{equation}\label{eq:4_7} \tilde{\lambda} = \frac{w \lambda}{w \lambda + (1 - \lambda)} \end{equation}",
    "4.8": r"\begin{equation}\label{eq:4_8} \tilde{S}_k = \prod_j (1 - w \lambda_j) \approx (S_k)^w, \quad \text{so} \quad \tilde{F}_k \approx 1 - (1 - F_k)^w \end{equation}",
    "4.9": r"\begin{equation}\label{eq:4_9} R_d(\lambda) = \frac{|\{ t \in d : y_t = 1 \text{ and } \hat{p}_t < \lambda \}|}{\max(|\{ t \in d : y_t = 1 \}|, 1)} \end{equation}",
    "4.10": r"\begin{equation}\label{eq:4_10} \hat{\lambda} = \sup \left\{ \lambda \in [0, 1] : \frac{n \hat{R}(\lambda) + B}{n + 1} \le \alpha \right\} \end{equation}",
    "4.11": r"\begin{equation}\label{eq:4_11} R_d^{\text{ev}}(\lambda) = \frac{|\{ \tau \in E_d : \max_{t \in [\tau-h, \tau)} \hat{p}_t < \lambda \}|}{|E_d|} \end{equation}",
    "4.12": r"\begin{equation}\label{eq:4_12} \alpha \ge \frac{1}{n+1} \iff n \ge \frac{1}{\alpha} - 1 \end{equation}",
    "4.13": r"\begin{equation}\label{eq:4_13} \mu(t) = \mu_0 + \sum_{t_i < t} \alpha \cdot \exp( -\beta ( t - t_i ) ) \end{equation}",
    "5.1": r"\begin{equation}\label{eq:5_1} m = 1 - \delta - x, \quad \text{with } \delta, x \text{ and } m \text{ all in seconds} \end{equation}",
}

def clean_text(text, is_table=False):
    if not text:
        return ""
    for pat, rep in DATE_SUBS:
        text = pat.sub(rep, text)
    for u, l in UNICODE_MAP.items():
        text = text.replace(u, l)
    text = text.replace('\u0303', '')  # strip combining tilde
    text = text.replace('\u0302', '')  # strip combining hat
    text = text.replace('±', r'$\pm$').replace('²', r'$^2$').replace('³', r'$^3$')
    text = text.replace('“', "``").replace('”', "''").replace('’', "'").replace('‘', "`")
    text = text.replace('#', r'\#')
    
    text = re.sub(r'(?<!\\)%', r'\%', text)
    text = re.sub(r'(?<!\\)&', r'\&', text)
    text = re.sub(r'(?<!\\)_', r'\_', text)
    
    text = re.sub(r'\$\\lambda\$\s*̃', r'$\\tilde{\\lambda}$', text)
    text = re.sub(r'\\lambdã', r'$\\tilde{\\lambda}$', text)
    text = re.sub(r'\$\\tilde\{\\lambda\}\$\\_k', r'$\\tilde{\\lambda}_k$', text)
    text = re.sub(r'\$\\lambda\$\\_k', r'$\\lambda_k$', text)
    text = re.sub(r'\bF\\_k\b', r'$F_k$', text)
    text = re.sub(r'\bS\\_k\b', r'$S_k$', text)
    text = re.sub(r'\(1\+\$\\epsilon\$\)\^k', r'$(1+\\epsilon)^k$', text)
    text = re.sub(r'\$\(1\+\\epsilon\)\$\^k', r'$(1+\\epsilon)^k$', text)
    text = re.sub(r'\$\(1\+\\epsilon\)\$\^k\$\$', r'$(1+\\epsilon)^k$', text)
    
    def sub_cite(match):
        inner = match.group(1).strip()
        range_match = re.match(r'^(\d+)\s*(?:-|--)\s*(\d+)$', inner)
        if range_match:
            s, e = int(range_match.group(1)), int(range_match.group(2))
            if 1 <= s <= 47 and 1 <= e <= 47 and s < e:
                return r'\cite{' + ', '.join(f'ref{i}' for i in range(s, e + 1)) + '}'
        parts = [p.strip() for p in inner.split(',')]
        if all(p.isdigit() and 1 <= int(p) <= 47 for p in parts):
            return r'\cite{' + ', '.join(f'ref{p}' for p in parts) + '}'
        return match.group(0)
    text = re.sub(r'\[([0-9\s,\-]+)\]', sub_cite, text)
    return text

def format_latex_figure(fig_num, fig_file, width, caption):
    label = f"fig:{fig_num.replace('.', '_')}"
    return (
        f"\n\\begin{{figure}}[htbp]\n"
        f"\\centering\n"
        f"\\includegraphics[width={width}]{{{fig_file}}}\n"
        f"\\caption{{{clean_text(caption)}}}\n"
        f"\\label{{{label}}}\n"
        f"\\end{{figure}}\n\n"
    )

def format_latex_table(tbl_idx, tbl, tab_num, caption):
    num_cols = len(tbl.columns)
    label = f"tab:{tab_num.replace('.', '_')}"
    cleaned_caption = clean_text(caption)
    
    hdr_cells = [clean_text(c.text, is_table=True).strip() for c in tbl.rows[0].cells]
    hdr_line = " & ".join(f"\\textbf{{{c}}}" for c in hdr_cells) + " \\\\\n\\midrule"
    
    row_lines = []
    for r in tbl.rows[1:]:
        cells = [clean_text(c.text, is_table=True).strip() for c in r.cells]
        row_lines.append(" & ".join(cells) + " \\\\")
    body = "\n".join(row_lines)
    
    if num_cols == 2:
        if tab_num == "6.3":
            col_spec = r"l X"
        else:
            col_spec = r"p{4.0cm} X"
        return (
            f"\n\\begin{{table}}[htbp]\n\\centering\n\\caption{{{cleaned_caption}}}\n\\label{{{label}}}\n"
            f"\\vspace{{0.4em}}\n\\singlespacing\n\\small\n"
            f"\\begin{{tabularx}}{{\\linewidth}}{{{col_spec}}}\n\\toprule\n{hdr_line}\n{body}\n\\bottomrule\n\\end{{tabularx}}\n\\end{{table}}\n\n"
        )
    elif num_cols == 3:
        if tab_num == "2.1":
            col_spec = r"p{5.0cm} c X"
        elif tab_num == "6.6":
            col_spec = r">{\raggedright\arraybackslash}p{4.4cm} X r"
        elif tab_num == "5.13":
            col_spec = r"X c c"
        else:
            col_spec = r"X c c"
        return (
            f"\n\\begin{{table}}[htbp]\n\\centering\n\\caption{{{cleaned_caption}}}\n\\label{{{label}}}\n"
            f"\\vspace{{0.4em}}\n\\singlespacing\n\\small\n"
            f"\\begin{{tabularx}}{{\\linewidth}}{{{col_spec}}}\n\\toprule\n{hdr_line}\n{body}\n\\bottomrule\n\\end{{tabularx}}\n\\end{{table}}\n\n"
        )
    elif num_cols == 4:
        if tab_num == "A.3":
            col_spec = r"p{2.8cm} X X X"
        elif tab_num == "A.5":
            col_spec = r"p{3.5cm} p{2.8cm} c X"
        elif tab_num == "4.3":
            col_spec = r"l c p{3.8cm} X"
        elif tab_num == "5.10":
            col_spec = r"p{3.5cm} X c p{3.5cm}"
        elif tab_num == "5.14":
            col_spec = r"p{5.5cm} c c c"
        elif tab_num == "6.2":
            col_spec = r"l >{\raggedright\arraybackslash}p{4.2cm} c X"
        elif tab_num == "6.4":
            col_spec = r"l >{\raggedright\arraybackslash}p{4.2cm} c X"
        elif tab_num == "6.5":
            col_spec = r"l >{\raggedright\arraybackslash}p{4.0cm} c X"
        else:
            col_spec = r"l X c c"
        return (
            f"\n\\begin{{table}}[htbp]\n\\centering\n\\caption{{{cleaned_caption}}}\n\\label{{{label}}}\n"
            f"\\vspace{{0.4em}}\n\\singlespacing\n\\small\n"
            f"\\begin{{tabularx}}{{\\linewidth}}{{{col_spec}}}\n\\toprule\n{hdr_line}\n{body}\n\\bottomrule\n\\end{{tabularx}}\n\\end{{table}}\n\n"
        )
    else:
        col_spec = "l " + " ".join(["c"] * (num_cols - 1))
        return (
            f"\n\\begin{{table}}[htbp]\n\\centering\n\\caption{{{cleaned_caption}}}\n\\label{{{label}}}\n"
            f"\\vspace{{0.4em}}\n\\singlespacing\n\\footnotesize\n"
            f"\\resizebox{{\\linewidth}}{{!}}{{%\n"
            f"\\begin{{tabular}}{{{col_spec}}}\n\\toprule\n{hdr_line}\n{body}\n\\bottomrule\n\\end{{tabular}}%\n"
            f"}}\n\\end{{table}}\n\n"
        )

CHAPTER_START = {
    223: ("chapters/ch1_introduction.tex", r"\chapter{Introduction}\label{ch:1}"),
    270: ("chapters/ch2_literature_review.tex", r"\chapter{Literature Review and Methodology}\label{ch:2}"),
    337: ("chapters/ch3_measurement_corpus.tex", r"\chapter{Measurement Campaign and Ground Truth}\label{ch:3}"),
    388: ("chapters/ch4_predictive_formulation.tex", r"\chapter{Predictive Formulation and System Design}\label{ch:4}"),
    490: ("chapters/ch5_results_and_analysis.tex", r"\chapter{Results and Discussion}\label{ch:5}"),
    672: ("chapters/ch6_demonstrative_case_studies.tex", r"\chapter{Demonstration of Outcome Based Education}\label{ch:6}"),
    718: ("chapters/ch7_conclusions.tex", r"\chapter{Conclusions}\label{ch:7}"),
    792: ("appendices/appendix_a.tex", r"\chapter{Full Per-Horizon Results}\label{app:A}"),
    806: ("appendices/appendix_b.tex", r"\chapter{Feature Inventory}\label{app:B}"),
    816: ("appendices/appendix_c.tex", r"\chapter{Reproduction Notes}\label{app:C}"),
    823: ("appendices/appendix_d.tex", r"\chapter{The 22 Audited Models}\label{app:D}"),
}

body = doc._element.body
p_idx = 0
tbl_idx = 0

current_target = None
chapter_buffers = {v[0]: [v[1] + "\n\n"] for v in CHAPTER_START.values()}

for child in body:
    if child.tag.endswith('p'):
        if p_idx in CHAPTER_START:
            current_target = CHAPTER_START[p_idx][0]
            p_idx += 1
            continue
        elif p_idx in [742, 827]:
            current_target = None
            
        p = doc.paragraphs[p_idx]
        txt = p.text.strip()
        
        if current_target is not None:
            buf = chapter_buffers[current_target]
            
            # 1. Figure check
            if p_idx in FIGURE_MAP:
                fig_num, fig_file, width, caption = FIGURE_MAP[p_idx]
                buf.append(format_latex_figure(fig_num, fig_file, width, caption))
                if txt.startswith(f"Figure {fig_num}") or not txt:
                    p_idx += 1
                    continue
            
            # 2. Section heading check
            sec_m = re.match(r'^(\d+\.\d+(?:\.\d+)?)\s+(.*)', txt)
            if sec_m:
                sec_num = sec_m.group(1)
                sec_title = clean_text(sec_m.group(2).strip())
                label = f"sec:{sec_num.replace('.', '_')}"
                if sec_num.count('.') == 1:
                    buf.append(f"\n\\section{{{sec_title}}}\n\\label{{{label}}}\n\n")
                else:
                    buf.append(f"\n\\subsection{{{sec_title}}}\n\\label{{{label}}}\n\n")
                p_idx += 1
                continue
            
            # 3. Equation check (matches any line ending in equation number (X.Y))
            eq_m = re.search(r'\((\d+\.\d+)\)\s*$', txt)
            if eq_m and eq_m.group(1) in EQUATION_MAP:
                buf.append(f"\n{EQUATION_MAP[eq_m.group(1)]}\n\n")
                p_idx += 1
                continue
                    
            # 4. Table / Figure caption line skip
            if re.match(r'^(?:Table|Figure)\s+\d+\.\d+', txt) or re.match(r'^Table\s+[A-D]\.\d+', txt):
                p_idx += 1
                continue
                
            # 5. Normal text
            if txt:
                cleaned = clean_text(txt)
                buf.append(f"{cleaned}\n\n")
                
        p_idx += 1
        
    elif child.tag.endswith('tbl'):
        if tbl_idx in TABLE_MAP and current_target is not None:
            tab_num, tab_caption = TABLE_MAP[tbl_idx]
            tbl = doc.tables[tbl_idx]
            chapter_buffers[current_target].append(format_latex_table(tbl_idx, tbl, tab_num, tab_caption))
        tbl_idx += 1

print(f"Extraction finished. Emitting {len(chapter_buffers)} files...")
for rel_path, chunks in chapter_buffers.items():
    out_file = os.path.join(LATEX_DIR, rel_path)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as fp:
        fp.write("".join(chunks))
    print(f"Wrote {rel_path} ({len(chunks)} chunks)")

print("All chapters and appendices written successfully!")
