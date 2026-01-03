from rest_framework.routers import DefaultRouter
from .views import BotUserViewSet,QuestionViewSet,TestAttemptViewSet,TestAttemptDetailViewSet,DashboardViewSet
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()

router.register('admin/questions', QuestionViewSet, basename='question')
router.register('admin/users', BotUserViewSet, basename='user')
router.register('admin/attempts', TestAttemptViewSet, basename='attempt')



urlpatterns = [
    path('', include(router.urls)),
    path('admin/dashboard/', DashboardViewSet.as_view()),
    path('api/admin/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/admin/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
