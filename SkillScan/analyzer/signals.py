from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver

from .models import *
from services.parse_parser import extract_cv
from services.skill_extractor import extract_skills

# CV -----------------------------------------------------
@receiver(pre_save, sender=CV)
def updating_skills_for_cv(sender, instance, *args, **kwargs):
    if not instance.pk:
        cv_raw_text = extract_cv(instance.file)
        skills = extract_skills(cv_raw_text)

        for skill in skills:
            SkillCv.objects.create(cv=instance, skill=skill)

    else:
        old_instance = CV.objects.get(pk=instance.pk)
        if old_instance.file != instance.file:
            SkillCv.objects.filter(cv=old_instance).delete()

            cv_raw_text = extract_cv(instance.file)
            skills = extract_skills(cv_raw_text)
            for skill in skills:
                SkillCv.objects.create(cv=instance, skill=skill)


@receiver(pre_delete, sender=CV)
def updating_skills_for_cv(sender, instance, *args, **kwargs):
    SkillCv.objects.filter(cv=instance).delete()




# SkillMatch -------------------------------------------------
@receiver(post_save, sender=SkillMatch)
def updating_status(sender, instance, *args, **kwargs):
    application = Application.objects.filter(id=instance.application.id).first()
    company = Company.objects.filter(id=instance.application.job.company.id).first()
    company_member = CompanyMember.objects.filter(company=company, user=instance.created_by).first()

    if application.status == 'submitted' and company_member:
        application.status = 'under_review'
        application.save()