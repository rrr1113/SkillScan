import re


def extract_skills(needed_skills, cv_raw_text):
    skills_cv = []
    cv_raw_text = cv_raw_text.lower()

    for skill in needed_skills:
        if re.search(rf"(?<![a-zA-Z0-9]){re.escape(skill.lower())}(?![a-zA-Z0-9])", cv_raw_text):
            skills_cv.append(skill)
            print(skill)

    return skills_cv


extract_skills(["a", "B", "d", "C++"], "I have the skill A and C++")