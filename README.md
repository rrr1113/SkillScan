# SkillScan

## Overview
SkillScan is a Django-based platform that analyzes CVs and matches them with job postings using a relational database design. The system supports CV parsing, skill extraction, job management, and candidate-job matching based on skill compatibility.

## Features
- CV upload and storage
- Automatic skill extraction from CVs 
- Job posting management
- Skill-based matching between CVs and jobs
- Company and location management
- Match scoring system between CVs and Jobs

## Technologies
- Python
- Django
- PostgreSQL
- spaCy
- SkillNER
- Bootstrap
- HTML/CSS

## Database Design
Core models:
- Skill
- CV
- Location
- Company
- CompanyMember
- Job
- Application
- SkillCv (CV <-> Skill)
- SkillJob (Job <-> Skill)
- JobLocation (Job <-> Location)
- SkillMatch (matching scores)

