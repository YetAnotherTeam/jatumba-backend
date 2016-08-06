from rest_framework.pagination import PageNumberPagination


class CompositionVersionPagination(PageNumberPagination):
    page_size = 5
