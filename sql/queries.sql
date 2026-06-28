-- ─────────────────────────────────────────────
-- A/B Test Analysis — Marketing Campaign
-- Database: SQLite (ab_test.db)
-- Table: ab_test
-- ─────────────────────────────────────────────


-- ── 1. Overall Conversion Rate by Group ──
SELECT
    test_group,
    COUNT(*)                                           AS total_users,
    SUM(converted)                                     AS conversions,
    ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
FROM ab_test
GROUP BY test_group;


-- ── 2. Conversion Rate by Day of Week ──
SELECT
    most_ads_day,
    test_group,
    COUNT(*)                                           AS users,
    ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
FROM ab_test
GROUP BY most_ads_day, test_group
ORDER BY most_ads_day;


-- ── 3. Best Hours for Ad Conversion (Top 5) ──
SELECT
    most_ads_hour,
    COUNT(*)                                           AS users,
    ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
FROM ab_test
WHERE test_group = 'ad'
GROUP BY most_ads_hour
ORDER BY conversion_rate_pct DESC
LIMIT 5;


-- ── 4. Conversion Rate by Ads Volume Bucket ──
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
ORDER BY MIN(total_ads);


-- ── 5. High Exposure Users (Converted vs Not) ──
SELECT
    test_group,
    COUNT(*)                                           AS high_exposure_users,
    ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
FROM ab_test
WHERE total_ads > 100
GROUP BY test_group;


-- ── 6. Weekend vs Weekday Conversion ──
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
ORDER BY day_type, test_group;


-- ── 7. Peak Hour Conversion (Ad Group, 4pm–8pm) ──
SELECT
    most_ads_hour,
    COUNT(*)                                           AS users,
    SUM(converted)                                     AS conversions,
    ROUND(SUM(converted) * 100.0 / COUNT(*), 4)       AS conversion_rate_pct
FROM ab_test
WHERE test_group = 'ad'
  AND most_ads_hour BETWEEN 16 AND 20
GROUP BY most_ads_hour
ORDER BY most_ads_hour;


-- ── 8. Overall Summary ──
SELECT
    COUNT(DISTINCT user_id)                               AS total_users,
    SUM(CASE WHEN test_group = 'ad'  THEN 1 ELSE 0 END)  AS ad_group_size,
    SUM(CASE WHEN test_group = 'psa' THEN 1 ELSE 0 END)  AS psa_group_size,
    SUM(converted)                                        AS total_conversions,
    ROUND(SUM(converted) * 100.0 / COUNT(*), 4)          AS overall_conversion_rate_pct
FROM ab_test;
