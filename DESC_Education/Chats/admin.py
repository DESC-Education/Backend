from django.contrib import admin
from Chats.models import Chat, ChatMembers, Message


admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(ChatMembers)
# Register your models here.
