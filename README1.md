## 01. 프로젝트 생성하기 

django-admin startproject 01_core . 명령으로 장고 프로젝트를 생성하자.

> (chatbot) C:\KT\my_bot>django-admin startproject 01_core .

이때 01_core 다음에 점 기호(.)가 있음에 주의하자. 점 기호는 현재 디렉터리를 의미한다. 

위 명령의 의미는 현재 디렉터리인 my_bot을 기준으로 프로젝트를 생성하겠다는 의미이다.

프로젝트가 생성되면 my_bot 디렉터리 안에 장고가 필요로 하는 01_core 폴더와 manage.py 파일이 생성되었다. 

## 01-01. 개발 서버 구동하고 웹 사이트에 접속해 보기

다음처럼 python manage.py runserver 명령을 입력하자.

> (chatbot) C:\KT\my_bot>python manage.py runserver