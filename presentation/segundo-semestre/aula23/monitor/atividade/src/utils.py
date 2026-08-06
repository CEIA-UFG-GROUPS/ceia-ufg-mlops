import os
import re

def get_latest_version(directory, prefix, extension):
    """
    Retorna o maior número de versão 'vX' encontrado para os arquivos 
    com o formato '{prefix}_vX{extension}' no diretório.
    Se não encontrar nenhum, retorna 0.
    """
    if not os.path.exists(directory):
        return 0

    max_version = 0
    # Create regex pattern ignoring raw string issues
    pattern = re.compile(re.escape(prefix) + r'_v(\d+)' + re.escape(extension))
    
    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            version = int(match.group(1))
            if version > max_version:
                max_version = version
                
    return max_version

def get_latest_file_path(directory, prefix, extension):
    """Retorna o caminho do arquivo mais recente, ou None se não existir."""
    version = get_latest_version(directory, prefix, extension)
    if version == 0:
        return None
    return os.path.join(directory, f"{prefix}_v{version}{extension}")

def get_next_file_path(directory, prefix, extension):
    """Retorna o caminho para a próxima versão (v+1) de um arquivo."""
    version = get_latest_version(directory, prefix, extension)
    return os.path.join(directory, f"{prefix}_v{version + 1}{extension}")


