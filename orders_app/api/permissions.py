from rest_framework.permissions import BasePermission


class IsUserBusinessOwner(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'PATCH':
            order = view.get_object()
            return bool(request.user == order.business_user)
        return True

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
