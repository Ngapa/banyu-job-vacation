from django.urls import reverse
from django.db import models
from django.utils import timezone

from account.models import User
from tags.models import Tag

JOB_TYPE = (("1", "Full Time"), ("2", "Part Time"), ("3", "Contract"), ("4", "Internship"))

class JobManager(models.Manager):
    def filled(self, *args, **kwargs):
        return self.filter(filled=True, *args, **kwargs)
    
    def unfilled(self, *args, **kwargs):
        return self.filter(filled=False, *args, **kwargs)


class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, help_text='Enter a job title')
    description = models.TextField(help_text='Enter a brief description of the job')
    location = models.CharField(max_length=100, help_text='Enter the location of the job')
    type = models.CharField(max_length=1, choices=JOB_TYPE, help_text='Select the job type')
    category = models.CharField(max_length=100, help_text='Enter the category of the job')
    last_date = models.DateField(help_text='Enter the last date of the job')
    name_company = models.CharField(max_length=100, help_text='Enter the name of the company')
    created_at = models.DateTimeField(auto_now_add=True)
    filled = models.BooleanField(default=False)
    salary = models.IntegerField(help_text='Enter the salary of the job', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    objects = JobManager()
    
    class Meta:
        ordering = ["id"]
        
    def get_absolute_url(self):
        return reverse('job-detail', args=[str(self.id)])
    
    def __str__(self):
        return self.title
    
    
class Applicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='applicants')
    created_at = models.DateTimeField(default=timezone.now)
    status = models.SmallIntegerField(default=0)
    
    def __str__(self):
        return self.user.username
    
    class Meta:
        ordering = ["id"]
        unique_together = ["user", "job"]
        
    @property
    def get_status(self):
        if self.status == 0:
            return 'Pending'
        elif self.status == 1:
            return 'Accepted'
        return 'Rejected'
    
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=False)
    
    def __str__ (self):
        return self.job.title
    