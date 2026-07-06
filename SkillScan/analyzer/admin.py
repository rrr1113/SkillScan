from django.contrib import admin
from django.core.exceptions import PermissionDenied, ValidationError

from .models import *

# Register your models here.


class CVAdmin(admin.ModelAdmin):
    list_display = ('name_surname', 'email', 'phone')
    exclude = ('applicant',)
    search_fields = ('name_surname', 'email', 'phone')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.applicant = request.user
        return super().save_model(request, obj, form, change)


    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return False

        active_application = Application.objects.filter(cv = obj, job__active_until__gte = timezone.now().date())
        if active_application.exists():
            raise ValidationError("This CV cannot be deleted because it has active job applications.")

        return request.user == obj.applicant or request.user.is_superuser


    def has_change_permission(self, request, obj=None):
        if obj is None:
            return False

        active_application = Application.objects.filter(cv = obj, job__active_until__gte = timezone.now().date())
        if active_application.exists():
            raise ValidationError("This CV cannot be changed because it has active job applications.")

        return request.user == obj.applicant



class CompanyAdmin(admin.ModelAdmin):
    search_fields = ('name',)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return False

        if request.user.is_superuser:
            return True

        company_member = CompanyMember.objects.filter(user=request.user, company=obj).first()
        if company_member and company_member.role == 'owner':
            return True
        return False



class CompanyMemberAdmin(admin.ModelAdmin):
    list_display = ('name_surname',)
    search_fields = ('name_surname' ,'role')

    def save_model(self, request, obj, form, change):
        if not change:
            is_owner = CompanyMember.objects.filter(user=request.user, role='owner', company=obj.company).exists()
            if not is_owner and not request.user.is_superuser:
                raise PermissionDenied("Only company owners can add members.")

        return super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        is_owner = CompanyMember.objects.filter(user = request.user, role = 'owner').exists()
        return request.user.is_superuser or is_owner

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return False

        owners = CompanyMember.objects.filter(user = request.user, role = 'owner', company = obj.company).count()
        if owners == 1:
            return False

        return request.user == obj.user or request.user.is_superuser








class SkillJobInline(admin.TabularInline):
    model = SkillJob
    extra = 1



class JobAdmin(admin.ModelAdmin):
    exclude = ('created_by',)
    list_display = ('position', 'industry', 'active_until','employment_type')
    search_fields = ('company', 'industry', 'position', 'employment_type')
    inlines = (SkillJobInline, )

    def save_model(self, request, obj, form, change):
        if not change:
            member_of_company = CompanyMember.objects.filter(user=request.user).first()

            if not member_of_company and not request.user.is_superuser:
                raise PermissionDenied("You are not a member of this company")

            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj = None):
        if obj is None:
            return False

        if request.user.is_superuser:
            return True

        return request.user == obj.created_by or obj.company.members.filter(user=request.user).exists()


    def has_delete_permission(self, request, obj = None):
        if obj is None:
            return False

        if request.user.is_superuser:
            return True

        return request.user == obj.created_by or obj.company.members.filter(user=request.user).exists()


    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        company_member = CompanyMember.objects.filter(user=request.user).first()
        if not company_member:
            return qs.none()

        return qs.filter(company = company_member.company)


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "company":
            if request.user.is_superuser:
                kwargs["queryset"] = Company.objects.all()
            else:
                kwargs["queryset"] = Company.objects.filter(members__user=request.user)



class ApplicationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            if obj.job.active_until.date() < timezone.now().date():
                raise PermissionDenied("This job post is expired.")

        super().save_model(request, obj, form, change)




class SkillMatchAdmin(admin.ModelAdmin):
    exclude = ('triggered_by',)
    search_fields = ('percentage', 'application')


    def save_model(self, request, obj, form, change):
        if not change:
            obj.triggered_by = request.user
        return super().save_model(request, obj, form, change)




admin.site.register(Skill)
admin.site.register(CV, CVAdmin)
admin.site.register(SkillCv)
admin.site.register(Location)
admin.site.register(Company, CompanyAdmin)
admin.site.register(CompanyMember, CompanyMemberAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(JobLocation)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(SkillMatch, SkillMatchAdmin)
