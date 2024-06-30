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

# from .models import Documents


# Agent-Tool 사용 시도해보기
class RAGPipeline:
    
    def __init__(self):
        """ 객체 생성 시 멤버 변수 초기화 """
        self.SIMILARITY_THRESHOLD = config["similarity_k"]
        self.llm = ChatOpenAI(
            model       = config['llm_predictor']['model_name'],
            temperature = config['llm_predictor']['temperature']
        )
        self.vector_store   = self.init_vector_store()
        self.retriever  = self.init_retriever()
        self.chain      = self.init_chain()
        self.session_histories = {}    
        self.redis_client = redis.Redis.from_url(settings.CACHES["default"]["LOCATION"])
        
    
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

        # Redis에 대화 기록 저장
        chat_history_key = f"chat_history:{session_id}"
        try:
            print(f'--------> Redis 키: {chat_history_key}')
            chat_history = self.redis_client.get(chat_history_key)
            print('-------->',chat_history)
            if chat_history:
                chat_history = json.loads(chat_history)
            else:
                chat_history = []

            chat_history.append({"question": question, "answer": response["answer"]})
            print(f'=========> 저장할 대화 기록: {chat_history}')
            print(f'=========> 저장할 대화 기록 json: {json.dumps(chat_history)}')
            self.redis_client.set(chat_history_key, json.dumps(chat_history))        
            print(f"[Redis 저장] 세션 ID [{session_id}]의 대화 기록을 Redis에 저장했습니다.")
        except Exception as e:
            print(f"[Redis 저장 실패] 세션 ID [{session_id}]의 대화 기록 저장 중 오류 발생: {e}")

        return response["answer"]

    
    
    def save_session_to_db(self, session_id: str):
        """
        Redis에 저장된 대화 기록을 데이터베이스로 옮김
        """
        chat_history_key = f"chat_history:{session_id}"
        print(f"[DB 저장] Redis에서 대화 기록을 가져옵니다: {chat_history_key}")
        chat_history = self.redis_client.get(chat_history_key)
        if chat_history:
            chat_history = json.loads(chat_history)
            print(f"[DB 저장] Redis에서 가져온 대화 기록: {chat_history}")
            ChatSession.objects.create(
                session_id=session_id,
                end_time=timezone.now(),
                chat_history=chat_history
            )
            self.redis_client.delete(chat_history_key)
            print(f"[DB 저장] 세션 ID [{session_id}]의 대화 기록을 데이터베이스에 저장했습니다.")
        else:
            print(f"[DB 저장 실패] 세션 ID [{session_id}]에 대한 대화 기록을 찾을 수 없습니다.")
    
    
    
    
    # 여기부터 아래에 있는 메서드는 추후 utils.py으로 이동 예정
    @staticmethod
    def split_document(doc: Document) -> list[Document]:
        """ LangchainDocument 객체를 받아 적절히 청크로 나눕니다. """
        filename = doc.metadata.get("filename", "")
        if filename.endswith(".csv"):
            return [doc]  # CSV 파일은 이미 로드 시에 청크로 나뉨
        else:
            content = doc.page_content
            chunk_size = 500
            chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
            return [Document(page_content=chunk) for chunk in chunks]


    @staticmethod
    def convert_file_to_documents(file):
        """파일을 읽어 Langchain의 Document 객체로 변환"""
        
        file_content = file.read().decode('utf-8')
        if file.name.endswith(".csv"): # 파일이 csv 확장자라면, row 단위로 읽어서 리스트로 변환
            documents = []
            reader = csv.reader(file_content.splitlines()) 
            for i, row in enumerate(reader):
                content = ",".join(row)
                metadata = {"filename": file.name, "chunk": i}
                documents.append(Document(page_content=content, metadata=metadata))
        else: # 나머지 확장자는 전체 파일 내용을 하나의 Document 객체로 변환 -> 기능 수정 필요
            documents = [Document(page_content=file_content, metadata={"filename": file.name})]
        return documents
    
    
    def update_vector_db(self, file, filename) -> bool:
        """
        벡터 스토어 업데이트: 새로운 문서 추가 시 호출 
        
        벡터 데이터베이스의 각 청크 <-> 새로운 문서 전체와 비교
        1. 새로운 문서 전체를 하나의 큰 청크로 읽어옵니다.
        2. 이 청크를 벡터 DB에 저장된 각 청크와 비교하여 유사도를 계산합니다.
        3. 유사도 점수가 SIMILARITY_THRESHOLD 보다 작은 경우(유사함) -> 추가하지 않음
        4. 유사도 점수가 SIMILARITY_THRESHOLD 보다 큰 경우(유사하지 않음) -> 벡터 DB 저장함
        
        비교 대상 수정 필요함.
        """
        upload_documents = self.convert_file_to_documents(file)
        
        new_documents = []
        for doc in upload_documents:
            # 유사도 검색 및 점수 계산
            results = self.vector_store.similarity_search_with_score(doc.page_content, k=1)
            print(f'유사도 검사 중...results : {results}')
            if results and results[0][1] <= self.SIMILARITY_THRESHOLD:
                print(f"유사한 청크로 판단되어 추가되지 않음 - {results[0][1]}")
                
                continue  # 유사한 문서가 존재하면 추가하지 않음

            chunks = self.split_document(doc)
            new_documents.extend(chunks)
            
        if new_documents:
            self.vector_store.add_documents(new_documents)
            print(f"Added {len(new_documents)} new documents to the vector store")
            return True
        else:
            print('모두 유사한 청크로 판단되어 해당 문서가 저장되지 않음')
            return False
    
    
    def delete_vector_db_by_doc_id(self, doc_id):
        """
        주어진 문서 ID에 해당하는 벡터 임베딩을 삭제
        """
        # 벡터 데이터베이스에서 모든 문서 가져오기
        all_documents = self.vector_store._collection.get(include=["metadatas"])
        documents_to_delete = [doc_id for i, metadata in enumerate(all_documents["metadatas"]) if metadata.get("doc_id") == doc_id]
        if documents_to_delete:
            self.vector_store._collection.delete(ids=documents_to_delete)
            print(f"[벡터 DB 삭제] 문서 ID [{doc_id}]의 임베딩을 벡터 DB에서 삭제했습니다.")
        else:
            print(f"[벡터 DB 삭제 실패] 문서 ID [{doc_id}]에 대한 임베딩을 찾을 수 없습니다.")