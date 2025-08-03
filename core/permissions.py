from rest_framework.permissions import BasePermission


class IsBusinessUser(BasePermission):
    """
    Permission class that grants access only to authenticated business users.

    Checks that the request has a valid authenticated user and that the user's
    `type` attribute equals `'business'`.

    Methods:
        has_permission(request, view) -> bool:
            Return True if the user is authenticated and is a business user.
    """
    def has_permission(self, request, view):
        """
        Determine whether the current user is allowed to access the view.

        Args:
            request (rest_framework.request.Request): The incoming HTTP request.
            view (rest_framework.views.APIView): The view being accessed.

        Returns:
            bool: True if `request.user` exists, is authenticated, and has
                  `type == 'business'`; False otherwise.
        """
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'type', None) == 'business')


class IsCustomerUser(BasePermission):
    """
    Permission class that grants access only to authenticated customer users.

    Checks that the request has a valid authenticated user and that the user's
    `type` attribute equals `'customer'`.

    Methods:
        has_permission(request, view) -> bool:
            Return True if the user is authenticated and is a customer user.
    """
    def has_permission(self, request, view):
        """
        Determine whether the current user is allowed to access the view.

        Args:
            request (rest_framework.request.Request): The incoming HTTP request.
            view (rest_framework.views.APIView): The view being accessed.

        Returns:
            bool: True if `request.user` exists, is authenticated, and has
                  `type == 'customer'`; False otherwise.
        """
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'type', None) == 'customer')
