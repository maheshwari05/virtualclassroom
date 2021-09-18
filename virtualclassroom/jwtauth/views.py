from .models import Profile
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from virtualclassroom import utils
# Create your views here.


class Register(APIView):

    def createProfile(self,username,password,role):
        try:
            user = User.objects.create(username=username)
            user.set_password(password)
            user.save()
            Profile.objects.create(user=user, role=role)
            return user
        except:
            return False

    def post(self,request):

        username = None
        password = None
        role = None

        try:
            username = request.data['username']
            password = request.data['password']
            role = request.data['role']

        except:
            return Response({'error':'please provide correct data format'},status=status.HTTP_400_BAD_REQUEST )   
            
    
        if role not in utils.roles:
            return Response({'error':'role can be student or teacher only!'}, status=status.HTTP_400_BAD_REQUEST)

        user = self.createProfile(username,password,role)

        if not user:
            return Response({'error':'username already exist or some internal error!'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            refresh = RefreshToken.for_user(user)
            return Response({'access':str(refresh.access_token),'refresh':str(refresh)})
        except:
            return Response({'error':'something went wrong!!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


