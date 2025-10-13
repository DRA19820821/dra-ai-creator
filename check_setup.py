#!/usr/bin/env python3
"""
Script de Verificação - AI Agent Flow
Execute este script para verificar se tudo está configurado corretamente.

Uso:
    python check_setup.py
"""

import sys
import os
from pathlib import Path


def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_check(name, status, details=""):
    """Imprime resultado de um check"""
    icon = "✅" if status else "❌"
    print(f"{icon} {name}")
    if details:
        print(f"   {details}")


def check_python_version():
    """Verifica versão do Python"""
    print_header("1. Verificando Versão do Python")
    
    version = sys.version_info
    is_ok = version.major == 3 and version.minor >= 11
    
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print_check(
        "Python 3.11+",
        is_ok,
        f"Versão atual: {version_str}"
    )
    
    if not is_ok:
        print("⚠️  Recomendado: Python 3.11 ou superior")
    
    return is_ok


def check_dependencies():
    """Verifica dependências instaladas"""
    print_header("2. Verificando Dependências")
    
    dependencies = {
        "langchain": "langchain",
        "langgraph": "langgraph",
        "streamlit": "streamlit",
        "pydantic": "pydantic",
        "python-dotenv": "dotenv",
        "loguru": "loguru",
    }
    
    all_ok = True
    for name, import_name in dependencies.items():
        try:
            __import__(import_name)
            print_check(name, True)
        except ImportError:
            print_check(name, False, "Não instalado")
            all_ok = False
    
    if not all_ok:
        print("\n💡 Execute: pip install -r requirements.txt")
    
    return all_ok


def check_structure():
    """Verifica estrutura de diretórios"""
    print_header("3. Verificando Estrutura de Diretórios")
    
    required_paths = [
        "config/settings.py",
        "config/llm_config.py",
        "core/state.py",
        "core/graph.py",
        "core/nodes/classifier.py",
        "core/nodes/planner.py",
        "core/nodes/builder.py",
        "utils/llm_factory.py",
        "utils/logger.py",
        "prompts/classifier.py",
        "prompts/planner.py",
        "prompts/builder.py",
        "app.py",
        "requirements.txt",
    ]
    
    all_ok = True
    for path in required_paths:
        exists = Path(path).exists()
        if not exists:
            print_check(path, False, "Arquivo não encontrado")
            all_ok = False
    
    if all_ok:
        print_check("Estrutura de arquivos", True, f"{len(required_paths)} arquivos verificados")
    
    return all_ok


def check_env_file():
    """Verifica arquivo .env"""
    print_header("4. Verificando Configuração (.env)")
    
    env_exists = Path(".env").exists()
    print_check(".env existe", env_exists)
    
    if not env_exists:
        print("💡 Execute: cp .env.example .env")
        print("💡 Depois edite .env e adicione suas API keys")
        return False
    
    return True


def check_api_keys():
    """Verifica API keys configuradas"""
    print_header("5. Verificando API Keys")
    
    try:
        from config.settings import check_api_keys, validate_minimum_config
        
        keys_status = check_api_keys()
        
        any_configured = False
        for provider, configured in keys_status.items():
            if configured:
                print_check(provider, True)
                any_configured = True
        
        if not any_configured:
            print("\n❌ Nenhuma API key configurada!")
            print("💡 Edite o arquivo .env e adicione pelo menos 1 API key:")
            print("   - ANTHROPIC_API_KEY (Recomendado)")
            print("   - OPENAI_API_KEY")
            print("   - GOOGLE_API_KEY")
            return False
        
        # Validação mínima
        is_valid, missing = validate_minimum_config()
        
        if is_valid:
            print_check("Configuração mínima", True, "Pronto para usar!")
        else:
            print_check("Configuração mínima", False)
            for item in missing:
                print(f"   ⚠️  {item}")
        
        return is_valid
        
    except Exception as e:
        print_check("Verificação de API keys", False, str(e))
        return False


def check_imports():
    """Testa imports principais"""
    print_header("6. Testando Imports Principais")
    
    imports_to_test = [
        ("config.settings", "Configurações"),
        ("config.llm_config", "Modelos LLM"),
        ("core.state", "Estados"),
        ("core.graph", "Grafo"),
        ("utils.llm_factory", "LLM Factory"),
        ("utils.logger", "Logger"),
    ]
    
    all_ok = True
    for module, name in imports_to_test:
        try:
            __import__(module)
            print_check(name, True)
        except Exception as e:
            print_check(name, False, str(e))
            all_ok = False
    
    return all_ok


def test_llm_factory():
    """Testa criação de LLM"""
    print_header("7. Testando LLM Factory")
    
    try:
        from utils.llm_factory import validate_model
        from config.llm_config import get_recommended_models
        
        recommended = get_recommended_models()
        planner_model = recommended.get("planning")
        
        if planner_model:
            is_valid, error = validate_model(planner_model.name)
            
            if is_valid:
                print_check("LLM Factory", True, f"Testado com {planner_model.display_name}")
                return True
            else:
                print_check("LLM Factory", False, error)
                return False
        else:
            print_check("LLM Factory", False, "Nenhum modelo configurado")
            return False
            
    except Exception as e:
        print_check("LLM Factory", False, str(e))
        return False


def print_summary(results):
    """Imprime resumo dos resultados"""
    print_header("📊 RESUMO")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal de checks: {total}")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {total - passed}")
    
    percentage = (passed / total) * 100
    
    print(f"\n{'🎉' if percentage == 100 else '⚠️ '} {percentage:.0f}% dos checks passaram\n")
    
    if percentage == 100:
        print("✅ Tudo pronto! Execute: streamlit run app.py")
    elif percentage >= 80:
        print("⚠️  Quase lá! Corrija os itens marcados com ❌")
    else:
        print("❌ Várias configurações faltando. Revise o QUICKSTART.md")
    
    return percentage == 100


def main():
    """Executa todas as verificações"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║         🤖 AI AGENT FLOW - Verificação de Setup         ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    results = {}
    
    # Executar checks
    results["python_version"] = check_python_version()
    results["dependencies"] = check_dependencies()
    results["structure"] = check_structure()
    results["env_file"] = check_env_file()
    
    # Só verificar API keys se .env existe
    if results["env_file"]:
        results["api_keys"] = check_api_keys()
    else:
        results["api_keys"] = False
    
    results["imports"] = check_imports()
    
    # Só testar LLM Factory se tudo anterior passou
    if all([results["dependencies"], results["env_file"], results["imports"]]):
        results["llm_factory"] = test_llm_factory()
    else:
        results["llm_factory"] = False
    
    # Resumo
    all_ok = print_summary(results)
    
    # Exit code
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()