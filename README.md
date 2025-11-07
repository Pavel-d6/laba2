Эмуляция основных Unix/Linux команд на Python с использованием фреймворка Typer.

Особенности

Полная эмуляция основных shell-команд
Управление файлами и директориями
Архивация ZIP и TAR.GZ форматов
Безопасность с подтверждением операций
Подробное логирование всех действий
Сохранение состояния между вызовами
Кроссплатформенность (Windows, Linux, macOS)

Установка

```bash
git clone https://github.com/yourusername/shell-emulator.git
cd shell-emulator

# Установка зависимостей
pip install typer

```


Использование

Базовые команды

```bash
# Навигация
python sh.py ls                    # Список файлов
python sh.py ls -l                 # Детальный список
python sh.py cd ~/Documents        # Смена директории
python sh.py pwd                   # Текущая директория

# Файловые операции
python sh.py cat README.md         # Просмотр файла
python sh.py cp file.txt backup/   # Копирование
python sh.py mv old.txt new.txt    # Переименование

```

Расширенные операции

```bash
# Рекурсивные операции
python sh.py cp -r directory/ backup/     # Рекурсивное копирование
python sh.py rm -r temp_files/            # Рекурсивное удаление

# Архивация
python sh.py zip project/ backup.zip      # Создание ZIP
python sh.py tar data/ data.tar.gz        # Создание TAR.GZ
python sh.py unzip archive.zip extract/   # Распаковка

```

Безопасность

Защита системных путей - запрещено удаление "/", ".."
Подтверждение операций - запрос для опасных действий
Проверка прав доступа - обработка PermissionError
Детальное логирование - запись всех операций


Доступные команды

Команда	Описание	Флаги

ls	Список файлов	-l - детальный формат
cd	Смена директории	-
pwd	Текущая директория	-
cat	Просмотр файлов	-
cp	Копирование	-r - рекурсивно
mv	Перемещение	-
rm	Удаление	-r - рекурсивно, -f - принудительно
zip	Создание ZIP	-
unzip	Распаковка ZIP	-
tar	Создание TAR.GZ	-


Структура проекта

shell-emulator/
├── sh.py                 # Основной исполняемый файл
├── shell_state.txt       # Состояние (текущая директория)
├── shell.log            # Логи операций
├── README.md            # Документация
└── requirements.txt     # Зависимости


Логирование

Все операции записываются в shell.log:

```bash
[2024-01-15 10:30:25] cd: changed to /home/user/documents
[2024-01-15 10:30:30] ls: Completed ls -l
[2024-01-15 10:30:35] cp: Copied 'file.txt' to 'backup/'
[2024-01-15 10:30:40] rm: Removed directory 'temp/'
```