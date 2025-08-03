from rest_framework.permissions import BasePermission


class IsUserBusinessOwner(BasePermission):
    """
    Permission class that allows PATCH requests only if the authenticated user
    is the business owner associated with the order.

    For HTTP PATCH operations, checks that `request.user` matches
    `order.business_user`. All other methods are permitted.

    Methods:
        has_permission(request, view) -> bool:
            Enforces ownership check for PATCH requests.
        has_object_permission(request, view, obj) -> bool:
            Delegates to has_permission for consistency.
    """
    def has_permission(self, request, view):
        """
        Determine if the current request should be permitted at all.

        Args:
            request (rest_framework.request.Request): The incoming HTTP request.
            view (rest_framework.views.APIView): The view being accessed.

        Returns:
            bool:
                - True for non-PATCH methods.
                - For PATCH, True only if request.user is the order’s business_user.
        """
        if request.method == 'PATCH':
            order = view.get_object()
            return bool(request.user == order.business_user)
        return True

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check.

        Delegates to has_permission so that ownership logic is centralized.

        Args:
            request (rest_framework.request.Request): The incoming HTTP request.
            view (rest_framework.views.APIView): The view being accessed.
            obj: The Order instance being acted upon.

        Returns:
            bool: Same result as has_permission.
        """
        return self.has_permission(request, view)
