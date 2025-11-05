import pytest
import os
import tempfile
import shutil
from unittest.mock import patch
import sys

sys.path.append('.')

try:
    import main as shell_module
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

pytestmark = pytest.mark.skipif(not HAS_MODULE, reason="Shell module not found")


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Фикстура для настройки и очистки перед/после каждого теста"""
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    
    # Создание тестовых файлов
    with open('test_file.txt', 'w') as f:
        f.write('Hello, World!')
    
    with open('binary_file.bin', 'wb') as f:
        f.write(b'\x00\x01\x02\x03')
    
    os.makedirs('test_dir/subdir', exist_ok=True)
    with open('test_dir/file_in_dir.txt', 'w') as f:
        f.write('File in directory')
    
    # Настройка логирования - исправленный вызов
    shell_module.setup_logging()
    
    yield test_dir, original_cwd
    
    # Очистка
    os.chdir(original_cwd)
    shutil.rmtree(test_dir)
    
    for log_file in ['shell.log', 'shell_state.txt']:
        if os.path.exists(log_file):
            os.remove(log_file)


class TestMiniShellPytest:
    
    def test_ls_basic(self, setup_and_teardown):
        """Тест команды ls без аргументов"""
        try:
            shell_module.ls()
            assert True 
        except Exception as e:
            pytest.fail(f"ls failed with exception: {e}")
    
    def test_ls_with_path(self, setup_and_teardown):
        """Тест команды ls с указанием пути"""
        try:
            shell_module.ls(path='test_dir')
            assert True
        except Exception as e:
            pytest.fail(f"ls with path failed with exception: {e}")
    
    def test_ls_detailed(self, setup_and_teardown):
        """Тест команды ls с опцией -l"""
        try:
            shell_module.ls(long_fotmat=True)
            assert True
        except Exception as e:
            pytest.fail(f"ls -l failed with exception: {e}")
    
    def test_cd_basic(self, setup_and_teardown):
        """Тест команды cd с существующей директорией"""
        test_dir, original_cwd = setup_and_teardown
        with patch('builtins.print'):
            shell_module.cd(path='test_dir')
            saved_path = shell_module.load_current_path()
            assert saved_path.endswith('test_dir')
    
    def test_cd_parent(self, setup_and_teardown):
        """Тест команды cd .."""
        original_path = os.getcwd()
        shell_module.cd(path='test_dir')
        shell_module.cd(path='..')
        final_path = shell_module.load_current_path()
        assert final_path == original_path
    
    def test_pwd(self, setup_and_teardown):
        """Тест команды pwd"""
        with patch('typer.echo') as mock_echo:
            shell_module.pwd()
            mock_echo.assert_called_once()
    
    def test_cat_file(self, setup_and_teardown):
        """Тест команды cat с существующим файлом"""
        with patch('typer.echo') as mock_echo:
            shell_module.cat(file='test_file.txt')
            mock_echo.assert_called_once_with('Hello, World!')
    
    def test_cat_nonexistent(self, setup_and_teardown):
        """Тест команды cat с несуществующим файлом"""
        with patch('typer.echo') as mock_echo:
            shell_module.cat(file='nonexistent.txt')
            assert mock_echo.called
            call_args = str(mock_echo.call_args)
            assert 'No such file or directory' in call_args
    
    def test_cp_file_basic(self, setup_and_teardown):
        """Тест команды cp для файлов - базовый случай"""
        test_content = "Test content for copy"
        with open('source_file.txt', 'w') as f:
            f.write(test_content)
        source_path = os.path.abspath('source_file.txt')
        dest_path = os.path.abspath('dest_file.txt')
        
        try:
            shell_module.cp(source=source_path, destination=dest_path)
            assert os.path.exists(dest_path)
            with open(dest_path, 'r') as f:
                content = f.read()
            assert content == test_content
        except Exception as e:
            pytest.fail(f"cp failed with exception: {e}")
    
    def test_cp_file_relative(self, setup_and_teardown):
        """Тест команды cp для файлов с относительными путями"""
        test_content = "Test content"
        with open('source.txt', 'w') as f:
            f.write(test_content)
        
        try:
            os.chdir('test_dir')
            shell_module.cp(source='../source.txt', destination='copied.txt')
            assert os.path.exists('copied.txt')
        except Exception as e:
            pytest.fail(f"cp with relative paths failed: {e}")
    
    def test_cp_directory_recursive(self, setup_and_teardown):
        """Тест команды cp -r для директорий"""
        os.makedirs('dir_to_copy/nested', exist_ok=True)
        with open('dir_to_copy/file1.txt', 'w') as f:
            f.write('file1')
        with open('dir_to_copy/nested/file2.txt', 'w') as f:
            f.write('file2')
        
        try:
            shell_module.cp(source='dir_to_copy', destination='dir_copied', recursive=True)
            assert os.path.exists('dir_copied')
            assert os.path.exists('dir_copied/file1.txt')
            assert os.path.exists('dir_copied/nested/file2.txt')
        except Exception as e:
            pytest.fail(f"cp -r failed with exception: {e}")
    
    def test_mv_file(self, setup_and_teardown):
        """Тест команды mv для файлов"""
        with open('file_to_move.txt', 'w') as f:
            f.write('Content')
        
        shell_module.mv(source='file_to_move.txt', destination='moved_file.txt')
        assert not os.path.exists('file_to_move.txt')
        assert os.path.exists('moved_file.txt')
    
    def test_save_and_load_path(self, setup_and_teardown):
        """Тест сохранения и загрузки пути"""
        test_path = '/tmp/test_path'
        shell_module.save_current_path(test_path)
        loaded_path = shell_module.load_current_path()
        assert loaded_path == test_path
    
    def test_cd_nonexistent_directory(self):
        """Тест cd с несуществующей директорией"""
        original_path = shell_module.load_current_path()
        
        with patch('builtins.print'):
            shell_module.cd(path='nonexistent_directory_12345')
        current_path = shell_module.load_current_path()
        assert current_path == original_path
    
    
        
    def test_cat_directory_error(self, setup_and_teardown):
        """Тест команды cat с директорией вместо файла"""
        with patch('typer.echo') as mock_echo:
            shell_module.cat(file='test_dir')
            assert mock_echo.called
            call_args = str(mock_echo.call_args)
            assert 'Is a directory' in call_args


@pytest.mark.parametrize("command_func,args,kwargs", [
    (shell_module.ls, [], {}),
    (shell_module.ls, [], {'long_fotmat': True}),
    (shell_module.pwd, [], {}),
])
def test_commands_no_errors(command_func, args, kwargs):
    """Параметризованный тест что команды выполняются без ошибок"""
    try:
        with patch('typer.echo'):
            command_func(*args, **kwargs)
        assert True
    except Exception as e:
        pytest.fail(f"Command {command_func.__name__} failed with: {e}")