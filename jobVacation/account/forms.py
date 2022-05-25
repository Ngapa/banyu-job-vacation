from dataclasses import fields
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from account.models import User

GENDER_CHOICES = (('male', 'Male'), ('female', 'Female'))

class EmployeeRegistrationForm(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(EmployeeRegistrationForm, self).__init__(*args, **kwargs)
        self.fields["gender"].required = True
        self.fields["first_name"].label = "First Name"
        self.fields["last_name"].label = "Last Name"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm Password"
        
        self.fields["first_name"].widget.attrs.update({'class': 'form-control', 'placeholder': 'First Name'})
        self.fields["last_name"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields["password1"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields["password2"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender', 'password1', 'password2']
        error_messages = {
            "first_name" : {"required":"First Name is Required", "max_length":"Name is too long"},
            "last_name" : {"required":"Last Name is Required", "max_length":"Last Name is too long"},
            "gender" : {"required":"Gender is required"},
        }
        
    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if not gender:
            raise forms.ValidationError("Gender is required")
        return gender
    
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.role = "employee"
        if commit:
            user.save()
        return user
    
class EmployerRegistrationForm(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(EmployerRegistrationForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].label = "Company Name"
        self.fields["last_name"].label = "Company Address"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm Password"
        
        self.fields["first_name"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Company Name'})
        self.fields["last_name"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Company Address'})
        self.fields["email"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields["password1"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields["password2"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        error_messages = {
            "first_name" : {"required":"Company Name is Required", "max_length":"Company Name is too long"},
            "last_name" : {"required":"Company Address is Required", "max_length":"Address is too long"},
        }
        
    def save(self, commit=True):
        user = super(EmployerRegistrationForm, self).save(commit=False)
        user.role = 'employer'
        if commit:
            user.save()
        return user
    
class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, label="Password", widget=forms.PasswordInput, strip=False)
    
    def __init__(self, *args, **kwarg):
        super(UserLoginForm, self).__init__(*args, **kwarg)
        self.user = None
        self.fields["email"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields["password"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        
    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        
        if email and password:
            self.user = authenticate(email=email, password=password)
            
            if self.user is None:
                raise forms.ValidationError("Users does not exist")
            if not self.user.check_password(password):
                raise forms.ValidationError("Incorrect Password")
            if not self.user.is_active:
                raise forms.ValidationError("User is not active")
            
        return super(UserLoginForm, self).clean(*args, **kwargs)
    def get_user(self):
        return self.user
    
class EmployeeUpdateProfileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(EmployeeUpdateProfileForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter First Name'})
        self.fields["last_name"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Last Name'})
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender']
        
class EmployerUpdateProfileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(EmployerUpdateProfileForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Company Name', 'label': 'Company Name'})
        self.fields["last_name"].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Company Address', 'label': 'Company Address'})
        
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        