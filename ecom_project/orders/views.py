from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView , CreateAPIView

from .serializers import OrderSerializer
# Create your views here.



class OrderCreateView(CreateAPIView):
    """
    View to create a new order.
    """
    serializer_class = OrderSerializer  
