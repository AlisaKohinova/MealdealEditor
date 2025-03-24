from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from .models import InvitationCode, PartnerApplication, Contact

import firebase_admin.auth as firebase_auth

# Create your views here.

class FirebaseTokenView(APIView):
    def post(self, request):
        firebase_id_token = request.data.get("firebase_id_token")
        invitation_code = request.data.get("invitation_code")
        
        if not firebase_id_token:
            return Response({"error": "Firebase ID token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not invitation_code:
            return Response({"error": "Invitation code is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify the invitation code first
            code_obj = InvitationCode.objects.filter(code=invitation_code, is_used=False).first()
            if not code_obj:
                return Response({"error": "Invalid or already used invitation code"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Proceed with Firebase authentication
            decoded_token = firebase_auth.verify_id_token(firebase_id_token)
            uid = decoded_token["uid"]
            email = decoded_token.get("email", "")

            user, created = User.objects.get_or_create(username=email, email=email)
            refresh = RefreshToken.for_user(user)

            # Mark the invitation code as used
            code_obj.is_used = True
            code_obj.used_at = timezone.now()
            code_obj.used_by = email
            code_obj.save()

            response = Response({"message": "Authenticated via Firebase"}, status=status.HTTP_200_OK)

            #todo: change to secure=True in production
            response.set_cookie(key="refresh", value=str(refresh), httponly=True, secure=False, samesite="Lax", max_age=7 * 24 * 60 * 60)
            response.set_cookie(key="access", value=str(refresh.access_token), httponly=True, secure=False, samesite="Lax", max_age=30 * 60) #todo 5 minutes

            return response

        except Exception as e:
            return Response({"error": f"Registration failed: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)

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

class VerifyInvitationCodeView(APIView): 
    def post(self, request):
        invitation_code = request.data.get("invitation_code")
        if not invitation_code:
            return Response({"error": "Invitation code is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Check if the invitation code exists and is not used
            code_obj = InvitationCode.objects.filter(code=invitation_code, is_used=False).first()
            if code_obj:
                return Response({"message": "Invitation code verified"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or already used invitation code"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error verifying invitation code: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class PartnerApplyView(APIView):
    def post(self, request):
        form_data = request.data.get("formData")
        if not form_data:
            return Response({"error": "Form data is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create a new application in the database
            application = PartnerApplication.objects.create(
                business_name=form_data.get('businessName', ''),
                business_type=form_data.get('businessType', ''),
                address=form_data.get('address', ''),
                city=form_data.get('city', ''),
                phone_number=form_data.get('phoneNumber', ''),
                email=form_data.get('email', ''),
                contact_name=form_data.get('contactName', ''),
                website_url=form_data.get('websiteUrl', ''),
                instagram_url=form_data.get('instagramUrl', ''),
                additional_info=form_data.get('additionalInfo', '')
            )
            
            return Response({
                "message": "Application submitted successfully",
                "application_id": application.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "error": f"Failed to submit application: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

class ContactView(APIView):
    def post(self, request):
        form_data = request.data.get("formData")
        if not form_data:
            return Response({"error": "Form data is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create a new contact in the database
            contact = Contact.objects.create(
                name=form_data.get('name', ''),
                email=form_data.get('email', ''),
                subject=form_data.get('subject', ''),
                message=form_data.get('message', '')
            )
            
            return Response({
                "message": "Contact submitted successfully",
                "contact_id": contact.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "error": f"Failed to submit contact: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
