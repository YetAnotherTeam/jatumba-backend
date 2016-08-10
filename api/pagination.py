from rest_framework.pagination import PageNumberPagination


class CompositionVersionPagination(PageNumberPagination):
    page_size = 5


class UserPagination(PageNumberPagination):
    page_size = 21
