from django.shortcuts import render
from .models import BotUser,Question, TestAttempt, AttemptDetail
from .serializers import BotUserSerializer,QuestionSerializer,TestAttemptSerializer, AttemptDetailSerializer
from rest_framework import viewsets,filters

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
    serializer_class = AttemptDetailSerializer

    


