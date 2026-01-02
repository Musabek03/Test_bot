from django.shortcuts import render
from rest_framework.response import Response
from .models import BotUser,Question, TestAttempt, AttemptDetail
from .serializers import BotUserSerializer,QuestionSerializer,TestAttemptSerializer, AttemptDetailSerializer,DashboardSerializer
from rest_framework import viewsets,filters
from rest_framework.views import APIView
from django.db.models import Count, Sum


class BotUserViewSet(viewsets.ModelViewSet):
    queryset = BotUser.objects.all()
    serializer_class = BotUserSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class TestAttemptViewSet(viewsets.ModelViewSet):
    queryset = TestAttempt.objects.all()
    serializer_class = AttemptDetailSerializer

class TestAttemptDetailViewSet(viewsets.ModelViewSet):
    queryset = AttemptDetail.objects.all()
    serializer_class = TestAttemptSerializer

class DashboardViewSet(APIView):

    def get(self, request):
        total_users = BotUser.objects.count()

        users_with_attempts = BotUser.objects.filter(testattempt__isnull = False).distinct().count()

        top_users = TestAttempt.objects.values('user__id', 'user__full_name').annotate(total_score=Sum('score')).order_by('-total_score')[:10]

        top_users = list(top_users)

        hard_questions = ( AttemptDetail.objects
                          .filter(is_correct = False)
                          .values('question__id', 'question__text')
                          .annotate(wrong_count = Count('id'))
                          .order_by('-wrong_count')[:10] )
        

        hard_questions = list(hard_questions)

        data = {
            'total_users': total_users,
            'users_with_attempts': users_with_attempts,
            'top_users': top_users,
            'hard_questions': hard_questions

        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data)
