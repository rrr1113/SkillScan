import spacy
from skillNer.skill_extractor_class import SkillExtractor
from skillNer.general_params import SKILL_DB
from spacy.matcher import PhraseMatcher


def extract_skills(cv_raw_text):
    nlp = spacy.load("en_core_web_lg")

    skill_extractor = SkillExtractor(
        nlp,
        SKILL_DB,
        PhraseMatcher
    )

    annotations = skill_extractor.annotate(cv_raw_text)
    print(annotations)
    print(annotations["results"]["ngram_scored"][1]["doc_node_value"])

    skills = set()

    for item in annotations["results"]["full_matches"]:
        skills.add(item["doc_node_value"])
        print(item["doc_node_value"])

    for item in annotations["results"]["ngram_scored"]:
        skills.add(item["doc_node_value"])
        print(item["doc_node_value"])

    return sorted(skills)


