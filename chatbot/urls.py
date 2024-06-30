from django.urls import path, include
from .views import ChatbotResponseView, ChatbotIndexView, StartNewSessionView, ChatSessionViewSet # , UpdateDocumentView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='session')

app_name = 'chatbot'
urlpatterns = [
    path('', ChatbotIndexView.as_view(), name='chatbot_index'),
    path("result/", ChatbotResponseView.as_view(), name='chatbot_result'),
    path('new_session/', StartNewSessionView.as_view(), name='new_session'),
    path('api/', include(router.urls)),
    # path("admin/chatbot/update_document/", UpdateDocumentView.as_view(), name='update_document'),
]
