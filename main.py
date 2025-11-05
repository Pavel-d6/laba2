import typer
import os
import grp
import pwd as pwd_mod
import time
import logging
import shutil
from pathlib import Path
from typing import Optional
app = typer.Typer()
STATE_FILE = "shell_state.txt"
def save_current_path(current_path):
    """Сохранить текущий путь в файл"""
    with open(STATE_FILE, "w") as f:
        f.write(current_path)

def load_current_path():
    """Загрузить сохраненный путь из файла"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return os.getcwd() 


def setup_logging():
    """Настройка системы логирования"""
    log_file = Path('shell.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')


@app.command()
def ls(
    path: Optional[str] = typer.Argument(None, help="Directory or file path"),
    long_fotmat: bool = typer.Option(False, "-l", help="Long format")
):  
    logger = logging.getLogger()
    try:
        target_path = path or load_current_path()
        now_file = sorted([file for file in os.listdir(target_path) if not file.startswith(".")])
        if long_fotmat:
            for file in now_file:
                    filepath = os.path.join(target_path, file)
                    mode = int(oct(os.stat(filepath).st_mode),8)
                    
                    file_type = '?'
                    if os.path.isdir(filepath):
                        file_type = 'd'
                    elif os.path.isfile(filepath):
                        file_type = '-'
                    elif os.path.islink(filepath):
                        file_type = 'l'

                    permissions = ''
                    permissions += 'r' if mode & 0o400 else '-'
                    permissions += 'w' if mode & 0o200 else '-'  
                    permissions += 'x' if mode & 0o100 else '-'

                    permissions += 'r' if mode & 0o040 else '-'
                    permissions += 'w' if mode & 0o020 else '-'
                    permissions += 'x' if mode & 0o010 else '-'

                    permissions += 'r' if mode & 0o004 else '-'
                    permissions += 'w' if mode & 0o002 else '-'
                    permissions += 'x' if mode & 0o001 else '-'
                    full_permissions = file_type + permissions
                    files = os.stat(filepath)
                    output = f"{full_permissions+'@'} {files.st_nlink:2} " \
                            f"{pwd_mod.getpwuid(files.st_uid).pw_name:8} " \
                            f"{grp.getgrgid(files.st_gid).gr_name} " \
                            f"{files.st_size:8} " \
                            f"{time.strftime('%b %d %H:%M', time.localtime(files.st_mtime)):8} " \
                            f"{file:8}"
                    typer.echo(output)
            logger.info("Complite ls -l")
        else:
            output_limit = 3
            line = []
            for i in now_file:
                line.append(i)
                output_limit -= 1
                if output_limit == 0:
                    output_limit = 3
                    typer.echo(f"{line[0]:20}" f"{line[1]:20}" f"{line[2]:20}")
                    line = []
            logger.info("Complite ls")
    except:
        logger.info("Error ls")






@app.command()
def cd(
    path: Optional[str] = typer.Argument(None, help="Input Directory")
):  
    logger = logging.getLogger()
    now_path = load_current_path()

    if path is None:
        path = "~"

    if path == "~":
        new_path = os.path.expanduser("~")

    elif path == "/":
        new_path = "/"

    elif path == "..":
        new_path = os.path.dirname(now_path)

    else:
        if os.path.isabs(path):
            new_path = path
        else:
            new_path = os.path.abspath(os.path.join(now_path, path))
    
    if os.path.exists(new_path) and os.path.isdir(new_path):
        save_current_path(new_path)
        print(new_path)
        logger.info("Complite cd")
    else:
        logger.info(f"cd: Incorrect path {new_path}")

@app.command()
def pwd():
    typer.echo(load_current_path())


@app.command()
def cat(
    file: Optional[str] = typer.Argument(None, help="Input file name")
):
    current_path = load_current_path()
    if file is None:
        error_msg = "cat: missing file operand"
        typer.echo(error_msg)
        logger.info(error_msg)
        return
        
    new_path = os.path.join(current_path, file) if not os.path.isabs(file) else file
    logger = logging.getLogger()
    
    if not os.path.exists(new_path):
        error_msg = f"cat: {file}: No such file or directory"
        typer.echo(error_msg)
        logger.info(error_msg)
        return

    if os.path.isdir(new_path):
        error_msg = f"cat: {file}: Is a directory"
        typer.echo(error_msg)
        logger.info(error_msg)
        return

    try:
        with open(new_path, 'r', encoding='utf-8') as f:
            content = f.read()
            typer.echo(content)
    except UnicodeDecodeError:
        file_size = os.path.getsize(new_path)
        typer.echo(f"cat: {file}: Binary file ({file_size} bytes)")
    except Exception as e:
        error_msg = f"cat: {file}: {str(e)}"
        typer.echo(error_msg)
        logger.info(error_msg)



@app.command()
def cp(
    source: str = typer.Argument(..., help="Source file/directory"),
    destination: str = typer.Argument(..., help="Destination path"),
    recursive: bool = typer.Option(False, "-r", "--recursive", help="Copy directories recursively"),
):  
    current_path = load_current_path()
    
    # Получаем абсолютные пути
    if os.path.isabs(source):
        abs_source = source
    else:
        abs_source = os.path.join(current_path, source)
    
    if os.path.isabs(destination):
        abs_destination = destination
    else:
        abs_destination = os.path.join(current_path, destination)
    
    # Проверяем существует ли источник
    if not os.path.exists(abs_source):
        typer.echo(f"cp: cannot stat '{source}': No such file or directory")
        return
    
    try:
        if os.path.isfile(abs_source):
            # Копирование файла
            shutil.copy2(abs_source, abs_destination)
            typer.echo(f"Copied '{source}' to '{destination}'")
        
        elif os.path.isdir(abs_source):
            if recursive:
                # Рекурсивное копирование директории
                shutil.copytree(abs_source, abs_destination)
                typer.echo(f"Copied directory '{source}' to '{destination}'")
            else:
                typer.echo(f"cp: -r not specified; omitting directory '{source}'")
    
    except FileExistsError:
        typer.echo(f"cp: cannot copy '{source}': Destination already exists")
    except Exception as e:
        typer.echo(f"cp: cannot copy '{source}' to '{destination}': {str(e)}")


@app.command()
def mv(
    source: str = typer.Argument(..., help="Source file/directory"),
    destination: str = typer.Argument(..., help="Destination path"),
):
    """Move or rename files and directories"""

    logger = logging.getLogger()
    if not os.path.exists(source):
        error_msg = f"cannot stat '{source}': No such file or directory"
        typer.echo(f"mv: {error_msg}")
        logger.info(f"mv: {error_msg}")
        return
    
    try:
        if os.path.isdir(destination):
            basename = os.path.basename(source)
            final_dest = os.path.join(destination, basename)

            if os.path.abspath(source) == os.path.abspath(final_dest):
                typer.echo(f"mv: cannot move '{source}' to a subdirectory of itself")
                logger.info(f"mv: cannot move '{source}' to a subdirectory of itself")
                return
            
            shutil.move(source, final_dest)
            success_msg = f"Moved '{source}' to '{final_dest}'"
            
        else:
            if os.path.abspath(source) == os.path.abspath(destination):
                typer.echo(f"mv: '{source}' and '{destination}' are the same file")
                logger.info(f"mv: '{source}' and '{destination}' are the same file")
                return
                
            shutil.move(source, destination)
            success_msg = f"Moved and rename '{source}' to '{destination}'"
        logger.info(success_msg)
        
    except PermissionError as e:
        error_msg = f"cannot move '{source}': Permission denied"
        typer.echo(f"mv: {error_msg}")
        logger.info(f"mv: {error_msg}")
    except OSError as e:
        if "Directory not empty" in str(e):
            error_msg = f"cannot move '{source}': Directory not empty"
        else:
            error_msg = f"cannot move '{source}': {e}"
        typer.echo(f"mv: {error_msg}")
        logger.info(f"mv: {error_msg}")
    except Exception as e:
        error_msg = f"unexpected error: {e}"
        typer.echo(f"mv: {error_msg}")
        logger.info(f"mv: {error_msg}")


@app.command()
def rm(
    path: str = typer.Argument(..., help="File or directory to remove"),
    recursive: bool = typer.Option(False, "-r", "--recursive", help="Remove directories recursively"),
    force: bool = typer.Option(False, "-f", "--force", help="Force removal without confirmation"),
):
    """Remove files or directories"""
    
    # Проверка существования пути
    if not os.path.exists(path):
        error_msg = f"cannot remove '{path}': No such file or directory"
        typer.echo(f"rm: {error_msg}")
        logger.info(f"rm: {error_msg}")
        return

    # Защита от удаления критических путей
    if protected_path(path):
        error_msg = f"cannot remove '{path}': Protected directory"
        typer.echo(f"rm: {error_msg}")
        logger.info(f"rm: {error_msg}")
        return

    try:
        if os.path.isfile(path):
            # Удаление файла
            if not force:
                confirmation = typer.confirm(f"Remove file '{path}'?")
                if not confirmation:
                    typer.echo("Operation cancelled")
                    return
            
            os.remove(path)
            success_msg = f"Removed file '{path}'"
            typer.echo(success_msg)
            logger.info(success_msg)

        elif os.path.isdir(path):
            if not recursive:
                error_msg = f"cannot remove '{path}': Is a directory (use -r)"
                typer.echo(f"rm: {error_msg}")
                logger.info(f"rm: {error_msg}")
                return

            if not force:
                item_count = count_items(path)
                confirmation = typer.confirm(
                    f"Recursively remove directory '{path}' with {item_count} items?"
                )
                if not confirmation:
                    typer.echo("Operation cancelled")
                    return

            shutil.rmtree(path)
            success_msg = f"Removed directory '{path}'"
            typer.echo(success_msg)
            logger.info(success_msg)

    except PermissionError as e:
        error_msg = f"cannot remove '{path}': Permission denied"
        typer.echo(f"rm: {error_msg}")
        logger.info(f"rm: {error_msg}")
    except OSError as e:
        error_msg = f"cannot remove '{path}': {e}"
        typer.echo(f"rm: {error_msg}")
        logger.info(f"rm: {error_msg}")
    except Exception as e:
        error_msg = f"unexpected error: {e}"
        typer.echo(f"rm: {error_msg}")
        logger.info(f"rm: {error_msg}")

def protected_path(path: str) -> bool:
    """защищенные от удаления"""
    abs_path = os.path.abspath(path)
    protected_paths = [
        "/",
        "/.",
        "/..",
        os.path.abspath("/"),
        os.path.abspath("/.."),
        os.path.abspath(".."),
    ]
    if abs_path in protected_paths:
        return True
    if abs_path == os.path.abspath("/") or abs_path == os.path.abspath("/.."):
        return True
        
    return False

def count_items(directory: str) -> int:
    """кол-во элементов в директории"""
    count = 0
    try:
        for dirs, files in os.walk(directory):
            count += len(dirs) + len(files)
    except (PermissionError, OSError):
        return -1
    return count
    
    
    


if __name__ == "__main__":

    logger = logging.getLogger()
    setup_logging()
    app()


#python sh.py cp -r /Users/pavel/Documents/nf  /Users/pavel/Downloads/ 