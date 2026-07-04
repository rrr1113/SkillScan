from django.contrib import admin

from .models import *

# Register your models here.


class CVAdmin(admin.ModelAdmin):
    list_display = ('name_surname', 'email', 'phone')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.applicant = request.user
        return super().save_model(request, obj, form, change)



class SkillMatchAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.applicant = request.user
        return super().save_model(request, obj, form, change)



class CompanyMemberAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.applicant = request.user
        return super().save_model(request, obj, form, change)


admin.site.register(Skill)
admin.site.register(CV, CVAdmin)
admin.site.register(SkillCv)
admin.site.register(Location)
admin.site.register(Company)
admin.site.register(CompanyMember, CompanyMemberAdmin)
admin.site.register(Job)
admin.site.register(JobLocation)
admin.site.register(Application)
admin.site.register(SkillJob)
admin.site.register(SkillMatch, SkillMatchAdmin)
