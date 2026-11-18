# SupeRR Selector Season 2 – Round 1: Identifying the Most Reliable Players Under Pressure in T20 Cricket (2022 Onwards)

**Author:** Kishalay Das  
**Submission:** SupeRR Selector Season 2 – Round 1 Submission  
**Dataset:** Historical IPL and T20 International (T20I) ball-by-ball records (2022 onwards, 883 matches, 200,999 deliveries)  
**Scope:** Ordered Top 10 Batters and Top 10 Bowlers Under Pressure  
**Key Document Links:**  
- [methodology_report.pdf](file:///e:/E%20Drive/College/projects/rajsthanroyals/report/methodology_report.pdf) (Strictly 3-page publication PDF)  
- [final_top10_batters.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/final_top10_batters.csv)  
- [final_top10_bowlers.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/final_top10_bowlers.csv)  
- [shrinkage_verification_table.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/shrinkage_verification_table.csv)  
- [top20_bowlers_wicket_specs.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/top20_bowlers_wicket_specs.csv)  
- [top10_sensitivity_matrix.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/top10_sensitivity_matrix.csv)  
- [excluded_pakistan_players.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/excluded_pakistan_players.csv)  

---

## Executive Summary

Evaluating clutch performance in T20 cricket requires disentangling genuine repeatable skill from extreme small-sample noise. Conventional cricket heuristics—such as designating overs 16–20 in chases as "pressure"—conflate match phase with match stakes. A death over in a 60-run blowout carries negligible leverage, while a top-order collapse of 20/3 in the powerplay of a knockout match carries match-defining gravity.

This report presents a complete, sabermetric-grade hierarchical Bayesian framework that evaluates player impact under pressure:
1. **Mathematical Outcome Leverage (Zero Subjective Multipliers):** Pressure is defined strictly as the expected absolute win-probability swing across all 7 mutually exclusive delivery outcomes, weighted by phase-specific empirical transition probabilities. The top quartile ($\ge 75\text{th percentile}$) defines **High Pressure** (50,241 deliveries).
2. **Context-Aware Expected Value Baselines with Exact Recentering:** Using 5-fold grouped cross-validation by match, player-agnostic LightGBM models estimate Expected Runs ($xR$, RMSE 1.71) and Expected Wickets ($xW$, AUC 0.595). Out-of-fold predictions were recentred by subtracting residual means so that the league-wide residual mean across all 200,999 deliveries is identically zero ($1.7 \times 10^{-17}$ runs/ball, $-1.3 \times 10^{-18}$ outs/ball). The expected-wicket model achieves an AUC of 0.595, reflecting that dismissals carry substantial single-delivery stochastic noise.
3. **Phase-Specific Runs-Per-Wicket Conversion:** Marginal rates of substitution derived directly from win-probability utility establish phase-specific wicket valuations (**Powerplay: 14.36 runs**, **Middle: 8.13 runs**, **Death: 2.92 runs**, weighted mean 8.85 runs). Recomputations on high-pressure deliveries alone yield **Powerplay: 14.40 runs**, **Middle: 10.71 runs**, **Death: 5.89 runs** (mean: 9.52 runs).
4. **Hierarchical Model Formulation:** Each player's pressure performance is decomposed into an **Ordinary Baseline Impact** ($B_i$) plus a **Pressure Effect** ($\Delta_i$):
   $$\text{Final Rating}_i = \hat{B}_i + \hat{\Delta}_i$$
   Baseline skill is shrunk toward the population baseline ($\mu_B$) using REML variance components ($K_B = 1,717.4$ bat, $1,312.9$ bowl), and the pressure effect is shrunk toward the population mean effect ($\mu_\Delta$) using $K_\Delta = 773.0$ bat, $1,041.4$ bowl. Typical sample weights are **24.8%** for batters and **19.1%** for bowlers. K values were estimated on the full cohort, while population means and ratings use the filtered (non-Pakistan) cohort; the filtered-cohort K values are shown in Table 4.1.
5. **Eligibility Rules & Author's Eligibility Choice:** Eligibility filters ($\ge 100$ HP balls, $\ge 6$ HP matches, $\ge 10$ total career matches) identify **131 eligible batters** and **140 eligible bowlers**. Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. A dedicated audit table transparently documents the 4 excluded Pakistan players who would have ranked in the unconstrained top 20.
6. **Explicit Ordering Rule & Pressure Elevation Findings:** Primary selections are strictly ranked in descending order of their total hierarchical posterior mean impact rating ($\hat{B}_i + \hat{\Delta}_i$). 90% credible intervals indicate that six top-10 players—**Suryakumar Yadav, Reeza Hendricks, Rinku Singh, Shreyas Iyer, Matheesha Pathirana, and Mitchell Santner**—possess clutch pressure elevation ($\hat{\Delta}_i$) strictly above zero at the 90% credibility level, while all other players remain statistically indistinguishable from zero or exhibit pressure dips.
7. **Within-Match Null Permutation Test (1,000 Draws):** Permuting pressure labels within matches establishes that bowling displays statistically distinguishable pressure separation ($p = 0.0300$ filtered cohort, $0.0060$ full cohort), whereas evidence for genuine clutch elevation in batting is borderline ($p = 0.0440$ filtered cohort, $0.0500$ full cohort), indicating that single-match batting variance is high and clutch differences are harder to distinguish from chance.
8. **Uncertainty & Dual Rankings via a Single Bootstrap Run:** A single 1,000 match-grouped bootstrap run (fixed seed 42) re-estimates priors in each draw, providing identical 90% credible intervals for ratings, deltas, and $P(\text{top 10})$ across all tables, charts, and text.

---

### Final Top 10 Selections

#### Final Top 10 Batters Under Pressure (Primary Ranking: No Dip Exclusion)
*Ranked by Posterior Mean Shrunk Rating: Net Runs Added Above Expected per 100 Balls ($\text{Rating} = \hat{B}_i + \hat{\Delta}_i$)*

| Rank | Player Name | Primary Team(s) | HP Balls | Significant Innings (Pos) | HP SR | HP Avg | Shrunk Rating | 90% Credible Interval | Shrunk Baseline ($\hat{B}_i$) | Shrunk Delta ($\hat{\Delta}_i$) | Delta 90% CI | Delta Label | Raw Succ % | Shrunk Succ % | P(Top 10) |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Suryakumar Yadav** | India, Mumbai Indians | 697 | 40 (29) | 167.9 | 43.3 | **+28.39** | [+18.16, +36.22] | +19.39 | +8.99 | [+0.4, +17.1] | **rises** | 72.5% | 69.4% | 90.3% |
| **2** | **Vaibhav Sooryavanshi** | Rajasthan Royals, India | 168 | 14 (10) | 222.6 | 41.6 | **+23.89** | [+12.07, +33.34] | +22.18 | +1.71 | [-8.5, +11.3] | **neutral** | 71.4% | 65.3% | 63.2% |
| **3** | **Jos Buttler** | Rajasthan Royals, England, GT | 557 | 27 (19) | 164.6 | 48.2 | **+23.06** | [+12.10, +31.27] | +14.37 | +8.68 | [-1.5, +17.0] | **neutral** | 70.4% | 66.7% | 62.5% |
| **4** | **Heinrich Klaasen** | South Africa, SRH | 261 | 18 (15) | 181.2 | 36.4 | **+22.73** | [+13.14, +29.45] | +16.72 | +6.01 | [-2.9, +13.6] | **neutral** | 83.3% | 74.2% | 58.3% |
| **5** | **Reeza Hendricks** | South Africa | 224 | 14 (11) | 170.1 | 76.2 | **+22.64** | [+13.21, +28.09] | +8.33 | +14.31 | [+5.5, +22.5] | **rises** | 78.6% | 69.7% | 57.1% |
| **6** | **Abhishek Sharma** | Sunrisers Hyderabad, India | 494 | 36 (22) | 195.1 | 29.2 | **+21.93** | [+6.31, +35.02] | +24.17 | -2.25 | [-17.6, +11.4] | **neutral** | 61.1% | 60.0% | 53.6% |
| **7** | **Phil Salt** | England, DC, KKR, RCB | 397 | 25 (16) | 169.3 | 44.8 | **+21.69** | [+9.01, +30.90] | +15.90 | +5.79 | [-6.1, +16.9] | **neutral** | 64.0% | 61.8% | 49.5% |
| **8** | **Rinku Singh** | Kolkata Knight Riders, India | 294 | 16 (15) | 164.3 | 60.4 | **+20.98** | [+12.19, +26.66] | +8.92 | +12.06 | [+3.7, +18.7] | **rises** | 93.8% | 80.1% | 44.9% |
| **9** | **Shreyas Iyer** | India, KKR, PBKS | 448 | 25 (19) | 158.5 | 54.6 | **+19.97** | [+9.87, +26.82] | +9.64 | +10.33 | [+0.5, +19.8] | **rises** | 76.0% | 70.7% | 36.5% |
| **10** | **Tim David** | Mumbai Indians, Australia, RCB | 376 | 29 (20) | 178.5 | 30.5 | **+19.75** | [+9.47, +27.74] | +18.95 | +0.80 | [-8.6, +9.8] | **neutral** | 69.0% | 65.8% | 35.1% |

#### Final Top 10 Bowlers Under Pressure (Primary Ranking: No Dip Exclusion)
*Ranked by Posterior Mean Shrunk Rating: Net Runs Saved Above Expected per 100 Balls ($\text{Rating} = \hat{B}_i + \hat{\Delta}_i$)*

| Rank | Player Name | Primary Team(s) | HP Balls | Significant Spells (Pos) | HP Econ | HP SR | Shrunk Rating | 90% Credible Interval | Shrunk Baseline ($\hat{B}_i$) | Shrunk Delta ($\hat{\Delta}_i$) | Delta 90% CI | Delta Label | Raw Succ % | Shrunk Succ % | P(Top 10) |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Josh Hazlewood** | Australia, RCB | 399 | 26 (14) | 7.67 | 11.7 | **+17.83** | [+7.36, +27.86] | +9.13 | +8.70 | [-0.8, +17.9] | **neutral** | 53.8% | 53.5% | 73.5% |
| **2** | **Matheesha Pathirana** | CSK, Sri Lanka, KKR | 282 | 20 (14) | 7.43 | 10.8 | **+17.48** | [+10.12, +24.09] | +9.82 | +7.66 | [+0.7, +14.2] | **rises** | 70.0% | 64.9% | 82.7% |
| **3** | **Sunil Narine** | Kolkata Knight Riders | 468 | 27 (15) | 6.82 | 18.7 | **+14.39** | [+7.24, +21.49] | +9.07 | +5.32 | [-1.4, +11.9] | **neutral** | 55.6% | 54.8% | 56.8% |
| **4** | **Jasprit Bumrah** | Mumbai Indians, India | 439 | 34 (17) | 7.61 | 31.4 | **+13.48** | [+5.04, +22.47] | +18.59 | -5.11 | [-13.7, +4.0] | **neutral** | 50.0% | 50.4% | 51.3% |
| **5** | **Jacob Duffy** | New Zealand, RCB | 191 | 16 (8) | 8.58 | 11.9 | **+13.10** | [+2.44, +23.08] | +8.83 | +4.26 | [-5.2, +14.2] | **neutral** | 50.0% | 50.7% | 47.1% |
| **6** | **Rashid Khan** | Gujarat Titans, Afghanistan | 658 | 43 (27) | 6.72 | 15.7 | **+12.97** | [+5.49, +20.54] | +5.70 | +7.27 | [-0.4, +14.9] | **neutral** | 62.8% | 61.1% | 44.7% |
| **7** | **Lockie Ferguson** | GT, NZ, RCB, PBKS | 270 | 18 (10) | 7.47 | 15.9 | **+12.83** | [+2.43, +22.99] | +4.30 | +8.53 | [-1.1, +18.6] | **neutral** | 55.6% | 54.5% | 43.1% |
| **8** | **Varun Chakravarthy** | Kolkata Knight Riders, India | 608 | 42 (25) | 7.69 | 16.9 | **+12.29** | [+4.65, +19.64] | +12.03 | +0.26 | [-7.9, +8.1] | **neutral** | 59.5% | 58.3% | 39.1% |
| **9** | **Nathan Ellis** | Punjab Kings, Australia, CSK | 268 | 15 (10) | 8.10 | 17.9 | **+12.26** | [+5.14, +18.54] | +10.36 | +1.90 | [-7.0, +9.7] | **neutral** | 66.7% | 61.6% | 33.9% |
| **10** | **Mitchell Santner** | CSK, New Zealand, MI | 465 | 36 (22) | 7.06 | 17.2 | **+12.18** | [+5.22, +19.26] | +4.16 | +8.02 | [+0.3, +15.8] | **rises** | 61.1% | 59.5% | 39.7% |

*Interpretation of Delta Label:*
- **"rises":** 90% credible interval on $\hat{\Delta}_i$ strictly $> 0$ (statistically verifiable elevation under pressure: **Suryakumar, Hendricks, Rinku, Iyer, Pathirana, Santner**).
- **"neutral":** 90% credible interval spans 0 (performance under pressure is resilient and indistinguishable from ordinary baseline).
- **"dips":** 90% credible interval strictly $< 0$ (statistically verifiable regression under pressure).

---

## 1. Pressure Definition, Consistency Metrics & Calibration Auditing

### 1.1 True Mathematical Outcome Leverage
Rather than relying on arbitrary over cutoffs or subjective multipliers, leverage is formulated strictly as the expected absolute win-probability swing across all 7 mutually exclusive delivery outcomes, weighted by phase-specific transition probabilities:

$$\text{Leverage}_t = \sum_{o \in \mathcal{O}} P(o \mid \text{phase}) \cdot \left| WP(S_{t+1}(o)) - WP(S_t) \right|$$

Where $\mathcal{O} = \{\text{dot (0)}, \text{1 run}, \text{2 runs}, \text{3 runs}, \text{4 runs}, \text{6 runs}, \text{wicket}\}$.

Empirical transition probabilities $P(o \mid \text{phase})$ computed across 200,999 deliveries:
- **Powerplay (Overs 1–6):** Dot: $0.442$, 1s: $0.252$, 2s: $0.046$, 3s: $0.005$, 4s: $0.155$, 6s: $0.054$, Wicket: $0.045$.
- **Middle Overs (Overs 7–15):** Dot: $0.301$, 1s: $0.436$, 2s: $0.065$, 3s: $0.002$, 4s: $0.090$, 6s: $0.059$, Wicket: $0.047$.
- **Death Overs (Overs 16–20):** Dot: $0.283$, 1s: $0.350$, 2s: $0.081$, 3s: $0.003$, 4s: $0.113$, 6s: $0.088$, Wicket: $0.081$.

Two separate LightGBM models (GroupKFold by match) predict win probability:
- **Innings 1:** Log-loss: **0.6568** | Brier score: **0.2303**.
- **Innings 2:** Log-loss: **0.4770** | Brier score: **0.1555**.

Deliveries in the top quartile ($\ge 75\text{th percentile}$, 50,241 balls) define **High Pressure**.

![Win Probability Calibration](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/win_probability_calibration.png)

### 1.2 Non-Circular Domain Validation
To ensure that High Pressure identifies genuine match tension without circular reasoning, we tested delivery-level player behavioral shifts between High Pressure and Ordinary deliveries across independent physical dimensions:
1. **Strike Rotation Rate:** Batters significantly increase singles and twos running from 41.85% to 43.24% (+1.39 pp, Cohen's $d = 0.028$, $p < 10^{-10}$).
2. **Dot Ball Reduction:** Dot % drops from 35.59% to 34.42% (-1.17 pp, Cohen's $d = -0.024$, $p < 10^{-10}$).
3. **Runs Per Ball Variance:** Outcome variance narrows from 3.037 to 2.974 (-0.064 variance, Levene test $p = 0.0038$), demonstrating controlled defensive risk suppression under pressure.
4. **Desperation Dismissals (Run-Outs & Stumpings):** Risky dismissals rise from 7.22% to 8.22% (+1.00 pp, Cohen's $d = 0.038$), but $p = 0.0951$ (reported honestly as **Not Statistically Significant** at $\alpha = 0.05$).
5. **Scoring Rates:** Overall run rate is virtually unchanged: 8.52 vs 8.53 runs/over ($p = 0.799$); boundary % is 18.01% vs 17.81% ($p = 0.325$). Differences are negligible.
6. **Win-Probability Volatility (Definitional):** The average absolute swing per ball surges +126% from 1.59% to 3.60% (+2.00 pp/ball, Cohen's $d = 0.528$, $p < 10^{-10}$).

### 1.3 Consistency Metrics & Innings Count Reconciliation
Consistency is evaluated across matches using two complementary metrics:
1. **Raw Success %:**
   $$\text{Raw Succ\%} = \frac{\text{Positive Significant Innings}}{\text{Total Significant Pressure Innings}} \times 100$$
2. **Beta-Binomial Shrunk Success %:**
   $$\text{Shrunk Succ\%} = \frac{\text{Positive Significant Innings} + \alpha_0}{\text{Total Significant Pressure Innings} + \alpha_0 + \beta_0} \times 100$$
   where for batters: $\alpha_0 = 4.97, \beta_0 = 3.95$ (prior mean = $55.7\%$). For bowlers: $\alpha_0 = 4.22, \beta_0 = 3.86$ (prior mean = $52.2\%$).

**Significant Innings Filter Rationale:**
- In our primary pipeline, a **significant pressure innings** requires facing at least **5 High-Pressure deliveries** in that match (`min_match_balls = 5`). This filter prevents 1- or 2-ball cameos from skewing match-level consistency standard deviations. Under this threshold, Suryakumar Yadav faced significant pressure in **40 innings** (29 positive, 72.5% raw, 69.4% shrunk), and Jos Buttler in **27 innings** (19 positive, 70.4% raw, 66.7% shrunk).
- Counting every match where they faced even a single high-pressure delivery ($\ge 1$ ball), Suryakumar appeared in 86 matches and Buttler in 82 matches.

### 1.4 Calibration Auditing, Deciles & Recentering
To guarantee that baseline expected-value models are unbiased, we audited the out-of-fold residuals across all deliveries and recentered them by subtracting residual means so the out-of-fold average residual is 0.000000. 

#### Decile-by-Decile Calibration Audit (Out-of-Fold Test Deliveries)

| Decile | Predicted Runs ($xR$) | Actual Runs Off Bat | Run Diff | Predicted Out Prob ($xW$) | Actual Out Rate | Out Diff |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | 0.919 | 0.933 | +0.0132 | 3.35% | 3.68% | +0.33% |
| **2** | 1.065 | 1.095 | +0.0292 | 3.81% | 3.81% | -0.01% |
| **3** | 1.156 | 1.180 | +0.0242 | 4.09% | 4.38% | +0.29% |
| **4** | 1.234 | 1.286 | +0.0518 | 4.35% | 4.61% | +0.26% |
| **5** | 1.302 | 1.329 | +0.0277 | 4.61% | 4.65% | +0.04% |
| **6** | 1.364 | 1.431 | +0.0670 | 4.93% | 5.10% | +0.17% |
| **7** | 1.432 | 1.510 | +0.0772 | 5.32% | 5.51% | +0.19% |
| **8** | 1.509 | 1.590 | +0.0814 | 5.88% | 6.02% | +0.14% |
| **9** | 1.603 | 1.691 | +0.0885 | 7.04% | 7.46% | +0.42% |
| **10** | 1.816 | 1.901 | +0.0847 | 10.95% | 10.81% | -0.14% |

![Expected Value Calibration](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/expected_value_calibration_deciles_phases.png)

| Metric | League Mean (All 200,999 Deliveries) | Eligible Players Mean ($\ge 100$ HP Balls) | Eligible per 100 Balls |
|:---|:---:|:---:|:---:|
| **Batter Runs Above Expected ($RAE$)** | **$0.000000$** | **$+0.0351$ runs/ball** | **$+3.51$ runs / 100 balls** |
| **Batter Outs Above Expected ($OAE$)** | **$0.000000$** | **$-0.0038$ outs/ball** | **$-0.38$ outs / 100 balls** |
| **Bowler Runs Saved vs Expected ($RSE$)** | **$0.000000$** | **$+0.0157$ runs/ball** | **$+1.57$ runs / 100 balls** |
| **Bowler Wickets Above Expected ($WAE$)** | **$0.000000$** | **$+0.0004$ wkts/ball** | **$+0.04$ wkts / 100 balls** |

*Methodological Note:* The zero residual means are the result of explicit recentering. Non-Pakistan regulars hold positive baseline means because lower-order batters absorb negative residuals. Expected wicket models carry an AUC of 0.595, reflecting that dismissals are high-variance events in cricket that introduce substantial stochastic noise into single-match metrics.

---

## 2. Fair Comparisons, Eligibility Rules & Opposition Quality Audit

### 2.1 Eligibility Criteria and Cohort Counts
To prevent sample-size distortions while maintaining an expansive talent pool, we apply three strict, objective eligibility filters:
1. **$\ge 100$ High-Pressure Deliveries** (balls faced for batters excluding wides; legal deliveries bowled for bowlers).
2. **$\ge 6$ High-Pressure Matches** (ensuring exposure across multiple independent game contexts).
3. **$\ge 10$ Total Career Matches** (ensuring a stable ordinary baseline sample).

**Pakistan Player Exclusion:** Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement.

Across 883 matches and 200,999 deliveries, exactly **131 batters** and **140 bowlers** satisfy all criteria (8 batters and 8 bowlers excluded under this authorial choice).

### 2.2 Pooling IPL and T20 International Data
The dataset contains both Indian Premier League matches and men's T20 Internationals from January 2022 onwards. Rather than treating them as disjoint competitions, they are pooled within a unified context-aware model:
- **Grouped Cross-Validation by Match:** Prevents data leakage between deliveries in the same match.
- **Match-State Conditioning:** Context features (balls remaining, runs required, current run rate, phase, wickets down) dynamically calibrate expectations regardless of competition.
- **Competition-Level Normalization:** A binary `is_ipl` indicator captures structural differences in tournament run environments (e.g. flat Indian batting surfaces and Impact Player additions) versus lower-scoring international venues.

### 2.3 Definition of "Tier 1" Competition Scope
In our sensitivity suite, we evaluate a **Tier 1 Only** restriction:
- **Included as Tier 1:** All Indian Premier League (IPL) matches and all men's T20 Internationals contested between ICC Full Member nations.
- **Excluded in Tier 1:** Matches involving ICC Associate Member teams and secondary development tours (e.g. A-team fixtures in emerging cups).

### 2.4 Opposition Quality Estimation & Table 2.1 Reconciled Audit
To verify that top-ranked players did not achieve inflated ratings against weak opposition, we compute an **Opposition Quality Differential** for each player:
- For batters, opponent quality is the weighted average baseline Runs Saved ($RSE$) of the bowlers faced on high-pressure balls.
- For bowlers, opponent quality is the weighted average baseline Runs Above Expected ($RAE$) of the batters faced.

#### Opposition Quality Diagnostics:
- **Batters:** HP Opponent Strength has Mean = **+0.46 runs/100b**, SD = **1.89 runs/100b**; Ordinary Opponent Strength has Mean = **-0.16 runs/100b**, SD = **1.70 runs/100b**.
- **Bowlers:** HP Opponent Strength has Mean = **+6.07 runs/100b**, SD = **3.79 runs/100b**; Ordinary Opponent Strength has Mean = **+5.82 runs/100b**, SD = **3.18 runs/100b**.
- **Baseline Opposition Handling:** Baseline impact ($\text{Raw}_B$) is unadjusted; while batter ordinary opposition averages near zero ($-0.16$ runs/100b), bowler ordinary-opposition mean is $+5.82$ runs/100b. Consequently, bowler pressure effects are shifted up by a similar amount for everyone, and rankings are largely unaffected (demonstrated by the 8 of 10 bowler overlap without opposition adjustment and 9/10 overlap under symmetric recentering). High-pressure deliveries specifically encounter death-overs specialists and top-order batters (+6.07 runs/100b).
- **Stability With vs Without Opposition Adjustment:**
  - Batters: Top-10 Jaccard overlap = **1.0000** (10/10 identical; no player drops out).
  - Bowlers: Top-10 Jaccard overlap without opp = **0.6667** (8 of 10 bowlers retained, 8/10 overlap; Pathirana #1 11.43 vs Hazlewood #2 11.40 separated by 0.03 runs; Varun Chakravarthy drops #8 to #13, Mitchell Santner drops #10 to #12; Wanindu Hasaranga enters at #9 and Kuldeep Yadav enters at #10).
  - Under symmetric recentered opp: Overlap is **0.9000** (9/10 overlap; Hazlewood #1 12.10, Pathirana #2 11.40; Nathan Ellis drops to #12 and Jofra Archer enters at #10).

#### Table 2.1: Opposition Quality Audit & Mathematical Reconciliation (All 20 Selections)
*Mathematical Identity: For every player, $Raw_B + Raw_D \equiv Adj\_HP$ identically ($0.0000$ difference), and $Raw\_HP + Opp \equiv Adj\_HP$ identically.*

| Rk | Role | Player Name | Raw Baseline ($Raw_B$) | Raw Delta ($Raw_D$) | Opp Quality Diff ($Opp$) | Total HP Impact ($Adj\_HP$) | Raw HP ($Raw_{HP}$) | Primary Team(s) | Schedule Audit Finding |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---|:---|
| **1** | Bat | **Suryakumar Yadav** | +29.69 | +15.01 | -0.43 | **+44.70** | +45.13 | MI, India | Normal: Frontline international & IPL attacks. |
| **2** | Bat | **Vaibhav Sooryavanshi** | +73.40 | -6.83 | +0.82 | **+66.57** | +65.75 | RR, India | Normal: High baseline scoring against tournament attacks. |
| **3** | Bat | **Jos Buttler** | +19.93 | +15.78 | +0.07 | **+35.71** | +35.64 | RR, England, GT | Normal: Faces elite international and IPL bowling. |
| **4** | Bat | **Heinrich Klaasen** | +31.12 | +13.25 | +0.60 | **+44.37** | +43.77 | SRH, SA | Normal: High-caliber IPL and international spin/pace. |
| **5** | Bat | **Reeza Hendricks** | +11.98 | +51.38 | -0.44 | **+63.36** | +63.80 | South Africa | Normal: International full-member opening attacks. |
| **6** | Bat | **Abhishek Sharma** | +40.33 | -11.35 | -0.60 | **+28.98** | +29.58 | SRH, India | Normal: Elite powerplay bowling in IPL. |
| **7** | Bat | **Phil Salt** | +28.13 | +10.10 | -0.11 | **+38.23** | +38.34 | England, KKR | Normal: Top-tier international and IPL pace. |
| **8** | Bat | **Rinku Singh** | +12.21 | +34.39 | -0.09 | **+46.60** | +46.69 | KKR, India | Normal: Death-overs specialist bowling in IPL. |
| **9** | Bat | **Shreyas Iyer** | +12.80 | +22.00 | -0.44 | **+34.81** | +35.25 | India, KKR, PBKS | Normal: High-quality middle-overs spin and pace. |
| **10** | Bat | **Tim David** | +43.04 | -4.90 | +0.29 | **+38.14** | +37.85 | MI, Australia | Normal: Death-overs pace and yorkers. |
| **1** | Bowl | **Josh Hazlewood** | +17.17 | +28.42 | +7.37 | **+45.59** | +38.22 | Australia, RCB | Strong: Faced frontline international & IPL top orders. |
| **2** | Bowl | **Matheesha Pathirana** | +21.03 | +31.75 | +5.99 | **+52.78** | +46.80 | CSK, Sri Lanka | Strong: Executed death overs against elite finishers. |
| **3** | Bowl | **Sunil Narine** | +17.15 | +14.62 | +9.37 | **+31.78** | +22.40 | Kolkata Knight Riders | Elite: Highest quality opposing batting lineups in IPL. |
| **4** | Bowl | **Jasprit Bumrah** | +35.18 | -19.93 | +9.20 | **+15.25** | +6.05 | MI, India | Elite: Highest opposition caliber faced (+9.20 opp). |
| **5** | Bowl | **Jacob Duffy** | +20.90 | +21.28 | +9.01 | **+42.17** | +33.16 | New Zealand, RCB | Strong: Faced full-member international top orders. |
| **6** | Bowl | **Rashid Khan** | +7.69 | +16.97 | +3.45 | **+24.66** | +21.21 | GT, Afghanistan | Normal: IPL & international middle orders. |
| **7** | Bowl | **Lockie Ferguson** | +7.15 | +37.05 | +6.44 | **+44.20** | +37.76 | GT, NZ, RCB | Normal: High-caliber IPL and international attacks. |
| **8** | Bowl | **Varun Chakravarthy** | +20.23 | -1.24 | +9.07 | **+19.00** | +9.93 | KKR, India | Strong: High-quality opposing IPL batting orders. |
| **9** | Bowl | **Nathan Ellis** | +26.19 | +4.84 | +7.52 | **+31.03** | +23.51 | PBKS, Australia | Strong: Death overs against elite IPL finishers. |
| **10** | Bowl | **Mitchell Santner** | +5.84 | +23.43 | +7.93 | **+29.28** | +21.34 | CSK, New Zealand | Normal: Frontline IPL and international middle orders. |

### 2.5 Transparent Audit of Excluded Pakistan Players in Unconstrained Top 20 (Table 2.2)
To ensure complete methodological transparency, Table 2.2 documents the four Pakistan players who would have ranked in the unconstrained top 20:

| Discipline | Player Name | Unconstrained Rank | HP Balls | Shrunk Rating | Shrunk Baseline | Shrunk Delta | Primary Team(s) | Reason: author's eligibility choice |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|:---|
| **Batter** | Mohammad Rizwan | 15 | 400 | +17.86 | +10.57 | +7.29 | Pakistan | Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. |
| **Bowler** | Sufiyan Muqeem | 4 | 155 | +14.13 | +9.07 | +5.06 | Pakistan, Pakistan A | Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. |
| **Bowler** | Mohammad Nawaz | 16 | 289 | +11.27 | +6.13 | +5.14 | Pakistan | Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. |
| **Bowler** | Abrar Ahmed | 20 | 189 | +10.77 | +7.47 | +3.30 | Pakistan | Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. |

---

## 3. Performance Measurement & Wicket Run-Value Derivation

### 3.1 Primary Phase-Specific Runs-Per-Wicket
Evaluating the marginal rate of substitution $\frac{\mathbb{E}[|\Delta WP(\text{wkt})|]}{\mathbb{E}[|\Delta WP(\text{1 run})|]}$ across all match states yields phase-specific values:
- **Powerplay (Overs 1–6):** **14.36 runs** (Top-order dismissals severely truncate projected totals).
- **Middle Overs (Overs 7–15):** **8.13 runs** (Balance between acceleration and resource preservation).
- **Death Overs (Overs 16–20):** **2.92 runs** (Wickets have rapidly diminishing utility as balls expire).
- **Overall Weighted Mean:** **8.85 runs per wicket**.

### 3.2 Full Top 20 Bowlers Comparison Across Wicket Value Specifications
The table below presents the Top 20 bowlers evaluated under Phase-Specific (Primary), HP-Specific (PP 14.40, Mid 10.71, Death 5.89), and Flat 8.85 wicket run-values:

| Rank | Phase-Specific Player (Primary) | Phase Rating | HP-Specific Player | HP Rating | Flat 8.85 Player | Flat Rating |
|:---:|:---|:---:|:---|:---:|:---|:---:|
| **1** | **Josh Hazlewood** | **+17.83** | Josh Hazlewood | +20.13 | Matheesha Pathirana | +20.68 |
| **2** | **Matheesha Pathirana** | **+17.48** | Matheesha Pathirana | +19.97 | Josh Hazlewood | +19.08 |
| **3** | **Sunil Narine** | **+14.39** | Rashid Khan | +15.59 | Rashid Khan | +18.56 |
| **4** | **Jasprit Bumrah** | **+13.48** | Sunil Narine | +15.03 | Sunil Narine | +15.83 |
| **5** | **Jacob Duffy** | **+13.10** | Varun Chakravarthy | +14.18 | Varun Chakravarthy | +13.68 |
| **6** | **Rashid Khan** | **+12.97** | Jacob Duffy | +13.93 | Jasprit Bumrah | +13.35 |
| **7** | **Lockie Ferguson** | **+12.83** | Wanindu Hasaranga | +13.89 | Kuldeep Yadav | +13.32 |
| **8** | **Varun Chakravarthy** | **+12.29** | Kuldeep Yadav | +13.69 | Wanindu Hasaranga | +12.82 |
| **9** | **Nathan Ellis** | **+12.26** | Mitchell Santner | +13.13 | Mitchell Santner | +12.65 |
| **10** | **Mitchell Santner** | **+12.18** | Lockie Ferguson | +12.90 | Mustafizur Rahman | +11.98 |
| **11** | Kuldeep Yadav | +11.74 | Jasprit Bumrah | +12.80 | Mark Wood | +11.66 |
| **12** | Jofra Archer | +11.45 | Nathan Ellis | +12.21 | Nathan Ellis | +10.86 |
| **13** | Wanindu Hasaranga | +11.37 | Corbin Bosch | +12.17 | Corbin Bosch | +10.83 |
| **14** | Mustafizur Rahman | +11.32 | Jofra Archer | +12.07 | Mohsin Khan | +10.76 |
| **15** | Bhuvneshwar Kumar | +10.68 | Mark Wood | +12.04 | Harpreet Brar | +10.68 |
| **16** | Corbin Bosch | +10.45 | Mustafizur Rahman | +11.49 | Krunal Pandya | +10.54 |
| **17** | Mark Wood | +10.20 | Harpreet Brar | +11.19 | Jacob Duffy | +10.42 |
| **18** | Blessing Muzarabani | +9.85 | Mohsin Khan | +10.15 | Yuzvendra Chahal | +10.20 |
| **19** | Harpreet Brar | +9.59 | Krunal Pandya | +9.96 | Lockie Ferguson | +10.12 |
| **20** | Kagiso Rabada | +9.24 | Blessing Muzarabani | +9.82 | Mujeeb Ur Rahman | +10.03 |

**Wicket Sensitivity Rationale:**  
Top-10 Jaccard overlap is **0.6667** (8/10 overlap) between Phase-Specific and HP-Specific, and **0.5385** (7/10 overlap) between Phase-Specific and Flat 8.85. The bowler rankings exhibit moderate sensitivity to the wicket-run valuation rule because middle-overs spinners (e.g. Rashid, Hasaranga, Kuldeep) gain substantially when middle-overs wickets are credited at 8.85 or 10.71 runs rather than the phase-calibrated 8.13 runs; Phase-Specific valuation (PP 14.36, Mid 8.13, Death 2.92) is adopted as primary because it empirically reflects the actual subsequent innings run-penalty of losing a wicket in each respective phase.

---

## 4. Ordering Rules for Pressure Dips & Plain Finding on Vaibhav Sooryavanshi

Franchises must determine whether a player whose performance dips below their own baseline should qualify for a "best under pressure" list if their baseline is high enough to keep their net output among the league's best:
- **Rule A (Primary Ranking):** Rank strictly by posterior mean rating ($\text{Rating} = \hat{B}_i + \hat{\Delta}_i$) with **NO dip exclusion**.
- **Rule B (Clutch-Constrained Ranking):** Require $\hat{\Delta}_i \ge 0$ (player does not dip below baseline under pressure).

### 4.1 Clutch-Constrained Top 10 Tables ($\hat{\Delta}_i \ge 0$)

| Rank (Rule B) | Unconstrained Rank (Rule A) | Batter Name | Shrunk Rating | Shrunk Baseline | Shrunk Delta | Delta Label |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|
| **1** | 1 | **Suryakumar Yadav** | +28.39 | +19.39 | +8.99 | rises |
| **2** | 2 | **Vaibhav Sooryavanshi** | +23.89 | +22.18 | +1.71 | neutral |
| **3** | 3 | **Jos Buttler** | +23.06 | +14.37 | +8.68 | neutral |
| **4** | 4 | **Heinrich Klaasen** | +22.73 | +16.72 | +6.01 | neutral |
| **5** | 5 | **Reeza Hendricks** | +22.64 | +8.33 | +14.31 | rises |
| **6** | 7 | **Phil Salt** | +21.69 | +15.90 | +5.79 | neutral |
| **7** | 8 | **Rinku Singh** | +20.98 | +8.92 | +12.06 | rises |
| **8** | 9 | **Shreyas Iyer** | +19.97 | +9.64 | +10.33 | rises |
| **9** | 10 | **Tim David** | +19.75 | +18.95 | +0.80 | neutral |
| **10** | 11 | **Marcus Stoinis** | +19.64 | +16.03 | +3.61 | rises |

| Rank (Rule B) | Unconstrained Rank (Rule A) | Bowler Name | Shrunk Rating | Shrunk Baseline | Shrunk Delta | Delta Label |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|
| **1** | 1 | **Josh Hazlewood** | +17.83 | +9.13 | +8.70 | neutral |
| **2** | 2 | **Matheesha Pathirana** | +17.48 | +9.82 | +7.66 | rises |
| **3** | 3 | **Sunil Narine** | +14.39 | +9.07 | +5.32 | neutral |
| **4** | 5 | **Jacob Duffy** | +13.10 | +8.83 | +4.26 | neutral |
| **5** | 6 | **Rashid Khan** | +12.97 | +5.70 | +7.27 | neutral |
| **6** | 7 | **Lockie Ferguson** | +12.83 | +4.30 | +8.53 | neutral |
| **7** | 8 | **Varun Chakravarthy** | +12.29 | +12.03 | +0.26 | neutral |
| **8** | 9 | **Nathan Ellis** | +12.26 | +10.36 | +1.90 | neutral |
| **9** | 10 | **Mitchell Santner** | +12.18 | +4.16 | +8.02 | rises |
| **10** | 11 | **Kuldeep Yadav** | +11.74 | +7.97 | +3.77 | neutral |

### 4.2 Key Player Positions Under Both Rules
1. **Abhishek Sharma:** $\hat{B} = +24.17, \hat{\Delta} = -2.25$ (90% CI $[-17.6, +11.4]$). Under Rule A, he is **Rank 6**. Under Rule B ($\hat{\Delta} \ge 0$), he drops out and Marcus Stoinis enters at #10. However, under a *Credibly Negative* test ($\text{CI}_{\text{upper}} < 0$), Abhishek is retained because his interval spans zero.
2. **Jasprit Bumrah:** $\hat{B} = +18.59, \hat{\Delta} = -5.11$ (90% CI $[-13.7, +4.0]$). Under Rule A, he is **Rank 4**. Under Rule B ($\hat{\Delta} \ge 0$), he drops out and Kuldeep Yadav enters at #10. Under a *Credibly Negative* test, his 90% CI includes positive values up to $+4.0$, meaning his dip is not statistically distinguishable from zero.
3. **Vaibhav Sooryavanshi:** $\hat{B} = +22.18, \hat{\Delta} = +1.71$ (90% CI $[-8.5, +11.3]$). Retains **Rank 2** under both Rule A and Rule B.

### 4.3 Plain Finding on Vaibhav Sooryavanshi
A transparent, rigorous audit of Vaibhav Sooryavanshi reveals critical nuances that any scouting department must weigh:
- **Baseline Sample:** 508 ordinary-situation deliveries. Raw baseline impact: **+73.40 runs/100b**. Shrunk baseline: **+22.18 runs/100b**.
- **High-Pressure Sample:** 168 deliveries. Raw HP impact: **+65.75 runs/100b**, Opponent quality adjustment: **+0.82 runs/100b**.
- **Opposition-Adjusted HP Impact:** **+66.57 runs / 100 balls**.
- **Opposition-Adjusted Pressure Delta is Negative:** $\text{Adj Raw}_\Delta = 66.57 - 73.40 = \mathbf{-6.83\text{ runs / 100 balls}}$ (alongside the unadjusted raw figure: $\text{Unadjusted Raw}_\Delta = 65.75 - 73.40 = \mathbf{-7.65\text{ runs / 100 balls}}$).
- **Empirical Bayes Shrinkage Effect:** Because the eligible batter population mean effect is positive ($\mu_\Delta = +3.57$), shrinking his $-6.83$ opposition-adjusted delta with $N_\Delta = 168$ and $K_\Delta = 773.0$ pulls his posterior delta upward to **$\hat{\Delta} = +1.71$** (90% CI $[-8.5, +11.3]$).
- **Rule Qualification Impact:**
  - Because $\hat{\Delta} = +1.71 \ge 0$, Sooryavanshi qualifies under **Rule B at Rank 2**.
  - If a franchise enforces a **Raw Delta $\ge 0$** rule, he is excluded.
  - Under a volume cutoff of **$\ge 200$ HP balls**, his 168 deliveries make him **ineligible / unranked**.
  - His Rank 2 is primarily powered by an extraordinary baseline (+73.40 raw) regressed to +22.18, rather than a positive clutch spike.

---

## 5. REML Shrinkage & Complete 20-Player Verification (Table 3.1)

### 5.1 Verification of Recomputed Priors (Old Unfiltered vs Filtered Cohort from Actual Runs)

| Parameter / Diagnostic | Pre-Exclusion (All Cohort) | Post-Exclusion (Filtered Cohort Actual Run) | Status / Reconciliation Notes |
|:---|:---:|:---:|:---|
| **Eligible Batters Count** | 139 players ($\ge 100$ HP balls) | **131 players** | 8 Pakistan players excluded before estimating means |
| **Eligible Bowlers Count** | 148 players ($\ge 100$ HP balls) | **140 players** | 8 Pakistan players excluded before estimating means |
| **Batters REML Priors** | $K_B = 1717.4, K_\Delta = 773.0$ | **$K_B = 1894.4, K_\Delta = 671.6$** | Primary model retains tournament benchmark (1717.4 / 773.0) |
| **Bowlers REML Priors** | $K_B = 1312.9, K_\Delta = 1041.4$ | **$K_B = 1384.0, K_\Delta = 963.5$** | Primary model retains tournament benchmark (1312.9 / 1041.4) |
| **Population Means ($\mu$)** | Bat: +7.07 / +3.38 \| Bowl: +3.37 / +1.03 | **Bat: +7.02 / +3.57 \| Bowl: +2.53 / +1.14** | Filtered eligible cohort means used for all primary shrinkage |
| **Typical HP Shrinkage Weight** | 24.56% bat, 18.98% bowl | **24.82% bat, 19.09% bowl** | Data-driven REML weight for average eligible volume |
| **Split-Half Reliability $r_{SB}$** | 0.114 bat, 0.265 bowl | **0.107 bat, 0.212 bowl** | Spearman-Brown on observed split-half correlations |
| **Null Permutation $p$-value** | Bat $p = 0.0500$, Bowl $p = 0.0060$ | **Bat $p = 0.0440$, Bowl $p = 0.0300$** | Bowler $p$ shifts as excluding Muqeem narrows observed std from 4.089 to 4.052 |
| **Virat Kohli Rating & Rank** | Rating +17.43 (Rank 17) | **Rating +17.52 (Rank 16)** | Shrunk base +10.75, delta +6.76 ($N_B=1787, N_D=669$) |
| **Rohit Sharma Rating & Rank** | Rating +5.30 (Rank 124) | **Rating +5.40 (Rank 117)** | Shrunk base +1.87, delta +3.53 ($N_B=1181, N_D=438$) |

**Reliability Reconciliation:** Applying the Spearman-Brown prophecy formula ($r_{SB} = \frac{2r}{1+r}$) to the observed split-half correlations ($r = 0.057$ bat, $0.118$ bowl) yields $r_{SB} = 0.107$ ($10.7\%$) for batters and $r_{SB} = 0.212$ ($21.2\%$) for bowlers. The gap to implied reliability (24.8% bat, 19.1% bowl) indicates that batter clutch impact across independent halves is subject to substantial single-delivery variance, whereas bowling exhibits higher longitudinal repeatability.

### 5.2 Table 3.1: Complete Calculation Verification for All 20 Primary Selections
Anyone can verify $\hat{B}_i$ and $\hat{\Delta}_i$ directly using a hand calculator via:
$$\hat{B}_i = \left(\frac{N_B}{N_B + K_B}\right)Raw_B + \left(\frac{K_B}{N_B + K_B}\right)\mu_B, \quad \hat{\Delta}_i = \left(\frac{N_\Delta}{N_\Delta + K_\Delta}\right)Raw_\Delta + \left(\frac{K_\Delta}{N_\Delta + K_\Delta}\right)\mu_\Delta$$

*Note on Ball Counts: HP delivery counts reflect all non-wide legal deliveries in the master database (Abhishek 494b, Salt 397b, Iyer 448b), ensuring full accounting of all delivery-level events.*

| Rk | Player Name | Role | $N_B$ | $w_B$ | $Raw_B$ | $\hat{B}_i$ | $N_\Delta$ | $w_\Delta$ | $Raw_\Delta$ | $\hat{\Delta}_i$ | Shrunk Rating | 90% Credible Interval | P(Top 10) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Suryakumar Yadav** | Bat | 2,062 | 0.546 | +29.69 | +19.39 | 697 | 0.474 | +15.01 | +8.99 | **+28.39** | [+18.16, +36.22] | 90.3% |
| **2** | **Vaibhav Sooryavanshi** | Bat | 508 | 0.228 | +73.40 | +22.18 | 168 | 0.179 | -6.83 | +1.71 | **+23.89** | [+12.07, +33.34] | 63.2% |
| **3** | **Jos Buttler** | Bat | 2,272 | 0.570 | +19.93 | +14.37 | 557 | 0.419 | +15.78 | +8.68 | **+23.06** | [+12.10, +31.27] | 62.5% |
| **4** | **Heinrich Klaasen** | Bat | 1,156 | 0.402 | +31.12 | +16.72 | 261 | 0.252 | +13.25 | +6.01 | **+22.73** | [+13.14, +29.45] | 58.3% |
| **5** | **Reeza Hendricks** | Bat | 611 | 0.262 | +11.98 | +8.33 | 224 | 0.225 | +51.38 | +14.31 | **+22.64** | [+13.21, +28.09] | 57.1% |
| **6** | **Abhishek Sharma** | Bat | 1,823 | 0.515 | +40.33 | +24.17 | 494 | 0.390 | -11.35 | -2.25 | **+21.93** | [+6.31, +35.02] | 53.6% |
| **7** | **Phil Salt** | Bat | 1,246 | 0.420 | +28.13 | +15.90 | 397 | 0.339 | +10.10 | +5.79 | **+21.69** | [+9.01, +30.90] | 49.5% |
| **8** | **Rinku Singh** | Bat | 990 | 0.366 | +12.21 | +8.92 | 294 | 0.276 | +34.39 | +12.06 | **+20.98** | [+12.19, +26.66] | 44.9% |
| **9** | **Shreyas Iyer** | Bat | 1,417 | 0.452 | +12.80 | +9.64 | 448 | 0.367 | +22.00 | +10.33 | **+19.97** | [+9.87, +26.82] | 36.5% |
| **10** | **Tim David** | Bat | 850 | 0.331 | +43.04 | +18.95 | 376 | 0.327 | -4.90 | +0.80 | **+19.75** | [+9.47, +27.74] | 35.1% |
| **1** | **Josh Hazlewood** | Bowl | 1,078 | 0.451 | +17.17 | +9.13 | 399 | 0.277 | +28.42 | +8.70 | **+17.83** | [+7.36, +27.86] | 73.5% |
| **2** | **Matheesha Pathirana** | Bowl | 853 | 0.394 | +21.03 | +9.82 | 282 | 0.213 | +31.75 | +7.66 | **+17.48** | [+10.12, +24.09] | 82.7% |
| **3** | **Sunil Narine** | Bowl | 1,062 | 0.447 | +17.15 | +9.07 | 468 | 0.310 | +14.62 | +5.32 | **+14.39** | [+7.24, +21.49] | 56.8% |
| **4** | **Jasprit Bumrah** | Bowl | 1,270 | 0.492 | +35.18 | +18.59 | 439 | 0.297 | -19.93 | -5.11 | **+13.48** | [+5.04, +22.47] | 51.3% |
| **5** | **Jacob Duffy** | Bowl | 686 | 0.343 | +20.90 | +8.83 | 191 | 0.155 | +21.28 | +4.26 | **+13.10** | [+2.44, +23.08] | 47.1% |
| **6** | **Rashid Khan** | Bowl | 2,089 | 0.614 | +7.69 | +5.70 | 658 | 0.387 | +16.97 | +7.27 | **+12.97** | [+5.49, +20.54] | 44.7% |
| **7** | **Lockie Ferguson** | Bowl | 814 | 0.383 | +7.15 | +4.30 | 270 | 0.206 | +37.05 | +8.53 | **+12.83** | [+2.43, +22.99] | 43.1% |
| **8** | **Varun Chakravarthy** | Bowl | 1,520 | 0.537 | +20.23 | +12.03 | 608 | 0.369 | -1.24 | +0.26 | **+12.29** | [+4.65, +19.64] | 39.1% |
| **9** | **Nathan Ellis** | Bowl | 649 | 0.331 | +26.19 | +10.36 | 268 | 0.205 | +4.84 | +1.90 | **+12.26** | [+5.14, +18.54] | 33.9% |
| **10** | **Mitchell Santner** | Bowl | 1,272 | 0.492 | +5.84 | +4.16 | 465 | 0.309 | +23.43 | +8.02 | **+12.18** | [+5.22, +19.26] | 39.7% |

![Funnel Plot](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/rating_vs_samplesize_funnel.png)

---

## 6. Within-Match Null Permutation Test (1,000 Draws)

To test whether pressure differences reflect repeatable skill or random clusterings within matches, we ran a 1,000-draw within-match permutation test:
- Within each match, the high-pressure indicators were shuffled across deliveries, preserving match context, phase, venue, and total pressure balls per match.

### 6.1 Permutation Test Results

| Discipline | Observed Population Std ($S_{\text{obs}}$) | Null Mean Std ($\bar{S}_{\text{null}}$) | Null 95% CI Range | Permutation $p$-value | Empirical Conclusion |
|:---|:---:|:---:|:---:|:---:|:---|
| **Batters** | **5.0681** | **4.6147** | [3.91, 5.06] | **$p = 0.0440$** | **Borderline Signal ($p \approx 0.044$):** High single-match variance; difficult to distinguish from chance. |
| **Bowlers** | **4.0524** | **3.6532** | [3.02, 4.08] | **$p = 0.0300$** | **Statistically Distinguishable ($p = 0.030$):** Bowler pressure control exhibits repeatable divergence. |

![Batters Forest Plot](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/top10_batters_intervals.png)
![Bowlers Forest Plot](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/top10_bowlers_intervals.png)

---

## 7. Comprehensive Sensitivity Analysis across 14 Specifications & Volume Cutoff Policy

### 7.1 Table 7.1: Summary of All 14 Specifications and Top-10 Overlap

| Spec # | Specification Definition | Batters Jaccard (Overlap) | Bowlers Jaccard (Overlap) | Summary Sensitivity Impact |
|:---:|:---|:---:|:---:|:---|
| **S1** | **Primary Base: Phase-Specific Wickets (PP 14.36, Mid 8.13, Death 2.92)** | **1.00 (10/10)** | **1.00 (10/10)** | Primary model baseline reference specification |
| **S2** | Flat Wicket Value = 8.85 runs | 1.00 (10/10) | 0.54 (7/10) | Spinners gain with flat middle wickets |
| **S3** | Wicket Value = 7.0 runs | 1.00 (10/10) | 0.54 (7/10) | Economy-dominant bowlers gain rank |
| **S4** | Wicket Value = 9.0 runs | 1.00 (10/10) | 0.54 (7/10) | Similar to flat 8.85 benchmark |
| **S5** | Wicket Value = 11.0 runs | 1.00 (10/10) | 0.54 (7/10) | Wicket-taking specialists elevated |
| **S6** | Wicket Value = 13.0 runs | 0.82 (9/10) | 0.54 (7/10) | Wicket penalties impact aggressive hitters |
| **S7** | Pressure Threshold: Top 20% Leverage | 0.82 (9/10) | 0.54 (7/10) | Extreme crisis deliveries isolated |
| **S8** | Pressure Threshold: Top 30% Leverage | 0.67 (8/10) | 0.82 (9/10) | Broader pressure cohort expands sample size |
| **S9** | Minimum Sample: 150 Balls | 1.00 (10/10) | 0.82 (9/10) | All 10 batters qualify (Sooryavanshi #2 with 168b); 9/10 bowlers qualify (Duffy #5 with 191b; Ellis slips to #11 as Kuldeep enters at #8) |
| **S10** | Minimum Sample: 200 Balls | 0.82 (9/10) | 0.82 (9/10) | Sooryavanshi (168b) and Duffy (191b) unranked |
| **S11** | Competition: IPL-Only | 0.67 (8/10) | 0.54 (7/10) | Hendricks, Salt, Duffy, Santner lose T20I volume |
| **S12** | Competition: Tier 1 Only (No A-Team/Associate) | 1.00 (10/10) | 0.82 (9/10) | Highly robust; removes associate development games |
| **S13** | Competition: T20I Excluded | 0.67 (8/10) | 0.54 (7/10) | Identical to IPL-only constraint |
| **S14** | Weighting: Recency Weighting (2022-26) | 1.00 (10/10) | 0.67 (8/10) | Exponential decay favoring 2024–25 seasons |

### 7.2 Volume Cutoff Handling Policy
In Specification 10 ($\ge 200$ HP balls), players with fewer than 200 balls (e.g. Vaibhav Sooryavanshi with 168 balls, Jacob Duffy with 191 balls) do not meet the volume threshold.
**Explicit Policy:** Players who fail a volume cutoff are treated as **Unranked (Excluded from that specification's pool)** rather than penalized with an artificial low rank (e.g. 131 or 140). Their $[\min, \max]$ range is computed strictly over the valid specifications where they qualified, with Specification 1 anchoring their primary rank.

### 7.3 Complete Specification-by-Specification Rank Matrix for Top 10 Players

#### Batters Sensitivity Matrix Across 14 Specifications

| Player | Primary Rank | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 | S12 | S13 | S14 | Min | Max | Rank Range |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Suryakumar Yadav** | **1** | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | **[1, 2]** |
| **Vaibhav Sooryavanshi** | **2** | 2 | 4 | 3 | 4 | 6 | 7 | 2 | 2 | 2 | — | 2 | 2 | 2 | 3 | 2 | 7 | **[2, 7]** |
| **Jos Buttler** | **3** | 3 | 3 | 6 | 3 | 3 | 3 | 7 | 4 | 5 | 4 | 3 | 5 | 3 | 7 | 3 | 7 | **[3, 7]** |
| **Heinrich Klaasen** | **4** | 4 | 5 | 5 | 5 | 5 | 6 | 5 | 20 | 4 | 3 | 4 | 4 | 4 | 6 | 3 | 20 | **[3, 20]** |
| **Reeza Hendricks** | **5** | 5 | 6 | 9 | 6 | 4 | 4 | 6 | 9 | 3 | 2 | — | 3 | — | 4 | 2 | 9 | **[2, 9]** |
| **Abhishek Sharma** | **6** | 6 | 7 | 2 | 8 | 10 | 21 | 3 | 3 | 8 | 7 | 15 | 7 | 15 | 2 | 2 | 21 | **[2, 21]** |
| **Phil Salt** | **7** | 7 | 8 | 7 | 7 | 7 | 5 | 4 | 5 | 6 | 5 | 5 | 6 | 5 | 5 | 4 | 8 | **[4, 8]** |
| **Rinku Singh** | **8** | 8 | 2 | 4 | 2 | 2 | 1 | 12 | 10 | 7 | 6 | 10 | 8 | 10 | 9 | 1 | 12 | **[1, 12]** |
| **Shreyas Iyer** | **9** | 9 | 10 | 10 | 10 | 9 | 9 | 10 | 12 | 10 | 9 | 6 | 10 | 6 | 8 | 6 | 12 | **[6, 12]** |
| **Tim David** | **10** | 10 | 9 | 8 | 9 | 8 | 8 | 8 | 7 | 9 | 8 | 7 | 9 | 7 | 10 | 7 | 10 | **[7, 10]** |

#### Bowlers Sensitivity Matrix Across 14 Specifications

| Player | Primary Rank | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 | S12 | S13 | S14 | Min | Max | Rank Range |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Josh Hazlewood** | **1** | 1 | 2 | 2 | 2 | 2 | 1 | 1 | 3 | 2 | 2 | 6 | 2 | 6 | 3 | 1 | 6 | **[1, 6]** |
| **Matheesha Pathirana** | **2** | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 2 | 1 | 2 | 1 | 1 | 2 | **[1, 2]** |
| **Sunil Narine** | **3** | 3 | 4 | 3 | 4 | 4 | 4 | 3 | 2 | 3 | 3 | 1 | 3 | 1 | 2 | 1 | 4 | **[1, 4]** |
| **Jasprit Bumrah** | **4** | 4 | 11 | 6 | 12 | 21 | 25 | 8 | 13 | 7 | 6 | 9 | 7 | 9 | 7 | 4 | 25 | **[4, 25]** |
| **Jacob Duffy** | **5** | 5 | 9 | 11 | 9 | 10 | 9 | 4 | 6 | 5 | — | — | 5 | — | 8 | 4 | 11 | **[4, 11]** |
| **Rashid Khan** | **6** | 6 | 3 | 4 | 3 | 3 | 3 | 12 | 7 | 9 | 10 | 5 | 9 | 5 | 5 | 3 | 12 | **[3, 12]** |
| **Lockie Ferguson** | **7** | 7 | 15 | 15 | 15 | 16 | 16 | 6 | 5 | 6 | 5 | 21 | 6 | 21 | 14 | 5 | 21 | **[5, 21]** |
| **Varun Chakravarthy** | **8** | 8 | 5 | 5 | 5 | 5 | 5 | 10 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 10 | **[4, 10]** |
| **Nathan Ellis** | **9** | 9 | 18 | 13 | 18 | 19 | 20 | 13 | 8 | 11 | 9 | 3 | 11 | 3 | 11 | 3 | 20 | **[3, 20]** |
| **Mitchell Santner** | **10** | 10 | 7 | 8 | 7 | 8 | 10 | 16 | 9 | 10 | 8 | 11 | 10 | 11 | 10 | 7 | 16 | **[7, 16]** |

*Note:* Every player's $[\min, \max]$ range strictly includes their primary rank (e.g. Heinrich Klaasen Primary 4 in [3, 20]; Jacob Duffy Primary 5 in [4, 11]; Rashid Khan Primary 6 in [3, 12]).

![Rank Stability Heatmap](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/rank_stability_heatmap.png)

---

## 8. Sanity Diagnostics for Household Names (Direct Delivery-Level Verification)

To confirm that absences from the Top 10 are due to data-driven performance and not eligibility or modeling errors, we audited household names directly from `ball_by_ball.csv`:

### 8.1 Direct Delivery-Level Audit
- **Suryakumar Yadav (Rank 1):** 697 HP balls faced (723 total incl 26 wides), 1,170 runs, 27 dismissals, HP SR: **167.86** vs Expected 136.44 ($+31.4\text{ SR}$). HP Average: 43.33. Shrunk baseline $\hat{B} = +19.39$, shrunk delta $\hat{\Delta} = +8.99$, Rating **+28.39**. Rank 1 globally.
- **Jos Buttler (Rank 3):** 557 HP balls faced (568 total incl 11 wides), 917 runs, 19 dismissals, HP SR: **164.63** vs Expected 140.90 ($+23.7\text{ SR}$). HP Average: 48.26. Shrunk baseline $\hat{B} = +14.37$, shrunk delta $\hat{\Delta} = +8.68$, Rating **+23.06**. Rank 3 overall.
- **Virat Kohli (Rank 16 on Filtered Cohort):** 669 HP balls faced (692 total incl 23 wides), 1,002 runs, 20 dismissals, HP SR: **149.78** vs Expected 141.25 ($+8.5\text{ SR}$). Dismissal Rate: **2.99%** vs Expected 4.65% ($+11.1$ wickets preserved above expectation). Shrunk baseline $\hat{B} = +10.75$, shrunk delta $\hat{\Delta} = +6.76$, Rating **+17.52**, Rank 16.
- **Rohit Sharma (Rank 117 on Filtered Cohort):** 438 HP balls faced (453 total incl 15 wides), 660 runs, 26 dismissals, HP SR: **150.68** vs Expected 141.28 ($+9.4\text{ SR}$). Dismissal Rate: **5.94%** vs Expected 4.44% ($-6.6$ wicket deficit). Shrunk baseline $\hat{B} = +1.87$, shrunk delta $\hat{\Delta} = +3.53$, Rating **+5.40**, Rank 117.
- **Jasprit Bumrah (Rank 4):** 439 HP legal balls bowled, 557 runs conceded, 14 wickets, HP Economy: **7.61** vs Expected 8.68 (saving $1.07\text{ RPO}$). Wicket Rate: **3.19%** vs Expected 5.07% ($22.2$ expected wickets, a $-8.2$ wicket deficit). Elite baseline skill ($\hat{B} = +18.59$) secures Rank 4, despite a neutral clutch delta ($\hat{\Delta} = -5.11$, 90% CI $[-13.7, +4.0]$).
- **Rashid Khan (Rank 6):** 658 HP legal balls bowled, 737 runs conceded, 42 wickets, HP Economy: **6.72** vs Expected 8.35 (saving $1.63\text{ RPO}$). HP Wicket Rate: **6.38%** (strike rate 15.67 balls/wkt). Shrunk baseline $\hat{B} = +5.70$, shrunk delta $\hat{\Delta} = +7.27$, Rating **+12.97**, Rank 6.
- **Arshdeep Singh (Rank 115):** 784 HP balls. High exposure volume; HP economy elevates to $9.31$ under death pressure against elite finishers.
- **MS Dhoni (Ineligible):** Faced fewer than 100 high-pressure deliveries in the 2022–26 sample window.

---

## 9. Real-World Franchise Caveats & Reproduction Guide

### 9.1 Tactical & Franchise Realities
1. **Impact Player Rule Distortion:** Since 2023, the IPL Impact Player rule has lengthened batting orders, encouraging aggressive hitting earlier in innings.
2. **Venue and Pitch Variations:** Raw economy and strike rates vary dramatically across venues (e.g., Wankhede vs Chepauk). GroupKFold cross-validation normalizes match environments.
3. **Statistical Indistinguishability:** While the Top 10 players are statistically superior to average players, adjacent rank differences (e.g., Rank 2 vs Rank 4) are partly indistinguishable ($P(\text{Rank}_i > \text{Rank}_{i+1}) \approx 55\%–65\%$).
4. **Expected Wicket Stochasticity:** The expected-wicket model achieves an ROC-AUC of 0.595, reflecting that dismissals carry high variance; rolling Bayesian updates are recommended.

### 9.2 Reproduction Guide (PowerShell)

```powershell
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Run master execution pipeline end-to-end
python run_all.py
```
*Pipeline regenerates all models, bootstrap draws, permutations, figures, and publication documents in < 65 seconds.*
