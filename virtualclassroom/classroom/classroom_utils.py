from jwtauth.models import Profile
from django.contrib.auth.models import User
from .models import *

def check_user(user):
    user = Profile.objects.get(user=user)
    return str(user.role)

def getUserProfile(username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    return profile

def isStudentExist(username):
    user = None
    try:
        user = User.objects.get(username=username)
    except:
        return False
    
    profile = Profile.objects.get(user=user)
    
    if str(profile.role) == 'student':
        return True

    return False


def checkStudentSubmission(user,assignment):
    obj = Submission.objects.filter(submitted_by=getUserProfile(user.username),assignment=assignment)
    if obj:
        return True
    return False

def filterAssignment(user,publishedAt=None,status=None):
 
    if check_user(user) == 'student':

        assignments = None
        student_assignments = []

        if publishedAt == 'SCHEDULED':
            assignments = Assignment.objects.filter(publish_at__gt = timezone.now(), assigned_to=getUserProfile(user.username))
        elif publishedAt == 'ONGOING':
            assignments = Assignment.objects.filter(publish_at__lte= timezone.now(), assigned_to=getUserProfile(user.username))
        else:
            assignments = Assignment.objects.filter(assigned_to=getUserProfile(user.username))

        if status is None:
            return assignments

        if status == 'ALL':
            return assignments

        if status == 'SUBMITTED':
            for i in assignments:
                if checkStudentSubmission(user,i):
                    student_assignments.append(i)

        if status == 'PENDING':
            for i in assignments:
                if not checkStudentSubmission(user,i):
                    student_assignments.append(i)
        
        if status == 'OVERDUE':
            for i in assignments:
                if not checkStudentSubmission(user,i) and i.deadline < timezone.now() :
                    student_assignments.append(i)
        
        return student_assignments
    
    else:
        
        if publishedAt == 'SCHEDULED':
            assignments = Assignment.objects.filter(publish_at__gt = timezone.now(), created_by=getUserProfile(user.username))
        elif publishedAt == 'ONGOING':
            assignments = Assignment.objects.filter(publish_at__lte= timezone.now(), created_by=getUserProfile(user.username))
        else:
            assignments = Assignment.objects.filter(created_by=getUserProfile(user.username))
        
        return assignments

             


    

