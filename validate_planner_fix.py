#!/usr/bin/env python3
"""
Script de Validação - Correção do Planner
Verifica se a correção foi aplicada corretamente

Uso:
    python validate_planner_fix.py
"""
import sys
from pathlib import Path
from typing import Tuple


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


def check_file_exists() -> Tuple[bool, str]:
    """Verifica se arquivo existe"""
    filepath = Path("core/nodes/planner.py")
    
    if not filepath.exists():
        return False, f"Arquivo {filepath} não encontrado"
    
    return True, "Arquivo encontrado"


def check_has_robust_parse() -> Tuple[bool, str]:
    """Verifica se tem função robust_parse_plan_output"""
    filepath = Path("core/nodes/planner.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def robust_parse_plan_output' in content:
        return True, "Função robust_parse_plan_output presente"
    
    return False, "Falta função robust_parse_plan_output (CORREÇÃO PENDENTE)"


def check_has_fix_truncated_json() -> Tuple[bool, str]:
    """Verifica se tem função fix_truncated_json"""
    filepath = Path("core/nodes/planner.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def fix_truncated_json' in content:
        return True, "Função fix_truncated_json presente"
    
    return False, "Falta função fix_truncated_json (CORREÇÃO PENDENTE)"


def check_has_none_validation() -> Tuple[bool, str]:
    """Verifica se tem validação de None"""
    filepath = Path("core/nodes/planner.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procurar por validação explícita de None
    if 'if result is None' in content or 'if result is not None' in content:
        return True, "Validação de None presente"
    
    return False, "Falta validação de None (CRÍTICO)"


def check_has_retry_logic() -> Tuple[bool, str]:
    """Verifica se tem lógica de retry"""
    filepath = Path("core/nodes/planner.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'max_retries' in content and 'for attempt in range' in content:
        return True, "Lógica de retry presente"
    
    return False, "Falta lógica de retry (IMPORTANTE)"


def check_has_defaults() -> Tuple[bool, str]:
    """Verifica se tem setdefault para campos obrigatórios"""
    filepath = Path("core/nodes/planner.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procurar por setdefault
    if 'setdefault' in content and "'title'" in content:
        return True, "Defaults para campos obrigatórios presente"
    
    return False, "Falta defaults (RECOMENDADO)"


def check_syntax() -> Tuple[bool, str]:
    """Verifica sintaxe Python"""
    filepath = Path("core/nodes/planner.py")
    
    try:
        import py_compile
        py_compile.compile(str(filepath), doraise=True)
        return True, "Sintaxe Python válida"
    except py_compile.PyCompileError as e:
        return False, f"Erro de sintaxe: {str(e)}"


def check_imports() -> Tuple[bool, str]:
    """Verifica se imports estão OK"""
    filepath = Path("core/nodes/planner.py")
    
    try:
        # Adicionar path ao sys.path
        sys.path.insert(0, str(Path.cwd()))
        
        # Tentar importar
        import core.nodes.planner
        
        return True, "Imports funcionando"
    except ImportError as e:
        return False, f"Erro de import: {str(e)}"
    except Exception as e:
        return False, f"Erro ao importar: {str(e)}"


def check_version_marker() -> Tuple[bool, str]:
    """Verifica se tem marcador de versão corrigida"""
    filepath = Path("core/nodes/planner.py")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procurar por comentário de versão
    if 'ULTRA-ROBUSTA' in content or 'VERSÃO CORRIGIDA' in content:
        return True, "Versão corrigida confirmada"
    
    return False, "Sem marcador de versão (pode ser versão antiga)"


def main():
    """Executa todas as verificações"""
    print(f"""
{Colors.BOLD}╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║       🔍 VALIDAÇÃO DA CORREÇÃO DO PLANNER                       ║
║       AI Agent Flow - Verificação Automática                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.END}
    """)
    
    # Lista de checks
    checks = [
        ("1. Arquivo existe", check_file_exists),
        ("2. Versão corrigida", check_version_marker),
        ("3. Função robust_parse", check_has_robust_parse),
        ("4. Função fix_truncated", check_has_fix_truncated_json),
        ("5. Validação None", check_has_none_validation),
        ("6. Lógica retry", check_has_retry_logic),
        ("7. Defaults campos", check_has_defaults),
        ("8. Sintaxe válida", check_syntax),
        ("9. Imports OK", check_imports),
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
    
    # Análise por criticidade
    critical_checks = ["5. Validação None", "8. Sintaxe válida"]
    critical_failed = [name for name, passed, _ in results if not passed and name in critical_checks]
    
    if critical_failed:
        print_header("⚠️ CHECKS CRÍTICOS FALHARAM")
        print(f"{Colors.RED}{Colors.BOLD}Os seguintes checks críticos falharam:{Colors.END}\n")
        for check in critical_failed:
            print(f"  ❌ {check}")
        print(f"\n{Colors.YELLOW}O sistema NÃO funcionará corretamente até que estes sejam corrigidos.{Colors.END}\n")
    
    # Detalhes dos que falharam
    if failed > 0:
        print_header("AÇÕES NECESSÁRIAS")
        
        for check_name, passed, message in results:
            if not passed:
                print(f"{Colors.RED}❌ {check_name}{Colors.END}")
                print(f"   {message}\n")
        
        print(f"\n{Colors.YELLOW}📚 Consulte:{Colors.END}")
        print(f"   • GUIA_CORRECAO_ERRO_PLANNER.md - Guia completo")
        print(f"   • core/nodes/planner.py - Arquivo a ser substituído\n")
        
        print(f"{Colors.BOLD}Como corrigir:{Colors.END}")
        print(f"   1. Faça backup: cp core/nodes/planner.py core/nodes/planner.py.backup")
        print(f"   2. Substitua o arquivo pelo código corrigido")
        print(f"   3. Execute este script novamente: python validate_planner_fix.py\n")
    
    else:
        print_header("🎉 PARABÉNS!")
        print(f"{Colors.GREEN}Todas as correções foram aplicadas com sucesso!{Colors.END}\n")
        print("Próximos passos:")
        print("  1. Execute: streamlit run app.py")
        print("  2. Teste o fluxo completo de criação de plano")
        print("  3. Verifique os logs para confirmar sucesso\n")
        
        print(f"{Colors.BOLD}Logs esperados:{Colors.END}")
        print(f"  {Colors.GREEN}✅ Nó concluído: create_plan{Colors.END}")
        print(f"  {Colors.GREEN}🎉 Plano criado: [Título] (X passos){Colors.END}\n")
        
        print(f"{Colors.BOLD}🚀 Seu sistema está pronto!{Colors.END}\n")
    
    # Recomendações
    if passed >= 7:
        print_header("📊 STATUS")
        print(f"{Colors.GREEN}Status: BOM{Colors.END}")
        print(f"A correção está {percentage:.0f}% completa.")
        
        if failed > 0:
            print(f"\n{Colors.YELLOW}Itens não críticos faltando:{Colors.END}")
            non_critical = [name for name, p, _ in results if not p and name not in critical_checks]
            for check in non_critical:
                print(f"  ⚠️ {check} (opcional mas recomendado)")
    
    elif passed >= 5:
        print_header("📊 STATUS")
        print(f"{Colors.YELLOW}Status: PARCIAL{Colors.END}")
        print(f"Correção {percentage:.0f}% completa. Alguns itens importantes faltando.")
    
    else:
        print_header("📊 STATUS")
        print(f"{Colors.RED}Status: INCOMPLETO{Colors.END}")
        print(f"Apenas {percentage:.0f}% dos checks passaram.")
        print(f"\n{Colors.BOLD}A correção NÃO foi aplicada corretamente.{Colors.END}")
        print(f"Por favor, substitua o arquivo core/nodes/planner.py pelo código corrigido.\n")
    
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