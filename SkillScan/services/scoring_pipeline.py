from SkillScan.services.parse_parser import extract_cv
from SkillScan.services.skill_extractor import extract_skills
from SkillScan.services.scorer import score


def calcultate_score(cv, needed_skills):
    cv_raw_text = extract_cv(cv)
    has_skills = extract_skills(cv_raw_text)
    return score(has_skills, needed_skills)
