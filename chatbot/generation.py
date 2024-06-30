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
    
  