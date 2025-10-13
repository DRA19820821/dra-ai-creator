"""
Parser JSON Robusto para Respostas de LLMs

Este módulo fornece funções robustas para fazer parse de JSON
que pode vir malformado de LLMs.
"""
import json
import re
from typing import Any, Optional


def extract_json_from_text(text: str) -> str:
    """
    Extrai JSON de texto que pode conter markdown ou outros caracteres
    
    Args:
        text: Texto que pode conter JSON
        
    Returns:
        String JSON limpa
    """
    # Remover markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        # Tentar pegar qualquer bloco de código
        parts = text.split("```")
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Partes ímpares são code blocks
                # Verificar se parece com JSON
                part = part.strip()
                if part.startswith('{') or part.startswith('['):
                    text = part
                    break
    
    # Remover quebras de linha extras e espaços
    text = text.strip()
    
    return text


def fix_common_json_issues(json_str: str) -> str:
    """
    Corrige problemas comuns em JSON malformado
    
    Args:
        json_str: String JSON potencialmente malformada
        
    Returns:
        String JSON corrigida
    """
    # Corrigir aspas simples para duplas (comum em alguns LLMs)
    # Mas cuidado com apostrofos dentro de strings
    # json_str = json_str.replace("'", '"')  # Muito agressivo
    
    # Remover vírgulas antes de } ou ]
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # Adicionar vírgulas faltando entre propriedades
    # (mais complexo, pular por enquanto)
    
    # Remover comentários (// ou #)
    json_str = re.sub(r'//.*?\n', '\n', json_str)
    json_str = re.sub(r'#.*?\n', '\n', json_str)
    
    # Corrigir strings não fechadas (tentativa básica)
    # Muito complexo, deixar para json.decoder.JSONDecodeError handler
    
    return json_str


def parse_json_robust(text: str, max_attempts: int = 3) -> Optional[dict]:
    """
    Tenta fazer parse de JSON de forma robusta com múltiplas estratégias
    
    Args:
        text: Texto contendo JSON
        max_attempts: Número máximo de tentativas com diferentes estratégias
        
    Returns:
        Dict parsed ou None se falhar
    """
    if not text or not text.strip():
        return None
    
    # Estratégia 1: Parse direto
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Estratégia 2: Extrair de markdown e tentar novamente
    try:
        cleaned = extract_json_from_text(text)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Estratégia 3: Corrigir problemas comuns e tentar
    try:
        cleaned = extract_json_from_text(text)
        fixed = fix_common_json_issues(cleaned)
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass
    
    # Estratégia 4: Tentar encontrar primeiro objeto JSON válido
    try:
        cleaned = extract_json_from_text(text)
        # Procurar por { ... } ou [ ... ]
        start_brace = cleaned.find('{')
        start_bracket = cleaned.find('[')
        
        start = -1
        if start_brace >= 0 and (start_bracket < 0 or start_brace < start_bracket):
            start = start_brace
            end_char = '}'
        elif start_bracket >= 0:
            start = start_bracket
            end_char = ']'
        
        if start >= 0:
            # Encontrar o fechamento correspondente
            count = 0
            end = -1
            for i in range(start, len(cleaned)):
                if cleaned[i] == '{' or cleaned[i] == '[':
                    count += 1
                elif cleaned[i] == '}' or cleaned[i] == ']':
                    count -= 1
                    if count == 0:
                        end = i + 1
                        break
            
            if end > start:
                json_substring = cleaned[start:end]
                return json.loads(json_substring)
    except (json.JSONDecodeError, ValueError, IndexError):
        pass
    
    # Estratégia 5: Tentar com json5 (se instalado)
    try:
        import json5
        cleaned = extract_json_from_text(text)
        return json5.loads(cleaned)
    except (ImportError, Exception):
        pass
    
    # Todas as estratégias falharam
    return None


def safe_parse_llm_response(
    response_text: str,
    expected_keys: Optional[list[str]] = None,
    default: Optional[dict] = None
) -> dict:
    """
    Parse seguro de resposta de LLM com validação
    
    Args:
        response_text: Texto da resposta do LLM
        expected_keys: Lista de chaves esperadas no JSON
        default: Valor default se parse falhar
        
    Returns:
        Dict parsed ou default
    """
    result = parse_json_robust(response_text)
    
    if result is None:
        if default is not None:
            return default
        else:
            return {"error": "Failed to parse JSON", "raw_text": response_text[:500]}
    
    # Validar chaves esperadas
    if expected_keys:
        missing_keys = [key for key in expected_keys if key not in result]
        if missing_keys:
            result["_missing_keys"] = missing_keys
            result["_warning"] = f"Missing expected keys: {', '.join(missing_keys)}"
    
    return result


def extract_json_array(text: str) -> Optional[list]:
    """
    Extrai array JSON de texto
    
    Args:
        text: Texto contendo array JSON
        
    Returns:
        Lista ou None
    """
    result = parse_json_robust(text)
    
    if isinstance(result, list):
        return result
    elif isinstance(result, dict) and len(result) == 1:
        # Pode ser um objeto com uma chave contendo o array
        first_value = next(iter(result.values()))
        if isinstance(first_value, list):
            return first_value
    
    return None


def validate_json_structure(data: dict, schema: dict) -> tuple[bool, list[str]]:
    """
    Valida estrutura básica de JSON contra um schema simples
    
    Args:
        data: Dados para validar
        schema: Schema simples {key: type}
        
    Returns:
        Tupla (is_valid, errors)
    """
    errors = []
    
    for key, expected_type in schema.items():
        if key not in data:
            errors.append(f"Missing key: {key}")
            continue
        
        value = data[key]
        
        if expected_type == "str" and not isinstance(value, str):
            errors.append(f"Key '{key}' should be string, got {type(value).__name__}")
        elif expected_type == "int" and not isinstance(value, int):
            errors.append(f"Key '{key}' should be int, got {type(value).__name__}")
        elif expected_type == "float" and not isinstance(value, (int, float)):
            errors.append(f"Key '{key}' should be float, got {type(value).__name__}")
        elif expected_type == "bool" and not isinstance(value, bool):
            errors.append(f"Key '{key}' should be bool, got {type(value).__name__}")
        elif expected_type == "list" and not isinstance(value, list):
            errors.append(f"Key '{key}' should be list, got {type(value).__name__}")
        elif expected_type == "dict" and not isinstance(value, dict):
            errors.append(f"Key '{key}' should be dict, got {type(value).__name__}")
    
    return len(errors) == 0, errors


# Exemplo de uso:
if __name__ == "__main__":
    # Teste com JSON malformado
    malformed = """
    ```json
    {
        "title": "Test",
        "items": [1, 2, 3,],
        "description": "This has a trailing comma"
    }
    ```
    """
    
    result = parse_json_robust(malformed)
    print("Parsed:", result)