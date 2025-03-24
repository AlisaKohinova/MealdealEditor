from django.urls import path
from .views import (
    FirebaseTokenView, FirebaseLoginView, FirebaseLogoutView, 
    FirebaseRefreshView, PartnerProfileView, VerifyInvitationCodeView,
    PartnerApplyView, ContactView
)

urlpatterns = [
    path('auth/register/', FirebaseTokenView.as_view(), name='firebase-token'),
    path('auth/verify-invitation-code/', VerifyInvitationCodeView.as_view(), name='verify-invitation-code'),
    path('auth/login/', FirebaseLoginView.as_view(), name='firebase-login'),
    path('auth/logout/', FirebaseLogoutView.as_view(), name='firebase-logout'),
    path('auth/refresh/', FirebaseRefreshView.as_view(), name='firebase-refresh'),
    path('partner/profile/', PartnerProfileView.as_view(), name='partner-profile'),
    path('partner/apply/', PartnerApplyView.as_view(), name='partner-apply'),
    path('contact/', ContactView.as_view(), name='contact'),
]
