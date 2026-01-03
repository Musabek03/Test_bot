import os
import sys
import asyncio
import logging
import random
import django
from decouple import config as env

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton, 
    FSInputFile
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.conf import settings

# Modellerdi import qılamız
from testbot.models import BotUser, Question, TestAttempt, AttemptDetail

API_TOKEN = env('API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class UserStates(StatesGroup):
    register = State()
    test_process = State()

@sync_to_async
def get_user(tg_id):
    return BotUser.objects.filter(telegram_id=tg_id).first()

@sync_to_async
def create_user(tg_id, name):
    return BotUser.objects.create(telegram_id=tg_id, full_name=name)

@sync_to_async
def get_random_questions_data(count=10):
    """
    Sorawlardı bazadan alıp, olardı DICTIONARY (sözlik) formatına ótkizemiz.
    Bul State ishinde saqlaw ushın eń qawipsiz jol.
    """
    questions_query = list(Question.objects.order_by('?')[:count])
    
    questions_data = []
    
    for q in questions_query:
        variants = [
            {'key': 'option_a', 'text': q.option_a},
            {'key': 'option_b', 'text': q.option_b},
            {'key': 'option_c', 'text': q.option_c},
            {'key': 'option_d', 'text': q.option_d},
        ]
        random.shuffle(variants)
        
        questions_data.append({
            'id': q.id,
            'text': q.text,
            'image_path': str(q.image) if q.image else None,
            'variants': variants,
            'correct_key': q.correct_answer 
        })
        
    return questions_data

@sync_to_async
def save_test_result(user_tg_id, user_answers_dict, total_score):
    user = BotUser.objects.get(telegram_id=user_tg_id)
    total_q = len(user_answers_dict)
    
    attempt = TestAttempt.objects.create(user=user, score=total_score, total_questions=total_q)
    
    details = []
    for q_id, data in user_answers_dict.items():
        question = Question.objects.get(id=q_id)
        selected_text = getattr(question, data['selected_key'], "Belgisiz")
        
        details.append(AttemptDetail(
            attempt=attempt,
            question=question,
            user_answer=selected_text, 
            is_correct=data['is_correct']
        ))
    
    AttemptDetail.objects.bulk_create(details)
    return attempt

@sync_to_async
def get_last_results(tg_id):
    user = BotUser.objects.get(telegram_id=tg_id)
    attempts = TestAttempt.objects.filter(user=user).order_by('-created_at')[:10]
    return list(attempts)

async def main():
    print("Bot iske túsirildi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    