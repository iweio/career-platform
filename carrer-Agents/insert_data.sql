INSERT INTO promotion_transition (current_role, next_role, required_skills, years_exp, transition_type) VALUES
('Python Backend Dev', 'Senior Backend Engineer', '{"skills": ["System design", "Team management"]}', 3, 'promotion'),
('Python Backend Dev', 'Tech Lead', '{"skills": ["Architecture design", "Technical planning"]}', 5, 'promotion'),
('Java Developer', 'Senior Java Engineer', '{"skills": ["Microservices", "Performance optimization"]}', 3, 'promotion');

SELECT * FROM promotion_transition;
