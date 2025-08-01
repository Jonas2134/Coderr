from django.urls import path

from .views import GetBaseInfoView

urlpatterns = [
    path('base-info/', GetBaseInfoView.as_view(), name='base-info')
]
