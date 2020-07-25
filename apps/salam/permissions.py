from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # allow admins
        if request.user.is_staff:
            return True

        # if party is none, party is deleted or unknown, no access allowed
        if not obj.party_id:
            return False

        # Write permissions are only allowed to the party who made the order
        return obj.party_id == request.user.party_id