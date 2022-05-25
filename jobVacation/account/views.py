from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import CreateView, FormView, RedirectView

from account.forms import *
from account.models import User


class RegisterEmployeeView(CreateView):
    model = User
    form_class = EmployeeRegistrationForm
    template_name = "account/register_employee.html"
    success_url = "/"
    extra_content = {"title": "Register Employee"}
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)
        return super(RegisterEmployeeView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password1")
            user.set_password(password)
            user.save()
            return redirect('account:login')
        else:
            return render(request, self.template_name, {'form': form})

class RegisterEmployerView(CreateView):
    model = User
    form_class = EmployerRegistrationForm
    template_name = "account/register_employer.html"
    success_url = '/'
    extra_content = {"title": "Register Employer"}
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)
        return super(RegisterEmployerView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password1")
            user.set_password(password)
            user.save()
            return redirect('account:login')
        else:
            return render(request, self.template_name, {'form': form})
        
class LoginView(FormView):
    form_class = UserLoginForm
    template_name = "account/login.html"
    success_url = "/"
    extra_content = {"title": "Login"}
    
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super(LoginView, self).dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        if "next" in self.request.GET and self.request.GET["next"] != "":
            return self.request.GET["next"]
        return self.success_url
    
    def get_form_class(self):
        return self.form_class
    
    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
    
class LogoutView(RedirectView):
    url = '/login'
    
    def get(self, request, *args, **kwargs):
        auth.logout(request)
        messages.success(request, "You have been logged out.")
        return super(LogoutView, self).get(request, *args, **kwargs)