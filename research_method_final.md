# II. RESEARCH METHOD

This section delineates the empirical research design, data acquisition protocols, data validation procedures, non-parametric statistical frameworks, and visual synthesis utilized to investigate regional digital consumer search interest across Indonesian e-commerce platforms.

---

### A. Research Design and Data Source

This study employs a quantitative, non-experimental spatial comparative design to analyze digital consumer search interest across Indonesia's geographic subregions. The primary data were retrieved from Google Trends (Google LLC) utilizing the *Interest by Subregion* feature for the six-year observation window spanning January 1, 2020, to December 31, 2025. 

The empirical scope encompasses the five prominent e-commerce platforms operating in Indonesia: **Shopee, Tokopedia, Lazada, Blibli, and TikTok Shop**. Google Trends indexes digital search query intensity by calculating the proportion of queries for a designated entity relative to total searches across all topics within a specified geographic jurisdiction and time frame. The platform scales this proportion to a bounded relative index ranging from 0 to 100, where 100 signifies the subregion exhibiting the maximum query concentration for that specific query, and 0 denotes areas with negligible relative volume.

The geographic observation units comprise all **34 first-level administrative provinces** of Indonesia established during the study timeframe. For each e-commerce platform, Google Trends yields a single cross-sectional regional index per province representing the cumulative search propensity over the 2020–2025 period. Consequently, the dataset contains exactly **170 discrete observations** ($N = 34 \text{ provinces} \times 5 \text{ platforms}$).

> **Methodological Delimitation:** The Google Trends *Interest by Subregion* metric reflects normalized relative search propensity rather than absolute search volume, gross merchandise value (GMV), transaction counts, or financial market share. Furthermore, because each platform query was queried and extracted independently, each platform's index is normalized relative to its own regional maximum. Therefore, raw cross-platform score differentials do not signify absolute popularity disparities; instead, they capture intra-platform spatial dispersion patterns across Indonesia's provincial hierarchy.

---

### B. Data Preprocessing and Validation

Data preparation and validation were conducted in Python (v3.13) utilizing `pandas` (v2.2) and `numpy` (v2.1). The procedural pipeline enforced rigorous data integrity standards:

1. **Extraction and Harmonization:** The raw tabular records were parsed from the multi-sheet research dataset. Column nomenclature was standardized to eliminate case discrepancies and trailing whitespace (e.g., reconciling variations of `TikTok Shop`).
2. **Geographic Entity Reconciliation:** All 34 provincial names were cross-checked against official administrative designations cataloged by the Central Statistics Agency (*Badan Pusat Statistik* / BPS). The spatial coverage was partitioned into two mutually exclusive geographic strata:
   - **Java Island ($n_1 = 6$):** Banten, DKI Jakarta, Jawa Barat, Jawa Tengah, DI Yogyakarta, and Jawa Timur.
   - **Outer Islands / Non-Java ($n_2 = 28$):** The remaining 28 provinces spanning Sumatra, Kalimantan, Sulawesi, Bali, Nusa Tenggara, Maluku, and Papua.
3. **Data Quality Audit:**
   - **Completeness:** The regional matrix was verified to contain zero missing values (`NaN = 0`) across all 170 cells.
   - **Domain Validity:** Every observed value was audited to ensure strict adherence to the bounded interval $[0, 100]$.
   - **Tie-Breaking Formulation:** In instances where multiple platforms achieved identical maximum search indices within a single province (e.g., DKI Jakarta and Bali), a *Joint Dominance* framework was adopted to prevent algorithmic selection bias inherent in conventional programmatic first-match procedures (`idxmax`).

---

### C. Statistical Analysis

Given the bounded nature ($[0, 100]$), continuous ordinal attributes, and pronounced skewness of regional search indices, non-parametric inferential techniques were deployed throughout the investigation.

#### 1. Univariate Descriptive Statistics
To characterize the central tendency and spatial dispersion of regional interest for each platform, we computed:
- Measures of central location: Arithmetic Mean ($\bar{x}$) and Median ($\tilde{x}$).
- Measures of dispersion: Standard Deviation ($s$), Minimum ($\min$), and Maximum ($\max$).
- Spatial distributional metrics: Identification of provincial peak loci ($\arg\max_i x_i$).

#### 2. Spearman Rank-Order Correlation ($r_s$)
To evaluate whether e-commerce platforms share congruent geographic demand footprints across Indonesia's 34 provinces, pairwise Spearman rank correlation coefficients were estimated for all unique platform pairs ($k = \binom{5}{2} = 10$). For two platforms $X$ and $Y$ with provincial ranks $R(X_i)$ and $R(Y_i)$:

$$r_s = 1 - \frac{6 \sum_{i=1}^{n} d_i^2}{n(n^2 - 1)}$$

where $d_i = R(X_i) - R(Y_i)$ represents the rank difference for province $i$, and $n = 34$. The two-sided null hypothesis postulates an absence of monotonic rank association ($H_0: \rho_s = 0$).

#### 3. Mann–Whitney U Test
To empirically test for digital divide disparities between metropolitan centers and developing regions, the Mann–Whitney $U$ test was conducted. The distributions of search interest in Java ($n_1 = 6$) and Non-Java ($n_2 = 28$) were compared independently for each platform. The test statistic is formulated as:

$$U_1 = n_1 n_2 + \frac{n_1(n_1 + 1)}{2} - R_1$$

where $R_1$ is the sum of ranks assigned to the Java group. The effect size of the regional divergence was quantified via the Rank-Biserial Correlation ($r_{rb}$):

$$r_{rb} = 1 - \frac{2U_1}{n_1 n_2}$$

where $r_{rb} \in [-1, 1]$, with values approaching $1.0$ indicating absolute stochastic dominance of Java over Non-Java provinces.

#### 4. Multiple Comparison Adjustment (Holm–Bonferroni Correction)
To safeguard against Family-Wise Error Rate (FWER) inflation arising from simultaneous hypothesis testing (10 pairwise Spearman tests and 5 Mann–Whitney $U$ tests), the sequential step-down **Holm–Bonferroni procedure** was applied. For $m$ ordered unadjusted $p$-values ($p_{(1)} \le p_{(2)} \le \dots \le p_{(m)}$), each null hypothesis $H_{(k)}$ is rejected at nominal level $\alpha = 0.05$ if and only if:

$$p_{(k)} \le \frac{\alpha}{m - k + 1}$$

---

### D. Data Visualization

Visualization assets were generated using `matplotlib` (v3.9) and `seaborn` (v0.13) to facilitate rigorous graphical interpretation:
1. **Regional Search Intensity Heatmap:** A two-dimensional intensity matrix ($34 \text{ provinces} \times 5 \text{ platforms}$) ordered by aggregate mean search intensity to depict regional clustering and peripheral adoption gradients.
2. **Bivariate Correlation Matrix Heatmap:** A symmetrical $5 \times 5$ heatmap annotating pairwise Spearman $\rho_s$ coefficients using a diverging colormap (`RdBu_r`), highlighting clusters of conventional e-commerce versus social commerce footprints.
3. **Comparative Distribution Boxplots:** Grouped box-and-whisker plots contrasting the median, interquartile range (IQR), and distributional spread between Java and Non-Java provinces for each platform.

---

### E. Research Workflow

The end-to-end execution of this research follows a structured, sequential seven-stage protocol illustrated in **Fig. 1**:

$$\text{Google Trends Data Collection} \longrightarrow \text{Data Cleaning \& Validation} \longrightarrow \text{Descriptive Statistical Analysis} \longrightarrow \text{Spearman Rank Correlation} \longrightarrow \text{Mann–Whitney U Test with Holm Correction} \longrightarrow \text{Data Visualization} \longrightarrow \text{Interpretation \& Conclusion}$$

```
+---------------------------------------------------------------------------------------------------+
|                                  RESEARCH METHODOLOGY WORKFLOW                                    |
+---------------------------------------------------------------------------------------------------+
|  [STAGE 1] Google Trends Data Collection                                                          |
|            • Query 5 platforms (Shopee, Tokopedia, Lazada, Blibli, TikTok Shop)                   |
|            • Geographic scope: 34 Indonesian Provinces (Interest by Subregion)                    |
|            • Temporal scope: 2020–2025 aggregate relative index (0–100)                           |
+--------------------------------------------------+------------------------------------------------+
                                                   |
                                                   v
+---------------------------------------------------------------------------------------------------+
|  [STAGE 2] Data Cleaning & Validation                                                             |
|            • Column name standardization & platform label reconciliation                          |
|            • Administrative province validation (6 Java, 28 Non-Java)                             |
|            • Data integrity audit: 170 observations, 0 missing values, bounded [0, 100]           |
+--------------------------------------------------+------------------------------------------------+
                                                   |
                                                   v
+---------------------------------------------------------------------------------------------------+
|  [STAGE 3] Descriptive Statistical Analysis                                                       |
|            • Central tendency & dispersion: Mean, Median, Std. Dev., Min, Max                     |
|            • Evaluation of spatial skewness, dispersion, and peak index distribution              |
+--------------------------------------------------+------------------------------------------------+
                                                   |
                                                   v
+---------------------------------------------------------------------------------------------------+
|  [STAGE 4] Spearman Rank Correlation Analysis                                                     |
|            • Pairwise monotonic association (r_s) across 34 provinces (10 platform pairs)         |
|            • Assessment of spatial ranking co-alignment between platform footprints               |
|            • Family-wise error rate control via Holm–Bonferroni correction (alpha = 0.05)         |
+--------------------------------------------------+------------------------------------------------+
                                                   |
                                                   v
+---------------------------------------------------------------------------------------------------+
|  [STAGE 5] Mann–Whitney U Test with Holm Correction                                               |
|            • Non-parametric rank-sum comparison: Java (n1 = 6) vs. Non-Java (n2 = 28)            |
|            • Computation of test statistic (U) and Rank-Biserial correlation (r_rb)               |
|            • Multiple testing adjustment using sequential Holm method (p_Holm)                     |
+--------------------------------------------------+------------------------------------------------+
                                                   |
                                                   v
+---------------------------------------------------------------------------------------------------+
|  [STAGE 6] Academic Data Visualization                                                            |
|            • Cross-provincial search intensity heatmap (34 provinces x 5 platforms)               |
|            • Inter-platform Spearman correlation matrix heatmap                                   |
|            • Java vs. Non-Java comparative distribution boxplots                                  |
+--------------------------------------------------+------------------------------------------------+
                                                   |
                                                   v
+---------------------------------------------------------------------------------------------------+
|  [STAGE 7] Interpretation & Conclusion                                                            |
|            • Synthesis of spatial digital divide and multi-platform consumer search behavior      |
|            • Delineation of relative search interest vs. absolute GMV/transaction volume         |
|            • Scientific conclusions on provincial market maturity and consumer dynamics           |
+---------------------------------------------------------------------------------------------------+
```

*Fig. 1. Methodological workflow of regional Google Trends search pattern analysis in Indonesian e-commerce (see accompanying high-resolution file `research_workflow.png`).*
