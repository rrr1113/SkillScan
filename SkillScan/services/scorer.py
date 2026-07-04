
def score(has_skills, needed_skills):
    total = 0
    earned = 0

    for ns in needed_skills:
        points = ns.points if ns.points is not None else 1
        total += points

        if ns.skill in has_skills:
            earned += points

    print(round((earned / total) * 100, 2) if total else 0)
    return round((earned / total) * 100, 2) if total else 0

