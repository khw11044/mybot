from django.urls import path, include
from .views import ChatbotIndexView, ChatbotResponseView

from . import views

app_name = 'chatbot'
urlpatterns = [
    path('', ChatbotIndexView.as_view(), name='chatbot_index'),
    # 추가 
    path("result/", ChatbotResponseView.as_view(), name='chatbot_result'),
]