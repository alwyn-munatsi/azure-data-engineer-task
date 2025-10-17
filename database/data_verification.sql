--- Query 1: Check Submissions
SELECT COUNT(*) as total_submissions FROM Submissions;

--- Query 2: Check Scores
SELECT COUNT(*) as total_scores FROM SubmissionScores;

--- Query 3: View Sample Data
SELECT TOP 5 * FROM Submissions;