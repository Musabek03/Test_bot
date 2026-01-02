from django.shortcuts import render
from rest_framework.response import Response
from .models import BotUser,Question, TestAttempt, AttemptDetail
from .serializers import BotUserSerializer,QuestionSerializer,TestAttemptSerializer, AttemptDetailSerializer,DashboardSerializer, ImportQuestionSerializer
from rest_framework import viewsets,filters,status
from rest_framework.views import APIView
from django.db.models import Count, Sum
import pandas 
from rest_framework.decorators import action


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


class QuestionViewSet(viewsets.ModelViewSet):
    # Bul jerler o'zgerissiz turadi
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    
    @action(detail=False, methods=['POST'], url_path='import-excel', serializer_class=ImportQuestionSerializer)
    def import_excel(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file = serializer.validated_data['file']
        
        try:
            df = pandas.read_excel(file).fillna('')
            
            questions = [
                Question(
                    text=row['text'],
                    option_a=row['option_a'],
                    option_b=row['option_b'],
                    option_c=row['option_c'],
                    option_d=row['option_d'],
                    correct_answer=row['correct_answer'],
                    is_active=True
                )
                for index, row in df.iterrows()
            ]
            
            Question.objects.bulk_create(questions)
            return Response({"status": "Success", "count": len(questions)}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




# class QuestionImportViewSet(viewsets.ModelViewSet):
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer

#     @action(detail=False, methods=['POST'], url_path='import-excel', serializer_class=ImportQuestionSerializer)

#     def import_excel(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         file = serializer.validated_data['file']
        
#         try:
          
#             df = pandas.read_excel(file).fillna('')
            
#             questions = [
#                 Question(
#                     text=row['text'],
#                     option_a=row['option_a'],
#                     option_b=row['option_b'],
#                     option_c=row['option_c'],
#                     option_d=row['option_d'],
#                     correct_answer=row['correct_answer'],
#                     is_active=True
#                 )
#                 for index, row in df.iterrows()
#             ]
            
#             Question.objects.bulk_create(questions)

#             return Response({"status": "Success", "count": len(questions)}, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)