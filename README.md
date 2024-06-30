## 04. 장고 관리자

### 슈슈슈 슈퍼노바, 아니 슈퍼유저 

장고 관리자를 사용하기 위해서는 장고 관리자 화면에 접속할 수 있는 슈퍼유저(superuser)를 먼저 생성해야 한다. 다음처럼 python manage.py createsuperuser 명령으로 슈퍼유저를 생성하자.

    ```
    (chatbot) C:\KT\mybot> python manage.py createsuperuser

    $ Username (leave blank to use 'your-username'): admin
    $ Email address: admin@example.com
    $ Password: 1234
    $ Password (again): 1234
    Superuser created successfully.
    ```

### 장고 관리자 화면
슈퍼유저가 생성되었으니 로컬 서버를 구동한 후 http://localhost:8000/admin/ 페이지에 접속해 보자. 다음과 같은 화면을 볼 수 있을 것이다.

> python manage.py runserver

http://127.0.0.1:8000/admin 에 접속 

![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/afce9bd7-cdc4-4781-8999-df7d577191d7)

![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/e9dad7a5-6520-4d75-9334-204ce4eba26c)

### 모델 관리 

우리는 RagDocument 모델과 ChatSession 모델을 만들었다. 

RagDocument 모델과 ChatSession 모델을 관리자에 등록하자 

[파일이름: /mybot/chatbot/admin.py]

```python

"""
Django 관리자 사이트에 모델 등록, 관리하는 모듈
"""
from django.contrib import admin
from django.http import HttpRequest
from .models import RagDocument, ChatSession
from django.apps import apps
import os

admin.site.register(RagDocument)

```

admin.site.register로 RagDocument 모델을 등록했다. 그리고 장고 관리자 화면을 갱신해 보면 다음처럼 RagDocument 추가된 것을 확인할 수 있다.

![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/93c0db12-d93c-47fc-adff-62e921829147)


이제 admin.py 파일에 최종 코드를 올려보자. 

```python

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


```

![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/45c625f1-4e7b-48dc-96a0-1e2c6c91e6eb)


![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/dc4de5a6-370b-488f-9c6e-2172ffb3e623)

![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/14cf365d-b794-4635-bebd-a0ead19cb520)

![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/9424683b-14e0-4d85-9487-d181caad84d1)

documents 폴더를 보면 내가 올린 pdf파일이 있다. 

와 이제 맘껏 데이터를 모을 수 있다~ 

