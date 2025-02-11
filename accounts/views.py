from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from accounts.models import CustomUser
from .serializers import UserSerializer,ChangePasswordSerializer
from rest_framework.authtoken.models import Token  
from django.contrib.auth import authenticate ,update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated


# Create your views here.

#API view for getting all users
@api_view(['GET'])
def get_all_users(request):
    if request.method=='GET':
        users=CustomUser.objects.all() #get all the users
        serializer=UserSerializer(users,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


#register a new user
@api_view(['POST'])
def register_user(request):
    if request.method=='POST':
        serializer=UserSerializer(data=request.data) #create a new user with the data
        if serializer.is_valid(): 
            serializer.save() 
            return Response(serializer.data,status=status.HTTP_201_CREATED) 
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
  

#API view for login a user
@api_view(['POST'])
def login_user(request):
    if request.method=='POST':
        username=request.data.get('username') #get the username
        password=request.data.get('password') #get the password

        user= None
        if '@' in username:
            try:
                user=CustomUser.objects.get(email=username) #get the user by email
            except CustomUser.DoesNotExist:
                pass

        if not user:
            user=authenticate(username=username,password=password)

        if user:
            token, created=Token.objects.get_or_create(user=user)
            return Response({'token':token.key},status=status.HTTP_200_OK)
        
        return Response({'error':'Invalid Credentials'},status=status.HTTP_400_BAD_REQUEST)

#API view for logout a user
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    if request.method=='POST':
        try:
            request.user.auth_token.delete() #delete the token
            return Response({'message':'User Logged Out'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)

#API view for changing password
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method=='POST':
        serializer=ChangePasswordSerializer(data=request.data)
        if serializer.is_valid(): #check if the data is valid
            user=request.user   #get the user
            if not request.user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request,user)  #update the session hash
                return Response({'message':'Password Updated Successfully!'},status=status.HTTP_200_OK)
            return Response({'error':'Invalid Password'},status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
