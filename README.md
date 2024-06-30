## 05. 템플릿 스태틱 홈화면 

먼저 템플릿이랑, 스태틱 준비 

__TEMPLATES__

BASE_DIR 위치에 templates 폴더 만들고 공유한 index.html 파일 넣기 


__static__

front end, 열심히 주서오기 

static 폴더 만들고 그 안에 home 폴더 만들고 공유한 .js 파일과 .css 파일 넣기 




### core/settings.py


ALLOWED_HOSTS = ['*']

core/settings.py에 TEMPLATES

__TEMPLATES의 DIRS 아래와 같이 고치기__



```python

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')], # template 경로 설정
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

__언어랑 시간 바꾸기__

```python

# # LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = "ko-kr"

# TIME_ZONE = "UTC"
TIME_ZONE = 'Asia/Seoul'

```

__static 폴더를 정적파일에 추가__

아래 코드 넣기 

```python
# root 아래의 static 폴더를 정적파일에 추가
STATICFILES_DIRS = [ BASE_DIR / 'static', ]
```


__Application 초기화__

core/settings.py에 INSTALLED_APPS에 
"chatbot" 추가 

```python
# Application 초기화
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "chatbot",
]
```

### core/urls.py 

아래와 같이 코드 바꾸기 

```python

from django.contrib import admin
from django.urls import path, include

from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', index),     
    path('chatbot/', include('chatbot.urls')),         
]


```

**완성** 

![image](https://github.com/khw11044/llm_rag_start_note/assets/51473705/6f440d96-6a4b-44d2-937b-6b3bfcc8fbba)




