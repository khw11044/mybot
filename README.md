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

