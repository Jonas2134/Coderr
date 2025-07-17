from django.urls import path

from .views import ProfileDetailPatchView, BusinessProfileListView, CustomerProfileListView

urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailPatchView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profile-list'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='customer-profile-list'),
]
