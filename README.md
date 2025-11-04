# Estudo Guiado: LangGraph

Bem-vindo ao estudo guiado completo de **LangGraph**! Este tutorial progressivo vai desde os conceitos básicos até implementações avançadas.

## 📚 Estrutura do Curso

### Parte 1: Fundamentos
- **[01_introducao_basica.py](01_introducao_basica.py)** - Introdução aos conceitos básicos
  - Estados (State)
  - Nós (Nodes)
  - Arestas (Edges)
  - Primeiro grafo linear

### Parte 2: Controle de Fluxo
- **[02_condicionais_e_branches.py](02_condicionais_e_branches.py)** - Ramificações condicionais
  - Arestas condicionais
  - Roteamento baseado em estado
  - Múltiplos caminhos de execução

### Parte 3: Iteração
- **[03_loops_e_recursao.py](03_loops_e_recursao.py)** - Loops e recursão
  - Criando ciclos no grafo
  - Condições de parada
  - Padrão retry/tentativas
  - Processamento iterativo

### Parte 4: Integração com IA
- **[04_integracao_llm.py](04_integracao_llm.py)** - Integração com LLMs
  - Conectando com modelos de linguagem
  - Agentes conversacionais
  - Tool calling (chamada de ferramentas)
  - Agentes com capacidades específicas

### Parte 5: Persistência
- **[05_persistencia_memoria.py](05_persistencia_memoria.py)** - Memória e persistência
  - Salvando estado entre execuções
  - MemorySaver e Checkpointers
  - Versionamento de estado
  - Histórico e rollback

### Parte 6: Padrões Avançados
- **[06_agentes_avancados.py](06_agentes_avancados.py)** - Padrões de design avançados
  - Supervisor (orquestrador de agentes)
  - Reflexão (auto-crítica)
  - Human-in-the-Loop
  - Multi-agente colaborativo

### Parte 7: Aplicações Práticas
- **[07_casos_praticos.py](07_casos_praticos.py)** - Casos de uso reais
  - Assistente de atendimento ao cliente
  - Sistema de aprovação de crédito
  - Processador de documentos

## 🚀 Como Usar Este Guia

### Pré-requisitos

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Ativar ambiente (Linux/Mac)
source venv/bin/activate

# Instalar dependências básicas
pip install langgraph langchain
```

### Executando os Exemplos

Cada arquivo é independente e pode ser executado diretamente:

```bash
python 01_introducao_basica.py
python 02_condicionais_e_branches.py
# ... e assim por diante
```

### Ordem Recomendada

1. **Iniciantes**: Siga a ordem numérica (01 → 07)
2. **Intermediários**: Comece do 03 ou 04
3. **Avançados**: Vá direto para 06 e 07

## 📖 Conceitos-Chave

### O que é LangGraph?

LangGraph é uma biblioteca para construir aplicações **stateful** e **multi-agente** usando grafos. Principais características:

- ✅ Suporta **ciclos** (ao contrário do LangChain tradicional)
- ✅ **Persistência** de estado entre execuções
- ✅ **Checkpointing** para pausar e retomar
- ✅ **Human-in-the-Loop** para aprovações
- ✅ **Streaming** de resultados intermediários

### Anatomia de um Grafo

```python
from langgraph.graph import StateGraph, END

# 1. Definir o Estado
class MeuEstado(TypedDict):
    dado: str

# 2. Criar Nós (funções)
def meu_no(estado: MeuEstado) -> MeuEstado:
    return {"dado": "processado"}

# 3. Construir o Grafo
workflow = StateGraph(MeuEstado)
workflow.add_node("processar", meu_no)
workflow.set_entry_point("processar")
workflow.add_edge("processar", END)

# 4. Compilar e Executar
app = workflow.compile()
resultado = app.invoke({"dado": "inicial"})
```

## 🎯 Casos de Uso

### Quando Usar LangGraph?

- ✅ Agentes que precisam de **múltiplas etapas** de raciocínio
- ✅ Workflows que exigem **loops** ou **tentativas**
- ✅ Sistemas com **aprovação humana**
- ✅ Processos que precisam ser **pausados e retomados**
- ✅ **Multi-agente** colaborativo (supervisor + especialistas)

### Quando NÃO Usar?

- ❌ Tarefas simples e lineares (use LangChain direto)
- ❌ Quando não precisa de estado/memória
- ❌ Chamadas únicas a LLM sem contexto

## 🔧 Configuração para Produção

### Integração com LLMs Reais

```python
# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4", api_key="sua-chave")

# Anthropic (Claude)
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-sonnet-20240229", api_key="sua-chave")

# Outros provedores
from langchain_community.llms import Ollama
llm = Ollama(model="llama2")
```

### Persistência com SQLite

```python
from langgraph.checkpoint.sqlite import SqliteSaver

memory = SqliteSaver.from_conn_string("checkpoints.db")
app = workflow.compile(checkpointer=memory)
```

### Configuração de Threads

```python
# Cada usuário tem seu próprio thread
config = {"configurable": {"thread_id": f"user_{user_id}"}}
resultado = app.invoke(estado_inicial, config)
```

## 📊 Padrões Comuns

### 1. Linear (Pipeline)
```
[A] → [B] → [C] → [END]
```

### 2. Condicional (Branch)
```
      ┌→ [B] →┐
[A] →→┤       ├→ [D] → [END]
      └→ [C] →┘
```

### 3. Loop (Ciclo)
```
[A] → [B] → [Decisão]
       ↑         ↓
       └─────────┘ (continuar)
              ↓
           [END] (parar)
```

### 4. Supervisor
```
          ┌→ [Agente1] →┐
[Supervisor] → [Agente2] → [Supervisor]
          └→ [Agente3] →┘
```

## 🎓 Exercícios Práticos

Ao final de cada módulo, há exercícios sugeridos. Tente implementá-los para fixar o aprendizado!

### Projeto Final Sugerido

Combine tudo que aprendeu para criar um **Assistente Pessoal Completo**:

1. Classifica intenção do usuário
2. Usa ferramentas (calculadora, busca, etc.)
3. Mantém contexto da conversa
4. Pede aprovação para ações sensíveis
5. Auto-reflete e melhora respostas
6. Persiste histórico

## 🐛 Troubleshooting

### Erro: "Ciclo infinito detectado"
- Verifique se há condição de parada no loop
- Adicione contador de iterações máximas

### Erro: "Estado não encontrado"
- Certifique-se de usar o mesmo `thread_id`
- Verifique se o checkpointer está configurado

### Performance lenta
- Use modelo menor (haiku vs opus)
- Reduza contexto enviado ao LLM
- Paraleliza nós independentes

## 📚 Recursos Adicionais

- [Documentação Oficial LangGraph](https://python.langchain.com/docs/langgraph)
- [LangChain Documentation](https://python.langchain.com/)
- [Exemplos no GitHub](https://github.com/langchain-ai/langgraph/tree/main/examples)

## 🤝 Contribuindo

Encontrou um erro? Tem uma sugestão de melhoria?
- Abra uma issue
- Envie um pull request
- Compartilhe seus próprios exemplos!

## 📝 Licença

Este guia é disponibilizado gratuitamente para fins educacionais.

---

## 🎉 Próximos Passos

Após completar este guia:

1. ✅ Experimente integrar com LLMs reais
2. ✅ Implemente seus próprios casos de uso
3. ✅ Explore padrões avançados (RAG + LangGraph, etc.)
4. ✅ Compartilhe o que aprendeu com a comunidade!

**Bons estudos e divirta-se construindo com LangGraph!** 🚀
