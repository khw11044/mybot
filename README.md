## 03. 모델 - 장고 앱 migrate


> 데이터베이스가 필요한 앱은 migrate가 필요하다.


core/settings.py 파일을 잘 살펴보면 설치된 앱 뿐만 아니라 사용하는 데이터베이스에 대한 정보도 다음과 같이 정의되어 있다.

[파일이름: /mybot/core/settings.py]

![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/43c05dd9-3d18-4655-8fbe-7808c5f2be07)


데이터베이스 엔진은 django.db.backends.sqlite3 라고 정의되어 있다. 그리고 데이터베이스 파일은 BASE_DIR 디렉터리 밑에 db.sqlite3 파일에 저장한다고 정의되어 있다. BASE_DIR은 프로젝트 디렉터리를 의미한다.

> 우리 프로젝트의 BASE_DIR은 C:\KT\mybot>이다. (※ 맥 사용자는 /Users/<사용자>/KT\mybot)

------
__SQLite에 대하여__

SQLite는 주로 개발용이나 소규모 프로젝트에서 사용되는 가벼운 파일 기반의 데이터베이스이다. 개발시에는 SQLite를 사용하여 빠르게 개발하고 실제 운영시스템은 좀 더 규모있는 DB를 사용하는 것이 일반적인 개발 패턴이다.

------

이제 경고 문구에서 안내하는 것처럼 python manage.py migrate 명령을 실행하여 해당 앱들이 필요로 하는 데이터베이스 테이블들을 생성해 보자.

명령 프롬프트에서 다음과 같이 입력하자.

> (chatbot) C:\KT\mybot> python manage.py migrate

db.sqlite3가 생성되었다. 

## 03.01. 모델 작성하기

이제 chatbot이 사용할 데이터 모델을 만들어 보자. 

chatbot은 사용자와 대화하고 그 대화 내용을 기억하며 이후에도 이전 대화 내용을 기억하며 대화가 이어져야 할 것이다. 

또한 다양한 법률/규범등의 추가되는 데이터를 다루기 위한 Rag에서 file을 관리해야 할 것이다. 

따라서 chatbot은 추가되는 데이터와 챗세션에 해당하는 데이터 모델이 있어야 한다. 


### 모델의 속성

[참고 링크](https://velog.io/@vkfkd1107/Django-%EA%B8%B0%EC%A1%B4-%ED%95%84%EB%93%9C%EC%97%90-UUID-%ED%95%84%EB%93%9Cor-uniqueTrue%EC%9D%B8-%ED%95%84%EB%93%9C-%EC%B6%94%EA%B0%80%ED%95%98%EA%B8%B0-RunPython-%ED%99%9C%EC%9A%A9-%EB%B0%A9%EB%B2%95)

그렇다면 질문과 답변 모델에는 어떤 속성들이 필요한지 먼저 생각해 보자. 질문(Question) 모델에는 최소한 다음과 같은 속성이 필요하다.

[RagDocument]

| 속성 | 설명 |
| --- | ---| 
| id | UUID 형식의 기본 키 (primary key) |
| file | 파일 경로 |
| uploaded_at | 파일 업로드 시간 |

[ChatSession]

| 속성 | 설명 |
| --- | ---| 
| session_id | 세션 ID (고유 값) |
| start_time | 세션 시작 시간 |
| end_time | 세션 종료 시간  |
| chat_history | 채팅 내역 (JSON 형식) |

### models.py

이렇게 생각한 속성을 바탕으로 'RagDocument'와 'ChatSession'에 해당되는 모델을 chatbot/models.py 파일에 정의해 보자.

[파일이름: /mybot/chatbot/models.py]


```python
"""
앱의 데이터베이스 테이블 구조를 정의하는 모듈 + API에서 사용할 DAO 정의
"""
from django.db import models
import uuid # UUID(Universally Unique Identifier) 모듈을 임포트합니다. UUID는 고유한 식별자를 생성하는 데 사용됩니다.


class RagDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)                 # id 필드는 UUID 형식의 기본 키(primary key)입니다. 기본값은 uuid.uuid4 함수를 사용해 생성됩니다. 이 필드는 수정할 수 없습니다(editable=False).
    file = models.FileField(upload_to='documents/', default='documents/default.txt')            # file 필드는 파일을 저장하는 필드입니다. 파일은 documents/ 디렉토리에 업로드됩니다. 기본값은 documents/default.txt 파일입니다.
    uploaded_at = models.DateTimeField(auto_now_add=True)                       # uploaded_at 필드는 파일이 업로드된 시간을 저장하는 날짜/시간 필드입니다. 

    def __str__(self):                  # __str__ 메서드는 file 필드의 파일 이름을 반환합니다. 이 메서드는 Django 관리자(admin) 인터페이스 등에서 객체를 사람이 읽을 수 있는 형태로 표시하는 데 사용됩니다.
        return self.file.name
    
    
class ChatSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)          # session_id 필드는 최대 255자의 문자열을 저장하는 필드입니다. 이 필드는 고유(unique)해야 하므로 동일한 session_id 값을 가지는 레코드는 존재할 수 없습니다.
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    chat_history = models.JSONField()

    def __str__(self):
        return self.session_id                              # __str__ 메서드는 session_id 값을 반환합니다. 이 메서드는 Django 관리자(admin) 인터페이스 등에서 객체를 사람이 읽을 수 있는 형태로 표시하는 데 사용됩니다.

```

### 테이블 생성하기

자 chatbot/models.py 파일에 위 코드를 넣었다면 이제 작성한 모델을 이용하여 테이블을 생성해 보자. 테이블 생성을 위해 가장 먼저 해야 할 일은 chatbot 앱을 core/settings.py 파일의 INSTALLED_APPS 항목에 추가하는 일이다.


![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/cd5c466d-6146-4900-a82b-fdca99672e17)
먼저 chatbot/apps.py 에 보면 ChatbotConfig 라는 이름의 클래스를 볼 수 있다.



[파일이름: /mybot/core/settings.py]

```python
(... 생략 ...)
INSTALLED_APPS = [
    "chatbot.apps.ChatbotConfig",             # <- 이거 
    "django.contrib.admin",
    "django.contrib.auth",
    (... 생략 ...)
]
(... 생략 ...)

```

## makemigrations

이제 테이블 생성을 위해 다음처럼 migrate 명령을 수행해보자. 

> (chatbot) C:\KT\mybot> python manage.py migrate

오류가 발생하는것을 볼 수 있다. 

오류 문구를 보니 migrate가 정상적으로 수행되지 않았다. 왜냐하면 모델이 신규로 생성되거나 변경되면 makemigrations 명령을 먼저 수행한 후에 migrate 명령을 수행해야 하기 때문이다.

따라서 다음 명령을 수행해야 한다.

> (chatbot) C:\KT\mybot> python manage.py makemigrations

**makemigrations 명령은 모델을 생성하거나 모델에 변화가 있을 경우에 실행해야 하는 명령이다.** 

위 명령을 수행하면 chatbot\migrations\0001_initial.py 라는 파이썬 파일이 자동으로 생성된다.

한번 더 실행하더라도 변경사항 없음을 보여주므로 여러번 실행시 뭔가 잘못 될까 걱정할 필요는 없다.

makemigrations 명령을 수행하더라도 실제로 테이블이 생성되지는 않는다. makemigrations 명령은 장고가 테이블 작업을 수행하기 위한 작업 파일(예: 0001_initial.py)을 생성하는 명령어다. 실제 테이블 작업은 migrate 명령을 통해서만 가능하다.

### sqlmigrate

makemigrations로 데이터베이스 작업 파일을 생성하고 migrate 명령을 실행하기 전에 실제 어떤 쿼리문이 실행되는지 sqlmigrate 명령으로 확인해 볼수 있다.

sqlmigrate 명령은 단지 실행되는 쿼리만 조회할 뿐이다. 실제 쿼리가 수행되지는 않는다.

> (chatbot) C:\KT\mybot> python manage.py sqlmigrate chatbot 0001

### migrate

이제 migrate 명령을 수행하여 실제 테이블을 생성하자.

> (chatbot) C:\KT\mybot> python manage.py migrate



documents 폴더를 만든다. 

database 폴더를 만든다.

