# SupeRR Selector Season 2 – Round 1
## Identify the Most Reliable Players Under Pressure in T20 Cricket (2022 Onwards)

**Submission:** SupeRR Selector Season 2 – Round 1 Submission  
**Author:** Kishalay Das  
**Deliverables:** Top 10 Batters & Top 10 Bowlers Under Pressure + Full Reproducible Pipeline & Methodology  
**Dataset:** 883 Matches, 200,999 Deliveries (IPL & T20I from 2022 onwards)  
**Core Artifacts:**  
- [methodology_report.pdf](file:///e:/E%20Drive/College/projects/rajsthanroyals/report/methodology_report.pdf) (Strictly 3-page publication PDF)  
- [methodology_report.md](file:///e:/E%20Drive/College/projects/rajsthanroyals/report/methodology_report.md) (Full Comprehensive Methodology Report)  
- [final_top10_batters.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/final_top10_batters.csv)  
- [final_top10_bowlers.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/final_top10_bowlers.csv)  
- [shrinkage_verification_table.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/shrinkage_verification_table.csv)  
- [top20_bowlers_wicket_specs.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/top20_bowlers_wicket_specs.csv)  
- [top10_sensitivity_matrix.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/top10_sensitivity_matrix.csv)  
- [excluded_pakistan_players.csv](file:///e:/E%20Drive/College/projects/rajsthanroyals/outputs/excluded_pakistan_players.csv)  

---

## 🏆 Final Deliverables: Top 10 Selections

### Explicit Ordering Rule
*Primary selections are strictly ranked in descending order of their total hierarchical posterior mean impact rating ($\hat{B}_i + \hat{\Delta}_i$), combining shrunk baseline performance with shrunk high-pressure delta. 90% credible intervals indicate that six top-10 players—**Suryakumar Yadav, Reeza Hendricks, Rinku Singh, Shreyas Iyer, Matheesha Pathirana, and Mitchell Santner**—possess clutch pressure elevation ($\hat{\Delta}_i$) strictly above zero at the 90% credibility level while all other players remain statistically indistinguishable from zero or exhibit pressure dips.*

### Primary Ranking: Top 10 Batters Under Pressure (Phase-Specific Wickets, No Dip Exclusion)
*Ranked by Posterior Mean Shrunk Rating from the Hierarchical Model: $\text{Rating}_i = \hat{B}_i + \hat{\Delta}_i$ (Net Runs Added per 100 Balls Above Expected)*

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

---

### Primary Ranking: Top 10 Bowlers Under Pressure (Phase-Specific Wickets, No Dip Exclusion)
*Ranked by Posterior Mean Shrunk Rating from the Hierarchical Model: $\text{Rating}_i = \hat{B}_i + \hat{\Delta}_i$ (Net Runs Saved per 100 Balls Above Expected)*

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

---

## 🔍 Fair Comparisons, Eligibility & Opposition Quality Audit

### Eligibility Framework & Author's Eligibility Choice
- Strict eligibility: **$\ge 100$ High-Pressure Deliveries**, **$\ge 6$ High-Pressure Matches**, and **$\ge 10$ Total Career Matches**.
- **Pakistan Player Exclusion:** Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement.
- Qualifying cohort: exactly **131 batters** and **140 bowlers** (8 batters and 8 bowlers excluded under this authorial choice).

### Table 2.1: Opposition Quality Audit & Mathematical Reconciliation (All 20 Selections)
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

### Transparent Audit of Excluded Pakistan Players in Unconstrained Top 20 (Table 2.2)
To ensure complete methodological transparency, the four Pakistan players who would have ranked in the unconstrained top 20 are documented below:

| Discipline | Player Name | Unconstrained Rank | HP Balls | Shrunk Rating | Shrunk Baseline | Shrunk Delta | Primary Team(s) | Reason: author's eligibility choice |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|:---|
| **Batter** | Mohammad Rizwan | 15 | 400 | +17.86 | +10.57 | +7.29 | Pakistan | Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. |
| **Bowler** | Sufiyan Muqeem | 4 | 155 | +14.13 | +9.07 | +5.06 | Pakistan, Pakistan A | Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. |
| **Bowler** | Mohammad Nawaz | 16 | 289 | +11.27 | +6.13 | +5.14 | Pakistan | Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. |
| **Bowler** | Abrar Ahmed | 20 | 189 | +10.77 | +7.47 | +3.30 | Pakistan | Players representing Pakistan or Pakistan A are excluded from both rankings as an eligibility choice made by the author; this is not required by the dataset or the problem statement. |

### Plain Finding on Vaibhav Sooryavanshi
- Baseline Impact: 508 ordinary deliveries, Raw Baseline **+73.40 runs/100b**, Shrunk Baseline **+22.18**.
- High-Pressure Impact: 168 deliveries, Raw HP **+65.75 runs/100b**, opponent quality diff **+0.82 runs/100b**, yielding an **opposition-adjusted HP impact of +66.57 runs/100b**.
- **Opposition-Adjusted Pressure Delta is Negative:** $\text{Adj Raw}_\Delta = 66.57 - 73.40 = \mathbf{-6.83\text{ runs/100b}}$ (alongside the unadjusted raw figure: $\text{Unadjusted Raw}_\Delta = 65.75 - 73.40 = \mathbf{-7.65\text{ runs/100b}}$).
- Shrunk Delta pulls upward to **$\hat{\Delta} = +1.71 \ge 0$** (90% CI $[-8.5, +11.3]$) due to empirical Bayes regression toward population mean $\mu_\Delta = +3.57$.
- **Scouting takeaway:** He qualifies under Rule B at Rank 2 due to empirical Bayes shrinkage; however, if evaluated under a strict **Raw Delta $\ge 0$** rule, he is excluded. Under a **$\ge 200$ HP balls** threshold, his 168 balls render him ineligible / unranked.

---

## 🔬 Methodology Highlights

1. **Win-Probability Mathematical Outcome Leverage (Zero Subjective Multipliers):**
   - Out-of-fold LightGBM Win Probability models (Innings 1 Brier: $0.2303$, Innings 2 Brier: $0.1555$).
   - Leverage is formulated as the expected absolute WP swing across 7 delivery outcomes weighted by phase transition probabilities:
     $$\text{Leverage}_t = \sum_{o \in \mathcal{O}} P(o \mid \text{phase}) \cdot |WP(S_{t+1}(o)) - WP(S_t)|$$
   - Top quartile ($\ge 75\text{th}$ percentile, 50,241 deliveries) defines High Pressure.
   - Non-circular validation confirms pressure reduces dot balls ($35.59\% \to 34.42\%$, $p < 10^{-10}$), increases singles/twos running ($41.85\% \to 43.24\%$, $p < 10^{-10}$), and narrows runs/ball variance ($3.037 \to 2.974$, $p = 0.0038$).

2. **Calibration Auditing & Exact Out-of-Fold Recentering:**
   - League-wide residual mean across all 200,999 deliveries is identically $0.000000$ for runs and wickets ($1.7 \times 10^{-17}$ runs/ball, $-1.3 \times 10^{-18}$ outs/ball) following explicit recentering.
   - Expected wicket models achieve ROC-AUC 0.595, reflecting that dismissals are high-variance events in cricket that introduce substantial stochastic noise.
   - Eligible players ($\ge 100$ HP balls) hold positive baseline means ($+3.51$ runs/100b bat, $+1.57$ runs saved/100b bowl) because tailenders absorb negative residuals.

3. **Phase-Specific vs HP-Only Wicket Valuations:**
   - Primary Phase Wickets: **14.36 (Powerplay)**, **8.13 (Middle)**, **2.92 (Death)**, mean **8.85 runs/wkt**.
   - HP-Only Wickets: **14.40 (Powerplay)**, **10.71 (Middle)**, **5.89 (Death)**, mean **9.52 runs/wkt**.
   - Jaccard similarity between Primary Phase and HP-Only is **1.0000** for batters (10/10 overlap) and **0.6667** for bowlers (8/10 overlap).
   - *Rationale:* The bowler rankings exhibit moderate sensitivity to the wicket-run valuation rule because middle-overs spinners gain substantially when middle-overs wickets are credited at 8.85 or 10.71 runs rather than the phase-calibrated 8.13 runs; Phase-Specific valuation is adopted as primary because it empirically reflects the actual subsequent innings run-penalty.

4. **Hierarchical REML Shrinkage & Reliability Reconciliation:**
   - Variance components estimated separately via Restricted Maximum Likelihood (REML) on match-level data:
     * Batters: $K_B = 1,717.4$ balls ($\mu_B = +7.02$), $K_\Delta = 773.0$ balls ($\mu_\Delta = +3.57$). Typical weight = $24.82\%$.
     * Bowlers: $K_B = 1,312.9$ balls ($\mu_B = +2.53$), $K_\Delta = 1,041.4$ balls ($\mu_\Delta = +1.14$). Typical weight = $19.09\%$.
   - K values were estimated on the full cohort, while population means and ratings use the filtered (non-Pakistan) cohort; the filtered-cohort K values are shown in Table 4.1.
   - Applying Spearman-Brown ($r_{SB} = \frac{2r}{1+r}$) yields $r_{SB} = 0.107$ (batters) vs $r_{SB} = 0.212$ (bowlers). The gap to implied reliability indicates that batter clutch impact across independent halves is subject to substantial single-delivery variance, whereas bowling exhibits higher repeatability.

5. **1,000 Within-Match Null Permutation Test:**
   - Permuting `high_pressure` binary labels within matches confirms *statistically distinguishable bowling pressure control* ($p = 0.0300$ filtered cohort, $0.0060$ full cohort), while batting exhibits *borderline signal* ($p = 0.0440$ filtered cohort, $0.0500$ full cohort) due to heavy single-match randomness.

6. **Single Bootstrap Run (Fixed Seed 42):**
   - 1,000 match-grouped bootstrap draws re-estimating priors ensure that credible intervals, $P(\text{top 10})$, and rankings match bit-for-bit across all tables, charts, CSVs, and narrative text.

7. **Comprehensive Sensitivity Analysis Across 14 Specifications:**
   - Evaluated across 14 specifications:

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

   - Volume cutoff policy: Players failing a volume threshold (e.g. $\ge 200$ HP balls in Spec 10) are treated as **Unranked (Excluded)** rather than penalized with an artificial low rank.
   - Every top-10 player's $[\min, \max]$ range strictly bounds their primary rank:
     * *Batters:* Suryakumar Yadav [1, 2]; Vaibhav Sooryavanshi [2, 7]; Jos Buttler [3, 7]; Heinrich Klaasen [3, 20]; Reeza Hendricks [2, 9]; Abhishek Sharma [2, 21]; Phil Salt [4, 8]; Rinku Singh [1, 12]; Shreyas Iyer [6, 12]; Tim David [7, 10].
     * *Bowlers:* Josh Hazlewood [1, 6]; Matheesha Pathirana [1, 2]; Sunil Narine [1, 4]; Jasprit Bumrah [4, 25]; Jacob Duffy [4, 11]; Rashid Khan [3, 12]; Lockie Ferguson [5, 21]; Varun Chakravarthy [4, 10]; Nathan Ellis [3, 20]; Mitchell Santner [7, 16].

8. **Famous Players Verification on Filtered Cohort:**
   - Virat Kohli: Rating **+17.52** (Rank **16** on filtered cohort). 669 HP balls, 1,002 runs, 20 outs, SR 149.8 (+8.6 SR above exp), preserves +11.1 wickets above exp. Shrunk base +10.75, shrunk delta +6.76.
   - Rohit Sharma: Rating **+5.40** (Rank **117** on filtered cohort). 438 HP balls, 660 runs, 26 outs, SR 150.7. Shrunk base +1.87, shrunk delta +3.53.

---

## 📁 Repository Structure

```
rajsthanroyals/
├── data/                               # Historical dataset (IPL & T20I 2022 onwards)
│   ├── ball_by_ball.csv
│   ├── matches.csv
│   ├── competitions.csv
│   ├── teams.csv
│   ├── playing_eleven.csv
│   └── competition_team_player_mapping.csv
├── src/                                # Modular analysis codebase
│   ├── config.py                       # Global parameters, paths, and seeds (42)
│   ├── data_audit.py                   # Stage 0: Schema inspection & exclusions
│   ├── match_state.py                  # Stage 1: Pre-ball match state & par score
│   ├── pressure_model.py               # Stage 2: Win-probability leverage model
│   ├── expected_value.py               # Stage 3: Out-of-fold xR and xW baselines
│   ├── player_metrics.py               # Stage 4: High-pressure vs baseline metrics & consistency
│   ├── fair_comparison.py              # Stage 5: Hierarchical REML shrinkage & bootstrap
│   ├── reliability.py                  # Stage 6: Null permutation test, sensitivity & sanity
│   ├── visualizations.py               # Stage 7: Publication-quality charts (PNG)
│   ├── build_notebook.py               # Generates narrative Jupyter notebook
│   └── export_report_pdf.py            # Compiles 3-page publication PDF document
├── notebooks/
│   └── analysis.ipynb                  # Narrative interactive Jupyter Notebook
├── outputs/                            # Tables, intermediate CSVs, and charts
│   ├── final_top10_batters.csv         # Top 10 Batters CSV for submission
│   ├── final_top10_bowlers.csv         # Top 10 Bowlers CSV for submission
│   ├── top20_bowlers_wicket_specs.csv  # Top 20 Bowlers across 3 wicket value specifications
│   ├── shrinkage_verification_table.csv# Complete 20-Player Table 3.1 Verification
│   ├── excluded_pakistan_players.csv   # Transparent audit of excluded Pakistan players in top 20
│   ├── opposition_audit_top10.csv      # Opposition quality differential & audit (20 players)
│   ├── top10_sensitivity_matrix.csv    # Specification-by-specification matrix (14 specs)
│   ├── hp_wicket_comparison.csv        # HP-only vs Primary phase vs Flat wicket Jaccard
│   ├── top10_batters_flat.csv          # Flat 8.85 Top 10 Batters
│   ├── top10_bowlers_flat.csv          # Flat 8.85 Top 10 Bowlers
│   ├── phase_vs_flat_comparison_batters.csv # Comparative audit (batters)
│   ├── phase_vs_flat_comparison_bowlers.csv # Comparative audit (bowlers)
│   ├── top10_clutch_constrained_batters.csv # Rule B Batters (Delta >= 0)
│   ├── top10_clutch_constrained_bowlers.csv # Rule B Bowlers (Delta >= 0)
│   ├── calibration_summary.csv         # League-wide residual calibration audit
│   ├── null_test_summary.csv           # Within-match permutation test results
│   ├── null_top10_bands.csv            # 95% null distribution chance bands
│   ├── pairwise_probabilities_batters.csv # Adjacent rank superiority matrix (batters)
│   ├── pairwise_probabilities_bowlers.csv # Adjacent rank superiority matrix (bowlers)
│   ├── top10_rank_ranges.csv           # Min/max rank range across 14 specifications
│   ├── sanity_table_famous_batters.csv # Famous player diagnostic table (batters)
│   ├── sanity_table_famous_bowlers.csv # Famous player diagnostic table (bowlers)
│   ├── pressure_validation_stats.csv   # Validation statistics with effect sizes
│   ├── sensitivity_analysis.csv        # Comprehensive sensitivity benchmarks across 14 specs
│   ├── win_probability_calibration.png # LightGBM WP reliability diagram
│   ├── expected_value_calibration_deciles_phases.png # EV calibration across deciles & phases
│   ├── pressure_vs_ordinary_comparison.png # Event rates by pressure tier
│   ├── rating_vs_samplesize_funnel.png # Bayesian shrinkage funnel plot
│   ├── top10_batters_intervals.png     # Forest plot with 90% CIs and null chance band
│   ├── top10_bowlers_intervals.png     # Forest plot with 90% CIs and null chance band
│   ├── baseline_vs_pressure_scatter.png# Clutch delta scatter plot
│   └── rank_stability_heatmap.png      # Jaccard overlap heatmap
├── report/
│   ├── methodology_report.md           # Full Methodology Report (Markdown)
│   └── methodology_report.pdf          # 3-Page Publication PDF Document
├── requirements.txt                    # Project dependencies
├── run_all.py                          # Master one-click execution pipeline
└── README.md                           # Documentation and instructions
```

---

## ⚡ Reproduction Guide (PowerShell)

To reproduce the complete pipeline end-to-end:

```powershell
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Execute the entire pipeline end-to-end (Stages 0 through 7, plus PDF and Notebook)
python run_all.py
```

All models, data transformations, tables, bootstrap resamples, null permutation tests, charts, Jupyter notebook, and the 3-page publication PDF will regenerate in `< 65` seconds with 100% bit-for-bit reproducibility.
