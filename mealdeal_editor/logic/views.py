from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

import firebase_admin.auth as firebase_auth

# Create your views here.

class FirebaseTokenView(APIView):
    #todo: add invitatoin code processing
    def post(self, request):
        firebase_id_token = request.data.get("firebase_id_token")
        if not firebase_id_token:
            return Response({"error": "Firebase ID token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            decoded_token = firebase_auth.verify_id_token(firebase_id_token)
            uid = decoded_token["uid"]
            email = decoded_token.get("email", "")

            user, created = User.objects.get_or_create(username=email, email=email)
            refresh = RefreshToken.for_user(user)

            response = Response({"message": "Authenticated via Firebase"}, status=status.HTTP_200_OK)

            #todo: change to secure=True in production
            response.set_cookie(key="refresh", value=str(refresh), httponly=True, secure=False, samesite="Lax", max_age=7 * 24 * 60 * 60)
            response.set_cookie(key="access", value=str(refresh.access_token), httponly=True, secure=False, samesite="Lax", max_age=30 * 60) #todo 5 minutes

            return response

        except Exception as e:
            return Response({"error": "Invalid Firebase ID token"}, status=status.HTTP_401_UNAUTHORIZED)

class FirebaseLoginView(APIView):
    def post(self, request):
        firebase_id_token = request.data.get("firebase_id_token")
        if not firebase_id_token:
            return Response({"error": "Firebase ID token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            try:
                decoded_token = firebase_auth.verify_id_token(firebase_id_token)
                email = decoded_token.get("email", "")

                user, created = User.objects.get_or_create(username=email, email=email)

                
            except Exception as e:
                return Response({"error": "Verification failed"}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)

            response = Response({"message": "Authenticated via Firebase"}, status=status.HTTP_200_OK)

            response.set_cookie(key="refresh", value=str(refresh), httponly=True, secure=False, samesite="Lax", max_age=7 * 24 * 60 * 60)
            response.set_cookie(key="access", value=str(refresh.access_token), httponly=True, secure=False, samesite="Lax", max_age=30 * 60) #todo 5 minutes

            return response

        except Exception as e:
            return Response({"error": "Login failed"}, status=status.HTTP_401_UNAUTHORIZED)
        
class FirebaseLogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh")
        response.delete_cookie("access")
        return response
    
class FirebaseRefreshView(APIView):
    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh)
            access = refresh.access_token

            response = Response({"message": "Access token refreshed"}, status=status.HTTP_200_OK)

            response.set_cookie(key="access", value=str(access), httponly=True, secure=False, samesite="Lax", max_age=30 * 60) #todo 5 minutes

            return response
        except Exception as e:
            return Response({"error": "Refresh token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
            
class PartnerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({"message": f"Partner profile retrieved for {user.email}"}, status=status.HTTP_200_OK)
            
            
            
            

