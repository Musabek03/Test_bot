from rest_framework import serializers
from .models import Question,BotUser,TestAttempt,AttemptDetail


class BotUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotUser
        fields =('id','telegram_id','full_name','username')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
    

class TestAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestAttempt
        fields = ('id','user', 'score', 'total_questions','created_at')


class AttemptDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttemptDetail
        fields = ('id', 'question','user_answer','is_correct')


class DashboardSerializer(serializers.Serializer):
  
  total_users = serializers.IntegerField()
  users_with_attempts = serializers.IntegerField()
  top_users = serializers.ListField()
  hard_questions = serializers.ListField()
