from django.urls import path, include
from .views import ChatbotIndexView

from . import views

app_name = 'chatbot'
urlpatterns = [
    path('', ChatbotIndexView.as_view(), name='chatbot_index'),
]