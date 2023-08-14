from rest_framework.pagination import CursorPagination


class MyCursorPagination(CursorPagination):
    page_size = 3
    cursor_query_param = 'c'
    ordering = 'roll'