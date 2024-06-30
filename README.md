## 06. 채팅 페이지 추가하기

### 1. 직렬화 - chatbot/serializers.py

우리는 admin에서 관리 가능한 챗 세션을 미리 만들었다. 

앞으로 채팅 페이지에서 챗에 대한 세션 관리를 하기 위해 미리 아래와 같은 작업을 해준다. 

chatbot 폴더에 serializers.py 파일을 만들고 아래 코드 넣기 

```python 

from rest_framework import serializers
from .models import ChatSession

class MessageSerializer(serializers.Serializer):
    question = serializers.CharField(help_text='사용자 메시지')
    session_id = serializers.CharField(help_text='세션 ID', required=False)


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['session_id', 'start_time', 'end_time', 'chat_history']

```

### 2. chatbot/views.py 

다음 코드 넣기 

```python

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

```


swagger 공부하기 

[링크1](https://velog.io/@lu_at_log/drf-yasg-and-swagger)

[링크1](https://hello-cruiser.tistory.com/entry/%EB%AC%B8%EC%84%9C%ED%99%94%EB%A5%BC-%EC%9C%84%ED%95%9C-drf-yasg-%EC%A0%81%EC%9A%A9%ED%95%98%EA%B8%B0)


### 3. chatbot/urls.py

```python

from django.urls import path, include
from .views import ChatbotIndexView

from . import views

app_name = 'chatbot'
urlpatterns = [
    path('', ChatbotIndexView.as_view(), name='chatbot_index'),
]

```


### templates 

코드 업데이트 

'채팅 시작하기' 버튼 클릭하면 'chatbot:chatbot_index' 로 페이지 이동 

templates/index.html 

```html

<div class="wrapper">
    <div class="hero-container">
        <div class="hero">
            <h1 class="hero__heading">당신의 도전이 조금 더 쉬어지도록 </h1>
            <h3 class="hero__heading"> 리트리버가 당신의 도전을 보조할께요 </h3>
            <a class="btn" href="#" title="채팅 시작하기">채팅 시작하기</a>
        </div>
        <div class="hero hero--secondary" aria-hidden="true" data-hero>
            <p class="hero__heading">Welcome to Retriver</p>
            <a class="btn" href="{% url 'chatbot:chatbot_index' %}" title="채팅 시작하기">채팅 시작하기</a>
        </div>
    </div>
</div>

```

templates/chatbot 폴더 추가 하기 

static/chatbot 폴더 추가 하기 



