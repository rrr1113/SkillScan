from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SkillMatch, Application, CompanyMember, Company


@receiver(post_save, sender=SkillMatch)
def updating_status(sender, instance, *args, **kwargs):
    application = Application.objects.filter(id=instance.application.id).first()
    company = Company.objects.filter(id=instance.application.job.company.id).first()
    company_member = CompanyMember.objects.filter(company=company, user=instance.created_by).first()

    if application.status == 'submitted' and company_member:
        application.status = 'under_review'
        application.save()


