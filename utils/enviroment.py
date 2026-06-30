import os

def get_env_variaveis(nome_variavel, variavel_padrao=''):
    return os.environ.get(nome_variavel, variavel_padrao)

def parse_separar_virgula_str_to_list(virgula_str):
    if not virgula_str or not isinstance(virgula_str, str):
        return []
    return [string.strip() for string in virgula_str.split(',') if string]
