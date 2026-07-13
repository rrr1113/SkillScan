from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from .forms import EditJobForm
from .models import Job, JobLocation, SkillJob, CompanyMember, Application, CV


# Create your views here.

def index(request):
    jobs = Job.objects.exclude(active_until__lte = now()).order_by('-created_at')

    is_company_member = False

    if request.user.is_authenticated:
        is_company_member = CompanyMember.objects.filter(user=request.user).exists()

        if is_company_member:
            jobs = jobs.filter(company__members__user=request.user).distinct().order_by('-created_at')

    position = request.GET.get('position')
    location = request.GET.get('location')
    work_type = request.GET.get('work_type')

    if position:
        jobs = jobs.filter(position__icontains=position)

    if location:
        jobs = jobs.filter(Q(locations__location__city__icontains=location) | Q(locations__location__country__icontains=location))

    if work_type:
        jobs = jobs.filter(employment_type__icontains=work_type)

    job_data = []
    for job in jobs:
        location = JobLocation.objects.filter(job=job)
        job_data.append({"locations" : location, "job" : job})



    return render(request, 'index.html', {'all_jobs': job_data, 'is_company_member' : is_company_member})


@login_required
def job_details(request, id):
    job = get_object_or_404(Job, id=id)

    is_member = CompanyMember.objects.filter(id=id, user=request.user).exists()
    if not is_member:
        Job.objects.filter(id = id).update(num_views = F('num_views') + 1)
        job.refresh_from_db()


    if request.method == 'POST':
        form = EditJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('job_details', id=id)

    locations = JobLocation.objects.filter(job=job)
    skills = SkillJob.objects.filter(job=job)
    is_company_member = CompanyMember.objects.filter(user=request.user, company=job.company).exists()
    applications = Application.objects.filter(job=job)

    form = EditJobForm(instance=job)
    return render(request, 'job_details.html', {'job' : job, 'locations' : locations, 'skills' : skills, 'is_company_member' : is_company_member, 'applications' : applications, 'edit_from' : form})


@login_required
def company_jobs_overview(request):
    active_jobs = Job.objects.filter(company__members__user=request.user).exclude(active_until__lte=now()).distinct().order_by('-created_at')
    not_active_jobs = Job.objects.filter(company__members__user=request.user).exclude(active_until__gt=now()).order_by('-created_at')

    position = request.GET.get('position')
    location = request.GET.get('location')
    work_type = request.GET.get('work_type')

    if position:
        active_jobs = active_jobs.filter(position__icontains=position)
        not_active_jobs = not_active_jobs.filter(position__icontains=position)

    if location:
        active_jobs = active_jobs.filter(
            Q(locations__location__city__icontains=location) | Q(locations__location__country__icontains=location))
        not_active_jobs = not_active_jobs.filter(
            Q(locations__location__city__icontains=location) | Q(locations__location__country__icontains=location))

    if work_type:
        active_jobs = active_jobs.filter(employment_type__icontains=work_type)
        not_active_jobs = not_active_jobs.filter(employment_type__icontains=work_type)

    active_job_data = []
    for job in active_jobs:
        location = JobLocation.objects.filter(job=job)
        active_job_data.append({"locations": location, "job": job})

    not_active_job_data = []
    for job in not_active_jobs:
        location = JobLocation.objects.filter(job=job)
        not_active_job_data.append({"locations": location, "job": job})


    return render(request, 'company_jobs_overview.html', {'active_jobs' : active_job_data, 'not_active_jobs' : not_active_job_data})


@login_required
def user_profile(request):
    company_memberships = CompanyMember.objects.filter(user=request.user).order_by("-created_at")
    is_owner = CompanyMember.objects.filter(user=request.user, role = 'owner').order_by("-created_at")
    cvs = CV.objects.filter(user=request.user)

    return render(request, 'user_profile.html', { 'user': request.user, 'companies': company_memberships,
        'cvs': cvs, 'is_company_member': company_memberships.exists(), 'is_owner' : is_owner  })


@login_required
def user_applications_overview(request):
    pending_applications = Application.objects.filter(cv__user=request.user, status='submitted')
    under_review_applications = Application.objects.filter(cv__user=request.user, status='under_review')
    rejected_applications = Application.objects.filter(cv__user=request.user, status='rejected')
    return render(request, 'user_applications_overview.html',
                  {'pending_applications' : pending_applications, 'under_review_applications' : under_review_applications, 'rejected_applications' : rejected_applications })