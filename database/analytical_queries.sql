-- 1. Average scores per indicator
SELECT 
    i.indicator_name,
    AVG(ss.score_value) as average_score,
    COUNT(ss.score_value) as response_count
FROM SubmissionScores ss
JOIN Indicators i ON ss.indicator_id = i.indicator_id
GROUP BY i.indicator_id, i.indicator_name
ORDER BY i.indicator_id;

-- 2. Average scores by region  
SELECT 
    r.region_name,
    i.indicator_name,
    AVG(ss.score_value) as average_score
FROM SubmissionScores ss
JOIN Submissions s ON ss.submission_id = s.submission_id
JOIN Regions r ON s.region_id = r.region_id
JOIN Indicators i ON ss.indicator_id = i.indicator_id
GROUP BY r.region_name, i.indicator_name
ORDER BY r.region_name, i.indicator_name;

-- 3. Recent submissions with email
SELECT 
    email,
    first_name,
    last_name, 
    created_at,
    instability_ratio
FROM Submissions 
WHERE email IS NOT NULL
ORDER BY created_at DESC;