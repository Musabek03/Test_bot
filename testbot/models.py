from django.db import models


class BotUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    full_name = models.CharField(max_length=80)
    username = models.CharField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Question(models.Model):
    text = models.TextField()
    image = models.ImageField(null=True, blank=True)
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_answer = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)


class TestAttempt(models.Model):
    user = models.ForeignKey(BotUser,on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)


class AttemptDetail(models.Model):
    attempt = models.ForeignKey(TestAttempt,on_delete=models.CASCADE)
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=10)
    is_correct = models.BooleanField()
    