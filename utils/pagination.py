from rest_framework.pagination import CursorPagination

from alx_project_nexus import settings


class CursorSetPagination(CursorPagination):
    """
    Custom pagination class that extends CursorPagination.
    This class allows for cursor-based pagination with a customizable page size
    and ordering based on query parameters.
    It uses the `PAGINATION_PER_PAGE` setting to determine the number of items per page.
    The `get_ordering` method retrieves the ordering from the request query parameters,
    allowing for dynamic ordering of the queryset.
    If no ordering is specified, it defaults to the `ordering` attribute of the view or
    the class-level `ordering` attribute.
    """
    page_size = settings.PAGINATION_PER_PAGE

    def get_ordering(self, request, queryset, view):
        ordering_param = request.query_params.get('ordering')

        if ordering_param:
            return [field.strip() for field in ordering_param.split(',')]

        return getattr(view, 'ordering', self.ordering)
