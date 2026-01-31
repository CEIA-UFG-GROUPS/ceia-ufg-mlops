import pytest

def limpar_nome_escola(nome):
    """Exemplo de função de limpeza de dados"""
    if not nome:
        return "N/A"
    return nome.strip().upper()

def test_limpar_nome_escola_valido():
    assert limpar_nome_escola("  ufg  ") == "UFG"

def test_limpar_nome_escola_vazio():
    assert limpar_nome_escola("") == "N/A"

def test_limpar_nome_escola_none():
    assert limpar_nome_escola(None) == "N/A"