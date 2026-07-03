from django.contrib import admin

from .models import *

# Register your models here.


admin.site.register(Skill)
admin.site.register(CV)
admin.site.register(SkillCv)
admin.site.register(Location)
admin.site.register(Company)
admin.site.register(CompanyMember)
admin.site.register(Job)
admin.site.register(JobLocation)
admin.site.register(Application)
admin.site.register(SkillJob)
admin.site.register(SkillMatch)
