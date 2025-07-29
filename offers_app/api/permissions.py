from rest_framework.permissions import BasePermission

class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'type', None) == 'business')


class IsUserCreator(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            offer = view.get_object()
            return bool(request.user and request.user.is_authenticated and offer.creator == request.user)
        return True

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
