## 07. LLM 모델 

chatbot/config.py 파일을 만들고 아래 코드 넣기 

llm 모델과 임베딩 모델 선정 

입력 파일, 추가되는 데이터 위치와 VectorDB 위치 

```python

"""
PATH, URL 등 전역 상수 설정
"""
# 필요시 클래스로 선언

# intfloat/multilingual-e5-small
config = {
    "llm_predictor" : {
        "model_name"  : "gpt-3.5-turbo", # gpt-3.5-turbo-0613,
        "temperature" : 0
    },
    "embed_model" : {
        "model_name" : "text-embedding-ada-002", # "intfloat/e5-small",
        "cache_directory" : "",
    },
    "path" : {
        "input_directory" : "./documents",
    },
    "chroma" : {
        "persist_dir" : "./database",
    },
    
    "similarity_k" : 0.25,  # 유사도 측정시 기준 값
    "retriever_k" : 3,      # 유사도 top k개 청크 가져오기
}

```

### urls.py 

대화 시작 세션 이후 대화가 본격적으로 이루어지는 창 

```python

from django.urls import path, include
from .views import ChatbotIndexView, ChatbotResponseView

from . import views

app_name = 'chatbot'
urlpatterns = [
    path('', ChatbotIndexView.as_view(), name='chatbot_index'),
    # 추가 
    path("result/", ChatbotResponseView.as_view(), name='chatbot_result'),
]

```

### prompt.py 

LLM 모델의 프롬프트 

```python

'''
프롬프트 초기화
'''
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 사용자 질문 맥락화 프롬프트
contextualize_q_system_prompt = """
주요 목표는 사용자의 질문을 이해하기 쉽게 다시 작성하는 것입니다.
사용자의 질문과 채팅 기록이 주어졌을 때, 채팅 기록의 맥락을 참조할 수 있습니다.
채팅 기록이 없더라도 이해할 수 있는 독립적인 질문으로 작성하세요.
질문에 바로 대답하지 말고, 필요하다면 질문을 다시 작성하세요. 그렇지 않다면 질문을 그대로 반환합니다.        
"""
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])


# 질문 프롬프트
qa_system_prompt = """
당신의 역할은 해외진출을 계획하는 기업에게 해외진출 컨설팅을 도와주는 사람입니다.
질문자는 벤처기업, 스타트업 등 작은 회사의 직원 또는 사장입니다. 질문자의 질문에 대해 정확한 사실만을 대답해야하는 직원입니다.
아래에 주어지는 검색된 내용을 토대로 질문에 대해 답변하세요.
답을 모를 경우, '죄송합니다. 제가 아직 모르는 내용입니다.' 라고 대답하세요. 
최대한 명확하고 이해하기 쉽게 대답하세요.
질문자가 추가적인 대답을 원할 경우, 상세히 대답하며, 대답의 근거를 제시하세요.

{context}
"""

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", qa_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

```

### generation.py 

RagPipeLine을 만들어서 

DB에 접근해서 검색도 하고 

세션도 만들어 내고 

문장 생성도 하고 

```python

'''
인덱스 생성, RAG 파이프라인 구축
'''
import csv
import redis
import json
from django.conf import settings
from .models import ChatSession # lazy load 추가
from django.utils import timezone
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import HumanMessage, SystemMessage, Document
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain.memory import ConversationBufferMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_core.runnables import RunnableBranch, RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser
# from langchain.agents import Tool, create_openai_tools_agent, AgentExecutor
# from langchain import hub
# from langchain.tools.retriever import create_retriever_tool
# from llama_index.core import (
#     SimpleDirectoryReader
# )

from .config import config
from .prompt import contextualize_q_prompt, qa_prompt



# Agent-Tool 사용 시도해보기
class RAGPipeline:
    def __init__(self):
        """ 객체 생성 시 멤버 변수 초기화 """
        
        self.llm = ChatOpenAI(
                    model       = config['llm_predictor']['model_name'],        # llm 모델
                    temperature = config['llm_predictor']['temperature']        # 창의성
                    )
        
        self.vector_store       = self.init_vector_store()
        self.retriever          = self.init_retriever()
        
        self.chain              = self.init_chain()
        self.session_histories  = {}
    
    
    def init_vector_store(self):
        """ Vector store 초기화 """
        embeddings = OpenAIEmbeddings( model=config['embed_model']['model_name'] )
        vector_store = Chroma(
            persist_directory=config["chroma"]["persist_dir"], 
            embedding_function=embeddings
        )
        print(f"[초기화] vector_store 초기화 완료")
        return vector_store
        
        
    def init_retriever(self):
        """ Retriever 초기화 
        다른 검색방법 사용해보기
        Hybrid Search
        """
        retriever = self.vector_store.as_retriever(
            search_kwargs = {"k": config["retriever_k"]},
            search_type   = "similarity"
        )
        print(f"[초기화] retriever 초기화 완료")
        return retriever
    
    
    # 모델과 검색기 chain 걸기 
    def init_chain(self):
        """ chain 초기화 
        리트리버 전용 체인으로 변경해보기
        create_stuff_documents_chain[현재 사용] : 문서 목록을 가져와서 모두 프롬프트로 포맷한 다음 해당 프롬프트를 LLM에 전달합니다.
        create_history_aware_retriever : 대화 기록을 가져온 다음 이를 사용하여 검색 쿼리를 생성하고 이를 기본 리트리버에 전달
        create_retrieval_chain : 사용자 문의를 받아 리트리버로 전달하여 관련 문서를 가져옵니다. 그런 다음 해당 문서(및 원본 입력)는 LLM으로 전달되어 응답을 생성
        """
        
        # 사용자의 질문 문맥화 <- 프롬프트 엔지니어링
        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, contextualize_q_prompt
        )
        
        # 응답 생성 + 프롬프트 엔지니어링
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        
        # 최종 체인 생성
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        print("[초기화] RAG chain 초기화 완료")
        return rag_chain
    
    # 대화가 이어지게 대화 히스토리를 만들고 rag chain 
    def chat_generation(self, question: str, session_id: str) -> dict:
        # 채팅 기록 관리
        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            if session_id not in self.session_histories:
                self.session_histories[session_id] = ChatMessageHistory()
                print(f"[히스토리 생성] 새로운 히스토리를 생성합니다. 세션 ID: {session_id}")
            return self.session_histories[session_id]

        conversational_rag_chain = RunnableWithMessageHistory(
            self.chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )

        response = conversational_rag_chain.invoke(
            {"input": question},
            config={"configurable": {"session_id": session_id}}
        )

        print(f'[응답 생성] 실제 모델 응답: response => \n{response}\n')
        print(f"[응답 생성] 세션 ID [{session_id}]에서 답변을 생성했습니다.")


        return response["answer"]
    

```

### apps.py 

```python

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

```

### views.py 

```python

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

```

![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/6c20c47b-145a-4111-ad69-a4d5b8697c47)


