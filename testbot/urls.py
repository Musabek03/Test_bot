from rest_framework.routers import DefaultRouter
from .views import BotUserViewSet,QuestionViewSet,TestAttemptViewSet,TestAttemptDetailViewSet,DashboardViewSet

from django.urls import path, include

router = DefaultRouter()

router.register('admin/questions', QuestionViewSet, basename='question')
router.register('admin/users', BotUserViewSet, basename='user')
router.register('admin/attempts', TestAttemptViewSet, basename='attempt')
#router.register('admin/dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/dashboard/', DashboardViewSet.as_view()),
    #path('admin/import-questions/', QuestionImportViewSet.as_view(), name='import-questions'),
]
