
.. role:: bash(code)
   :language: bash


MINECHAT
==============

*Клиент подпольного чата.*

**Требования**:

* python3.9 или выше
* poetry

**Установка**:

* склонировать репозиторий
* создать виртуальное окружение
* установить зависимости :bash:`$ poetry install`
* задать переменные окружения (опционально)

**Запуск**:

Cкрипт прослушивания чата

.. code-block:: bash

  $ python -m minechat.commands.comsumer
  


Cкрипт отправки сообщений в чат 

.. code-block:: bash

  $ python -m minechat.commands.producer --msg Hello!

*для каждого из скриптов доступны аргументы коммандной строки*

**Переменные окружения**:

* HOST - хост
* PORT_IN - порт сервера для отправки сообщений в чат
* PORT_OUT - порт сервера для чтения сообщений чата

**Аргументы командной строки**:

Для просмотра доступных аргументов выполнить 

.. code-block:: bash

  $ python -m {path_to_script} --help
