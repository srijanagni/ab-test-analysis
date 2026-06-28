import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import sqlite3
import os
from scipy import stats
from scipy.stats import chi2_contingency
import numpy as np

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

DATA_PATH    = "data/marketing_AB.csv"
VISUALS_PATH = "visuals/"
DB_PATH      = "data/ab_test.db"

os.makedirs(VISUALS_PATH, exist_ok=True)
os.makedirs("data", exist_ok=True)

# ─────────────────────────────────────────────
# STEP 1: LOAD DATA
# ─────────────────────────────────────────────

print("=" * 55)
print("  A/B TEST ANALYSIS — MARKETING CAMPAIGN")
print("=" * 55)

print("\nLoading data...")
df = pd.read_csv(DATA_PATH, index_col=0)
print(f"Shape: {df.shape}")
print(df.head())
print("\nColumns:", df.columns.tolist())
print("\nData types:\n", df.dtypes)
print("\nMissing values:\n", df.isnull().sum())
print("\nTest group distribution:\n", df["test group"].value_counts())
print("\nConverted distribution:\n", df["converted"].value_counts())

# ─────────────────────────────────────────────
# STEP 2: CLEAN & PREPARE
# ─────────────────────────────────────────────

print("\nCleaning data...")

df = df.rename(columns={
    "user id":       "user_id",
    "test group":    "test_group",
    "total ads":     "total_ads",
    "most ads day":  "most_ads_day",
    "most ads hour": "most_ads_hour"
})

# Convert converted to int (True=1, False=0)
df["converted"] = df["converted"].astype(int)

# Drop duplicates
df = df.drop_duplicates(subset="user_id")

print(f"Cleaned shape: {df.shape}")
print(df.head())

# ─────────────────────────────────────────────
# STEP 3: CONVERSION RATE ANALYSIS
# ─────────────────────────────────────────────

print("\n" + "─" * 45)
print("STEP 3: CONVERSION RATE ANALYSIS")
print("─" * 45)

group_stats = df.groupby("test_group")["converted"].agg(
    total="count",
    conversions="sum"
)
group_stats["conversion_rate_pct"] = (group_stats["conversions"] / group_stats["total"] * 100).round(4)

print(group_stats)

ad_rate  = group_stats.loc["ad",  "conversion_rate_pct"]
psa_rate = group_stats.loc["psa", "conversion_rate_pct"]
lift     = ad_rate - psa_rate

print(f"\nAd group conversion rate:  {ad_rate:.4f}%")
print(f"PSA group conversion rate: {psa_rate:.4f}%")
print(f"Absolute lift:             {lift:.4f} percentage points")
print(f"Relative lift:             {lift / psa_rate * 100:.2f}%")

# ─────────────────────────────────────────────
# STEP 4: STATISTICAL SIGNIFICANCE — CHI-SQUARE TEST
# ─────────────────────────────────────────────

print("\n" + "─" * 45)
print("STEP 4: CHI-SQUARE TEST")
print("─" * 45)

ad_conv   = group_stats.loc["ad",  "conversions"]
ad_total  = group_stats.loc["ad",  "total"]
psa_conv  = group_stats.loc["psa", "conversions"]
psa_total = group_stats.loc["psa", "total"]

contingency_table = np.array([
    [ad_conv,  ad_total  - ad_conv],
    [psa_conv, psa_total - psa_conv]
])

chi2, p_value, dof, expected = chi2_contingency(contingency_table)

print(f"\nContingency Table:")
print(f"           Converted  Not Converted")
print(f"  Ad:      {ad_conv:>9,}  {ad_total - ad_conv:>13,}")
print(f"  PSA:     {psa_conv:>9,}  {psa_total - psa_conv:>13,}")
print(f"\nChi-square statistic: {chi2:.4f}")
print(f"Degrees of freedom:   {dof}")
print(f"P-value:              {p_value:.6f}")
print(f"Significance level:   0.05")

if p_value < 0.05:
    print(f"\nResult: STATISTICALLY SIGNIFICANT (p={p_value:.6f} < 0.05)")
    print("The ad campaign had a real effect on conversion — NOT due to chance.")
else:
    print(f"\nResult: NOT STATISTICALLY SIGNIFICANT (p={p_value:.6f} >= 0.05)")
    print("Cannot conclude the ad campaign made a difference.")

# ─────────────────────────────────────────────
# STEP 5: CONFIDENCE INTERVAL
# ─────────────────────────────────────────────

print("\n" + "─" * 45)
print("STEP 5: 95% CONFIDENCE INTERVAL FOR CONVERSION RATE DIFFERENCE")
print("─" * 45)

p1 = ad_conv  / ad_total
p2 = psa_conv / psa_total

se = np.sqrt(p1 * (1 - p1) / ad_total + p2 * (1 - p2) / psa_total)
z  = 1.96  # 95% CI
ci_lower = (p1 - p2 - z * se) * 100
ci_upper = (p1 - p2 + z * se) * 100

print(f"\n95% Confidence Interval for (Ad rate - PSA rate):")
print(f"  [{ci_lower:.4f}%, {ci_upper:.4f}%]")

if ci_lower > 0:
    print("  The CI is entirely above 0 → Ads perform better with 95% confidence.")
elif ci_upper < 0:
    print("  The CI is entirely below 0 → PSA performs better with 95% confidence.")
else:
    print("  The CI crosses 0 → Inconclusive at 95% confidence.")

# ─────────────────────────────────────────────
# STEP 6: EDA — VISUALIZATIONS
# ─────────────────────────────────────────────

print("\nGenerating visualizations...")

sns.set_style("whitegrid")
PALETTE = {"ad": "#2196F3", "psa": "#FF5722"}

# ── 6.1 Conversion Rate by Group ──
fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(
    ["Ad Group", "PSA Group"],
    [ad_rate, psa_rate],
    color=["#2196F3", "#FF5722"],
    width=0.5
)
ax.set_title("Conversion Rate: Ad vs PSA Group", fontsize=14, fontweight="bold")
ax.set_ylabel("Conversion Rate (%)")
ax.set_ylim(0, max(ad_rate, psa_rate) * 1.3)
for bar, val in zip(bars, [ad_rate, psa_rate]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
            f"{val:.2f}%", ha="center", fontweight="bold", fontsize=12)
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}conversion_rate_by_group.png", dpi=150)
plt.close()
print("Saved: conversion_rate_by_group.png")

# ── 6.2 Group Size Distribution ──
fig, ax = plt.subplots(figsize=(7, 5))
counts = df["test_group"].value_counts()
bars = ax.bar(
    ["Ad Group", "PSA Group"],
    [counts.get("ad", 0), counts.get("psa", 0)],
    color=["#2196F3", "#FF5722"],
    width=0.5
)
ax.set_title("Group Size: Ad vs PSA", fontsize=14, fontweight="bold")
ax.set_ylabel("Number of Users")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
for bar, val in zip(bars, [counts.get("ad", 0), counts.get("psa", 0)]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 500,
            f"{val:,}", ha="center", fontweight="bold")
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}group_size.png", dpi=150)
plt.close()
print("Saved: group_size.png")

# ── 6.3 Conversion Rate by Day of Week ──
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_conv = df.groupby(["most_ads_day", "test_group"])["converted"].mean() * 100
day_conv = day_conv.reset_index()
day_conv["most_ads_day"] = pd.Categorical(day_conv["most_ads_day"], categories=day_order, ordered=True)
day_conv = day_conv.sort_values("most_ads_day")

fig, ax = plt.subplots(figsize=(11, 5))
for group, color in PALETTE.items():
    subset = day_conv[day_conv["test_group"] == group]
    ax.plot(subset["most_ads_day"], subset["converted"], marker="o",
            label=group.upper(), color=color, linewidth=2)
ax.set_title("Conversion Rate by Day of Week", fontsize=14, fontweight="bold")
ax.set_xlabel("Day")
ax.set_ylabel("Conversion Rate (%)")
ax.legend()
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}conversion_by_day.png", dpi=150)
plt.close()
print("Saved: conversion_by_day.png")

# ── 6.4 Conversion Rate by Hour of Day ──
hour_conv = df.groupby(["most_ads_hour", "test_group"])["converted"].mean() * 100
hour_conv = hour_conv.reset_index()

fig, ax = plt.subplots(figsize=(13, 5))
for group, color in PALETTE.items():
    subset = hour_conv[hour_conv["test_group"] == group]
    ax.plot(subset["most_ads_hour"], subset["converted"], marker="o",
            label=group.upper(), color=color, linewidth=2)
ax.set_title("Conversion Rate by Hour of Day", fontsize=14, fontweight="bold")
ax.set_xlabel("Hour (24h)")
ax.set_ylabel("Conversion Rate (%)")
ax.set_xticks(range(0, 24))
ax.legend()
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}conversion_by_hour.png", dpi=150)
plt.close()
print("Saved: conversion_by_hour.png")

# ── 6.5 Total Ads Distribution (converted vs not) ──
fig, ax = plt.subplots(figsize=(10, 5))
ad_group = df[df["test_group"] == "ad"]
ad_group[ad_group["converted"] == 0]["total_ads"].clip(upper=200).hist(
    bins=50, alpha=0.6, color="#2196F3", label="Not Converted", ax=ax)
ad_group[ad_group["converted"] == 1]["total_ads"].clip(upper=200).hist(
    bins=50, alpha=0.6, color="#FF5722", label="Converted", ax=ax)
ax.set_title("Total Ads Seen: Converted vs Not Converted (Ad Group)", fontsize=13, fontweight="bold")
ax.set_xlabel("Total Ads Seen (capped at 200)")
ax.set_ylabel("Number of Users")
ax.legend()
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}total_ads_distribution.png", dpi=150)
plt.close()
print("Saved: total_ads_distribution.png")

# ── 6.6 Heatmap: Conversion Rate by Day and Hour (Ad group only) ──
pivot = ad_group.groupby(["most_ads_day", "most_ads_hour"])["converted"].mean() * 100
pivot = pivot.unstack(level="most_ads_hour")
pivot = pivot.reindex(day_order)

fig, ax = plt.subplots(figsize=(16, 6))
sns.heatmap(pivot, cmap="YlOrRd", ax=ax, linewidths=0.3,
            cbar_kws={"label": "Conversion Rate (%)"})
ax.set_title("Conversion Rate Heatmap — Ad Group (Day × Hour)", fontsize=13, fontweight="bold")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Day of Week")
plt.tight_layout()
plt.savefig(f"{VISUALS_PATH}heatmap_day_hour.png", dpi=150)
plt.close()
print("Saved: heatmap_day_hour.png")

# ─────────────────────────────────────────────
# STEP 7: SQL ANALYSIS
# ─────────────────────────────────────────────

print("\n" + "─" * 45)
print("STEP 7: SQL ANALYSIS")
print("─" * 45)

conn = sqlite3.connect(DB_PATH)
df.to_sql("ab_test", conn, if_exists="replace", index=False)
print("Data loaded into SQLite.")

queries = {
    "Overall Conversion Rate by Group": """
        SELECT
            test_group,
            COUNT(*)                                           AS total_users,
            SUM(converted)                                     AS conversions,
            ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
        FROM ab_test
        GROUP BY test_group
    """,
    "Conversion Rate by Day of Week": """
        SELECT
            most_ads_day,
            test_group,
            COUNT(*)                                           AS users,
            ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
        FROM ab_test
        GROUP BY most_ads_day, test_group
        ORDER BY most_ads_day
    """,
    "Best Hours for Ad Conversion": """
        SELECT
            most_ads_hour,
            COUNT(*)                                           AS users,
            ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
        FROM ab_test
        WHERE test_group = 'ad'
        GROUP BY most_ads_hour
        ORDER BY conversion_rate_pct DESC
        LIMIT 5
    """,
    "Conversion Rate by Ads Volume Bucket": """
        SELECT
            CASE
                WHEN total_ads < 10  THEN '0-9 ads'
                WHEN total_ads < 50  THEN '10-49 ads'
                WHEN total_ads < 100 THEN '50-99 ads'
                WHEN total_ads < 200 THEN '100-199 ads'
                ELSE '200+ ads'
            END AS ads_bucket,
            COUNT(*)                                           AS users,
            ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
        FROM ab_test
        WHERE test_group = 'ad'
        GROUP BY ads_bucket
        ORDER BY MIN(total_ads)
    """,
    "High Value Users (Converted + High Ad Exposure)": """
        SELECT
            test_group,
            COUNT(*)                                           AS high_exposure_users,
            ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
        FROM ab_test
        WHERE total_ads > 100
        GROUP BY test_group
    """,
    "Weekend vs Weekday Conversion": """
        SELECT
            CASE
                WHEN most_ads_day IN ('Saturday', 'Sunday') THEN 'Weekend'
                ELSE 'Weekday'
            END AS day_type,
            test_group,
            COUNT(*)                                           AS users,
            ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
        FROM ab_test
        GROUP BY day_type, test_group
        ORDER BY day_type, test_group
    """,
    "Peak Hour Conversion (Ad Group, 4pm-8pm)": """
        SELECT
            most_ads_hour,
            COUNT(*)                                           AS users,
            SUM(converted)                                     AS conversions,
            ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
        FROM ab_test
        WHERE test_group = 'ad'
          AND most_ads_hour BETWEEN 16 AND 20
        GROUP BY most_ads_hour
        ORDER BY most_ads_hour
    """,
    "Overall Summary": """
        SELECT
            COUNT(DISTINCT user_id)                            AS total_users,
            SUM(CASE WHEN test_group = 'ad'  THEN 1 ELSE 0 END) AS ad_group_size,
            SUM(CASE WHEN test_group = 'psa' THEN 1 ELSE 0 END) AS psa_group_size,
            SUM(converted)                                     AS total_conversions,
            ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS overall_conversion_rate_pct
        FROM ab_test
    """
}

for name, query in queries.items():
    print(f"\n── {name} ──")
    try:
        result = pd.read_sql_query(query, conn)
        print(result.to_string(index=False))
    except Exception as e:
        print(f"  Skipped: {e}")

conn.close()

# ─────────────────────────────────────────────
# STEP 8: FINAL SUMMARY
# ─────────────────────────────────────────────

print("\n" + "=" * 55)
print("  FINAL RESULTS SUMMARY")
print("=" * 55)
print(f"\n  Ad group size:             {ad_total:,}")
print(f"  PSA group size:            {psa_total:,}")
print(f"  Ad conversion rate:        {ad_rate:.4f}%")
print(f"  PSA conversion rate:       {psa_rate:.4f}%")
print(f"  Absolute lift:             +{lift:.4f} pp")
print(f"  Relative lift:             +{lift / psa_rate * 100:.2f}%")
print(f"  Chi-square statistic:      {chi2:.4f}")
print(f"  P-value:                   {p_value:.6f}")
print(f"  95% CI for difference:     [{ci_lower:.4f}%, {ci_upper:.4f}%]")
print(f"\n  CONCLUSION: {'STATISTICALLY SIGNIFICANT — ads worked.' if p_value < 0.05 else 'NOT SIGNIFICANT — ads did not show measurable effect.'}")
print("\nAll done! Check the visuals/ folder.")
