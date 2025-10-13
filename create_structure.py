#!/usr/bin/env python3
"""
Script de Criação de Estrutura - AI Agent Flow

Este script cria automaticamente toda a estrutura de diretórios
e arquivos necessários para o projeto.

Uso:
    python create_structure.py
    
Ou com opções:
    python create_structure.py --with-placeholders  # Cria arquivos placeholder
    python create_structure.py --clean              # Remove estrutura existente
"""

import os
import sys
from pathlib import Path
import argparse


# Cores para output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Imprime cabeçalho colorido"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_info(text):
    """Imprime mensagem informativa"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def print_warning(text):
    """Imprime aviso"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_error(text):
    """Imprime erro"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


# Estrutura de diretórios do projeto
DIRECTORY_STRUCTURE = {
    "config": "Módulo de Configuração",
    "core": "Lógica Principal",
    "core/nodes": "Nós do Grafo LangGraph",
    "prompts": "Templates de Prompts",
    "utils": "Utilitários",
    "logs": "Arquivos de Log (gerados automaticamente)",
    ".streamlit": "Configurações do Streamlit",
}


# Arquivos que precisam ser criados
FILES_TO_CREATE = {
    # Arquivos __init__.py
    "config/__init__.py": "# Módulo de Configuração\n",
    "core/__init__.py": "# Módulo Core\n",
    "core/nodes/__init__.py": "# Nós do Grafo\n",
    "prompts/__init__.py": "# Prompts\n",
    "utils/__init__.py": "# Utilitários\n",
    
    # Arquivo .gitignore
    ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/*.log
logs/*.log.*

# Streamlit
.streamlit/secrets.toml

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Testing
.pytest_cache/
.coverage
htmlcov/
""",
    
    # README placeholder (será substituído pelo README completo)
    "README.md": "# AI Agent Flow\n\n*Este arquivo será substituído pelo README completo*\n",
}


# Arquivos placeholder opcionais
PLACEHOLDER_FILES = {
    "config/settings.py": '''"""
Configurações Gerais da Aplicação
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "config/llm_config.py": '''"""
Configuração de Modelos LLM
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "core/state.py": '''"""
Estados do LangGraph
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "core/graph.py": '''"""
Grafo Principal
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "core/nodes/classifier.py": '''"""
Nó Classificador
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "core/nodes/planner.py": '''"""
Nó Planejador
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "core/nodes/builder.py": '''"""
Nó Construtor
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "core/nodes/reviewer.py": '''"""
Nó Revisor
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "core/nodes/feedback.py": '''"""
Nó de Feedback
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "prompts/classifier.py": '''"""
Prompts do Classificador
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "prompts/planner.py": '''"""
Prompts do Planejador
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "prompts/builder.py": '''"""
Prompts do Construtor
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "utils/llm_factory.py": '''"""
Factory de LLMs
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "utils/logger.py": '''"""
Sistema de Logging
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "utils/validators.py": '''"""
Validadores
TODO: Substituir pelo conteúdo completo do artefato
"""
pass
''',
    "app.py": '''"""
Interface Streamlit Principal
TODO: Substituir pelo conteúdo completo do artefato
"""
import streamlit as st

st.title("🤖 AI Agent Flow")
st.warning("⚠️ Este é um placeholder. Substitua pelo app.py completo.")
''',
}


def create_directories(base_path: Path = Path(".")):
    """Cria a estrutura de diretórios"""
    print_header("Criando Estrutura de Diretórios")
    
    created = []
    existed = []
    
    for dir_path, description in DIRECTORY_STRUCTURE.items():
        full_path = base_path / dir_path
        
        if full_path.exists():
            print_info(f"{dir_path}/ (já existe)")
            existed.append(dir_path)
        else:
            full_path.mkdir(parents=True, exist_ok=True)
            print_success(f"{dir_path}/ - {description}")
            created.append(dir_path)
    
    return created, existed


def create_files(base_path: Path = Path("."), with_placeholders: bool = False):
    """Cria arquivos necessários"""
    print_header("Criando Arquivos Essenciais")
    
    created = []
    existed = []
    
    files_dict = FILES_TO_CREATE.copy()
    
    if with_placeholders:
        print_info("Modo placeholder ativado - criando arquivos placeholder")
        files_dict.update(PLACEHOLDER_FILES)
    
    for file_path, content in files_dict.items():
        full_path = base_path / file_path
        
        if full_path.exists():
            print_info(f"{file_path} (já existe)")
            existed.append(file_path)
        else:
            # Garantir que o diretório pai existe
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Criar arquivo
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print_success(f"{file_path}")
            created.append(file_path)
    
    return created, existed


def create_env_example(base_path: Path = Path(".")):
    """Cria arquivo .env.example se não existir"""
    print_header("Criando Arquivo de Configuração")
    
    env_example = base_path / ".env.example"
    
    if env_example.exists():
        print_info(".env.example já existe")
        return False
    
    env_content = """# ========================================
# AI AGENT FLOW - Environment Variables
# ========================================

# Anthropic (Claude) - Recomendado
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI (GPT)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google (Gemini)
GOOGLE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# DeepSeek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# xAI (Grok)
XAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Alibaba Cloud (Qwen)
QWEN_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Configurações
LOG_LEVEL=INFO
DEFAULT_TIMEOUT=300
OLLAMA_BASE_URL=http://localhost:11434
"""
    
    with open(env_example, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print_success(".env.example criado")
    
    # Sugerir copiar para .env
    if not (base_path / ".env").exists():
        print_warning("Não esqueça de: cp .env.example .env")
    
    return True


def create_requirements_txt(base_path: Path = Path(".")):
    """Cria requirements.txt se não existir"""
    req_file = base_path / "requirements.txt"
    
    if req_file.exists():
        print_info("requirements.txt já existe")
        return False
    
    print_header("Criando requirements.txt")
    
    requirements = """# Core Framework - LangGraph 1.0
langgraph==0.6.10
langchain==0.3.9
langchain-core==0.3.19
langchain-community==0.3.8

# LLM Providers
langchain-anthropic==0.3.3
langchain-openai==0.2.9
langchain-google-genai==2.0.5
langchain-ollama==0.2.0

# Interface Web
streamlit==1.39.0
streamlit-aggrid==1.0.5

# Utilidades
python-dotenv==1.0.1
pydantic==2.9.2
pydantic-settings==2.5.2

# Logging
loguru==0.7.2

# Data Handling
pandas==2.2.3
numpy==2.1.2

# HTTP
httpx==0.27.2
requests==2.32.3
"""
    
    with open(req_file, 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print_success("requirements.txt criado")
    return True


def clean_structure(base_path: Path = Path(".")):
    """Remove a estrutura criada (use com cuidado!)"""
    print_header("⚠️  LIMPANDO ESTRUTURA EXISTENTE")
    print_warning("Esta operação removerá diretórios e arquivos!")
    
    response = input("Tem certeza? Digite 'CONFIRMAR' para continuar: ")
    
    if response != "CONFIRMAR":
        print_info("Operação cancelada")
        return
    
    import shutil
    
    removed = []
    
    # Remover diretórios
    for dir_path in DIRECTORY_STRUCTURE.keys():
        full_path = base_path / dir_path
        if full_path.exists() and full_path.name != "logs":  # Preservar logs
            try:
                shutil.rmtree(full_path)
                print_success(f"Removido: {dir_path}/")
                removed.append(dir_path)
            except Exception as e:
                print_error(f"Erro ao remover {dir_path}: {e}")
    
    # Remover arquivos
    files_to_remove = [
        ".gitignore",
        "README.md",
        ".env.example",
        "requirements.txt",
    ]
    
    for file_path in files_to_remove:
        full_path = base_path / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print_success(f"Removido: {file_path}")
                removed.append(file_path)
            except Exception as e:
                print_error(f"Erro ao remover {file_path}: {e}")
    
    print_info(f"Total removido: {len(removed)} itens")


def print_next_steps(with_placeholders: bool = False):
    """Imprime próximos passos"""
    print_header("🎯 Próximos Passos")
    
    if with_placeholders:
        print("""
1. ✅ Estrutura criada com arquivos placeholder
   
2. 📝 Substitua cada arquivo placeholder pelo conteúdo dos artefatos:
   - Copie o conteúdo de cada artefato para o arquivo correspondente
   - Os arquivos estão marcados com "TODO: Substituir pelo conteúdo completo"

3. ⚙️  Configure suas API keys:
   cp .env.example .env
   nano .env  # Adicione suas API keys

4. 📦 Instale as dependências:
   pip install -r requirements.txt

5. ✅ Verifique a instalação:
   python check_setup.py

6. 🚀 Execute a aplicação:
   streamlit run app.py
""")
    else:
        print("""
1. ✅ Estrutura de diretórios criada

2. 📝 Copie o conteúdo de cada artefato para os arquivos:
   
   Configuração:
   - config/settings.py
   - config/llm_config.py
   
   Core:
   - core/state.py
   - core/graph.py
   
   Nós:
   - core/nodes/classifier.py
   - core/nodes/planner.py
   - core/nodes/builder.py
   - core/nodes/reviewer.py
   - core/nodes/feedback.py
   
   Prompts:
   - prompts/classifier.py
   - prompts/planner.py
   - prompts/builder.py
   
   Utils:
   - utils/llm_factory.py
   - utils/logger.py
   - utils/validators.py
   
   Interface:
   - app.py
   
   Docs:
   - README.md
   - QUICKSTART.md
   - check_setup.py
   - .streamlit/config.toml

3. ⚙️  Configure suas API keys:
   cp .env.example .env
   nano .env  # Adicione suas API keys

4. 📦 Instale as dependências:
   pip install -r requirements.txt

5. ✅ Verifique a instalação:
   python check_setup.py

6. 🚀 Execute a aplicação:
   streamlit run app.py
""")
    
    print(f"{Colors.BOLD}{Colors.GREEN}✨ Boa sorte com seu projeto!{Colors.END}\n")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Cria estrutura de diretórios do AI Agent Flow"
    )
    parser.add_argument(
        "--with-placeholders",
        action="store_true",
        help="Cria arquivos Python com placeholders TODO"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove estrutura existente (use com cuidado!)"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Caminho base para criar a estrutura (padrão: diretório atual)"
    )
    
    args = parser.parse_args()
    
    base_path = Path(args.path)
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║    🏗️  AI AGENT FLOW - Criação de Estrutura             ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    print_info(f"Diretório base: {base_path.absolute()}")
    
    # Modo de limpeza
    if args.clean:
        clean_structure(base_path)
        return
    
    # Criar estrutura
    dirs_created, dirs_existed = create_directories(base_path)
    files_created, files_existed = create_files(base_path, args.with_placeholders)
    
    create_env_example(base_path)
    create_requirements_txt(base_path)
    
    # Resumo
    print_header("📊 Resumo")
    print(f"Diretórios criados: {Colors.GREEN}{len(dirs_created)}{Colors.END}")
    print(f"Diretórios já existentes: {Colors.YELLOW}{len(dirs_existed)}{Colors.END}")
    print(f"Arquivos criados: {Colors.GREEN}{len(files_created)}{Colors.END}")
    print(f"Arquivos já existentes: {Colors.YELLOW}{len(files_existed)}{Colors.END}")
    
    if args.with_placeholders:
        print(f"\n{Colors.BOLD}Modo: {Colors.BLUE}COM PLACEHOLDERS{Colors.END}")
    else:
        print(f"\n{Colors.BOLD}Modo: {Colors.BLUE}APENAS ESTRUTURA{Colors.END}")
    
    # Próximos passos
    print_next_steps(args.with_placeholders)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Operação cancelada pelo usuário{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Erro: {e}{Colors.END}\n")
        sys.exit(1)