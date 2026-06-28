# Marketing A/B Test Analysis

![Python](https://img.shields.io/badge/Python-3.9-blue) ![scipy](https://img.shields.io/badge/scipy-1.11-green) ![SQL](https://img.shields.io/badge/SQL-SQLite-lightgrey)

Statistical analysis of a marketing A/B test across 588,000+ users to determine whether real advertisements drive higher conversion rates compared to Public Service Announcements (PSAs). Uses chi-square hypothesis testing, confidence intervals, and exploratory segmentation.

---

## Table of Contents
- [Overview](#overview)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Setup & Usage](#setup--usage)
- [Results](#results)
- [Visualizations](#visualizations)
- [Tech Stack](#tech-stack)

---

## Overview

A/B testing is the gold standard for measuring the causal impact of a change. This project analyzes a real marketing experiment where users were randomly assigned to see either an ad or a PSA. The goal is to determine, with statistical confidence, whether the ads actually work.

**Business Questions Answered:**
- Do ads lead to significantly more conversions than PSAs?
- Is the result statistically significant or just random variation?
- What days and hours produce the highest conversion rates?
- Does ad exposure frequency affect conversion likelihood?

---

## Dataset

| Property | Value |
|---|---|
| Source | [Marketing A/B Testing — Kaggle (faviovaz)](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing) |
| Records | 588,101 users |
| Groups | Ad (564,577 users) vs PSA (23,524 users) |
| Target | Converted (True / False) |

> **Note:** Download `marketing_AB.csv` from the link above and place it in the `data/` folder before running.

---

## Project Structure

```
ab_test_project/
├── data/
│   ├── marketing_AB.csv          # raw dataset (download separately)
│   └── ab_test.db                # generated after running analysis.py
├── sql/
│   └── queries.sql               # 8 SQL queries
├── visuals/                      # charts saved after running analysis.py
├── analysis.py                   # main analysis script
├── requirements.txt
└── README.md
```

---

## Setup & Usage

**1. Clone the repository**
```bash
git clone https://github.com/srijanagni/ab-test-analysis.git
cd ab-test-analysis
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Download the dataset**

Download `marketing_AB.csv` from [Kaggle](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing) and place it in the `data/` folder.

**4. Run the analysis**
```bash
python3 analysis.py
```

Outputs: visualizations in `visuals/`, SQLite database in `data/`, full results printed to console.

---

## Results

### Conversion Rates

| Group | Users | Conversions | Rate |
|---|---|---|---|
| Ad | 564,577 | 14,423 | 2.55% |
| PSA | 23,524 | 420 | 1.79% |

### Statistical Test

| Metric | Value |
|---|---|
| Test | Chi-square |
| Chi-square statistic | 54.0 |
| P-value | < 0.000001 |
| Result | Reject H₀ — ads significantly outperform PSAs |
| 95% Confidence Interval | [0.60%, 0.94%] |
| Relative Lift | +43.09% |

### Peak Performance Windows

| Dimension | Best Performer |
|---|---|
| Day of week | Monday (3.32%), Tuesday (3.04%) |
| Hour of day | 4pm – 8pm |
| Ad frequency | 100–199 ads → 17.7% conversion rate |

---

## Visualizations

| Chart | Description |
|---|---|
| `conversion_rate_by_group.png` | Side-by-side conversion rate comparison |
| `conversion_by_day.png` | Conversion rate by day of week |
| `conversion_by_hour.png` | Conversion rate by hour |
| `total_ads_distribution.png` | Distribution of ad exposure |
| `heatmap_day_hour.png` | Heatmap of conversion rate by day and hour |
| `group_size.png` | Group size comparison |

---

## Tech Stack

- **Python** — pandas, NumPy, scipy, matplotlib, seaborn
- **SQL** — SQLite (via Python's `sqlite3`)
- **Statistics** — Chi-square test, confidence intervals, conversion rate analysis
