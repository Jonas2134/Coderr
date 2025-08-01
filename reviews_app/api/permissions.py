from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from reviews_app.models import Review


class OneReviewPerBusinessUserPermission(BasePermission):
    message = "You can only create one review per business user."

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        business_user_id = (request.data.get('business_user') or request.data.get('business_user_id'))
        if not business_user_id:
            return False
        exists = Review.objects.filter(reviewer=request.user, business_user_id=business_user_id).exists()
        return not exists
