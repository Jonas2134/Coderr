from rest_framework.permissions import BasePermission

from reviews_app.models import Review


class OneReviewPerBusinessUserPermission(BasePermission):
    """
    Permission class that ensures an authenticated user can create at most one review per business user.

    Attributes:
        message (str): Error message returned when creating a second review is disallowed.

    Methods:
        has_permission(request, view) -> bool:
            Allows non-POST requests for everyone.
            For POST, ensures the requester is authenticated and has not already reviewed the target business user.
    """
    message = "You can only create one review per business user."

    def has_permission(self, request, view):
        """
        Determine if the current request should be permitted.

        Args:
            request (rest_framework.request.Request): The incoming HTTP request.
            view (rest_framework.views.APIView): The view being accessed.

        Returns:
            bool:
                - True for non-POST methods.
                - For POST, True if the user is authenticated, a business_user_id is provided,
                  and no existing Review by this user for that business exists.
        """
        if request.method != 'POST':
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        business_user_id = (request.data.get('business_user') or request.data.get('business_user_id'))
        if not business_user_id:
            return False
        exists = Review.objects.filter(reviewer=request.user, business_user_id=business_user_id).exists()
        return not exists


class IsUserReviewerPermission(BasePermission):
    """
    Permission class that allows only the original reviewer to modify or delete their review.

    Methods:
        has_permission(request, view) -> bool:
            Allows all non-PATCH/DELETE methods.
            For PATCH/DELETE, ensures the requester matches the review's reviewer.
        has_object_permission(request, view, obj) -> bool:
            Delegates to has_permission for object-level enforcement.
    """
    def has_permission(self, request, view):
        """
        Determine if the current request should be permitted.

        Args:
            request (rest_framework.request.Request): The incoming HTTP request.
            view (rest_framework.views.APIView): The view being accessed.

        Returns:
            bool:
                - True for methods other than PATCH or DELETE.
                - For PATCH/DELETE, True if the authenticated user is the review's reviewer.
        """
        if request.method in ['PATCH', 'DELETE']:
            review = view.get_object()
            return bool(request.user == review.reviewer)
        return True

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check delegating to has_permission.

        Args:
            request (rest_framework.request.Request): The incoming HTTP request.
            view (rest_framework.views.APIView): The view being accessed.
            obj (Review): The review instance being acted upon.

        Returns:
            bool: Same result as has_permission for consistency.
        """
        return self.has_permission(request, view)
