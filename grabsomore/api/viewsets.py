from rest_framework import viewsets
from .serializers import UserSerializer
from grabsomore.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer