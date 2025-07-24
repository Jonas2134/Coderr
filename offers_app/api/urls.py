from django.urls import path

from .views import OffersGetPostView, OffersRetrieveUpdateDestroyView, DetailsRetrieveView

urlpatterns = [
    path('offers/', OffersGetPostView.as_view(), name='offers-list-create'),
    path('offers/<int:pk>/', OffersRetrieveUpdateDestroyView.as_view(), name='offers-detail'),
    path('offerdetails/<int:pk>/', DetailsRetrieveView.as_view(), name='offerdetails-detail'),
]
