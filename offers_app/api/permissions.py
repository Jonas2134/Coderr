from rest_framework.permissions import BasePermission

from offers_app.models import Offer


class IsUserCreator(BasePermission):
    """
    Permission class that grants update and delete permissions only to the creator of an Offer.

    For unsafe HTTP methods (PUT, PATCH, DELETE), checks that the authenticated user
    is the same as the `creator` of the Offer instance. Read-only methods are allowed
    for any user (including unauthenticated).

    Methods:
        has_permission(request, view) -> bool:
            Enforces creator check for modifying methods.
        has_object_permission(request, view, obj) -> bool:
            Delegates to has_permission to enforce object-level permission.
    """
    def has_permission(self, request, view):
        """
        Determine if the current request should be permitted at all.

        Args:
            request (rest_framework.request.Request): The incoming HTTP request.
            view (rest_framework.views.APIView): The view being accessed.

        Returns:
            bool:
                - True for safe methods (e.g., GET, HEAD, OPTIONS).
                - For modifying methods (PUT, PATCH, DELETE), True only if:
                  * request.user is authenticated, and
                  * request.user == offer.creator.
        """
        if request.method in ['PATCH', 'DELETE']:
            offer = view.get_object()
            return bool(request.user and request.user.is_authenticated and request.user == offer.creator)
        return True

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check.

        Delegates to has_permission so that unsafe methods are only allowed
        if the user is the creator, and safe methods remain open.

        Args:
            request (rest_framework.request.Request): The incoming HTTP request.
            view (rest_framework.views.APIView): The view being accessed.
            obj: The Offer instance being acted upon.

        Returns:
            bool: Same result as has_permission for consistency.
        """
        return self.has_permission(request, view)
