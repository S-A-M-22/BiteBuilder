from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class AdminUsersPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = "page_size"  

    def get_paginated_response(self, data):
        return Response({
            "results": data,
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
        })