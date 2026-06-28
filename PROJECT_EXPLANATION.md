# Project Explanation — A/B Test Analysis

This document explains what the project does and why, in plain English. Use this to explain the project in interviews.

---

## What is an A/B Test?

An A/B test is an experiment where you split users into two groups:
- **Group A (Control):** Gets the original version (in this case, a Public Service Announcement / PSA)
- **Group B (Treatment):** Gets the new version (a real advertisement)

Then you measure whether the treatment group behaves differently — in this case, whether they **converted** (made a purchase or signed up).

---

## The Business Question

> Did showing real ads to users result in more conversions compared to showing a PSA?

The company ran this experiment to decide whether to continue spending money on ads or switch to PSAs.

---

## The Dataset

- **588,101 users** split across two groups
- **Ad group:** 564,577 users who saw real ads
- **PSA group:** 23,524 users who saw public service announcements
- Each row represents one user
- We know: how many ads they saw, which day and hour they saw the most ads, and whether they converted

---

## Step-by-Step Walkthrough

### Step 1 — Load the Data
Load the CSV into Python using pandas. Check the shape, column names, data types, and whether there are missing values. There were no missing values in this dataset.

### Step 2 — Clean the Data
- Renamed columns to remove spaces (e.g., "test group" → "test_group")
- Converted `converted` from True/False to 1/0 so we can do math on it
- Removed duplicate users (same user appearing twice)

### Step 3 — Conversion Rate Analysis
Calculate what percentage of each group converted:
- **Ad group:** 2.55% converted
- **PSA group:** 1.79% converted
- **Absolute lift:** +0.77 percentage points
- **Relative lift:** 43% — the ad group converted 43% more than the PSA group

### Step 4 — Chi-Square Hypothesis Test
This is the core statistical test. The question is: *is the difference in conversion rates real, or could it just be random chance?*

We set up:
- **Null hypothesis (H₀):** There is no real difference — any variation is due to chance
- **Alternative hypothesis (H₁):** Ads genuinely increase conversions

The chi-square test compares how many conversions we **observed** in each group versus how many we would **expect** if ads had no effect.

**Result:**
- Chi-square statistic: 54.0 (a large number means the observed and expected counts are very different)
- **P-value: < 0.000001** — this means there is less than a 0.0001% chance the result is due to random chance
- Since p < 0.05 (our threshold), we **reject the null hypothesis**
- **Conclusion: The ads work.**

### Step 5 — Confidence Interval
A confidence interval tells us the range within which the true effect likely falls.

**95% CI: [0.60%, 0.94%]**

This means we are 95% confident the true difference between ad and PSA conversion rates is between 0.60 and 0.94 percentage points. Since the entire interval is above 0, we are confident ads outperform PSAs.

### Step 6 — Exploratory Analysis (Visualizations)
We looked for patterns in when and how much exposure drives conversions:
- **Best days:** Monday and Tuesday see the highest conversion rates
- **Best hours:** 4pm–8pm (users are more likely to convert in the evening)
- **Ad frequency:** Users who saw 50–199 ads had dramatically higher conversion rates (11–18%) vs those who saw fewer than 10 ads (0.3%)

### Step 7 — SQL Analysis
We loaded the data into SQLite and ran 8 queries to:
- Confirm conversion rates by group
- Find the best days and hours
- Segment users by ad exposure volume
- Compare weekday vs weekend performance
- Identify peak hour performance (4pm–8pm)

### Step 8 — Final Summary
Printed a clean summary with all key numbers, the statistical test result, and a clear conclusion.

---

## What the Results Mean for the Business

1. **Keep running the ads** — they are statistically proven to increase conversions by 43% relative to PSAs
2. **Schedule ads on Monday and Tuesday** — these days have the highest conversion rates
3. **Focus ad delivery between 4pm and 8pm** — evening hours consistently outperform
4. **Increase ad frequency** — users who saw 50–199 ads converted at 11–18%, vs 0.3% for users who barely saw any ads. There's a strong dose-response relationship.

---

## Why This Project is Interview-Relevant

- Shows you understand **hypothesis testing** and can explain p-values clearly
- Demonstrates **business thinking** — not just running stats but interpreting what they mean
- **Chi-square test** is one of the most commonly asked-about stats tests in data analyst interviews
- **Confidence intervals** show you know the difference between "statistically significant" and "practically meaningful"
- The SQL + Python combination is exactly what analysts do at companies like ZS Associates and HCL
