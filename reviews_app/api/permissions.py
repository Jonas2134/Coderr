from rest_framework.permissions import BasePermission

from reviews_app.models import Review


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
