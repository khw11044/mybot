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
        
        # 전역 pipeline 객체를 가져옴
        pipeline = apps.get_app_config('chatbot').pipeline
        
        # 벡터 DB에 문서 업데이트 시도
        file_path = obj.file.path
        with open(file_path, 'rb') as f:
            if pipeline.update_vector_db(f, obj.file):
                self.message_user(request, "[문서업로드] 벡터 스토어 업데이트에 성공하였습니다.")
            else:
                # 유사한 문서가 존재하여 업데이트에 실패 시 저장된 문서 삭제
                obj.delete()
                os.remove(file_path)
                self.message_user(request, "[문서업로드] 유사한 문서가 발견되어 벡터스토어 업데이트가 거절되었습니다.", level='error')


    def delete_model(self, request, obj):
        # 전역 pipeline 객체를 가져옴
        pipeline = apps.get_app_config('chatbot').pipeline
        
        # 벡터 DB에서 문서 임베딩 삭제
        pipeline.delete_vector_db_by_doc_id(str(obj.id))
        
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
