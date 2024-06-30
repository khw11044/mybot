<p align="center">
  <a href="https://aivle.kt.co.kr/home/main/indexMain">
    <img alt="KT AIVLE Logo" src="https://github.com/or-m-or/AIVLE-5th-MiniProject7_RAG-Chatbot/blob/master/asset/aivle_logo.png?row=true" width="100" style="border-radius: 50%;" />
  </a>
</p>
<h1 align="center">
    에이블스쿨 지원자들을 위한 QA Chatbot 서비스
</h1>

<img alt="Langchain" src="https://img.shields.io/badge/Langchain-1C3C3C.svg?style=for-the-badge&logo=langchain&logoColor=white"/><img alt="python" src ="https://img.shields.io/badge/python-3776AB.svg?&style=for-the-badge&logo=python&logoColor=white"/><img alt="Django" src ="https://img.shields.io/badge/Django-092E20.svg?&style=for-the-badge&logo=Django&logoColor=white"/><img alt="OpenAI" src ="https://img.shields.io/badge/OPENAI-412991.svg?&style=for-the-badge&logo=Openai&logoColor=white"/><img alt="Redis" src ="https://img.shields.io/badge/Redis-FF4438.svg?&style=for-the-badge&logo=Redis&logoColor=black"/><img alt="HTML" src ="https://img.shields.io/badge/HTML5-E34F26.svg?&style=for-the-badge&logo=HTML5&logoColor=white"/><img alt="CSS3" src ="https://img.shields.io/badge/CSS3-1572B6.svg?&style=for-the-badge&logo=CSS3&logoColor=white"/><img alt="JavaScript" src ="https://img.shields.io/badge/JavaScript-F7DF1E.svg?&style=for-the-badge&logo=JavaScript&logoColor=black"/><img alt="GASP" src ="https://img.shields.io/badge/GASP-88CE02.svg?&style=for-the-badge&logo=GreenSockt&logoColor=black"/>


---

본 프로젝트는 KT 에이블스쿨 5기 미니프로젝트 7차 결과 산출물로, 신규 지원자들을 위한 RAG 기반 챗봇 서비스입니다. 신규 지원자들을 위한 서비스인 만큼, 보다 정확하고 상세한 답변을 제공하는 것에 중점을 두고 개발되었습니다. <br>
  
현재 `master` 브랜치는 미니 프로젝트의 최종 결과물로 제출된 버전(v1.0)에 해당됩니다.<br>
KT 에이블스쿨에서 진행하는 미니 프로젝트 기간은 종료되었지만 <br>
챗봇의 성능(정확도 및 답변속도) 향상 및 코드 품질 개선을 위해 추가 개발이 계속 진행될 예정입니다.

---


🔥 [ KT AIVLE School 5기 미니프로젝트 7차 ] RAG Chatbot 구축하기 <br>
💻 개발기간 : 2024.06.03 - 2024.06.13

## 0. 목차
  - [1. 프로젝트 주요 기능](#1-main-feature-v10)
  - [2. 필요한 모듈 설치하기](#2-download-and-installation-window)
  - [3. 프로젝트 빌드 방법](#3-getting-started-window)
  - [4. 실행 후 사용 방법](#4-useage)
  - [5. 버그 및 문제 발생 시 해결 방법](#5-bugs-and-troubleshooting)
  - [6. 버전 변경 사항 기록보기](#6-changelog)
  - [7. 프로젝트 팀원 소개](#7-team)
  - [8. 지원이 필요할 경우](#8-support-and-contact)
  - [9. 라이선스](#9-license)


## 1. Main Feature (v1.0)

### 1) 채팅 페이지

- 자주 물어보는 질문에 대해 프롬프트 자동 생성 가능
- 프롬프트 엔지니어링 적용
- Langchain 라이브러리 사용 (`create_history_aware_retriever`, `create_stuff_documents_chain`, `create_retrieval_chain`) 

**[ 내부 동작 이해 ]**

1. Langchain의 `create_history_aware_retriever` 을 사용하여 이전 대화 기록을 토대로 벡터 DB에 대해 검색할 쿼리를 생성하고, 이를 기반으로 검색된 문서를 반환하는 체인을 생성합니다. 
2. `create_history_aware_retriever`는 이전 대화 히스토리가 없을 경우, 입력을 그대로 Retriever로 전달하고 히스토리가 있는 경우에는 정의된 프롬프트에 따라 사용자의 질문을 문맥화 시켜서 질문을 재구성하여 검색 쿼리를 (LLM을 사용하여)생성하고 이를 Retriever으로 전달합니다.
3. 이후, Langchin의 `create_stuff_documents_chain`을 사용하여 검색된 여러 문서를 하나의 프롬프트로 합쳐서 LLM에 전달합니다. 이 체인은 문서 목록을 받아서 각각 문서를 특정 형식으로 포맷한 다음, 이들을 하나의 문자열로 결합하여 프롬프트로 만듭니다. 이후 이 프롬프트를 LLM에게 전달하여 응답을 생성합니다.<br>
이때에도 커스텀 프롬프트를 추가해 줄 수 있으며, 본 프로젝트에서는 Retriever으로 검색된 내용을 토대로만 대답해야하며, 모르는 내용에 대해서는 모른다고 대답하게 유도하였습니다.
이로써 환각현상을 최소화하려 시도하였으며 실제로 임베딩된 문서의 내용에 대해서만 대답할 수 있음을 사전에 정의해둔 기준 질문을 통해 검증하였습니다.
4. Langchain의 `create_retrieval_chain` 을 최종 체인으로 사용하여 위 두 체인을 엮어 주었으며, 앞서 보았던 `history_aware_retriever`을 Retriever(검색기)으로 `question_answer_chain`을 Generator(생성기)으로 사용합니다.
5. 마지막으로 Langchain 의 `RunnableWithMessageHistory` 을 사용하여 세션 단위(문맥이 이어지는 하나의 대화 흐름 단위)로 대화 내용을 구분지었습니다. 또한, 긴 대화 내용에 대해서는 대화가 진행됨에 따라 해당 대화 내용에 대한 요약본을 생성하고 이 요약본을 저장하여 이후 대화에 사용함으로써(프롬프트에 포함 시킴으로써) 토큰 사용량을 줄일 수 있습니다. 


### 2) 관리자 페이지
- `Redis` 인 메모리 데이터베이스를 사용하여 하나의 채팅 사용 내역을 세션단위로 저장함.
  - 메모리 내에서 데이터를 저장하고 처리하여 디스크 기반 데이터베이스에 비해 빠른 읽기 및 쓰기 가능
  - 키-값 형태로 데이터를 저장할 수 있어 대화 내역을 세션 단위(하나의 대화흐름이 이어지는 단위)로 저장 가능
- 새로운 문서 업로드 기능, 이전에 업로드하여 벡터DB에 이미 존재하는 문서 중 유사도 점수가 
일정 기준 보다 크면 업로드 되지 않음.
- 벡터 DB에 저장된 문서 내용 조회 기능
- 채팅 사용 이력 표 형태로 조회 가능
    - 일자/기간 기준 필터링 가능
    - 마찬가지로 문맥이 유지되는 한번의 대화 흐름을 한개의 인스턴스 단위로 조회 가능


### 3) 사용된 데이터
- 웹 스크래핑으로 `에이블스쿨 홈페이지` 내 FAQ 데이터 수집
- 웹 크롤링으로 구글에 '에이블스쿨' 키워드로 검색했을 때 등장하는 뉴스기사 수집


## 2. Download and Installation (Window)

1. 먼저 `Conda` 가상환경을 사용하기 위해 사전에 미리 설치합니다.

2. 이어서 `Redis`를 설치한 후 Redis 서버를 실행합니다.

    1. [Redis 공식 Github 페이지](https://github.com/microsoftarchive/redis/releases) 에서 3.0.504 버전의 ZIP파일을 다운로드합니다. (redis-x.y.z.zip)

    2. 이후 다운로드한  ZIP파일을 원하는 폴더에 압축을 풉니다. 예를 들어, C:\redis 폴더를 사용할 수 있습니다.

    3. 압축을 푼 폴더로 이동한 후, redis-server.exe 파일이 있는지 확인합니다.

    4. `Windows 키 + R` 을 누르고 `cmd` 를 입력한 후 `Enter`를 눌러 명령 프롬프트를 엽니다.

    5. redis 디렉토리로 이동한 다음, 다음과 같이 명령어를 입력하여 Redis 서버를 실행합니다. <br> ( [다운 받은 ZIP을 압축 해제 한 경로]/redis 으로 이동해야 합니다. ) 
        ```
        $ cd C:\redis
        ```
        ```
        $ redis-server
        ```
        Redis 서버가 성공적으로 실행되면 `Ready to accept connections` 메시지가 표시됩니다.
    
    6. Redis 클라이언트로 정상적으로 연결되었는지 테스트를 합니다.
        - 다른 명령프롬프트를 열고, Redis 디렉토리로 이동합니다.
        ```
        $ cd C:\redis
        ```
        - Redis 클라이언트 실행
        ```
        $ redis-cli.exe
        ```
        - Ping 명령어 실행
        ```
        $ ping
        ```
        `Pong` 응답이 표시되면 Redis 서버가 제대로 작동하고 있는 것입니다.

    7. 추후 Redis 서버를 종료하려면 아래 명령어를 사용할 수 있습니다.
        ```
        $ redis-cli shutdown
        ```

## 3. Getting Started (Window)


1. 현재 레포지토리 본인 로컬로 가져오기
    ```bash
    $ git clone https://github.com/AIVLE-5th-TeamProject/MP7_AIVLE-RAG-Chatbot.git
    ```

3. 이후, 다음 명령어로 프로젝트 빌드에 필요한 디렉토리를 생성합니다.
    ```sh
    $ ./setup.sh
    ```

4. 가상환경을 생성한 뒤 활성화 합니다. 가상환경에서 사용하는 python 버전은 3.11.9 으로 세팅합니다. 아래 명령어를 그대로 실행하면 이름이 MP7, 파이썬 버전 3.11.9를 사용하는 conda 가상환경이 생성됩니다.
    ```
    $ conda create --name MP7 python=3.11.9
    ```

5. 가상환경을 실행한 후, 필요한 모듈을 설치합니다.
    ```
    (MP7)...$ pip install -r requirements.txt 
    ```

6. 데이터베이스 마이그레이션 파일을 생성합니다.
    ```
    (MP7)...$ python manage.py makemigrations
    ```

7. 생성된 마이그레이션 파일을 데이터베이스에 적용시킵니다.
    ```
    (MP7)...$ python manage.py migrate
    ```

8. 관리자 페이지 접근용 슈퍼유저 계정을 생성합니다. 다음과 같이 사용할 Username, Eamil, Password 를 본인이 원하는대로 지정합니다.
    ```
    (MP7)...$ python manage.py createsuperuser

    $ Username (leave blank to use 'your-username'): admin
    $ Email address: admin@example.com
    $ Password: 1234
    $ Password (again): 1234
    Superuser created successfully.
    ```


4. 이제 거의 다 끝났습니다. 가상환경이 활성화 되어 있는지 재확인 하고, Redis 서버가 잘 실행 되고 있는지 확인한 뒤, Django 서버를 실행하고 접속합니다. <br>
    (주의) Django 서버가 실행되기 전에 꼭 Redis 서버가 먼저 실행 중이어야 합니다. 
    ```
    $ conda activate mini7   
    $ python manage.py runserver
    ``` 
    서버를 실행하면 database 폴더 하위에 SQlite에서 제공하는 ChromaDB가 생성됩니다.


## 4. Useage

1. 챗봇과 채팅을 시작하기 전, RAG에 사용할 문서를 먼저 업로드 해야 합니다. <br>
    > 채팅 페이지의 우측 상단 `admin` 버튼을 눌러 관리자페이지어 접근합니다. <br>
    > 이후 사전에 입력했던 슈퍼유저 계정의 `Username`, `password`를 기입하여 로그인 할 수 있습니다. <br>
    > 이어서 화면 좌측의 `Rag documents` 를 클릭하고, 우측 상단 `Rag documents 추가`를 클릭하여 RAG에 사용할 문서를 업로드 합니다. <br>
    > 해당 프로젝트의 `sample` 디렉토리에 샘플로 사용할 수 있는 CSV 파일이 있으니 참고해주세요.
    > 이후 `파일선택`을 누르고 `저장`버튼을 눌러 원하는 파일을 업로드 합니다. <br>
    > 업로드 대기 시간 후, "[문서업로드] 벡터스토어 업데이트에 성공하였습니다." 문구가 보이고, 해당 문서가 벡터DB와 파일기반 디렉토리에 저장됩니다.

2. 메인(루트) 페이지에 접근하려면 http://127.0.0.1:8000/ 으로 접속합니다.

2. admin 페이지에 접근 하려면 http://127.0.0.1:8000/admin 으로 접속합니다.

3. swgger 문서를 통해 API 테스트를 해보려면 http://127.0.0.1:8000/swagger 으로 접속합니다.



## 5. Bugs and Troubleshooting

- 문서 업로드 시 유사도 검증 로직 수정 필요(현재는 새로 업로드하는 문서 전체와 기존 문서의 각 청크 끼리 비교함)
- MAC 환경에서 챗봇을 실행 시, 채팅 내용이 2개씩 보이는 문제 존재
- 한 번 업로드한 파일 삭제되지 않는 이슈 존재
- 채팅 속도 관련 성능 개선 필요(메시지 브로커 혹은 Websocket 방식 도입 예정)
- 관리자 페이지 UI 커스텀 디자인으로 수정 요구됨.(보다 나은 UX를 위해)
- AIVLE School 공지사항 실시간 추적하여 자동 업데이트 기능 추가 예정

## 6. Changelog

#### - *v1.0 : `Initial Release` (2024-06-13)*

## 7. Team

|<img src="https://avatars.githubusercontent.com/u/135506789?v=4" width="150" height="150"/>|<img src="https://avatars.githubusercontent.com/u/96802693?v=4" width="150" height="150"/>|<img src="https://avatars.githubusercontent.com/u/91467204?v=4" width="150" height="150"/>|<img src="https://avatars.githubusercontent.com/u/79041288?v=4" width="150" height="150"/>|<img src="https://avatars.githubusercontent.com/u/59814174?v=4" width="150" height="150"/>|<img src="https://avatars.githubusercontent.com/u/133032166?v=4" width="150" height="150"/>|
|:-:|:-:|:-:|:-:|:-:|:-:|
|taehwan heo<br/>[@or-m-or](https://github.com/or-m-or)|TaeHui Kim<br/>[@taehui7439](https://github.com/taehui7439)|Yeseo Kim<br/>[@xeonxeonx](https://github.com/xeonxeonx)|[@Han-sangwon](https://github.com/Han-sangwon)|[@Polasia](https://github.com/Polasia)|[@yhjin62](https://github.com/yhjin62)|


## 8. Support and Contact

`mail` : htth815@gmail.com <br>
`kakao Talk ID` : hth815<br> 
`GitHub Issues` : [Open an issue]()<br>
`Feature Requests` : [Feature Requests]()

## 9. License





