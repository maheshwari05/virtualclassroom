from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from . import classroom_utils as utils
from .models import *


# Create your views here.


class AssignmentCreateFilter(APIView):
    permission_classes = (IsAuthenticated,)

    def teacherAssignment(self,user,publishedAt):

        assignments = utils.filterAssignment(user,publishedAt)
        res = []

        for data in assignments:

            students = []
            datum = {}
            for i in data.assigned_to.all():
                students.append(i.user.username)
            
            datum = {'id':data.id,
                    'title':data.title,
                    'description':data.description,
                    'publishAt':data.publish_at,
                    'deadline':data.deadline,
                    'assignedTo':students,
                    }
            res.append(datum)
        
        return Response({'data':res})


    def studentAssignment(self,user,publishedAt, status):
        assignments = utils.filterAssignment(user,publishedAt,status)
        res = []
        for data in assignments:

            datum = {'id':data.id,
                    'title':data.title,
                    'description':data.description,
                    'publishAt':data.publish_at,
                    'deadline':data.deadline,
                    'assignedBy':data.created_by.user.username,
                    }
            res.append(datum)
        return Response({'data':res})

    def get(self,request):

        user = request.user
        publishedAt = request.query_params.get('publishedAt')
        status = request.query_params.get('status')

        if utils.check_user(user) == 'teacher':
            return self.teacherAssignment(user,publishedAt)

        else:
            return self.studentAssignment(user,publishedAt,status)


    def post(self,request):
        
        user = request.user

        if utils.check_user(user) == 'student':
            return Response({'error':'user should be teacher'}, status=status.HTTP_401_UNAUTHORIZED)

        description = None
        title = None
        publish_at = None
        deadline = None
        assigned_to = None

        try:
            description = request.data['description']
            title = request.data['title']
            publish_at = request.data['publish_at']
            deadline = request.data['deadline']
            assigned_to = request.data['assigned_to']

            if len(title)==0 or len(description)==0 or len(publish_at)==0 or len(deadline)==0:
                return Response({'error':'title, description, publish date and deadline cannot be empty'},status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({'error':'invalid format!!'},status=status.HTTP_400_BAD_REQUEST)
        
        for username in assigned_to:
            if not utils.isStudentExist(username):
                return Response({'error':username + ' does not exist or user is not student'},status=status.HTTP_400_BAD_REQUEST) 

        if publish_at > deadline:
            return Response({'error':'deadline should be greater then publish date'},status=status.HTTP_400_BAD_REQUEST)
        obj = None

        try:
            obj = Assignment.objects.create(description=description,title=title,publish_at=publish_at,deadline=deadline,created_by=utils.getUserProfile(user.username))
        except:
            return Response({'error':'invalid data format!!'},status=status.HTTP_400_BAD_REQUEST)
        

        for username in assigned_to:
            obj.assigned_to.add(utils.getUserProfile(username))
        
        obj.save()

        return Response({'msg':'assignment created !!'},status=status.HTTP_201_CREATED)
            


class AssignmentOperations(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self,request,pk):

        user = request.user

        try:
            assignment = Assignment.objects.get(pk=pk)
        except:
            return Response({'error':'assignment does not exist'},status=status.HTTP_400_BAD_REQUEST)
        
        
        if utils.check_user(user) == 'student':
            submission = Submission.objects.get(submitted_by=utils.getUserProfile(user.username))
            assignment_detail = [{'title':assignment.title, 'description':assignment.description,
                                'deadline':assignment.deadline, 'assignedBy':assignment.created_by.user.username}]
            res = {'remark':submission.remark,
                    'submissionDate':submission.submission_date,
                    'assignmentDetails':assignment_detail}

            if len(res) == 0:
                return Response({'msg':'Not Submitted Yet'},status=status.HTTP_200_OK)

            return Response({'data':res})
        
        else:
            submissions = Submission.objects.filter(assignment=assignment)
            res = []
            for data in submissions:
                datum = {'submittedBy':data.submitted_by.user.username,'remark':data.remark,
                        'submissionDate':data.submission_date}
                res.append(datum)

            if len(res) == 0:
                return Response({'msg':'No one has submitted yet!!'},status=status.HTTP_200_OK)
            
            return Response({'data':res})

    
    def delete(self,request,pk):

        user = request.user

        if utils.check_user(user) == 'student':
            return Response({'error':'You are not authorized'},status = status.HTTP_401_UNAUTHORIZED)
        
       
        try:
            assignment = Assignment.objects.get(pk=pk)
            assignment.delete()
            return Response({'msg':'Assignment deleted'},status=status.HTTP_200_OK)
        except:
            return Response({'error':'Assignment not found'},status=status.HTTP_400_BAD_REQUEST)

    
    def put(self,request,pk):
        
        user = request.user

        if utils.check_user(user) == 'student':
            return Response({'error':'student cannot edit assignment'},status=status.HTTP_401_UNAUTHORIZED)
        
        description = None
        title = None
        publish_at = None
        deadline = None
        # assigned_to = None
        add_students = None
        delete_students = None

        try:
            description = request.data['description']
            title = request.data['title']
            publish_at = request.data['publish_at']
            deadline = request.data['deadline']
            add_students = request.data['add_students']
            delete_students = request.data['delete_students']

            if len(title)==0 or len(description)==0 or len(publish_at)==0 or len(deadline)==0:
                return Response({'error':'title, description, publish date and deadline cannot be empty'},status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({'error':'invalid format!!'},status=status.HTTP_400_BAD_REQUEST)
        
        for username in add_students:
            if not utils.isStudentExist(username):
                return Response({'error':username + ' does not exist or user is not student'},status=status.HTTP_400_BAD_REQUEST) 
        
        for username in delete_students:
            if not utils.isStudentExist(username):
                return Response({'error':username + ' does not exist or user is not student'},status=status.HTTP_400_BAD_REQUEST)

        if publish_at > deadline:
            return Response({'error':'deadline should be greater then publish date'},status=status.HTTP_400_BAD_REQUEST)
        obj = None

        try:
            obj = Assignment.objects.get(pk=pk)
        except:
            return Response({'error':'Assignment Not found!!'},status=status.HTTP_400_BAD_REQUEST)
        
        obj.publish_at = publish_at
        obj.deadline = deadline
        obj.description = description
        obj.title = title

        for username in add_students:
            obj.assigned_to.add(utils.getUserProfile(username))
        
        for username in delete_students:
            obj.assigned_to.remove(utils.getUserProfile(username))

        obj.save()

        return Response({'msg':'assignment updated !!'},status=status.HTTP_200_OK)
        


class Submissions(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self,request,pk):
        
        user = request.user

        if utils.check_user(user) == 'teacher':
            return Response({'error':'Teacher cannot submit an assignment'},status=status.HTTP_401_UNAUTHORIZED)

        remark = request.data['remark']
        assignment = None

        try:
            assignment = Assignment.objects.filter(pk=pk,assigned_to=utils.getUserProfile(user.username))
        except:
            return Response({'error':'Assignment doesnot assigned to you'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            assignment = Assignment.objects.get(pk=pk)
        except:
            return Response({'error':'Assignment Doesnot exist!'}, status=status.HTTP_400_BAD_REQUEST)
        
        validate = Submission.objects.filter(assignment=assignment,submitted_by=utils.getUserProfile(user.username))
        if validate:
            return Response({'msg':'Assignment already submitted by you!!!'})
            
        submit = Submission.objects.create(assignment=assignment,remark=remark,submitted_by=utils.getUserProfile(user.username))

        try:
            return Response({'msg':'Submitted successfully!!'},status=status.HTTP_201_CREATED)
        except:
            return Response({'msg':'internal error'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

        

