# ⚡ Quick Start - AI Agent Flow

Comece em **5 minutos** com este guia rápido!

---

## 🚀 Setup Rápido

### 1. Clone e Instale (2 min)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/ai-agent-flow.git
cd ai-agent-flow

# Crie ambiente virtual
python -m venv venv

# Ative (Windows)
venv\Scripts\activate
# OU (Linux/Mac)
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

### 2. Configure API Key (1 min)

```bash
# Crie arquivo .env
cp .env.example .env
```

Edite `.env` e adicione pelo menos 1 API key:

```env
# Recomendado: Claude (melhor para código)
ANTHROPIC_API_KEY=sk-ant-seu-token-aqui

# OU OpenAI (mais barato)
OPENAI_API_KEY=sk-seu-token-aqui

# OU Google (maior context window)
GOOGLE_API_KEY=seu-token-aqui
```

**Como conseguir API Keys:**
- **Claude**: https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/api-keys
- **Google**: https://makersuite.google.com/app/apikey

### 3. Execute! (30 seg)

```bash
streamlit run app.py
```

✅ Pronto! A aplicação abrirá em `http://localhost:8501`

---

## 🎯 Primeiro Uso

### Passo 1: Configure os Modelos

Na **sidebar** (esquerda):
1. Verifique se suas API keys estão ✅
2. Selecione modelos para cada função

**Configuração Recomendada (Qualidade):**
```
Classificador: Claude Sonnet 4.5
Planejador:    Claude Sonnet 4.5
Construtor:    Claude Sonnet 4.5
Revisor:       Claude Opus 4.1
```

**Configuração Econômica:**
```
Classificador: GPT-4o-mini
Planejador:    Claude Sonnet 4.5
Construtor:    Claude Sonnet 4.5
Revisor:       GPT-5
```

### Passo 2: Descreva sua Demanda

Na aba **"📝 Input da Demanda"**, cole este exemplo:

```
Preciso de um sistema simples de gerenciamento de tarefas (To-Do List) 
em Python com Streamlit. Deve permitir:
- Adicionar tarefas com título e descrição
- Marcar como concluída
- Filtrar por status (todas, pendentes, concluídas)
- Persistir dados em arquivo JSON

Interface deve ser limpa e fácil de usar.
```

### Passo 3: Inicie o Processamento

1. Clique em **"🚀 Iniciar Processamento"**
2. Vá para aba **"⚙️ Execução"**
3. Clique em **"▶️ Executar Próximo Passo"** várias vezes

O sistema vai:
- ✅ Classificar sua demanda
- ✅ Extrair requisitos
- ✅ Criar um plano detalhado

### Passo 4: Aprove o Plano

Quando pausar:
1. Vá para aba **"📋 Planejamento"**
2. Revise o plano gerado
3. Clique em **"✅ Aprovar e Prosseguir"**

### Passo 5: Aguarde a Construção

Volte para **"⚙️ Execução"** e continue clicando **"▶️ Executar"**

O sistema vai:
- 🔨 Construir o código
- 👀 Fazer code review
- ✅ Validar a solução

### Passo 6: Baixe os Resultados!

Na aba **"📦 Resultados"**:
- Veja todos os arquivos gerados
- Faça download de cada um
- Leia a documentação

🎉 **Parabéns!** Você criou sua primeira solução com AI Agent Flow!

---

## 💡 Dicas Rápidas

### ✨ Para Melhores Resultados

**1. Seja Específico na Demanda**
❌ Ruim: "Quero um sistema de vendas"
✅ Bom: "Sistema de vendas com cadastro de produtos, carrinho de compras, checkout e relatório de vendas diárias em Streamlit"

**2. Mencione Tecnologias**
✅ "...usando FastAPI e PostgreSQL"
✅ "...pipeline PySpark no Databricks"
✅ "...interface React com TypeScript"

**3. Defina Outputs Esperados**
✅ "A saída deve ser um relatório PDF com gráficos"
✅ "Preciso de uma API REST com documentação Swagger"

### 🎛️ Ajustando Qualidade vs Velocidade

**Para Velocidade:**
```
Temperature: 0.3 (mais determinístico)
Modelos: GPT-4o-mini, Gemini Flash
```

**Para Qualidade Máxima:**
```
Temperature: 0.7 (mais criativo)
Modelos: Claude Opus 4.1, GPT-5
```

### 💰 Controlando Custos

**Custos Aproximados por Execução Completa:**

| Configuração | Custo Estimado |
|-------------|----------------|
| GPT-4o-mini everywhere | $0.01 - $0.05 |
| Claude Sonnet 4.5 | $0.10 - $0.30 |
| Claude Opus 4.1 | $0.50 - $1.50 |
| Mix (recomendado) | $0.15 - $0.50 |

**Dica:** Use modelos mais baratos no Classificador e Revisor, e reserve os melhores para Planejador e Construtor.

---

## 🐛 Problemas Comuns

### "Nenhum provider disponível"
➡️ Adicione pelo menos 1 API key no `.env`

### "Timeout Error"
➡️ Aumente `DEFAULT_TIMEOUT=600` no `.env`

### "Model not found"
➡️ Verifique se a API key está correta e ativa

### Execução trava no checkpoint
➡️ Vá para aba "Planejamento" e aprove/ajuste o plano

### Código gerado com erros
➡️ Use Claude Sonnet 4.5 no Construtor (melhor para código)

---

## 📚 Próximos Passos

Agora que você já usou o básico, explore:

1. **Teste diferentes tipos de demandas:**
   - 📊 Análise de dados
   - 💻 Aplicação web completa
   - 🔄 Pipeline de processamento

2. **Experimente diferentes modelos:**
   - Compare Claude vs GPT vs Gemini
   - Teste modelos locais com Ollama

3. **Customize o fluxo:**
   - Ajuste prompts em `prompts/`
   - Modifique nós em `core/nodes/`
   - Adicione validações customizadas

4. **Explore os logs:**
   - Veja na aba "Logs" o que acontece
   - Exporte logs para análise
   - Identifique oportunidades de melhoria

---

## 🎓 Exemplos Prontos

### Análise de Dados
```
Análise exploratória da base Titanic do Kaggle. Preciso de:
- Estatísticas descritivas
- Gráficos de distribuição (idade, classe, sobreviventes)
- Análise de correlação entre variáveis
- Insights sobre fatores de sobrevivência
Tudo em Python com Pandas e Plotly.
```

### API REST
```
API REST em FastAPI para gerenciamento de biblioteca. Endpoints para:
- CRUD de livros (título, autor, ISBN, ano)
- CRUD de usuários
- Sistema de empréstimos
- Consulta de disponibilidade
Com autenticação JWT e documentação Swagger.
```

### Dashboard
```
Dashboard em Streamlit para análise de vendas. Deve ter:
- Upload de CSV com dados de vendas
- Filtros por período, produto, região
- Gráficos: vendas no tempo, top produtos, mapa de vendas
- KPIs: total vendas, ticket médio, conversão
- Export de relatório em PDF
```

---

## 🆘 Precisa de Ajuda?

- 📖 Leia o [README.md](README.md) completo
- 🐛 Reporte bugs no [GitHub Issues](https://github.com/seu-usuario/ai-agent-flow/issues)
- 💬 Participe das [Discussões](https://github.com/seu-usuario/ai-agent-flow/discussions)
- 📧 Email: seu-email@example.com

---

## ⭐ Gostou?

Se este projeto foi útil, considere:
- ⭐ Dar uma estrela no GitHub
- 🐦 Compartilhar nas redes sociais
- 🤝 Contribuir com melhorias

---

<div align="center">
  <p><strong>Pronto para criar soluções incríveis com IA! 🚀</strong></p>
  <p>Volte para o <a href="README.md">README</a> para documentação completa</p>
</div>