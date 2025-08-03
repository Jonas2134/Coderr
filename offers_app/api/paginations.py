from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """
    Pagination class for paginating Offer list endpoints.

    Provides page-based navigation with a configurable default page size
    and an optional query parameter to override it per-request.

    Attributes:
        page_size (int): Default number of items returned per page.
        page_size_query_param (str): Query parameter name that allows clients
            to set a custom page size (e.g., `?page_size=5`).
    """
    page_size = 1
    page_size_query_param = "page_size"
