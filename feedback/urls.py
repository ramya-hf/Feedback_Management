from rest_framework.routers import DefaultRouter
from .views import BoardViewSet, FeedbackViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = router.urls
