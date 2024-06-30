"""
core project의 ASGI 구성 : 현재 프로젝트를 서비스하기 위한 ASGI-호환 웹 서버의 진입점

ASGI callable을 ``application``변수명을 사용하여 모듈 레벨 변수로 호출함.

참고 : https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_asgi_application()
