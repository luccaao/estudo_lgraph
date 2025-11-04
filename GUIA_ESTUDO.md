# 🤖 Estudo Completo: Agentes de IA com LangGraph

Um guia prático e progressivo para dominar a criação de agentes de IA usando LangGraph.

## 🎯 Objetivo

Este repositório foi criado para ensinar **de forma prática** como construir agentes de IA reais usando LangGraph. O foco está em **agentes**, não apenas em conceitos teóricos.

## 📚 Estrutura do Curso

### Parte 1: Fundamentos de Agentes
**Arquivo:** `01_introducao_basica.py`

- O que é um agente de IA
- Anatomia de um agente (observar, pensar, agir)
- Padrão ReAct (Reasoning + Acting)
- Estado e mensagens
- Primeiro agente funcional

### Parte 2: Agente Real com LLM
**Arquivo:** `02_agente_com_llm.py`

- Integração com LLM (OpenAI/Anthropic)
- Tool calling (ferramentas)
- Roteamento condicional
- Loop ReAct completo
- Agente que decide quais ferramentas usar

### Parte 3: Agente Conversacional
**Arquivo:** `03_agente_conversacional.py`

- Memória persistente com checkpoints
- Thread management (múltiplos usuários)
- Sistema de mensagens
- Contexto entre conversas
- Chatbot com memória

### Parte 4: Multi-Agentes
**Arquivo:** `04_multi_agentes.py`

- **Padrão Sequential:** Pipeline de agentes
- **Padrão Parallel:** Agentes trabalhando simultaneamente
- **Padrão Handoff:** Transferência entre especialistas
- Colaboração entre agentes

### Parte 5: Padrão Supervisor
**Arquivo:** `05_agente_supervisor.py`

- Supervisor que gerencia múltiplos agentes
- Delegação dinâmica de tarefas
- Orquestração inteligente
- Sistema escalável

### Parte 6: Human-in-the-Loop
**Arquivo:** `06_human_in_the_loop.py`

- Aprovação humana para ações críticas
- `interrupt_before` e `interrupt_after`
- Edição de planos pelo humano
- Modificação de estado durante pausa
- Supervisão humana essencial

### Parte 7: Casos Práticos Avançados
**Arquivo:** `07_casos_praticos.py`

- **RAG Agent:** Consulta base de conhecimento
- **Code Agent:** Escreve e executa código
- **Research Agent:** Pesquisa e sintetiza informações
- Implementações completas e prontas para uso

## 🚀 Como Usar

### 1. Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configuração

Crie um arquivo `.env` com suas credenciais:

```env
OPENAI_API_KEY=sua_chave_aqui
# ou
ANTHROPIC_API_KEY=sua_chave_aqui
```

### 3. Executar os Exemplos

Execute os arquivos na ordem:

```bash
# Parte 1 - Fundamentos
python 01_introducao_basica.py

# Parte 2 - Agente com LLM
python 02_agente_com_llm.py

# Parte 3 - Conversacional
python 03_agente_conversacional.py

# Parte 4 - Multi-Agentes
python 04_multi_agentes.py

# Parte 5 - Supervisor
python 05_agente_supervisor.py

# Parte 6 - Human-in-the-Loop
python 06_human_in_the_loop.py

# Parte 7 - Casos Práticos
python 07_casos_praticos.py
```

## 🎓 Progressão do Aprendizado

```
1. BÁSICO: Entender o que é um agente
   ↓
2. INTERMEDIÁRIO: Criar agente com LLM e ferramentas
   ↓
3. AVANÇADO: Memória, multi-agentes, supervisor
   ↓
4. PRODUÇÃO: Human-in-the-loop, casos práticos reais
```

## 🛠️ Tecnologias

- **LangGraph:** Framework para agentes stateful
- **LangChain:** Biblioteca para LLMs
- **OpenAI/Anthropic:** Modelos de linguagem
- **Python 3.10+**

## 📖 Conceitos-Chave Aprendidos

### ✅ Padrão ReAct
```
OBSERVE → THINK → ACT → (repeat if needed)
```

O agente:
1. Observa o input do usuário
2. Pensa sobre o que fazer
3. Age (usa ferramenta ou responde)
4. Repete se necessário

### ✅ State Management
Todo agente mantém um **estado** que flui pelo grafo:
- Mensagens (histórico)
- Variáveis de contexto
- Resultados de ferramentas

### ✅ Tool Calling
Agentes podem usar ferramentas:
```python
@tool
def calculadora(expressao: str) -> str:
    """Calcula expressões matemáticas"""
    return str(eval(expressao))
```

### ✅ Checkpoints e Memória
```python
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```

Permite:
- Pausar e retomar conversas
- Manter contexto entre sessões
- Múltiplos usuários isolados

### ✅ Conditional Edges
```python
workflow.add_conditional_edges(
    "agente",
    should_continue,  # Função que decide
    {
        "continue": "ferramentas",
        "end": END
    }
)
```

## 🎯 Casos de Uso Reais

Depois deste curso, você poderá construir:

1. **Assistentes Pessoais**
   - Agendar tarefas
   - Responder emails
   - Gerenciar calendário

2. **Sistemas de Suporte**
   - Classificação automática
   - Base de conhecimento (RAG)
   - Escalonamento inteligente

3. **Automação de Código**
   - Geração de código
   - Testes automatizados
   - Code review

4. **Pesquisa e Análise**
   - Research assistants
   - Análise de dados
   - Síntese de informações

5. **Workflows Complexos**
   - Aprovação de documentos
   - Análise de crédito
   - Processamento de pedidos

## 🔥 Recursos Adicionais

### Documentação Oficial
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangChain Docs](https://python.langchain.com/)

### Exemplos
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)

### Comunidade
- [Discord LangChain](https://discord.gg/langchain)

## 💡 Próximos Passos

Depois de completar este curso:

1. **Integre com Produção**
   - Use APIs reais
   - Adicione logging e monitoring
   - Implemente tratamento de erros

2. **Adicione Persistência**
   - PostgreSQL para checkpoints
   - Vector stores (Pinecone, Chroma)
   - Redis para cache

3. **Escale**
   - Deploy em cloud
   - Async para performance
   - Rate limiting

4. **Monitore**
   - LangSmith para tracing
   - Métricas de performance
   - Alertas

## ⭐ Projetos Sugeridos

Use o que aprendeu para construir:

1. **Assistente de Estudos**
   - RAG com seus documentos
   - Geração de quizzes
   - Resumos automáticos

2. **Agente de Email**
   - Classificação de emails
   - Respostas automáticas
   - Agendamento inteligente

3. **Sistema de Análise de Código**
   - Code review automatizado
   - Sugestões de melhorias
   - Detecção de bugs

4. **Research Assistant**
   - Busca em múltiplas fontes
   - Síntese de papers
   - Geração de relatórios

5. **Automation Bot**
   - Integração com APIs
   - Workflows complexos
   - Notificações inteligentes

---

## 🎉 Parabéns!

Se você chegou até aqui, agora você sabe como construir agentes de IA poderosos e práticos com LangGraph!

**Happy Coding! 🚀**
