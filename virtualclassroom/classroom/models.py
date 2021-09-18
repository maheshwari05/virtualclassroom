from django.db import models
from jwtauth.models import *
from django.utils import timezone


class Assignment(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=100)
    title = models.CharField(max_length=50)
    publish_at = models.DateTimeField()
    deadline = models.DateTimeField()
    created_by = models.ForeignKey(Profile,on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(Profile, related_name="students")

    def __str__(self):
        return self.title + " by " + str(self.created_by)

class Submission(models.Model):
    id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    remark = models.CharField(max_length=250)
    submitted_by = models.ForeignKey(Profile, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('assignment','submitted_by')

    def __str__(self):
        return self.remark + "by" + str(self.submitted_by)
