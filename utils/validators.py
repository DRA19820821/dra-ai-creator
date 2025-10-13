"""
Validadores e Utilidades de Validação
"""
import re
import ast
from typing import Tuple, List, Optional


def validate_python_syntax(code: str) -> Tuple[bool, Optional[str]]:
    """
    Valida sintaxe Python
    
    Args:
        code: Código Python como string
        
    Returns:
        Tupla (is_valid, error_message)
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Erro de sintaxe na linha {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Erro ao validar código: {str(e)}"


def validate_imports(code: str) -> Tuple[bool, List[str]]:
    """
    Extrai e valida imports Python
    
    Args:
        code: Código Python
        
    Returns:
        Tupla (is_valid, list_of_imports)
    """
    try:
        tree = ast.parse(code)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return True, imports
    except Exception as e:
        return False, []


def validate_json_structure(json_str: str) -> Tuple[bool, Optional[str]]:
    """
    Valida estrutura JSON
    
    Args:
        json_str: String JSON
        
    Returns:
        Tupla (is_valid, error_message)
    """
    import json
    try:
        json.loads(json_str)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"JSON inválido: {e.msg} na posição {e.pos}"
    except Exception as e:
        return False, f"Erro ao validar JSON: {str(e)}"


def check_code_quality_issues(code: str) -> List[str]:
    """
    Verifica issues básicos de qualidade de código
    
    Args:
        code: Código Python
        
    Returns:
        Lista de issues encontrados
    """
    issues = []
    
    lines = code.split('\n')
    
    # Check 1: Linhas muito longas (>100 chars)
    long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
    if long_lines:
        issues.append(f"Linhas muito longas (>100 chars): {long_lines[:5]}")
    
    # Check 2: Código comentado excessivo
    commented_lines = sum(1 for line in lines if line.strip().startswith('#'))
    if commented_lines > len(lines) * 0.3:  # Mais de 30% comentado
        issues.append(f"Muitos comentários: {commented_lines} linhas ({commented_lines/len(lines)*100:.0f}%)")
    
    # Check 3: Funções sem docstrings
    try:
        tree = ast.parse(code)
        functions_without_docstring = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_docstring = (
                    ast.get_docstring(node) is not None
                )
                if not has_docstring and not node.name.startswith('_'):
                    functions_without_docstring.append(node.name)
        
        if functions_without_docstring and len(functions_without_docstring) > 3:
            issues.append(f"Funções sem docstring: {len(functions_without_docstring)}")
    
    except:
        pass
    
    # Check 4: TODO/FIXME comments
    todo_pattern = re.compile(r'#\s*(TODO|FIXME|XXX|HACK)', re.IGNORECASE)
    todos = [i+1 for i, line in enumerate(lines) if todo_pattern.search(line)]
    if todos:
        issues.append(f"TODOs encontrados nas linhas: {todos}")
    
    # Check 5: Print statements (pode ser debug code)
    print_lines = [i+1 for i, line in enumerate(lines) if 'print(' in line and not line.strip().startswith('#')]
    if len(print_lines) > 5:
        issues.append(f"Muitos print statements: {len(print_lines)}")
    
    return issues


def validate_file_structure(files: dict) -> Tuple[bool, List[str]]:
    """
    Valida estrutura de arquivos gerados
    
    Args:
        files: Dict {filename: content}
        
    Returns:
        Tupla (is_valid, list_of_issues)
    """
    issues = []
    
    # Check 1: Deve ter pelo menos 1 arquivo
    if not files:
        issues.append("Nenhum arquivo gerado")
        return False, issues
    
    # Check 2: Deve ter README
    has_readme = any('readme' in f.lower() for f in files.keys())
    if not has_readme:
        issues.append("Sem arquivo README")
    
    # Check 3: Se tem .py, deve ter requirements.txt
    has_python = any(f.endswith('.py') for f in files.keys())
    has_requirements = any('requirements' in f.lower() for f in files.keys())
    
    if has_python and not has_requirements:
        issues.append("Projeto Python sem requirements.txt")
    
    # Check 4: Arquivos vazios
    empty_files = [f for f, content in files.items() if not content or len(content.strip()) == 0]
    if empty_files:
        issues.append(f"Arquivos vazios: {', '.join(empty_files)}")
    
    # Check 5: Nomes de arquivo inválidos
    invalid_names = []
    for filename in files.keys():
        if not re.match(r'^[\w\-. /]+$', filename):
            invalid_names.append(filename)
    
    if invalid_names:
        issues.append(f"Nomes de arquivo inválidos: {', '.join(invalid_names)}")
    
    return len(issues) == 0, issues


def validate_requirements_txt(content: str) -> Tuple[bool, List[str]]:
    """
    Valida conteúdo de requirements.txt
    
    Args:
        content: Conteúdo do arquivo
        
    Returns:
        Tupla (is_valid, list_of_issues)
    """
    issues = []
    
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Pattern para dependência válida
    valid_pattern = re.compile(r'^[\w\-]+([<>=!]+[\w.]+)?$')
    
    for i, line in enumerate(lines, 1):
        # Ignorar comentários
        if line.startswith('#'):
            continue
        
        # Validar formato
        if not valid_pattern.match(line):
            issues.append(f"Linha {i} inválida: {line}")
    
    # Check: deve ter pelo menos 1 dependência
    dependencies = [l for l in lines if not l.startswith('#')]
    if not dependencies:
        issues.append("Nenhuma dependência especificada")
    
    return len(issues) == 0, issues


def calculate_code_complexity(code: str) -> dict:
    """
    Calcula métricas básicas de complexidade
    
    Args:
        code: Código Python
        
    Returns:
        Dict com métricas
    """
    try:
        tree = ast.parse(code)
        
        stats = {
            "total_lines": len(code.split('\n')),
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "max_nesting_depth": 0,
            "average_function_length": 0,
        }
        
        function_lengths = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                stats["functions"] += 1
                # Calcular linhas da função
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    func_length = node.end_lineno - node.lineno
                    function_lengths.append(func_length)
            
            elif isinstance(node, ast.ClassDef):
                stats["classes"] += 1
            
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                stats["imports"] += 1
        
        if function_lengths:
            stats["average_function_length"] = sum(function_lengths) / len(function_lengths)
        
        return stats
    
    except:
        return {
            "total_lines": len(code.split('\n')),
            "error": "Não foi possível calcular complexidade"
        }


def suggest_improvements(code: str) -> List[str]:
    """
    Sugere melhorias para o código
    
    Args:
        code: Código Python
        
    Returns:
        Lista de sugestões
    """
    suggestions = []
    
    # Verificar issues de qualidade
    issues = check_code_quality_issues(code)
    if issues:
        suggestions.append("Corrigir issues de qualidade encontrados")
    
    # Verificar complexidade
    complexity = calculate_code_complexity(code)
    
    if complexity.get("average_function_length", 0) > 50:
        suggestions.append("Considere dividir funções muito longas (>50 linhas)")
    
    if complexity.get("functions", 0) == 0 and complexity.get("total_lines", 0) > 20:
        suggestions.append("Considere organizar código em funções")
    
    # Verificar type hints
    if 'def ' in code and '->' not in code:
        suggestions.append("Adicionar type hints para melhor documentação")
    
    # Verificar error handling
    if 'try' not in code and complexity.get("total_lines", 0) > 30:
        suggestions.append("Considere adicionar error handling (try/except)")
    
    return suggestions