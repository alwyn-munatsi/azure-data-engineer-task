-- Azure SQL Database Schema for Stability Evaluation App

-- 1. Indicator definitions table
CREATE TABLE Indicators (
    indicator_id INT IDENTITY(1,1) PRIMARY KEY,
    indicator_name NVARCHAR(100) NOT NULL,
    indicator_description NVARCHAR(500),
    display_order INT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- 2. Age ranges lookup table
CREATE TABLE AgeRanges (
    age_range_id INT IDENTITY(1,1) PRIMARY KEY,
    age_range_label NVARCHAR(20) NOT NULL UNIQUE
);

-- 3. Regions lookup table  
CREATE TABLE Regions (
    region_id INT IDENTITY(1,1) PRIMARY KEY,
    region_name NVARCHAR(50) NOT NULL UNIQUE
);

-- 4. Main submissions table
CREATE TABLE Submissions (
    submission_id UNIQUEIDENTIFIER PRIMARY KEY,
    created_at DATETIME2 NOT NULL,
    age_range_id INT,
    region_id INT,
    instability_ratio DECIMAL(5,2),
    first_name NVARCHAR(100),
    last_name NVARCHAR(100),
    email NVARCHAR(255),
    FOREIGN KEY (age_range_id) REFERENCES AgeRanges(age_range_id),
    FOREIGN KEY (region_id) REFERENCES Regions(region_id)
);

-- 5. Submission scores table
CREATE TABLE SubmissionScores (
    score_id INT IDENTITY(1,1) PRIMARY KEY,
    submission_id UNIQUEIDENTIFIER NOT NULL,
    indicator_id INT NOT NULL,
    score_value INT CHECK (score_value >= 0 AND score_value <= 100),
    FOREIGN KEY (submission_id) REFERENCES Submissions(submission_id) ON DELETE CASCADE,
    FOREIGN KEY (indicator_id) REFERENCES Indicators(indicator_id),
    UNIQUE (submission_id, indicator_id)
);

-- 6. Report requests table
CREATE TABLE ReportRequests (
    request_id INT IDENTITY(1,1) PRIMARY KEY,
    submission_id UNIQUEIDENTIFIER NOT NULL,
    email_sent_at DATETIME2,
    report_generated_at DATETIME2,
    status NVARCHAR(20) DEFAULT 'pending',
    FOREIGN KEY (submission_id) REFERENCES Submissions(submission_id)
);

-- 7. Insert default data
INSERT INTO Indicators (indicator_name, indicator_description, display_order) VALUES
('Economic Management', 'Evaluation of economic policies and management', 1),
('Immigration Policy', 'Assessment of immigration policies and implementation', 2), 
('Foreign Policy', 'Evaluation of international relations and foreign policy', 3),
('Domestic Policy', 'Assessment of domestic governance and policies', 4),
('Social Policy', 'Evaluation of social welfare and community policies', 5);

INSERT INTO AgeRanges (age_range_label) VALUES
('18-24'), ('25-34'), ('35-44'), ('45-54'), ('55-64'), ('65+');

INSERT INTO Regions (region_name) VALUES
('northeast'), ('midwest'), ('southeast'), ('southwest'), ('west');

-- 8. Create indexes for performance
CREATE INDEX IX_Submissions_Email ON Submissions(email);
CREATE INDEX IX_Submissions_CreatedAt ON Submissions(created_at);
CREATE INDEX IX_SubmissionScores_Submission ON SubmissionScores(submission_id);