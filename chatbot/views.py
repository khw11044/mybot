from django.shortcuts import render
# 추가
from django.http import HttpResponse

# 추가
def index(request):
    return HttpResponse("안녕하세요 chatbot에 오신것을 환영합니다.")
