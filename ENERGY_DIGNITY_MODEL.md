# A Mathematical Model for the Energy Dignity of the Countrymen of India

> **Author:** AI-assisted analytical framework  
> **Date:** June 2026  
> **Context:** This model operationalizes "energy dignity" — a normative concept that goes beyond conventional energy poverty measurement — into a rigorous, multi-dimensional mathematical index tailored for the Indian household context.

---

## 1. Philosophical & Theoretical Foundation

### 1.1 Defining Energy Dignity

**Energy Dignity** is defined as the state in which every individual has reliable, affordable, clean, and adequate access to modern energy services **sufficient to enable a life they have reason to value**. It is grounded in **Amartya Sen's Capability Approach**, which evaluates wellbeing not by what people *have* (resources), but by what they are *able to do and be* (capabilities and functionings).

| Concept | Definition |
|---|---|
| **Functioning** | A realized being or doing (e.g., being well-lit, cooking a meal, running a business) |
| **Capability** | The *real freedom* to achieve that functioning |
| **Conversion Factor** | Personal, social, or structural barriers that prevent a resource from becoming a functioning |
| **Energy Dignity** | The capability set of energy-related functionings an individual can actually realize |

### 1.2 Distinction from Energy Poverty

| Energy Poverty | Energy Dignity |
|---|---|
| Focuses on **deprivation** | Focuses on **flourishing** |
| Binary or threshold-based (poor / not poor) | Continuous spectrum from deprivation to thriving |
| Measures what is **lacking** | Measures what is **enabled** |
| Counts connections, kilowatt-hours | Measures agency, choice, and realized functionings |
| Static | Dynamic and aspirational |

---

## 2. The Energy Dignity Index (EDI): Mathematical Framework

### 2.1 Overview

The **Energy Dignity Index (EDI)** is a **multi-dimensional, hierarchical composite index** ranging from 0 to 1, where:

- **EDI = 0** represents complete energy indignity (no access to any modern energy service, no agency)
- **EDI = 1** represents full energy dignity (optimal access across all dimensions with full agency)

### 2.2 Dimensional Structure

Energy Dignity comprises **6 dimensions**, each representing a foundational capability necessary for a dignified life:

| # | Dimension | Symbol | Weight | Core Capability |
|---|---|---|---|---|
| 1 | **Basic Access** | \(A\) | \(w_A\) | The capability to be connected to modern energy systems |
| 2 | **Economic Affordability** | \(E\) | \(w_E\) | The capability to afford sufficient energy without sacrificing other necessities |
| 3 | **Reliability & Quality** | \(R\) | \(w_R\) | The capability to depend on consistent, high-quality energy supply |
| 4 | **Health & Environment** | \(H\) | \(w_H\) | The capability to use energy without compromising health or environment |
| 5 | **Productive & Developmental Adequacy** | \(P\) | \(w_P\) | The capability to use energy for education, livelihood, and human flourishing |
| 6 | **Agency & Empowerment** | \(G\) | \(w_G\) | The capability to choose, control, and participate in energy decisions |

**Weights constraint:** \(w_A + w_E + w_R + w_H + w_P + w_G = 1\)

### 2.3 Household-Level Energy Dignity: The Composite Index

We define the **Energy Dignity Index for household \(h\)** using a **weighted geometric mean** formulation:

\[
EDI_h = \prod_{d \in \mathcal{D}} \left( S_{h,d} \right)^{w_d}
\]

where:
- \(\mathcal{D} = \{A, E, R, H, P, G\}\) is the set of dimensions
- \(S_{h,d} \in [0, 1]\) is household \(h\)'s score in dimension \(d\)
- \(w_d \in (0, 1)\) is the weight of dimension \(d\), with \(\sum w_d = 1\)

> **Why geometric mean?** The geometric mean ensures that a low score in **any** dimension significantly penalizes the overall EDI. Unlike the arithmetic mean, it prevents perfect substitutability — a household cannot compensate for severe deprivation in one dimension with abundance in another. This aligns with the normative principle that all six capabilities are fundamental and non-fungible.

#### Special Case: Complete Deprivation
If any \(S_{h,d} = 0\), then \(EDI_h = 0\) — a household completely deprived in any single dimension has zero energy dignity.

---

## 3. Dimension-Level Formulation

Each dimension score \(S_{h,d}\) is itself a composite of **indicators** within that dimension. For dimension \(d\) with \(n_d\) indicators:

\[
S_{h,d} = \sum_{i=1}^{n_d} \omega_{d,i} \cdot x_{h,d,i}
\]

where:
- \(x_{h,d,i} \in [0, 1]\) is the normalized score of household \(h\) on indicator \(i\) of dimension \(d\)
- \(\omega_{d,i}\) are indicator-level weights, with \(\sum_{i=1}^{n_d} \omega_{d,i} = 1\)

### 3.1 Dimension A: Basic Access (\(S_{h,A}\))

Indicators of whether the household has a physical connection to modern energy.

| Indicator | Symbol | Data Source (India) | Normalization |
|---|---|---|---|
| Electricity connection | \(x_{h,A,1}\) | NFHS/NSSO | 1 if grid-connected, 0 otherwise |
| Clean cooking fuel access | \(x_{h,A,2}\) | NFHS/NSSO | 1 if primary fuel is LPG/PNG/electricity/biogas; 0 if biomass/kerosene/coal |
| Basic lighting adequacy | \(x_{h,A,3}\) | NFHS | 1 if ≥ 4 rooms have electric lighting; else 0.5 if 1-3 rooms; 0 if none |

\[
S_{h,A} = \omega_{A,1}\,x_{h,A,1} + \omega_{A,2}\,x_{h,A,2} + \omega_{A,3}\,x_{h,A,3}
\]

**Suggested weights:** \(\omega_{A,1}=0.4,\; \omega_{A,2}=0.4,\; \omega_{A,3}=0.2\)

### 3.2 Dimension E: Economic Affordability (\(S_{h,E}\))

Indicators of whether the household can afford sufficient energy for all needs.

| Indicator | Symbol | Data Source | Normalization |
|---|---|---|---|
| Energy expenditure ratio | \(x_{h,E,1}\) | NSSO Consumer Expenditure | \(1 - \min\left(\frac{\text{energy expenditure}}{\text{total expenditure}}, 0.15\right) \) |
| Refill affordability (LPG) | \(x_{h,E,2}\) | PMUY administrative data | 1 if ≥ 6 LPG refills/year; 0.5 if 3-5; 0 if < 3 |
| Electricity bill payment ease | \(x_{h,E,3}\) | DISCOM/survey | 1 if never missed payment; 0.5 if sometimes delayed; 0 if regularly in arrears |

\[
S_{h,E} = \omega_{E,1}\,x_{h,E,1} + \omega_{E,2}\,x_{h,E,2} + \omega_{E,3}\,x_{h,E,3}
\]

**Suggested weights:** \(\omega_{E,1}=0.4,\; \omega_{E,2}=0.35,\; \omega_{E,3}=0.25\)

### 3.3 Dimension R: Reliability & Quality (\(S_{h,R}\))

Indicators of whether energy supply is consistent and of sufficient quality.

| Indicator | Symbol | Data Source | Normalization |
|---|---|---|---|
| Hours of electricity per day | \(x_{h,R,1}\) | DISCOM data / survey | \(\min(\text{hours}/24,\;1)\) |
| Voltage stability | \(x_{h,R,2}\) | Survey | 1 if no voltage issues; 0.5 if occasional; 0 if frequent |
| Frequency of unplanned outages | \(x_{h,R,3}\) | DISCOM data / survey | \(e^{-\lambda \cdot \text{outages per month}}\), with \(\lambda = 0.2\) |

\[
S_{h,R} = \omega_{R,1}\,x_{h,R,1} + \omega_{R,2}\,x_{h,R,2} + \omega_{R,3}\,x_{h,R,3}
\]

**Suggested weights:** \(\omega_{R,1}=0.45,\; \omega_{R,2}=0.25,\; \omega_{R,3}=0.30\)

> **Note on the exponential decay function:** The function \(e^{-\lambda \cdot n}\) maps outage frequency to a \([0,1]\) score. With \(\lambda=0.2\), a household with 0 outages scores 1.0; with 5 outages per month scores 0.37; with 10 outages scores 0.14; with 15+ outages → 0.

### 3.4 Dimension H: Health & Environment (\(S_{h,H}\))

Indicators of whether the household's energy use protects health and the environment.

| Indicator | Symbol | Data Source | Normalization |
|---|---|---|---|
| Cooking location | \(x_{h,H,1}\) | NFHS | 1 if separate kitchen with ventilation; 0.5 if separate without ventilation; 0 if cooking in living area |
| Fuel type cleanliness | \(x_{h,H,2}\) | NFHS | Clean fuel ladder: Electricity=1.0, LPG/PNG=0.9, Biogas=0.8, Kerosene=0.3, Coal=0.15, Biomass/wood=0.1, Dung=0.05 |
| Indoor air quality proxy | \(x_{h,H,3}\) | NFHS | 1 if clean cooking + ventilation; 0.5 if clean cooking only; 0 if biomass cooking without ventilation |

\[
S_{h,H} = \omega_{H,1}\,x_{h,H,1} + \omega_{H,2}\,x_{h,H,2} + \omega_{H,3}\,x_{h,H,3}
\]

**Suggested weights:** \(\omega_{H,1}=0.25,\; \omega_{H,2}=0.45,\; \omega_{H,3}=0.30\)

### 3.5 Dimension P: Productive & Developmental Adequacy (\(S_{h,P}\))

Indicators of whether energy enables education, livelihood, and quality of life.

| Indicator | Symbol | Data Source | Normalization |
|---|---|---|---|
| Appliance ownership index | \(x_{h,P,1}\) | NFHS/Census | \(\min\left(\frac{\text{owned appliances}}{8},\;1\right)\) where appliances = fan, TV, fridge, washing machine, computer, iron, mixer/grinder, water pump |
| Lighting for study/education | \(x_{h,P,2}\) | Survey | 1 if dedicated study light available for children; 0 otherwise |
| Energy for productive use | \(x_{h,P,3}\) | Survey | 1 if uses energy for income generation (e.g., irrigation, shop, craft); 0.5 if wants to but cannot; 0 if no need or no capacity |

\[
S_{h,P} = \omega_{P,1}\,x_{h,P,1} + \omega_{P,2}\,x_{h,P,2} + \omega_{P,3}\,x_{h,P,3}
\]

**Suggested weights:** \(\omega_{P,1}=0.4,\; \omega_{P,2}=0.3,\; \omega_{P,3}=0.3\)

### 3.6 Dimension G: Agency & Empowerment (\(S_{h,G}\))

Indicators of whether the household has choice, control, and voice in energy matters. This dimension is the **core novelty** of the Energy Dignity framework — it captures the capability aspect that conventional energy poverty indices miss.

| Indicator | Symbol | Data Source | Normalization |
|---|---|---|---|
| Choice in primary cooking fuel | \(x_{h,G,1}\) | Survey | 1 if could freely choose; 0.5 if constrained by cost/availability; 0 if no alternative available |
| Metering & billing fairness | \(x_{h,G,2}\) | Survey | 1 if metered and bill reflects usage; 0.5 if flat rate/unmetered; 0 if no bill or disputed |
| Grievance redressal access | \(x_{h,G,3}\) | Survey | 1 if knows how to report issues and they are resolved; 0.5 if knows but issues not resolved; 0 if does not know |
| Participation in energy decisions | \(x_{h,G,4}\) | Survey | 1 if household has voice in energy-related community decisions; 0 otherwise |

\[
S_{h,G} = \omega_{G,1}\,x_{h,G,1} + \omega_{G,2}\,x_{h,G,2} + \omega_{G,3}\,x_{h,G,3} + \omega_{G,4}\,x_{h,G,4}
\]

**Suggested weights:** \(\omega_{G,1}=0.3,\; \omega_{G,2}=0.25,\; \omega_{G,3}=0.25,\; \omega_{G,4}=0.20\)

---

## 4. Recommended Baseline Weights

Drawing on the Alkire-Foster methodology literature adapted for India (Nussbaumer et al., 2012; Sadath & Acharya, 2017), and adjusting for the expanded dignity framework, the following **baseline weights** are recommended:

\[
\begin{aligned}
w_A &= 0.20 \quad \text{(Basic Access — foundational but increasingly achieved)} \\
w_E &= 0.20 \quad \text{(Affordability — critical for sustained dignity)} \\
w_R &= 0.15 \quad \text{(Reliability — quality matters post-electrification)} \\
w_H &= 0.15 \quad \text{(Health — clean energy is a right)} \\
w_P &= 0.15 \quad \text{(Productive Use — energy for flourishing)} \\
w_G &= 0.15 \quad \text{(Agency — choice and voice)}
\end{aligned}
\]

These weights can be calibrated via **expert elicitation** or **Principal Component Analysis (PCA)** on Indian household survey data for empirical validation.

---

## 5. Aggregation: National and Sub-National EDI

### 5.1 Mean EDI for a Region

For a region (state or district) with \(N\) households:

\[
EDI_{\text{region}} = \frac{1}{N} \sum_{h=1}^{N} EDI_h
\]

This gives the **average level of energy dignity** in the region.

### 5.2 Alkire-Foster Style Headcount (Supplementary)

To identify **energy-dignity deficient** households, we employ a dual-cutoff approach:

**Step 1: Deprivation cutoff per indicator.**  
For each indicator \(i\) in dimension \(d\), define a deprivation cutoff \(z_{d,i}\).  
Household \(h\) is **deprived** in that indicator if \(x_{h,d,i} < z_{d,i}\).

**Step 2: Weighted deprivation score.**  
\[
c_h = \sum_{d \in \mathcal{D}} \sum_{i=1}^{n_d} w_d \cdot \omega_{d,i} \cdot \mathbb{1}(x_{h,d,i} < z_{d,i})
\]

**Step 3: Dignity deficiency cutoff.**  
Define \(k \in [0, 1]\) as the threshold. Household \(h\) is **energy-dignity deficient** if \(c_h \geq k\).

**Step 4: Incidence.**  
\[
H = \frac{1}{N} \sum_{h=1}^{N} \mathbb{1}(c_h \geq k)
\]

**Step 5: Intensity.**  
\[
I = \frac{\sum_{h=1}^{N} c_h \cdot \mathbb{1}(c_h \geq k)}{\sum_{h=1}^{N} \mathbb{1}(c_h \geq k)}
\]

**Step 6: Adjusted Headcount Ratio (M₀).**  
\[
M_0 = H \times I
\]

This \(M_0\) is the **multidimensional energy dignity deficiency** measure, comparable to the MEPI but using dignity-aligned indicators and including the Agency dimension.

---

## 6. Suggested Deprivation Cutoffs for India

| Dimension | Indicator | Deprivation Cutoff (\(z\)) | Justification |
|---|---|---|---|
| **A** | Electricity connection | < 1 (no connection) | Saubhagya target is universal |
| **A** | Clean cooking fuel | < 1 (uses biomass) | Ujjwala target is LPG connection |
| **E** | Energy expenditure ratio | > 0.10 (>10% of spending) | International affordability benchmark |
| **E** | LPG refills per year | < 4 | PMUY average ~4.34; <4 indicates underuse |
| **R** | Daily electricity hours | < 20 hours | RDSS quality target |
| **R** | Unplanned outages/month | > 3 | More than weekly disruption |
| **H** | Fuel type | < 0.5 on cleanliness ladder | Health risk threshold |
| **H** | Cooking location | < 1 (no separate kitchen) | Indoor air pollution risk |
| **P** | Appliances owned | < 3 of 8 | Minimum for modern life |
| **P** | Study lighting | < 1 (no study light) | Education deprivation |
| **G** | Fuel choice | < 1 (constrained) | Agency deprivation |
| **G** | Grievance redressal | < 1 (no knowledge) | Voice deprivation |

---

## 7. Policy-Relevant Decompositions

### 7.1 Dimensional Contribution to Dignity Deficiency

For any region, the contribution of each dimension to overall dignity deficiency:

\[
\text{Contribution}_d = \frac{w_d \cdot \sum_{h} \sum_{i} \omega_{d,i} \cdot \mathbb{1}(x_{h,d,i} < z_{d,i})}{\sum_h c_h}
\]

This tells policymakers **which dimension causes the most dignity deficit** — enabling targeted intervention.

### 7.2 Urban vs. Rural Decomposition

\[
EDI_{\text{urban}} - EDI_{\text{rural}} = \text{Urban-Rural Dignity Gap}
\]

### 7.3 State-Level Ranking

For comparative policy analysis, states can be ranked by EDI and the gap between the highest and lowest state quantifies **geographic energy dignity inequality**.

---

## 8. Dynamic Model: Tracking Energy Dignity Over Time

To capture the evolution of energy dignity, define a **time-indexed EDI**:

\[
EDI_{h,t} = \prod_{d} \left( S_{h,d,t} \right)^{w_{d,t}}
\]

The **change in energy dignity** from \(t_0\) to \(t_1\):

\[
\Delta EDI_h = EDI_{h,t_1} - EDI_{h,t_0}
\]

A positive \(\Delta EDI\) indicates improvement. The **rate of change** of each dimension's contribution:

\[
\frac{\partial EDI}{\partial S_d} = w_d \cdot \frac{EDI}{S_d}
\]

This partial derivative reveals which dimension improvements yield the highest marginal impact on overall energy dignity — enabling **optimal policy investment**.

---

## 9. Calibration Notes for India

### 9.1 Recommended Data Sources

| Source | Agency | Useful For |
|---|---|---|
| **NFHS-6** (2020-22) | MoHFW, IIPS | Household energy use, cooking fuel, appliances, housing |
| **NSSO 78th Round** (2020-21) | MoSPI | Energy expenditure, consumption patterns |
| **India Human Development Survey (IHDS)** | NCAER/University of Maryland | Panel data on energy access and wellbeing |
| **DISCOM-level data** | MoP, State utilities | Reliability, outages, hours of supply |
| **PMUY Dashboard** | MoPNG | LPG connections and refill data |
| **CEEW ACCESS Survey** | Council on Energy, Environment and Water | Multi-tier energy access quality data |

### 9.2 Implementation Steps

```
Step 1: Select data source and extract indicator values per household
Step 2: Normalize each indicator to [0, 1] per Section 3
Step 3: Compute dimension scores \(S_{h,d}\) per household
Step 4: Compute \(EDI_h\) using weighted geometric mean
Step 5: Compute \(M_0\) using Alkire-Foster dual cutoff (Section 5.2)
Step 6: Decompose by dimension (Section 7), geography, and demographics
Step 7: Analyze \(\frac{\partial EDI}{\partial S_d}\) for policy targeting
```

---

## 10. Worked Example (Illustrative)

Consider a rural household in Uttar Pradesh with the following profile:

| Indicator | Value | Score |
|---|---|---|
| Electricity connection | Yes | 1.0 |
| Cooking fuel | LPG + occasional wood | 0.5 (proxy for partial adoption) |
| Energy expenditure ratio | 8% of total | 0.47 (1 - 0.08/0.15) |
| LPG refills/year | 3 | 0.5 |
| Electricity hours/day | 18 hours | 0.75 |
| Outages/month | 8 | \(e^{-0.2 \times 8} = 0.20\) |
| Fuel type | LPG (0.9) but mixed use | 0.7 |
| Cooking location | Separate, no window | 0.5 |
| Appliances owned | 4 of 8 | 0.5 |
| Study lighting | Yes | 1.0 |
| Fuel choice | Constrained by cost | 0.5 |
| Grievance redressal | Does not know | 0.0 |

**Dimension Scores:**
- \(S_A = 0.4(1.0) + 0.4(0.5) + 0.2(1.0) = 0.70\)
- \(S_E = 0.4(0.47) + 0.35(0.5) + 0.25(1.0) = 0.61\)
- \(S_R = 0.45(0.75) + 0.25(1.0) + 0.30(0.20) = 0.60\)
- \(S_H = 0.25(0.5) + 0.45(0.7) + 0.30(0.5) = 0.59\)
- \(S_P = 0.4(0.5) + 0.3(1.0) + 0.3(0.5) = 0.65\)
- \(S_G = 0.3(0.5) + 0.25(1.0) + 0.25(0.0) + 0.20(0.0) = 0.40\)

**EDI:**
\[
EDI_h = 0.70^{0.20} \times 0.61^{0.20} \times 0.60^{0.15} \times 0.59^{0.15} \times 0.65^{0.15} \times 0.40^{0.15}
\]
\[
EDI_h = 0.931 \times 0.907 \times 0.928 \times 0.925 \times 0.939 \times 0.870 = 0.595
\]

**Interpretation:** This household has an Energy Dignity score of **0.60 out of 1.0**. The Agency dimension is the weakest (\(S_G = 0.40\)), suggesting policy interventions should focus on empowering energy choice and establishing grievance mechanisms. The household is **energy-dignity deficient** under the Alkire-Foster method if \(k \leq 0.35\) (given multiple depriations).

---

## 11. Limitations & Future Extensions

### 11.1 Limitations
1. **Data availability:** The Agency dimension requires new survey questions not currently in NFHS/NSSO — proxy indicators may be needed initially.
2. **Weight sensitivity:** Results may be sensitive to weight choices; robustness checks (e.g., Spearman rank correlation under alternative weights) are recommended.
3. **Household vs. individual:** EDI is computed at the household level; intra-household gender disparities (e.g., women bearing cooking burden) are not captured.

### 11.2 Future Extensions
1. **Gender-disaggregated EDI (G-EDI):** Separate indicators for the energy burden experienced by women within the household.
2. **Climate-adjusted EDI:** Incorporate the carbon footprint of household energy use to ensure dignity does not come at the cost of climate justice.
3. **Community-level EDI:** Add indicators for community infrastructure (e.g., street lighting, village-level mini-grid reliability).
4. **Predictive EDI:** Use machine learning on panel data to predict households at risk of energy dignity decline.

---

## 12. Conclusion

This model provides a mathematically rigorous framework for measuring **Energy Dignity** — a concept that goes beyond counting connections or kilowatt-hours. By grounding the index in the **capability approach** and building on established multidimensional poverty measurement methodology, the EDI captures the **real freedom** of India's countrymen to use energy to live lives they have reason to value.

The addition of the **Agency dimension** is the key innovation — it recognizes that dignity is not merely about receiving energy services, but about having **choice, control, and voice** in energy decisions. This is particularly resonant in a rapidly electrifying India where the focus has shifted from access-to-grid to access-to-dignity.

---

## References

1. Alkire, S., & Foster, J. (2011). Counting and multidimensional poverty measurement. *Journal of Public Economics*, 95(7-8), 476-487.
2. Nussbaumer, P., Bazilian, M., Modi, V., & Yumkella, K. K. (2012). Measuring energy poverty: Focusing on what matters. *Renewable and Sustainable Energy Reviews*, 16(1), 231-243.
3. Sadath, A. C., & Acharya, R. H. (2017). Assessing the extent and intensity of energy poverty using Multidimensional Energy Poverty Index: Empirical evidence from households in India. *Energy Policy*, 102, 540-550.
4. Sen, A. (1999). *Development as Freedom*. Oxford University Press.
5. Gupta, R., & Sarangi, G. K. (2020). Household Energy Poverty Index (HEPI) for India: An analysis of inter-state differences. *Energy for Sustainable Development*, 59, 63-73.
6. Przybylinski, S., & Sidortsov, R. (2023). The Capabilities Approach. In *Theorising Justice: A Primer for Social Scientists*. Bristol University Press.
7. Ministry of Petroleum and Natural Gas, Government of India. PMUY Dashboard and Annual Reports (2024-25).
8. Council on Energy, Environment and Water (CEEW). ACCESS Survey Series on Energy Access in India.
