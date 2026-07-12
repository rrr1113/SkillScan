"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

import analyzer.views as analyzer_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', analyzer_views.index, name='index'),
    path('job_details/<id>', analyzer_views.job_details, name='job_details'),
    path('company_jobs_overview/', analyzer_views.company_jobs_overview, name='company_jobs_overview'),
    path('user_profile/', analyzer_views.user_profile, name='user_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
