import os
import sys
import asyncio
import logging
import random
import django
from decouple import config as env

# Django sazlamaların júklew
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

# Bot hám Dispatcherdi jaratamız
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- STATE (Jaǵdaylar) ---
class UserStates(StatesGroup):
    register = State()      # Dizimnen ótiw waqtı
    test_process = State()  # Test islep atırǵan waqıt

# --- KOMEKSHI FUNKCIYALAR (DB menen islesiw) ---
# Siz jibergen funkciyalar, azmaz tolıqtırıldı

@sync_to_async
def get_user(tg_id):
    return BotUser.objects.filter(telegram_id=tg_id).first()

@sync_to_async  
def create_user(tg_id, name):
    return BotUser.objects.create(telegram_id=tg_id, full_name=name)

@sync_to_async
def get_random_questions_data(count=10):
    """
    Bazadan aktiv sorawlardı alıp, olardı aralastırıp qaytaradı.
    """
    # Tek 'is_active=True' sorawlardı alamız
    questions_query = list(Question.objects.filter(is_active=True).order_by('?')[:count])
    
    questions_data = []
    
    for q in questions_query:
        # Variantlardı formalarıstıramız
        variants = [
            {'key': 'option_a', 'text': q.option_a},
            {'key': 'option_b', 'text': q.option_b},
            {'key': 'option_c', 'text': q.option_c},
            {'key': 'option_d', 'text': q.option_d},
        ]
        random.shuffle(variants) # Variantlardı aralastıramız (A, B, C, D ornın almastıradı)
        
        questions_data.append({
            'id': q.id,
            'text': q.text,
            'image_path': str(q.image) if q.image else None,
            'variants': variants,
            'correct_key': q.correct_answer # Bazada 'option_a' sıyaqlı saqlanǵan dep esaplaymız
        })
        
    return questions_data

@sync_to_async
def save_test_result(user_tg_id, user_answers_dict, total_score):
    """
    Test juwmaqlanǵannan keyin nátiyjelerdi bazasǵa jazıw.
    """
    user = BotUser.objects.get(telegram_id=user_tg_id)
    total_q = len(user_answers_dict)
    
    # Ulıwma urınıstı (TestAttempt) jazamız
    attempt = TestAttempt.objects.create(user=user, score=total_score, total_questions=total_q)
    
    details = []
    for q_id, data in user_answers_dict.items():
        question = Question.objects.get(id=q_id)
        # Paydalanıwshı tańlaǵan varianttıń tekstin anıqlaymız (Mısalı: 'option_b' -> 'Tashkent')
        selected_text = getattr(question, data['selected_key'], "Belgisiz")
        
        details.append(AttemptDetail(
            attempt=attempt,
            question=question,
            user_answer=selected_text[:10], # DB check (max_length=10), eger A,B,C bolsa. Eger tolıq tekst bolsa lengthti arttırıń.
            is_correct=data['is_correct']
        ))
    
    AttemptDetail.objects.bulk_create(details)
    return attempt

@sync_to_async
def get_last_results(tg_id):
    """
    Paydalanıwshınıń sońǵı 10 nátiyjesin alıw.
    """
    user = BotUser.objects.filter(telegram_id=tg_id).first()
    if not user:
        return []
    attempts = TestAttempt.objects.filter(user=user).order_by('-created_at')[:10]
    return list(attempts)


# --- KEYBOARDS (Túymeler) ---

def get_main_menu():
    kb = [
        [KeyboardButton(text="🎯Test baslaw")],
        [KeyboardButton(text="📊 Meniń nátiyjelerim")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_question_keyboard(variants):
    """
    Sorawlar ushın Inline (tekst astındaǵı) túymeler.
    callback_data = varianttıń gilti (option_a, option_b...)
    """
    builder = InlineKeyboardBuilder()
    for v in variants:
        # Callback dataǵa variant giltin beremiz
        builder.add(InlineKeyboardButton(text=v['text'], callback_data=v['key']))
    builder.adjust(1) # Hár qatarda 1 túymeden bolsın
    return builder.as_markup()


# --- HANDLERS (Bot logikası) ---

# 1. /start komandası
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    user = await get_user(tg_id)

    if user:
        await message.answer(f"Qayta xosh keldińiz, {user.full_name}!", reply_markup=get_main_menu())
    else:
        await message.answer("Assalawma aleykum! Testti baslaw ushın atı-familiyańızdı kiritin:")
        await state.set_state(UserStates.register)

# 2. Registraciya (Atın jazǵanda)
@dp.message(UserStates.register)
async def process_register(message: types.Message, state: FSMContext):
    full_name = message.text
    tg_id = message.from_user.id
    
    await create_user(tg_id, full_name)
    await message.answer("Siz tabıslı dizimnen óttińiz! Bottaǵı menyu arqalı paydalanıwıńız múmkin.", reply_markup=get_main_menu())
    await state.clear()

# 3. Testti baslaw ("🎯Test baslaw" túymesi)
@dp.message(F.text == "🎯Test baslaw")
async def start_test(message: types.Message, state: FSMContext):
    # Sorawlardı júkleymiz
    questions = await get_random_questions_data(10)
    
    if not questions:
        await message.answer("Házirshe bazada sorawlar joq.")
        return

    # Stateke (yadqa) kerekli maǵlıwmatlardı saqlaymız
    await state.set_state(UserStates.test_process)
    await state.set_data({
        'questions': questions,       # Barlıq sorawlar dizimi
        'current_index': 0,           # Házirgi soraw nomeri (0-den baslanadı)
        'answers': {},                # Juwaplardı saqlaw ushın
        'score': 0                    # Toplaǵan ball
    })
    
    # Birinshi sorawdı jiberemiz
    await send_question(message, questions[0], 0, len(questions))

async def send_question(message: types.Message, question_data, current_index, total_count):
    """
    Sorawdı paydalanıwshıǵa jiberiwshi funkciya.
    Ózgeris: Soraw nomerin kórsetiw qosıldı.
    """
    # 0-den baslanǵanı ushın +1 qosamız
    q_num = current_index + 1
    
    # Mısalı: "❓ 1/10-soraw:"
    text = f"❓ <b>{q_num}/{total_count}-soraw:</b>\n\n{question_data['text']}"
    
    markup = get_question_keyboard(question_data['variants'])
    
    # Eger súwret bolsa
    if question_data['image_path']:
        full_path = os.path.join(settings.MEDIA_ROOT, question_data['image_path'])
        if os.path.exists(full_path):
            photo = FSInputFile(full_path)
            await message.answer_photo(photo=photo, caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            await message.answer(text, reply_markup=markup, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=markup, parse_mode="HTML")

# 4. Juwap beriw (Inline button basılǵanda)
@dp.callback_query(UserStates.test_process)
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    questions = data['questions']
    current_index = data['current_index']
    current_q = questions[current_index]
    
    selected_key = callback.data # option_a, option_b...
    correct_key = current_q['correct_key']
    
    # Durıs yamasa qáte ekenin tekseremiz
    is_correct = (selected_key == correct_key)
    
    # Juwaptı yadqa saqlaymız
    answers = data['answers']
    answers[current_q['id']] = {
        'selected_key': selected_key,
        'is_correct': is_correct,
        'q_text': current_q['text'],
        'correct_key': correct_key,
        'variants': current_q['variants']
    }
    
    # Balldı esaplaymız
    if is_correct:
        data['score'] += 1
        
    # Eski xabardı óshiriw (chat taza turıwı ushın)
    await callback.message.delete()
    
    # Keyingi sorawǵa ótiw
    next_index = current_index + 1
    
    if next_index < len(questions):
        # Hali sorawlar bar
        data['current_index'] = next_index
        data['answers'] = answers
        await state.set_data(data)
        await send_question(callback.message, questions[next_index], next_index, len(questions))
    else:
        # Test juwmaqlandı
        await finish_test(callback.message, state, data)

async def finish_test(message: types.Message, state: FSMContext, data):
    """
    Testti juwmaqlaw hám nátiyjeni kórsetiw.
    """
    score = data['score']
    total = len(data['questions'])
    answers = data['answers']
    
    # Bazaga saqlaymız
    await save_test_result(message.chat.id, answers, score)
    
    result_text = f"🏁 <b>Test juwmaqlandı!</b>\n\n"
    result_text += f"✅ Nátiyje: {total} sorawdan {score} durıs taptıńız.\n\n"
    
    # Qátelerdi kórsetiw
    if score < total:
        result_text += "<b>❌ Qáte juwaplar:</b>\n\n"
        counter = 1
        for q_id, ans_data in answers.items():
            if not ans_data['is_correct']:
                # Qáte ketken sorawdı tabamız
                q_text = ans_data['q_text']
                
                # Paydalanıwshı tańlaǵan variant tekstin tabıw
                user_choice_text = "Belgisiz"
                correct_choice_text = "Belgisiz"
                
                for v in ans_data['variants']:
                    if v['key'] == ans_data['selected_key']:
                        user_choice_text = v['text']
                    if v['key'] == ans_data['correct_key']:
                        correct_choice_text = v['text']
                
                result_text += f"{counter}. {q_text}\n"
                result_text += f"   Siz: {user_choice_text} ❌\n"
                result_text += f"   Durıs: {correct_choice_text} ✅\n\n"
                counter += 1
    
    await message.answer(result_text, parse_mode="HTML", reply_markup=get_main_menu())
    await state.clear()

# 5. Statistika ("📊 Meniń nátiyjelerim")
@dp.message(F.text == "📊 Meniń nátiyjelerim")
async def show_stats(message: types.Message):
    attempts = await get_last_results(message.from_user.id)
    
    if not attempts:
        await message.answer("Sizde hálishe sheshilgen testler joq.")
        return
    
    text = "📊 <b>Sońǵı nátiyjelerińiz:</b>\n\n"
    for att in attempts:
        # Tashkent waqtı menen kórsetiw ushın (simple formatting)
        date_str = att.created_at.strftime("%d.%m.%Y %H:%M")
        text += f"📅 {date_str} | 🎯 {att.score}/{att.total_questions}\n"
        
    await message.answer(text, parse_mode="HTML")

# --- START BOT ---
async def main():
    print("Bot iske túsirildi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())