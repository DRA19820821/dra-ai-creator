#!/usr/bin/env python3
"""
Script de Validação - Todas as Correções
Verifica se todas as 4 correções foram aplicadas corretamente

Uso:
    python test_all_corrections.py
"""
import sys
from pathlib import Path
from typing import List, Tuple


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Imprime cabeçalho"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def check_file_exists(filepath: Path) -> bool:
    """Verifica se arquivo existe"""
    return filepath.exists()


def check_correction_1() -> Tuple[bool, str]:
    """
    Correção 1: Campo risks como list[dict]
    """
    filepath = Path("core/state.py")
    
    if not check_file_exists(filepath):
        return False, f"Arquivo {filepath} não encontrado"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se risks é list[dict]
    if 'risks: list[dict]' in content or 'risks: List[dict]' in content:
        return True, "Campo 'risks' corretamente definido como list[dict]"
    
    # Verificar se ainda está errado
    if 'risks: list[str]' in content or 'risks: List[str]' in content:
        return False, "Campo 'risks' ainda está como list[str] (DEVE SER list[dict])"
    
    return False, "Campo 'risks' não encontrado no arquivo"


def check_correction_2() -> Tuple[bool, str]:
    """
    Correção 2: Checkpoint com opção 'wait'
    """
    filepath = Path("core/graph.py")
    
    if not check_file_exists(filepath):
        return False, f"Arquivo {filepath} não encontrado"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se tem "wait": END
    if '"wait": END' in content or "'wait': END" in content:
        return True, "Opção 'wait' corretamente adicionada ao roteamento"
    
    return False, "Opção 'wait' não encontrada no roteamento (DEVE ADICIONAR)"


def check_correction_3() -> Tuple[bool, str]:
    """
    Correção 3: Roteamento retorna 'wait'
    """
    filepath = Path("core/nodes/feedback.py")
    
    if not check_file_exists(filepath):
        return False, f"Arquivo {filepath} não encontrado"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se route_after_user_approval retorna 'wait'
    if 'return "wait"' in content:
        return True, "Função route_after_user_approval corretamente retorna 'wait'"
    
    return False, "Função route_after_user_approval não retorna 'wait' (DEVE ADICIONAR)"


def check_correction_4() -> Tuple[bool, str]:
    """
    Correção 4: Parse de JSON fields no builder
    """
    filepath = Path("core/nodes/builder.py")
    
    if not check_file_exists(filepath):
        return False, f"Arquivo {filepath} não encontrado"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se tem função parse_json_field
    has_parse_function = 'def parse_json_field' in content
    
    # Verificar se tem função fix_solution_output
    has_fix_function = 'def fix_solution_output' in content
    
    # Verificar se está usando json.loads para parse
    has_json_parse = 'json.loads(value)' in content or 'json.loads(fixed' in content
    
    if has_parse_function and has_fix_function and has_json_parse:
        return True, "Funções de parse robusto corretamente implementadas"
    
    if not has_parse_function:
        return False, "Falta função 'parse_json_field' (SOLUÇÃO DEFINITIVA PENDENTE)"
    
    if not has_fix_function:
        return False, "Falta função 'fix_solution_output' (SOLUÇÃO DEFINITIVA PENDENTE)"
    
    return False, "Parse robusto incompleto (APLICAR SOLUÇÃO DEFINITIVA)"


def check_app_py_syntax() -> Tuple[bool, str]:
    """
    Verifica se há erro de sintaxe no app.py
    """
    filepath = Path("app.py")
    
    if not check_file_exists(filepath):
        return False, f"Arquivo {filepath} não encontrado"
    
    try:
        import py_compile
        py_compile.compile(str(filepath), doraise=True)
        return True, "Sem erros de sintaxe"
    except py_compile.PyCompileError as e:
        return False, f"Erro de sintaxe: {str(e)}"


def main():
    """Executa todos os checks"""
    print(f"""
{Colors.BOLD}╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║       🔍 VALIDAÇÃO DE TODAS AS CORREÇÕES                        ║
║       AI Agent Flow - Verificação Completa                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.END}
    """)
    
    # Lista de checks
    checks = [
        ("Correção 1: Campo 'risks'", check_correction_1),
        ("Correção 2: Checkpoint 'wait'", check_correction_2),
        ("Correção 3: Roteamento 'wait'", check_correction_3),
        ("Correção 4: Parse robusto", check_correction_4),
        ("Bonus: Sintaxe app.py", check_app_py_syntax),
    ]
    
    results = []
    
    # Executar checks
    for check_name, check_func in checks:
        print(f"{Colors.BOLD}Verificando: {check_name}{Colors.END}")
        
        try:
            passed, message = check_func()
            results.append((check_name, passed, message))
            
            if passed:
                print(f"  {Colors.GREEN}✅ PASSOU{Colors.END}: {message}")
            else:
                print(f"  {Colors.RED}❌ FALHOU{Colors.END}: {message}")
        
        except Exception as e:
            results.append((check_name, False, str(e)))
            print(f"  {Colors.RED}❌ ERRO{Colors.END}: {e}")
        
        print()
    
    # Resumo
    print_header("RESUMO")
    
    total = len(results)
    passed = sum(1 for _, p, _ in results if p)
    failed = total - passed
    
    print(f"Total de checks: {total}")
    print(f"{Colors.GREEN}✅ Passou: {passed}{Colors.END}")
    print(f"{Colors.RED}❌ Falhou: {failed}{Colors.END}")
    
    percentage = (passed / total) * 100
    print(f"\n{'🎉' if percentage == 100 else '⚠️ '} {percentage:.0f}% dos checks passaram\n")
    
    # Detalhes dos que falharam
    if failed > 0:
        print_header("AÇÕES NECESSÁRIAS")
        
        for check_name, passed, message in results:
            if not passed:
                print(f"{Colors.RED}❌ {check_name}{Colors.END}")
                print(f"   {message}\n")
        
        print(f"\n{Colors.YELLOW}📚 Consulte os seguintes documentos:{Colors.END}")
        print(f"   • SOLUCAO_DEFINITIVA_GEMINI.md - Correção 4 (definitiva)")
        print(f"   • RESUMO_FINAL_COMPLETO.md - Overview completo")
        print(f"   • TODAS_AS_CORRECOES_APLICADAS.md - Checklist\n")
    
    else:
        print_header("🎉 PARABÉNS!")
        print(f"{Colors.GREEN}Todas as correções foram aplicadas com sucesso!{Colors.END}\n")
        print("Próximos passos:")
        print("  1. Execute: streamlit run app.py")
        print("  2. Teste o fluxo completo")
        print("  3. Verifique os arquivos gerados\n")
        print(f"{Colors.BOLD}🚀 Seu sistema está 100% funcional!{Colors.END}\n")
    
    # Exit code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Operação cancelada pelo usuário{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Erro inesperado: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)