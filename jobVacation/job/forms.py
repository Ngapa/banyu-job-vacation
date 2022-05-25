from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError

from job.models import Job, Applicant

class CreateJobForm(forms.Form):
    class Meta:
        model = Job
        exclude = ('user', 'created_at')
        labels = {
            'last_date' : 'Last Date',
            'company_name' : 'Company Name', 
            'company_description' : 'Company Description'
        }
        
    def is_valid(self):
        valid = super(CreateJobForm, self).is_valid()
        
        if valid:
            return valid
        return valid
    
    def clean_last_date(self):
        date = self.cleaned_data['last_date']
        if date.date() < datetime.now().date():
            raise ValidationError("Last date can't be before from today")
        return date
    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if tags > 7:
            raise ValidationError("You can't add tags more than 7 tags")
        return tags
    def save(self, commit=False):
        job = super(CreateJobForm, self).save(commit=False)
        if commit:
            job.save()
            for tag in self.clean_tags["tags"]:
                job.tags.add(tag)
        return job
    
class ApplyJobForm(forms.Form):
    class Meta:
        model = Applicant
        field = ('job', )