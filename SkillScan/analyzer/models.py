from accounts.models import User
from django.core.validators import FileExtensionValidator
from django.db import models

from django.utils import timezone

# Create your models here.

# SKILLS & CVs ------------------------------------------
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name



class CV(models.Model):
    file = models.FileField(upload_to='cv', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    raw_text = models.TextField(null=True, blank=True)
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cvs')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name



class SkillCv(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='cvs')

    def __str__(self):
        return f"{self.cv.user.first_name} {self.cv.user.last_name} ({self.skill.name})"

    class Meta:
        unique_together = ('cv', 'skill')




# JOBS & COMPANIES ------------------------------------------------

class Location(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city} ({self.country})"

    class Meta:
        unique_together = ('city', 'country')




class Company(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logo', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    description = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name




class CompanyMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('recruiter', 'Recruiter')
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='recruiter')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    still_member = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'user', 'location', 'created_at')





class Job(models.Model):
    TYPE_CHOICES = [("fulltime", "Full time"),
                    ("parttime", "Part time"),
                    ("internship", "Internship"),
                    ("remote", "Remote")
                    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    industry = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    active_until = models.DateField()
    description = models.TextField()
    salary = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    employment_type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    num_views = models.IntegerField(default=0)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.position} ({self.company.name}) - {self.employment_type}"




class JobLocation(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='locations')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='jobs')

    def __str__(self):
        return f"{self.job.position} ({self.job.company}) - {self.location.city} ({self.location.country})"
    class Meta:
        unique_together = ('job', 'location')


class Application(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('rejected', 'Rejected'),
    ]

    cv = models.ForeignKey(CV, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'cv')

    def __str__(self):
        return f"{self.cv.user.first_name} {self.cv.user.last_name} - {self.job.position} ({self.status})"


# ANALYZER ------------------------------------------------

class SkillJob(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='jobs')
    points = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.job.position} ({self.job.company}) - {self.skill.name}"

    class Meta:
        unique_together = ('job', 'skill')




class SkillMatch(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='matches')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    matched_skills = models.ManyToManyField(Skill, related_name='matched_in', blank=True)
    missing_skills = models.ManyToManyField(Skill, related_name='missing_in', blank=True)

    analyzed_at = models.DateTimeField(auto_now=True)
    outdated = models.BooleanField(default=False)
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.application.job.position} ({self.application.job.company}) - {self.application.cv.user.first_name} {self.application.cv.user.last_name} - {self.percentage}%"