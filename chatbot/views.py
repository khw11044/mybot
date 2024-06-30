from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.generic.base import TemplateResponseMixin
from django.apps import apps

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser

from .serializers import MessageSerializer 


import uuid

from drf_yasg.utils import swagger_auto_schema

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

class ChatbotResponseView(APIView, TemplateResponseMixin):
    permission_classes = [AllowAny]
    # parser_classes = [JSONParser]
    template_name = "chatbot/result.html"


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