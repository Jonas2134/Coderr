from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = "page_size"
