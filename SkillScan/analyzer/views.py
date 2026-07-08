from django.shortcuts import render
from django.utils.timezone import now

from .models import Job, JobLocation


# Create your views here.

def index(request):
    jobs = Job.objects.exclude(active_until__lte = now()).order_by('-created_at')
    job_data = []
    for job in jobs:
        location = JobLocation.objects.filter(job=job)
        job_data.append({"locations" : location, "job" : job})

    return render(request, 'index.html', {'all_jobs': job_data})