from django.urls import path, include

from job.views import *

app_name = 'job'

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("favorite/", favorite, name="favorite"),
    path("search/", SearchView.as_view(), name="search"),
    path("employer/dashboard/",
         include(
             [
                 path("", DashboardView.as_view(), name="dashboard"),
                 path("all-applicants/", ApplicantListView.as_view(),
                      name="employer-applicant-list"),
                 path("applicant/<int:job_id>/", AppliciantPerJobView.as_view(),
                      name="employer-dashboard-applicant"),
                 path("applied-applicant/<int:job_id>/view/<int:applicant_id>",
                      AppliedApplicantView.as_view(),  name="applied-applicant-view"),
                 path("mark-filled/<int:job_id>/",
                      filled, name="job-mark-filled"),
                 path("send-response/<int:applicant_id>",
                      SendResponseView.as_view(), name="applicant-send-response"),
                 path("jobs/create/", JobCreateView.as_view(),
                      name="employer-jobs-create"),
                 path("jobs/<int:id>/edit/", JobUpdateView.as_view(),
                      name="employer-jobs-edit"),
             ]
         ),
         ),
    path(
        "employee/",
        include(
            [
                path("my-applications", EmployeeMyJobListView.as_view(),
                     name="employee-my-applications"),
                path("favorites", FavoriteListView.as_view(),
                     name="employee-favorites"),
            ]
        ),
    ),
    path("apply-job/<int:job_id>/", ApplyJobView.as_view(), name="apply-job"),
    path("jobs/", JobListView.as_view(), name="jobs"),
    path("jobs/<int:id>/", JobDetailsView.as_view(), name="jobs-detail"),
]
