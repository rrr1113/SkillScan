from django.contrib import admin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q

from .models import *

# Register your models here.


class CVAdmin(admin.ModelAdmin):
    list_display = ('name_surname', 'email', 'phone')
    exclude = ('applicant', 'created_at', 'raw_text')
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
            raise False

        return request.user == obj.applicant or request.user.is_superuser


    def has_change_permission(self, request, obj=None):
        if obj is None:
            return False

        active_application = Application.objects.filter(cv = obj, job__active_until__gte = timezone.now().date())
        if active_application.exists():
            return False
        return request.user == obj.applicant


class CompanyMemberAdmin(admin.ModelAdmin):
    model = CompanyMember
    extra = 0

    list_display = ('name_surname',)
    search_fields = ('name_surname', 'role')

    def save_model(self, request, obj, form, change):
        if not change:
            is_owner = CompanyMember.objects.filter(user=request.user, role='owner', company=obj.company).exists()
            if not is_owner and not request.user.is_superuser:
                raise PermissionDenied("Only company owners can add members.")

        return super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        is_owner = CompanyMember.objects.filter(user=request.user, role='owner').exists()
        return request.user.is_superuser or is_owner

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return False

        owners = CompanyMember.objects.filter(user=request.user, role='owner', company=obj.company).count()
        if owners == 1:
            return False

        return request.user == obj.user or request.user.is_superuser

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            if request.user.is_superuser:
                kwargs["queryset"] = User.objects.all()
            else:
                company = CompanyMember.objects.get(user=request.user,role="owner").company
                kwargs["queryset"] = User.objects.exclude(companymember__company=company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)






class CompanyAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    exclude = ('created_at',)

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

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        is_company_member = CompanyMember.objects.filter(user=request.user).exists()
        if is_company_member:
            return qs.filter(members__user=request.user).distinct()

        return qs

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if obj is None:
            return True

        return CompanyMember.objects.filter(user=request.user, company=obj).exists()






class SkillJobInline(admin.TabularInline):
    model = SkillJob
    extra = 1

class JobLocationInline(admin.TabularInline):
    model = JobLocation
    extra = 0


class JobAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'num_views', 'created_at',)
    list_display = ('position', 'industry', 'active_until','employment_type')
    search_fields = ('company', 'industry', 'position', 'employment_type')
    inlines = (SkillJobInline, JobLocationInline)

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
            return qs.filter(company__members__user=request.user)

        return qs


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "company":
            if request.user.is_superuser:
                kwargs["queryset"] = Company.objects.all()
            else:
                kwargs["queryset"] = Company.objects.filter(members__user=request.user)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'status', 'updated_at')
    search_fields = ('status', 'job')
    exclude = ('status', 'created_at')

    def save_model(self, request, obj, form, change):
        if not change:
            if obj.job.active_until < timezone.now().date():
                raise PermissionDenied("This job post is expired.")

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        is_company_member = CompanyMember.objects.filter(user=request.user).exists()
        if is_company_member:
            return qs.filter(job__company__members__user = request.user).distinct()

        return qs.filter(cv__applicant = request.user)




class SkillMatchAdmin(admin.ModelAdmin):
    exclude = ('triggered_by',)
    search_fields = ('percentage', 'application')

    def save_model(self, request, obj, form, change):
        if not change:
            existing = SkillMatch.objects.filter(
                application=obj.application,
                triggered_by=request.user
            ).first()

            if existing:
                obj.pk = existing.pk

            obj.triggered_by = request.user

        return super().save_model(request, obj, form, change)


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "application":
            if request.user.is_superuser:
                kwargs["queryset"] = Application.objects.all()
            else:
                kwargs["queryset"] = Application.objects.filter(
                    Q(job__company__members__user=request.user)
                ).distinct()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        is_company_member = CompanyMember.objects.filter(user=request.user).exists()
        if is_company_member:
            return qs.filter(application__job__company__members__user = request.user).distinct()

        return qs.filter(application__cv__applicant = request.user)







class LocationAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj = None):
        return request.user.is_superuser

    def has_add_permission(self, request, obj = None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj = None):
        return request.user.is_superuser






admin.site.register(Skill)
admin.site.register(CV, CVAdmin)
admin.site.register(SkillCv)
admin.site.register(Location, LocationAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(CompanyMember, CompanyMemberAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(SkillMatch, SkillMatchAdmin)
