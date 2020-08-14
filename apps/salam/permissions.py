from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # we'll always allow OPTIONS requests
        if request.method == 'OPTIONS':
            return True

        # allow admins
        if request.user.is_staff:
            return True

        # if firm is none, firm is deleted or unknown, no access allowed
        if not obj.firm_id:
            return False

        # permissions are only allowed to the firm who made the order
        return obj.firm_id == request.user.firm_id


class WarehousePermissions(permissions.BasePermission):
    """
    Allows warehouse operators to edit receipt and owner of receipt to view
    """

    def has_permission(self, request, view):
        # only warehouses can add receipts
        if request.method not in permissions.SAFE_METHODS:
            return request.user.firm.type == 'WRHS'
        return True

    def has_object_permission(self, request, view, obj):
        # always allow OPTIONS requests
        if request.method == 'OPTIONS':
            return True

        if request.user.is_staff or (request.user.firm_id == obj.warehouse_id):
            return True

        # warehouse receipt holders have read access only
        if request.method in ['GET', 'HEAD']:
            return request.user.firm_id == obj.firm_id

        # all others have no access
        return False
