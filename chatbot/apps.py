"""
앱 설정을 정의하는 모듈
"""
from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chatbot"
    
    def ready(self):
        from .generation import RAGPipeline
        self.pipeline = RAGPipeline() # 앱 실행 시 전역 파이프라인 객체 생성

    def initialize_pipeline(self):
        from .generation import RAGPipeline
        self.pipeline = RAGPipeline()