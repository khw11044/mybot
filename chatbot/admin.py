"""
Django 관리자 사이트에 모델 등록, 관리하는 모듈
"""
from django.contrib import admin
from django.http import HttpRequest
from .models import RagDocument, ChatSession
from django.apps import apps
import os


@admin.register(RagDocument)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')

    def save_model(self, request: HttpRequest, obj: RagDocument, form, change):
        # 파일 경로 중복 확인
        if RagDocument.objects.filter(file=f"documents/{os.path.basename(obj.file.path)}").exists(): # aivle_article.csv
            self.message_user(request, "RDB에 같은 파일이 이미 존재합니다.", level='error')
            return

        # 임시로 문서 저장
        super().save_model(request, obj, form, change)
        
       

    def delete_model(self, request, obj):
       
        # 문서 및 메타데이터 삭제
        file_path = obj.file.path
        super().delete_model(request, obj)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            
        self.message_user(request, "[문서삭제] 벡터 스토어에서 해당 문서와 임베딩 데이터를 성공적으로 삭제하였습니다.")


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'start_time', 'end_time')
    list_filter = ('start_time', 'end_time')
    search_fields = ('session_id', 'chat_history')
    actions = ['delete_selected']
