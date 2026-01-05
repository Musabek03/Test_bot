from django.contrib import admin
from models import BotUser,AttemptDetail

@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id','full_name','username')


@admin.register(AttemptDetail)
class AttemptDetailAdmin(admin.ModelAdmin):
    list_display = ('attempt','question','user_answer','is_correct')