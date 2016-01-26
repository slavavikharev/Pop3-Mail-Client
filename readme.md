Pop3 Mail Client
================

What is it?
-----------
pop3 - приложение для просмотра входящих сообщений

Integrated servers
------------------
+ GMail
+ Yandex.Mail
+ Mail.ru
+ Yahoo.com

How to run?
-----------
```bash
mailclient.py [options]
```

Commands
--------
```
quit      - выход из программы
show <n>  - вывести сообщение под номером <n>
command (long|short) <command>
          - отправить long или short команду <command> на сервер
```

Using scripts
-------------
+ Скрипт должен состоять из поддерживаемых команд
+ Неизвестные команды игнорируются
+ Скрипт заканчивается командой quit
+ Использование скрипта SCRIPT:
    ```mailclient.py [options] < SCRIPT```

Direct output
-------------
+ Перенаправление вывода в файл OUTPUT:
    ```mailclient.py [options] > OUTPUT```
+ Перенаправление ошибок в файл ERRORS:
    ```mailclient.py [options] > ERRORS```
    
Using configs
-------------
Формат файла:
```
    email
    [password]
    [host]
    [port]
```

Options
-------
```
-h, --help            show this help message and exit
-a, --attachments     Save attachments
-m, --messages        Save messages
-q, --quiet           Silent mode
-t HOST, --host HOST  Server host
-p PORT, --port PORT  Server port
-c CFG, --config CFG  Configuration file
```

-----------------------
*&copy; Vikharev Slava CS-201*
