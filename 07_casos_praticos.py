"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 7
Casos Práticos Avançados: Agentes de IA Reais
===========================================

Implementações completas e práticas de agentes de IA que você pode usar:

1. RAG Agent: Agente que consulta base de conhecimento
2. Code Agent: Agente que escreve e executa código
3. Research Agent: Agente que pesquisa na web
4. Data Analysis Agent: Agente que analisa dados
"""

import os
from typing import TypedDict, Annotated, Sequence, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import operator


# ===================================================================
# CASO 1: RAG AGENT - AGENTE COM BASE DE CONHECIMENTO
# ===================================================================
print("\n" + "="*70)
print("CASO 1: RAG Agent - Consulta Base de Conhecimento")
print("="*70)
print("""
RAG = Retrieval Augmented Generation

O agente:
1. Recebe uma pergunta
2. Busca informações relevantes na base de conhecimento
3. Usa LLM para responder com base nos documentos encontrados
""")


# Simular base de conhecimento
BASE_CONHECIMENTO = {
    "produtos": [
        {"id": 1, "nome": "Plano Basic", "preco": 29.90, "features": "5GB storage, suporte email"},
        {"id": 2, "nome": "Plano Pro", "preco": 79.90, "features": "50GB storage, suporte 24/7, API access"},
        {"id": 3, "nome": "Plano Enterprise", "preco": 199.90, "features": "Ilimitado, suporte dedicado, SLA"},
    ],
    "politicas": {
        "cancelamento": "Pode cancelar a qualquer momento. Reembolso proporcional até 7 dias.",
        "upgrade": "Upgrade imediato com cobrança proporcional.",
        "suporte": "Basic: email. Pro: email + chat. Enterprise: telefone dedicado."
    },
    "documentacao": {
        "api": "Nossa API REST usa OAuth2. Endpoint base: api.empresa.com/v1",
        "integracao": "Suportamos Zapier, Slack, Microsoft Teams",
        "seguranca": "Certificação ISO 27001, LGPD compliant, criptografia end-to-end"
    }
}


class EstadoRAG(TypedDict):
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    documentos_relevantes: List[str]
    resposta_final: str


@tool
def buscar_documentos(query: str, categoria: str = "all") -> str:
    """
    Busca documentos relevantes na base de conhecimento.

    Args:
        query: Termo de busca
        categoria: produtos, politicas, documentacao, ou all
    """
    print(f"\n🔍 [RETRIEVAL] Buscando: '{query}' em categoria '{categoria}'")

    resultados = []

    query_lower = query.lower()

    # Buscar em produtos
    if categoria in ["produtos", "all"]:
        for prod in BASE_CONHECIMENTO["produtos"]:
            if (query_lower in prod["nome"].lower() or
                query_lower in prod["features"].lower() or
                any(term in prod["nome"].lower() for term in ["plano", "preço", "features"] if term in query_lower)):
                resultados.append(f"Produto: {prod['nome']} - R${prod['preco']} - {prod['features']}")

    # Buscar em políticas
    if categoria in ["politicas", "all"]:
        for key, value in BASE_CONHECIMENTO["politicas"].items():
            if query_lower in key or query_lower in value.lower():
                resultados.append(f"Política de {key}: {value}")

    # Buscar em documentação
    if categoria in ["documentacao", "all"]:
        for key, value in BASE_CONHECIMENTO["documentacao"].items():
            if query_lower in key or query_lower in value.lower():
                resultados.append(f"Doc {key}: {value}")

    if not resultados:
        resultados.append("Nenhum documento relevante encontrado.")

    print(f"   📄 Encontrados {len(resultados)} documentos")

    return "\n".join(resultados)


ferramentas_rag = [buscar_documentos]


def agente_rag(estado: EstadoRAG):
    """
    Agente RAG que decide buscar documentos e responder.
    """
    print("\n🤖 [RAG AGENT] Processando query...")

    if not os.getenv("OPENAI_API_KEY"):
        # Versão sem LLM
        query = estado["mensagens"][-1].content
        docs = buscar_documentos.invoke({"query": query, "categoria": "all"})

        resposta = f"Baseado na documentação:\n{docs}"

        return {
            "documentos_relevantes": [docs],
            "resposta_final": resposta,
            "mensagens": [AIMessage(content=resposta)]
        }

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_com_tools = llm.bind_tools(ferramentas_rag)

    system_prompt = SystemMessage(content="""
Você é um assistente de suporte especializado.

Use a ferramenta buscar_documentos para encontrar informações relevantes
na base de conhecimento antes de responder.

Sempre base suas respostas nos documentos encontrados.
Se não encontrar informação, diga que não tem essa informação.
""")

    mensagens = [system_prompt] + list(estado["mensagens"])
    resposta = llm_com_tools.invoke(mensagens)

    return {"mensagens": [resposta]}


def executar_ferramentas_rag(estado: EstadoRAG):
    """Executa ferramentas de busca"""
    print("\n⚡ [EXECUTING TOOLS]")

    from langchain_core.messages import ToolMessage

    ultima_msg = estado["mensagens"][-1]
    resultados = []

    for tool_call in ultima_msg.tool_calls:
        ferramenta = ferramentas_rag[0]  # buscar_documentos
        resultado = ferramenta.invoke(tool_call["args"])

        resultados.append(
            ToolMessage(content=str(resultado), tool_call_id=tool_call["id"])
        )

    return {"mensagens": resultados, "documentos_relevantes": [str(r.content) for r in resultados]}


def should_continue_rag(estado: EstadoRAG) -> str:
    """Router para RAG agent"""
    ultima_msg = estado["mensagens"][-1]

    if hasattr(ultima_msg, "tool_calls") and ultima_msg.tool_calls:
        return "ferramentas"
    return "fim"


def criar_rag_agent():
    """Cria RAG Agent completo"""

    workflow = StateGraph(EstadoRAG)

    workflow.add_node("agente", agente_rag)
    workflow.add_node("ferramentas", executar_ferramentas_rag)

    workflow.set_entry_point("agente")

    workflow.add_conditional_edges(
        "agente",
        should_continue_rag,
        {"ferramentas": "ferramentas", "fim": END}
    )

    workflow.add_edge("ferramentas", "agente")

    return workflow.compile()


# Testar RAG Agent
if __name__ == "__main__" and os.getenv("OPENAI_API_KEY"):
    print("\n🧪 Testando RAG Agent...")

    rag_agent = criar_rag_agent()

    perguntas = [
        "Quais são os planos disponíveis e preços?",
        "Como funciona o cancelamento?",
        "Vocês têm API disponível?",
    ]

    for pergunta in perguntas:
        print(f"\n{'='*70}")
        print(f"❓ Pergunta: {pergunta}")
        print(f"{'='*70}")

        resultado = rag_agent.invoke({
            "mensagens": [HumanMessage(content=pergunta)],
            "query": pergunta,
            "documentos_relevantes": [],
            "resposta_final": ""
        })

        print(f"\n💬 Resposta:")
        print(resultado["mensagens"][-1].content)


# ===================================================================
# CASO 2: CODE AGENT - AGENTE QUE ESCREVE E EXECUTA CÓDIGO
# ===================================================================
print("\n\n" + "="*70)
print("CASO 2: Code Agent - Escreve e Executa Código")
print("="*70)


class EstadoCodeAgent(TypedDict):
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    codigo_gerado: str
    resultado_execucao: str
    erro: str


@tool
def executar_python(codigo: str) -> str:
    """
    Executa código Python de forma segura (sandbox).

    Args:
        codigo: Código Python para executar
    """
    print(f"\n💻 [EXEC] Executando código Python...")

    try:
        # ATENÇÃO: Em produção, use sandbox adequado (docker, pyodide, etc)
        # Aqui é apenas demonstração - NUNCA use eval/exec em produção assim!

        import io
        from contextlib import redirect_stdout

        # Capturar output
        f = io.StringIO()
        with redirect_stdout(f):
            # Ambiente restrito
            ambiente = {"__builtins__": __builtins__}
            exec(codigo, ambiente)

        output = f.getvalue()

        print(f"   ✅ Executado com sucesso")
        print(f"   📤 Output: {output[:100]}...")

        return f"Executado com sucesso.\nOutput:\n{output}"

    except Exception as e:
        erro = f"Erro na execução: {str(e)}"
        print(f"   ❌ {erro}")
        return erro


ferramentas_code = [executar_python]


def agente_programador(estado: EstadoCodeAgent):
    """
    Agente que escreve e executa código.
    """
    print("\n👨‍💻 [CODE AGENT] Analisando tarefa...")

    if not os.getenv("OPENAI_API_KEY"):
        # Versão simplificada
        tarefa = estado["mensagens"][-1].content

        if "fibonacci" in tarefa.lower():
            codigo = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")
"""
        else:
            codigo = """
# Código de exemplo
print("Hello from Code Agent!")
"""

        return {
            "codigo_gerado": codigo,
            "mensagens": [AIMessage(content=f"Código gerado:\n```python\n{codigo}\n```")]
        }

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_com_tools = llm.bind_tools(ferramentas_code)

    system_prompt = SystemMessage(content="""
Você é um programador especialista em Python.

Quando receber uma tarefa:
1. Escreva código Python limpo e funcional
2. Use a ferramenta executar_python para testar o código
3. Se houver erro, corrija e tente novamente
4. Explique o código para o usuário

Sempre teste o código antes de apresentar ao usuário!
""")

    mensagens = [system_prompt] + list(estado["mensagens"])
    resposta = llm_com_tools.invoke(mensagens)

    return {"mensagens": [resposta]}


def executar_ferramentas_code(estado: EstadoCodeAgent):
    """Executa código"""
    print("\n⚡ [EXECUTING CODE]")

    from langchain_core.messages import ToolMessage

    ultima_msg = estado["mensagens"][-1]
    resultados = []

    for tool_call in ultima_msg.tool_calls:
        resultado = executar_python.invoke(tool_call["args"])

        resultados.append(
            ToolMessage(content=str(resultado), tool_call_id=tool_call["id"])
        )

    return {"mensagens": resultados}


def should_continue_code(estado: EstadoCodeAgent) -> str:
    """Router para code agent"""
    ultima_msg = estado["mensagens"][-1]

    if hasattr(ultima_msg, "tool_calls") and ultima_msg.tool_calls:
        return "executar"
    return "fim"


def criar_code_agent():
    """Cria Code Agent completo"""

    workflow = StateGraph(EstadoCodeAgent)

    workflow.add_node("programador", agente_programador)
    workflow.add_node("executar", executar_ferramentas_code)

    workflow.set_entry_point("programador")

    workflow.add_conditional_edges(
        "programador",
        should_continue_code,
        {"executar": "executar", "fim": END}
    )

    workflow.add_edge("executar", "programador")

    return workflow.compile()


# Testar Code Agent
print("\n🧪 Testando Code Agent...")

code_agent = criar_code_agent()

tarefas = [
    "Escreva uma função que calcula fatorial",
    "Crie um código que imprime números primos até 20",
]

for tarefa in tarefas:
    print(f"\n{'='*70}")
    print(f"🎯 Tarefa: {tarefa}")
    print(f"{'='*70}")

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Executando em modo simulado (sem LLM)")

    resultado = code_agent.invoke({
        "mensagens": [HumanMessage(content=tarefa)],
        "codigo_gerado": "",
        "resultado_execucao": "",
        "erro": ""
    })

    print(f"\n📝 Resultado:")
    print(resultado["mensagens"][-1].content[:200] + "...")


# ===================================================================
# CASO 3: RESEARCH AGENT - PESQUISA NA WEB
# ===================================================================
print("\n\n" + "="*70)
print("CASO 3: Research Agent - Pesquisa e Sintetiza Informações")
print("="*70)


class EstadoResearch(TypedDict):
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    query_original: str
    queries_geradas: List[str]
    resultados_busca: List[str]
    sintese_final: str


@tool
def buscar_web(query: str) -> str:
    """
    Busca informações na web (simulado).

    Args:
        query: Termo de busca
    """
    print(f"\n🌐 [WEB SEARCH] Buscando: '{query}'")

    # Simular resultados de busca
    # Em produção, usaria API real (Google, Bing, Tavily, etc)

    resultados_simulados = {
        "langgraph": """
LangGraph é uma biblioteca da LangChain para criar aplicações stateful com LLMs.
Permite construir agentes complexos usando grafos direcionados.
Principais features: checkpoints, human-in-the-loop, multi-agentes.
""",
        "agentes ia": """
Agentes de IA são sistemas autônomos que usam LLMs para raciocinar e agir.
Padrão comum: ReAct (Reasoning + Acting).
Podem usar ferramentas e manter memória de longo prazo.
""",
        "default": f"Resultados de busca para '{query}' [simulado]"
    }

    for key in resultados_simulados:
        if key in query.lower():
            resultado = resultados_simulados[key]
            break
    else:
        resultado = resultados_simulados["default"]

    print(f"   📄 Resultados encontrados")
    return resultado


ferramentas_research = [buscar_web]


def criar_research_agent():
    """
    Agente de pesquisa que:
    1. Gera múltiplas queries de busca
    2. Busca em cada uma
    3. Sintetiza os resultados
    """

    workflow = StateGraph(EstadoResearch)

    def gerar_queries(estado: EstadoResearch):
        """Gera múltiplas queries para pesquisa"""
        print("\n🧠 [RESEARCH] Gerando queries de pesquisa...")

        query_original = estado["mensagens"][-1].content

        # Simples: gerar variações
        queries = [
            query_original,
            f"{query_original} definição",
            f"{query_original} exemplos práticos",
        ]

        print(f"   📝 Geradas {len(queries)} queries")
        for q in queries:
            print(f"      - {q}")

        return {"queries_geradas": queries, "query_original": query_original}

    def executar_buscas(estado: EstadoResearch):
        """Executa todas as buscas"""
        print("\n🔍 [RESEARCH] Executando buscas...")

        resultados = []
        for query in estado["queries_geradas"]:
            resultado = buscar_web.invoke({"query": query})
            resultados.append(resultado)

        return {"resultados_busca": resultados}

    def sintetizar(estado: EstadoResearch):
        """Sintetiza resultados"""
        print("\n📊 [RESEARCH] Sintetizando resultados...")

        if not os.getenv("OPENAI_API_KEY"):
            sintese = "RESUMO:\n" + "\n".join(estado["resultados_busca"])
            return {
                "sintese_final": sintese,
                "mensagens": [AIMessage(content=sintese)]
            }

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

        prompt = f"""
Você é um pesquisador especializado.

Query original: {estado['query_original']}

Resultados encontrados:
{chr(10).join([f"{i+1}. {r}" for i, r in enumerate(estado['resultados_busca'])])}

Crie um resumo executivo abrangente e bem estruturado.
"""

        resposta = llm.invoke([HumanMessage(content=prompt)])

        return {
            "sintese_final": resposta.content,
            "mensagens": [AIMessage(content=resposta.content)]
        }

    workflow.add_node("gerar_queries", gerar_queries)
    workflow.add_node("buscar", executar_buscas)
    workflow.add_node("sintetizar", sintetizar)

    workflow.set_entry_point("gerar_queries")
    workflow.add_edge("gerar_queries", "buscar")
    workflow.add_edge("buscar", "sintetizar")
    workflow.add_edge("sintetizar", END)

    return workflow.compile()


# Testar Research Agent
print("\n🧪 Testando Research Agent...")

research_agent = criar_research_agent()

topicos = [
    "O que é LangGraph?",
    "Como funcionam agentes de IA?",
]

for topico in topicos:
    print(f"\n{'='*70}")
    print(f"🔎 Pesquisando: {topico}")
    print(f"{'='*70}")

    resultado = research_agent.invoke({
        "mensagens": [HumanMessage(content=topico)],
        "query_original": "",
        "queries_geradas": [],
        "resultados_busca": [],
        "sintese_final": ""
    })

    print(f"\n📄 Síntese:")
    print(resultado["sintese_final"][:300] + "...")


# ===================================================================
# RESUMO FINAL
# ===================================================================
print("\n\n" + "="*70)
print("🎓 PARABÉNS! ESTUDO COMPLETO DE LANGGRAPH")
print("="*70)
print("""
✅ VOCÊ APRENDEU:

1. Fundamentos de Agentes
   - O que são agentes de IA
   - Padrão ReAct
   - State management

2. Agente com LLM e Tools
   - Tool calling
   - Roteamento condicional
   - Loop de raciocínio

3. Memória e Conversação
   - Checkpoints
   - Thread management
   - Memória persistente

4. Multi-Agentes
   - Padrão Sequential
   - Padrão Parallel
   - Padrão Handoff

5. Supervisor Pattern
   - Delegação dinâmica
   - Orquestração inteligente
   - Gerenciamento de agentes

6. Human-in-the-Loop
   - Interrupt before/after
   - State modification
   - Aprovação humana

7. Casos Práticos
   - RAG Agent
   - Code Agent
   - Research Agent

🚀 PRÓXIMOS PASSOS:

1. INTEGRE COM PRODUÇÃO:
   - Adicione APIs reais
   - Use vector stores reais (Pinecone, Chroma)
   - Implemente logging e monitoring

2. ADICIONE PERSISTÊNCIA:
   - PostgreSQL checkpointer
   - Redis para cache
   - S3 para armazenamento

3. ESCALE:
   - Deploy em cloud
   - Use async para performance
   - Implemente rate limiting

4. MONITORE:
   - LangSmith para tracing
   - Métricas de performance
   - Alertas de erro

5. APRIMORE:
   - Adicione mais ferramentas
   - Implemente RAG avançado
   - Crie UIs interativas

📚 RECURSOS ADICIONAIS:

- Documentação oficial: https://langchain-ai.github.io/langgraph/
- Exemplos: https://github.com/langchain-ai/langgraph/tree/main/examples
- Discord LangChain: discord.gg/langchain

💡 PROJETOS SUGERIDOS:

1. Assistente Pessoal com Calendário
2. Agente de Análise de Dados
3. Sistema de Atendimento Multicanal
4. Agente de Automação de Tarefas
5. Research Assistant Avançado

VOCÊ ESTÁ PRONTO PARA CONSTRUIR AGENTES DE IA PODEROSOS! 🎉
""")

print("="*70)
