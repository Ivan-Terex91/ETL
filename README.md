

    git clone https://github.com/Ivan-Terex91/ETL
    Для запуска всего проекта, в корневом каталоге нужно использовать команду docker-compose up -d --build
    Для сбора статических файлов нужно использовать команду docker-compose exec movies-admin python manage.py collectstatic
    Непосредственно задание находится в папке postgres_to_es

	P.S. С контекстным менеджером ошибку я конечно исправил и в запаре не заметил очевидного.
	У меня есть вопрос один. Я сегодня дебажил код и заметил что если я много раз подряд буду останавливать и поднимать контейнер с Postgres, то у меня выскакивает ошибка StopIteration.
	Судя по тому что я смог найти и понять, то эта ошибка происходит из корутины related_table_coroutine и возникает при попытке сделать send. Как я понял это ошибка возникает когда корутина закончила свою 		работу но к ней приходят данные. Лаконичного и хорошего решения я не нашёл. Сделал костыль на перехват и откат времени обновления на то которое пришло и далее в main в while продожим брать данные. Как мне 	 сделать это так чтобы не было больно на это смотреть или может направление дадите?
	P.P.S. Я понимаю что попытка ревью последняя и технически надо было подправить только часть с контекстным менеджером , но я пришёл в первую очередь за знаниями :) Заранее спасибо!!! 
