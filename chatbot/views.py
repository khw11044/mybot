"""
뷰 함수 정의 : 사용자 요청 처리, HTTP 응답 반환 
"""
import os
import csv
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin
from django.views import View
from .models import ChatSession

from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# from .generation import chat_generation, update_vector_store, initialize_vector_store, initialize_chain
from .serializers import MessageSerializer 
from .models import ChatSession, RagDocument
from .serializers import ChatSessionSerializer
from django.apps import apps
from django.shortcuts import get_object_or_404
import uuid

    
class ChatbotIndexView(TemplateView):
    template_name = "chatbot/index.html"
    
    @swagger_auto_schema(
        operation_id='첫 접속 시 새 채팅 시작',
        operation_description='채팅 페이지 첫 접속 시 새로운 세션 생성',
        tags=['Chat'],
        request_body=MessageSerializer,
        responses={200: 'Success'}
    )
    def get(self, request, *args, **kwargs):
        if not request.session.get('session_id'):
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
            request.session['question'] = None
            request.session['answer'] = None
            print(f'새로운 세션 생성 >> {session_id}')
        
        return render(request, self.template_name)
   

class StartNewSessionView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='버튼을 눌러 새로운 채팅 시작하기',
        operation_description='유저가 새로운 채팅 시작 버튼을 누르면 새로운 세션으로 변경(현재 대화 문맥가 다른 별도의 대화 시작)',
        tags=['Chat'],
        request_body=MessageSerializer,
        responses={200: 'Success'}
    )
    def post(self, request):
        print("StartNewSessionView POST 호출됨")
        # 기존 세션 저장
        if 'session_id' in request.session:
            session_id = request.session['session_id']
            pipeline = apps.get_app_config('chatbot').pipeline
            print(f"[세션 저장] 세션 ID: {session_id}")
            pipeline.save_session_to_db(session_id)

        # 기존 세션 삭제
        request.session.flush()
        print("[세션 삭제] 기존 세션을 삭제했습니다.")

        # 새로운 세션 생성
        session_id = str(uuid.uuid4())
        request.session['session_id'] = session_id
        request.session['question'] = None
        request.session['answer'] = None
        print(f"[새로운 세션 생성] 새로운 세션 ID: {session_id}")

        # RAGPipeline 객체 초기화
        apps.get_app_config('chatbot').initialize_pipeline()
        print(f"[RAGPipeline 초기화] 새로운 RAGPipeline 객체를 생성했습니다.")

        return Response({'message': 'New session started', 'session_id': session_id})


class ChatbotResponseView(APIView, TemplateResponseMixin):
    permission_classes = [AllowAny]
    # parser_classes = [JSONParser]
    template_name = "chatbot/result.html"

    @swagger_auto_schema(
        operation_id='채팅 쿼리 송수신',
        operation_description='사용자로부터 쿼리를 입력받고 LLM으로부터 받은 답변 반환, 브라우저에서 새로 고침 시 현재 채팅 내용 유지',
        tags=['Chat'],
        request_body=MessageSerializer,
        responses={200: 'Success'}
    )
    def post(self, request):
        print("ChatbotResponseView POST 호출됨")
        question = request.data.get('question')
        
        
        if 'session_id' in request.session:
            session_id = request.session['session_id']
        else:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
            print(f'새로운 세션 생성 >> {session_id}')
            
        # print('===========================================>',session_id)
            
        # session_id = request.data.get('session_id')
        # # 세션 ID 확인 및 생성
        # if not session_id or session_id == 'default-session-id':
        #     session_id = str(uuid.uuid4())
        #     request.session['session_id'] = session_id
        #     print(f'새로운 세션 생성 >> {session_id}')
        
        
        print(f'현재 세션 ID : {session_id}')
        # 전역 pipeline 객체 가져오기
        pipeline = apps.get_app_config('chatbot').pipeline
        
        answer = pipeline.chat_generation(question, session_id) 
        request.session['question'] = question
        request.session['answer'] = answer
        # context = {'question': question, 'answer': answer}
     
        # return render(request, 'chatbot/result.html', context)
        # return JsonResponse({'question': question, 'answer': answer}) # API 호출 반환 용
        return JsonResponse({'answer': answer})


    def get(self, request, *args, **kwargs):
        # 브라우저에서 새로고침을 누르면 기존 세션에서 질문과 답변을 가져옴
        session_id = request.session.get('session_id')
        question = request.session.get('question')
        answer = request.session.get('answer')

        # 만약 세션이 없으면, 새로운 세션 생성
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
            question = None
            answer = None
            print(f'새로운 세션 생성 >> {session_id}')

        context = {'question': question, 'answer': answer}
        return render(request, 'chatbot/result.html', context)
    
    
class ChatSessionViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_id='list_sessions',
        operation_description='모든 채팅 세션 목록을 가져옵니다.',
        responses={200: ChatSessionSerializer(many=True)}
    )
    def list(self, request):
        queryset = ChatSession.objects.all()
        serializer = ChatSessionSerializer(queryset, many=True)
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_id='retrieve_session',
        operation_description='세션 ID로 특정 채팅 세션을 가져옵니다.',
        responses={200: ChatSessionSerializer()}
    )
    def retrieve(self, request, pk=None):
        queryset = ChatSession.objects.all()
        session = get_object_or_404(queryset, session_id=pk)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_id='delete_session',
        operation_description='세션 ID로 특정 채팅 세션을 삭제합니다.',
        responses={204: 'No Content'}
    )
    def destroy(self, request, pk=None):
        queryset = ChatSession.objects.all()
        session = get_object_or_404(queryset, session_id=pk)
        session.delete()
        return Response({'message': 'Session deleted successfully'}, status=204)