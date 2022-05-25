from audioop import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponseNotAllowed
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from job.models import Job
from jobVacation.job.decorators import user_is_employee, user_is_employer
from jobVacation.job.forms import ApplyJobForm, CreateJobForm
from jobVacation.job.models import Applicant, Favorite
from jobVacation.account.models import User
from jobVacation.account.forms import EmployeeUpdateProfileForm, EmployerUpdateProfileForm
from jobVacation.tags.models import Tag


class HomeView(ListView):
    model = Job
    template_name = "job/home.html"
    context_object_name = 'jobs'

    def get_queryset(self):
        return self.model.objects.undefilled()[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trendings"] = self.model.objects.unfilled(
            created_at__month=timezone.now().month)[:3]
        return context


class SearchView(ListView):
    model = Job
    template_name = "job/jobs.html"
    context_object_name = 'jobs'

    def get_queryset(self):
        return self.model.objects.filter(
            location__contain=self.request.GET("location", ""),
            title__contain=self.request.GET("title", ""),
        )


class JobListView(ListView):
    model = Job
    template_name = "job/jobs.html"
    context_object_name = 'jobs'
    paginate_by = 10


class JobDetailsView(DetailView):
    model = Job
    template_name = "job/job_details.html"
    context_object_name = 'job'
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj == None:
            raise Http404("Job not found")
        return obj

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            raise Http404("Job not found")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ApplyJobView(CreateView):
    model = Applicant
    form_class = ApplyJobForm
    slug_field = 'job_id'
    slug_url_kwarg = 'job_id'

    @method_decorator(login_required(login_url=reverse_lazy('account:login')))
    @method_decorator(user_is_employee)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(self._allowed_methods())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            messages.info(self.request, "Success for apply job")
            return self.form_valid(form)
        return HttpResponseRedirect(reverse_lazy('job:home'))

    def get_success_url(self):
        return reverse_lazy('job:job-detail', kwargs={'id': self.kwargs['job_id']})

    def form_valid(self, form):
        applicant = Applicant.objects.filter(
            user_id=self.request.user.id, job_id=self.kwargs["job_id"])
        if applicant:
            messages.info(
                self.request, "You have already applied for this job")
            return HttpResponseRedirect(self.get_success_url())
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)


def favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse(data={"auth": False, "status": "You need to login first"}, status=401)

    job_id = request.POST.get("job_id")
    user_id = request.user.id

    try:
        fav = Favorite.objects.get(
            user_id=user_id, job_id=job_id, soft_deleted=False)
        if fav:
            fav.soft_deleted = True
            fav.save()
            return JsonResponse(data={"auth": True, "status": "removed", "message": "Job has been removed from your favorite list"}, status=200)
    except Favorite.DoesNotExist:
        Favorite.objects.create(job_id=job_id, user_id=user_id)
        return JsonResponse(data={"auth": True, "status": "added", "message": "Job has been added to your favorite list"}, status=200)


# EMPLOYEE VIEWS
@method_decorator(login_required(login_url=reverse_lazy('account:login')), name='dispatch')
@method_decorator(user_is_employee, name='dispatch')
class EmployeeMyJobListView(ListView):
    model = Applicant
    template_name = "job/employee_my_jobs.html"
    context_object_name = 'applicants'
    paginate_by: int = 10

    def get_queryset(self):
        self.queryset = self.model.objects.select_related("job").filter(
            user_id=self.request.user.id).order_by('-created_at')

        if (
            "status" in self.request.GET
            and len(self.request.GET.get("status")) > 0
            and int(self.request.GET.get("status")) > 0
        ):
            self.queryset = self.queryset.filter(
                status=int(self.request.GET.get("status")))

        return self.queryset


class EditProfileView(UpdateView):
    model = User
    form_class = EmployeeUpdateProfileForm
    context_object_name = 'employee'
    template_name = "job/employee_edit_profile.html"
    success_url = reverse_lazy('job:employee-profile-update')

    @method_decorator(login_required(login_url=reverse_lazy('account:login')))
    @method_decorator(user_is_employee)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            raise Http404("User not found")

        return self.render_to_response(self.get_context_data())

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj == None:
            raise Http404("User not found")
        return obj


@method_decorator(login_required(login_url=reverse_lazy('account:login')))
@method_decorator(user_is_employee)
class FavoriteListView(ListView):
    model = Favorite
    template_name = 'job/employee_favorite_list.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return self.model.objects.select_related("job__user").filter(soft_deleted=False, user=self.request.user)


# EMPLOYER VIEWS
class DashboardView(ListView):
    model = Job
    template_name = "job/employer_dashboard.html"
    context_object_name = 'jobs'

    @method_decorator(login_required(login_url=reverse_lazy('account:login')))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(user_id=self.request.user.id)


class AppliciantPerJobView(ListView):
    model = Applicant
    template_name = "job/employer_applicant_per_job.html"
    context_object_name = 'applicants'
    paginate_by = 5

    @method_decorator(login_required(login_url=reverse_lazy('account:login')))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_query_set(self):
        return Applicant.objects.filter(job_id=self.kwargs['job_id']).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job"] = Job.objects.get(id=self.kwargs['job_id'])
        return context


class JobCreateView(CreateView):
    extra_context = {"title": "Create Job"}
    form_class = CreateJobForm
    template_name = "job/employer_create_job.html"
    success_url = reverse_lazy('job:employer-dashboard')

    @method_decorator(login_required(login_url=reverse_lazy('account:login')))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return reverse_lazy('account:login')
        if self.request.user.is_authenticated and self.request.user.role != "employer":
            return reverse_lazy('account:login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Job has been created")
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


@method_decorator(login_required(login_url=reverse_lazy('account:login')))
@method_decorator(user_is_employer)
class JobUpdateView(UpdateView):
    form_class = CreateJobForm
    template_name = "job/employer_update_job.html"
    extra_context = {"title": "Edit Job"}
    slug_field = "id"
    slug_url_kwarg = "id"
    success_url = reverse_lazy('job:employer-dashboard')
    context_object_name = 'job'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Job.objects.filter(user_id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Job has been updated")
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


class ApplicantView(ListView):
    model = Applicant
    template_name = "job/employer_applicant_list.html"
    context_object_name = 'applicants'

    @method_decorator(login_required(login_url=reverse_lazy('account:login')))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.model.object.filter(
            job__user_id=self.request.user.id).order_by('id')
        if "status" in self.request.GET and len(self.request.GET.get("status")) > 0:
            self.queryset = self.queryset.filter(
                status=self.request.GET.get("status"))
        return self.queryset


@method_decorator(login_required(login_url=reverse_lazy('account:login')))
@method_decorator(user_is_employer)
def filled(request, job_id=None):
    try:
        job = Job.objects.get(user_id=request.user.id, id=job_id)
        job.filled = True
        job.save()
    except IntegrityError:
        return HttpResponseRedirect(reverse_lazy('job:employer-dashboard'))
    return HttpResponseRedirect(reverse_lazy('job:employer-dashboard'))


@method_decorator(login_required(login_url=reverse_lazy('account:login')))
@method_decorator(user_is_employer)
class AppliedApplicantView(DetailView):
    model = Applicant
    template_name = "job/employer_applicant_detail.html"
    context_object_name = 'applicant'
    slug_field = "id"
    slug_url_kwarg = "applicant_id"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Applicant.objects.select_related('job').get(job_id=self.kwargs['job_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@method_decorator(login_required(login_url=reverse_lazy('account:login')))
@method_decorator(user_is_employer)
class SendResponseView(UpdateView):
    model = Applicant
    http_method_names = ['post']
    pk_url_kwarg = 'applicant_id'
    fields = ('status', 'comment')

    def get_success_url(self):
        return reverse_lazy(
            'job:employer-applied-applicant',
            kwargs={'job_id': self.kwargs['job_id'],
                    'applicant_id': self.kwargs['applicant_id']}
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status != request.POST.get("status"):
            if request.POST.get("status") == "0":
                status = "Pending"
            elif request.POST.get("status") == "1":
                status = "Accepted"
            else:
                status = "Rejected"
            messages.success(
                self.request, "Response was successfully sent to applicant")
        else:
            messages.warning(
                self.request, "Response was not sent to applicant, maybe already sent")
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = queryset.filter(pk=pk)
        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("No %(verbose_name)s found matching the query" % {
                "verbose_name": queryset.model._meta.verbose_name})

        return obj


class EmployerProfileUpdateView(UpdateView):
    form_class = EmployerUpdateProfileForm
    context_object_name = "employer"
    template_name = "job/employer_profile_update.html"
    success_url = reverse_lazy('job:employer-update-profile')

    @method_decorator(login_required(login_url=reverse_lazy("accounts:login")))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            raise Http404("User doesn't exists")
        return self.render_to_response(self.get_context_data())

    def get_object(self, queryset=None):
        obj = self.request.user
        if obj is None:
            raise Http404("Job doesn't exists")
        return obj
