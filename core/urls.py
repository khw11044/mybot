"""
core project의 URL 구성
: 현재 Django project 의 URL 선언을 저장하며, Django 로 작성된 사이트의 “목차” 라고 할 수 있음.

urlpatterns` 리스트는 URLs를 view로 라우팅함.
참고: https://docs.djangoproject.com/en/5.0/topics/http/urls/

예제:
Function views
    1. import 추가            : from my_app import views
    2. urlpatterns에 url 추가 : path('', views.home, name='home')
Class-based views
    1. import 추가            : from other_app.views import Home
    2. urlpatterns에 url 추가 : path('', Home.as_view(), name='home')
Including another URLconf
    1. include() 추가         : from django.urls import include, path
    2. urlpatterns에 url 추가 : path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path # re_path
# from chatbot.views import MainIndexView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import permissions
from django.shortcuts import render
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
   openapi.Info(
        title="AIVLE RAG Chatbot API",
        default_version='v1',
        description="에이블스쿨 빅프로젝트 RAG Chatbot API 문서",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

def index(request):
    return render(request, 'index.html')

urlpatterns = [
    path(r'swagge.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),
    path("admin/", admin.site.urls),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),    
    path('', index),
    path("chatbot/", include("chatbot.urls")),
]


from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

