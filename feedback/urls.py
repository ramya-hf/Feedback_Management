from rest_framework.routers import DefaultRouter
from .views import BoardViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

urlpatterns = router.urls
