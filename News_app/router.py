from grabsomore.api.viewsets import UserViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('user', UserViewSet, basename='user_api')
urlpatterns = router.urls
