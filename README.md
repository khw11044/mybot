## 02. 앱(App)

우리는 앞에서 mybot 프로젝트를 생성했다. 

하지만 프로젝트 단독으로는 아무런 일도 할 수 없다. 

프로젝트에 기능을 추가하기 위해서는 앱을 생성해야 한다. 

이제 챗봇 기능을 담당할 chatbot 앱을 생성해 보자.

다음처럼 명령 프롬프트에서 django-admin의 startapp 명령을 이용하여 chatbot 앱을 생성하자.

> (chatbot) C:\KT\mybot>django-admin startapp chatbot

chatbot 디렉터리가 생성되고 그 하위에 여러 파일들이 생성되었다.


### Hello chatbot
이제 본격적으로 장고 프로그램을 만들어 보자.

브라우저에서 http://localhost:8000/chatbot 페이지를 요청했을 때, 

"안녕하세요 chatbot에 오신것을 환영합니다."라는 문자열을 출력하도록 만들어 보자.

로컬서버를 먼저 구동하자.

> (chatbot) C:\KT\mybot>python manage.py runserver

그리고 그냥 한번 브라우저에서 http://localhost:8000/chatbot 페이지를 요청해 보자.

------------------

아마  "Page not found (404)" 라는 오류가 발생할 것이다. 여기서 404는 HTTP 오류코드 중 하나이다.

404 오류는 브라우저가 요청한 페이지를 찾을 수 없을 경우에 발생한다.

장고는 오류가 발생하면 오류의 원인을 화면에 자세히 보여주기 때문에 오류를 파악하기 쉽다. 오류의 내용을 자세히 읽어보면 core/urls.py 파일에 요청한 pybo/ URL에 해당되는 매핑이 없다고 적혀 있다.

그렇다면 이제 오류를 해결하기 위해 해야 할일은 무엇일까? 

-> core/urls.py 파일에 chatbot/ URL에 대한 매핑을 추가하는 것이다. 

장고의 urls.py 파일은 페이지 요청이 발생하면 가장 먼저 호출되는 파일로 URL과 뷰 함수 간의 매핑을 정의한다. 뷰 함수는 views.py 파일에 정의된 함수를 말한다.

### core/urls.py

URL 매핑을 추가하기 위해 core/urls.py 파일을 다음과 같이 수정하자.

[파일이름: /mybot/core/urls.py]

```python
from django.contrib import admin
from django.urls import path

# 추가 
from chatbot import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # 추가
    path('chatbot/', views.index),                 
]
```

chatbot/ URL이 요청되면 views.index를 호출하라는 매핑을 urlpatterns에 추가하였다. views.index는 views.py 파일의 index 함수를 의미한다.

### views.py

이제 다시 http://localhost:8000/chatbot 페이지를 요청해 보자. 

아마도 "사이트에 연결할 수 없음"이라는 오류가 화면에 표시될 것이다. 오류의 원인은 URL 매핑에 추가한 뷰 함수 views.index가 없기 때문이다.

그렇다면 이제 chatbot/views.py 파일에 index 함수를 추가해야 할 것이다. 다음과 같이 추가해 보자.

[파일이름: /mybot/core/views.py]

```python
from django.shortcuts import render
# 추가
from django.http import HttpResponse

# 추가
def index(request):
    return HttpResponse("안녕하세요 chatbot에 오신것을 환영합니다.")
```

![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/2b2542bd-1d12-49f0-bfed-3bda0c1bd4d4)

성공 

### 장고 개발 흐름 정리하기

지금 여러분이 경험한 개발 과정은 앞으로의 실습 과정에서 여러 번 반복될 것이다. 그만큼 이 과정은 중요하다!

![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/187d9b82-f97b-4cf4-8ad9-718b08bac1da)

장고의 기본적인 흐름을 다시 정리해 보자.

- [1] 브라우저에서 로컬 서버로 http://localhost:8000/pybo 페이지를 요청하면
- [2] urls.py 파일에서 /pybo URL 매핑을 확인하여 views.py 파일의 index 함수를 호출하고
- [3] 호출한 결과를 브라우저에 반영한다.

### URL 분리

chatbot 앱에 관련한 것들은 chatbot 앱 디렉터리 하위에 위치해야 한다. 

하지만 이대로라면 chatbot과 관련된 URL 매핑을 추가할 때마다 core/urls.py 파일을 수정해야 한다. 

__core의 urls.py 파일은 앱이 아닌 프로젝트 성격의 파일이므로 이곳에는 프로젝트 성격의 URL 매핑만 추가되어야 한다.__

따라서 chatbot 앱에서만 사용하는 URL 매핑을 core/urls.py 파일에 계속 추가하는 것은 좋은 방법이 아니다.

__해결방안__

core/urls.py 파일을 다음처럼 수정하자.

[파일이름: /mybot/core/urls.py]


```python

from django.contrib import admin
from django.urls import path

# 삭제  
# from chatbot import views
# 추가
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('chatbot/', views.index),    -> 수정      
    path('chatbot/', include('chatbot.urls')),         
]

```

chatbot/ URL에 대한 매핑을 path('chatbot/', views.index) 에서 path('chatbot/', include('chatbot.urls'))로 수정했다.

path('chatbot/', include('chatbot.urls'))의 의미는 chatbot/ 로 시작하는 페이지를 요청하면,

이제 chatbot/urls.py 파일의 매핑 정보를 읽어서 처리하라는 의미이다. 


따라서 이제 chatbot/question/create, chatbot/answer/create 등의 chatbot/로 시작하는 URL을 추가해야 할 때 core/urls.py 파일을 수정할 필요없이 chatbot/urls.py 파일만 수정하면 된다.

__그렇다면 이제 chatbot/urls.py 파일을 생성해야 한다.__

그리고 chatbot/urls.py 파일은 다음과 같이 작성하자.

[파일이름: /mybot/chatbot/urls.py]

```python
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
]

```

기존 core/urls.py 파일에 설정했던 내용과 별반 차이가 없다.

다만 path('', views.index) 처럼 chatbot/ 가 생략된 '' 이 사용되었다. 이렇게 되는 이유는 core/urls.py 파일에서 이미 chatbot/로 시작하는 URL이 chatbot/urls.py 파일과 먼저 매핑되었기 때문이다.

즉, chatbot/ URL은 다음처럼 core/urls.py 파일에 매핑된 chatbot/ 와 core/urls.py 파일에 매핑된 '' 이 더해져 chatbot/가 된다.

| core/urls.py | | chatbot/urls.py | | 최종 URL |
|--------------|---|---------------|---| ------ |
| 'chatbot/' | + | '' | = | 'chatbot/' |
| 'chatbot/' | + | 'question/create/' | = | 'chatbot/question/create/' |

위의 두번째 예시처럼 chatbot/urls.py 파일에 path('question/create/', ...) 라는 URL매핑이 추가된다면 최종 매핑되는 URL은 chatbot/가 더해진 chatbot/question/create/가 될 것이다.

이제 다시 http://localhost:8000/chatbot 페이지를 요청해 보자. URL 분리 후에도 동일한 결과가 나타나는 것을 확인할 수 있을 것이다.