from decouple import config
from django.core.mail import send_mail
from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import *
from services.parse_parser import extract_cv
from services.skill_extractor import extract_skills

# CV -----------------------------------------------------
@receiver(post_save, sender=CV)
def updating_skills_for_cv(sender, instance, created, **kwargs):
    if created:
        cv_raw_text = extract_cv(instance.file)
        skills = extract_skills(cv_raw_text)

        with transaction.atomic():
            for skill in skills:
                skill_obj, _ = Skill.objects.get_or_create(name=skill.strip().lower())
                SkillCv.objects.create(cv=instance, skill=skill_obj)

    else:
        old_instance = CV.objects.get(pk=instance.pk)
        if old_instance.file != instance.file:
            SkillCv.objects.filter(cv=instance ).delete()

            cv_raw_text = extract_cv(instance.file)
            skills = extract_skills(cv_raw_text)

            with transaction.atomic():
                for skill in skills:
                    skill_obj, _ = Skill.objects.get_or_create(name=skill.strip().lower())
                    SkillCv.objects.create(cv=instance, skill=skill_obj)


@receiver(pre_delete, sender=CV)
def deleting_old_skill_matches (sender, instance, *args, **kwargs):
    SkillCv.objects.filter(cv=instance).delete()




# SkillMatch -------------------------------------------------
@receiver(post_save, sender=SkillMatch)
def updating_status(sender, instance, *args, **kwargs):
    application = Application.objects.filter(id=instance.application.id).first()
    company = Company.objects.filter(id=instance.application.job.company.id).first()
    company_member = CompanyMember.objects.filter(company=company, user=instance.triggered_by).first()

    if application.status == 'submitted' and company_member:
        application.status = 'under_review'

        def send_confirmation_email():
            send_mail(
                subject="Application Status changed",
                message=(
                    f"Hello {instance.application.cv.name_surname},\n\n"
                    f"Your application for the position "
                    f"'{instance.application.job.position}' at '{instance.application.job.company.name}' "
                    f"has been {application.status}."
                ),
                from_email=config("DEFAULT_FROM_EMAIL"),
                recipient_list=[instance.application.cv.email],
                fail_silently=False,
            )

        transaction.on_commit(send_confirmation_email)

        application.save()



@receiver(post_save, sender=SkillJob)
def deleting_old_skill_matches(sender, instance, created, **kwargs):
    if created:
        old_skill_matches = SkillMatch.objects.filter(application__job=instance.job)
        for old_skill_match in old_skill_matches:
            old_skill_match.outdated = True
            old_skill_match.save()

@receiver(pre_delete, sender=SkillJob)
def deleting_old_skill_matches_(sender, instance, created, **kwargs):
    old_skill_matches = SkillMatch.objects.filter(application__job=instance.job)
    for old_skill_match in old_skill_matches:
        old_skill_match.outdated = True
        old_skill_match.save()


# Application -----------------------------------------------
@receiver(post_save, sender=Application)
def deleting_old_skill_matches(sender, instance, created, **kwargs):
    if created:
        def send_confirmation_email():
            send_mail(
                subject="Application Submitted",
                message=(
                    f"Hello {instance.cv.name_surname},\n\n"
                    f"Your application for the position "
                    f"'{instance.job.position}' at '{instance.job.company.name}' "
                    f"has been successfully submitted."
                ),
                from_email=config("DEFAULT_FROM_EMAIL"),
                recipient_list=[instance.cv.email],
                fail_silently=False,
            )
        transaction.on_commit(send_confirmation_email)