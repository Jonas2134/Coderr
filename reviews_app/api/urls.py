from django.urls import path

from .views import ReviewsGetPostView, ReviewsPatchDeleteView

urlpatterns = [
    path('reviews/', ReviewsGetPostView.as_view(), name='reviews-list-create'),
    path('reviews/<int:pk>/', ReviewsPatchDeleteView.as_view(), name='reviews-update-delete'),
]

