from rest_framework.pagination import PageNumberPagination

class ProductListPagination(PageNumberPagination):
    page_size = 12  # default page size
    page_size_query_param = 'page_size'  # allows frontend override
    max_page_size = 100
