from django.shortcuts import render
from django.views.generic import TemplateView

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
