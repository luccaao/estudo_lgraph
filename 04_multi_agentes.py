"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 4
Sistema Multi-Agente Colaborativo
===========================================

Aprenda a criar sistemas onde MÚLTIPLOS agentes trabalham juntos:
- Cada agente tem especialização
- Agentes se comunicam entre si
- Colaboração para resolver tarefas complexas
- Padrões: Sequential, Parallel, Hierarchical
"""

import os
from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import operator


# ===================================================================
# EXEMPLO 1: AGENTES EM SEQUÊNCIA (PIPELINE)
# ===================================================================
print("\n" + "="*70)
print("EXEMPLO 1: Multi-Agente em Sequência (Pipeline)")
print("="*70)
print("""
Cenário: Sistema de análise de feedback de clientes

AGENTE 1 (Tradutor) → AGENTE 2 (Analisador) → AGENTE 3 (Resumidor)
""")


class EstadoPipeline(TypedDict):
    """Estado compartilhado entre os agentes"""
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    feedback_original: str
    feedback_traduzido: str
    sentimento: str
    resumo_final: str


def agente_tradutor(estado: EstadoPipeline):
    """
    AGENTE 1: Especialista em tradução
    """
    print("\n🌐 [AGENTE TRADUTOR] Traduzindo feedback...")

    feedback = estado["feedback_original"]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""
Você é um tradutor especializado. Traduza o seguinte texto para português:

{feedback}

Retorne APENAS a tradução, sem explicações.
"""

    resposta = llm.invoke([HumanMessage(content=prompt)])
    traduzido = resposta.content

    print(f"   Original: {feedback[:50]}...")
    print(f"   Traduzido: {traduzido[:50]}...")

    return {
        "feedback_traduzido": traduzido,
        "mensagens": [AIMessage(content=f"Tradutor: {traduzido}")]
    }


def agente_analisador_sentimento(estado: EstadoPipeline):
    """
    AGENTE 2: Especialista em análise de sentimento
    """
    print("\n😊 [AGENTE ANALISADOR] Analisando sentimento...")

    feedback = estado["feedback_traduzido"]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""
Você é um especialista em análise de sentimento.
Analise o sentimento deste feedback e classifique como:
POSITIVO, NEGATIVO ou NEUTRO

Feedback: {feedback}

Retorne APENAS: POSITIVO, NEGATIVO ou NEUTRO
"""

    resposta = llm.invoke([HumanMessage(content=prompt)])
    sentimento = resposta.content.strip().upper()

    emoji_map = {
        "POSITIVO": "😊",
        "NEGATIVO": "😞",
        "NEUTRO": "😐"
    }

    print(f"   Sentimento: {emoji_map.get(sentimento, '❓')} {sentimento}")

    return {
        "sentimento": sentimento,
        "mensagens": [AIMessage(content=f"Analisador: Sentimento {sentimento}")]
    }


def agente_resumidor(estado: EstadoPipeline):
    """
    AGENTE 3: Especialista em sumarização
    """
    print("\n📝 [AGENTE RESUMIDOR] Criando resumo executivo...")

    feedback = estado["feedback_traduzido"]
    sentimento = estado["sentimento"]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    prompt = f"""
Você é um especialista em criar resumos executivos.

Feedback: {feedback}
Sentimento: {sentimento}

Crie um resumo executivo de 1-2 linhas para o time de produto.
"""

    resposta = llm.invoke([HumanMessage(content=prompt)])
    resumo = resposta.content

    print(f"   Resumo: {resumo}")

    return {
        "resumo_final": resumo,
        "mensagens": [AIMessage(content=f"Resumidor: {resumo}")]
    }


def criar_pipeline_agentes():
    """Cria pipeline sequencial de agentes"""

    workflow = StateGraph(EstadoPipeline)

    # Adicionar agentes como nós
    workflow.add_node("tradutor", agente_tradutor)
    workflow.add_node("analisador", agente_analisador_sentimento)
    workflow.add_node("resumidor", agente_resumidor)

    # Fluxo linear: tradutor → analisador → resumidor
    workflow.set_entry_point("tradutor")
    workflow.add_edge("tradutor", "analisador")
    workflow.add_edge("analisador", "resumidor")
    workflow.add_edge("resumidor", END)

    return workflow.compile()


# Testar pipeline
if __name__ == "__main__" and os.getenv("OPENAI_API_KEY"):
    print("\n🧪 Testando Pipeline de Agentes...")

    pipeline = criar_pipeline_agentes()

    feedback_teste = "This product is amazing! The customer service was excellent and delivery was fast."

    resultado = pipeline.invoke({
        "mensagens": [],
        "feedback_original": feedback_teste,
        "feedback_traduzido": "",
        "sentimento": "",
        "resumo_final": ""
    })

    print("\n" + "="*70)
    print("📊 RESULTADO FINAL DO PIPELINE")
    print("="*70)
    print(f"Original: {feedback_teste}")
    print(f"Traduzido: {resultado['feedback_traduzido']}")
    print(f"Sentimento: {resultado['sentimento']}")
    print(f"Resumo: {resultado['resumo_final']}")


# ===================================================================
# EXEMPLO 2: AGENTES EM PARALELO
# ===================================================================
print("\n\n" + "="*70)
print("EXEMPLO 2: Multi-Agente em Paralelo")
print("="*70)
print("""
Cenário: Pesquisar informações de múltiplas fontes simultaneamente

          ┌─→ AGENTE WEATHER ─┐
START ────┼─→ AGENTE NEWS ────┼──→ AGGREGATOR → END
          └─→ AGENTE FINANCE ─┘
""")


class EstadoParalelo(TypedDict):
    """Estado para execução paralela"""
    query: str
    resultado_weather: str
    resultado_news: str
    resultado_finance: str
    resultado_agregado: str


def agente_weather(estado: EstadoParalelo):
    """Agente especialista em clima"""
    print("\n🌤️  [AGENTE WEATHER] Buscando clima...")

    # Simulação - em produção usaria API real
    return {
        "resultado_weather": "São Paulo: 25°C, parcialmente nublado"
    }


def agente_news(estado: EstadoParalelo):
    """Agente especialista em notícias"""
    print("\n📰 [AGENTE NEWS] Buscando notícias...")

    # Simulação
    return {
        "resultado_news": "Principais notícias: Tech stocks em alta, novo produto lançado"
    }


def agente_finance(estado: EstadoParalelo):
    """Agente especialista em finanças"""
    print("\n💰 [AGENTE FINANCE] Buscando dados financeiros...")

    # Simulação
    return {
        "resultado_finance": "Dólar: R$5.20, Bitcoin: $45k"
    }


def agente_agregador(estado: EstadoParalelo):
    """Agrega resultados de todos os agentes"""
    print("\n🔄 [AGENTE AGREGADOR] Consolidando informações...")

    if not os.getenv("OPENAI_API_KEY"):
        # Agregação simples sem LLM
        agregado = f"""
Weather: {estado['resultado_weather']}
News: {estado['resultado_news']}
Finance: {estado['resultado_finance']}
"""
        return {"resultado_agregado": agregado}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    prompt = f"""
Você é um assistente que consolida informações.

Dados coletados:
- Clima: {estado['resultado_weather']}
- Notícias: {estado['resultado_news']}
- Finanças: {estado['resultado_finance']}

Crie um resumo executivo amigável para o usuário.
"""

    resposta = llm.invoke([HumanMessage(content=prompt)])

    return {"resultado_agregado": resposta.content}


def criar_sistema_paralelo():
    """
    Cria sistema com agentes em paralelo.

    NOTA: O LangGraph executa em ordem, mas você pode usar
    threads/async para verdadeiro paralelismo.
    """

    workflow = StateGraph(EstadoParalelo)

    # Agentes paralelos
    workflow.add_node("weather", agente_weather)
    workflow.add_node("news", agente_news)
    workflow.add_node("finance", agente_finance)
    workflow.add_node("agregador", agente_agregador)

    # Todos começam do START
    workflow.set_entry_point("weather")
    workflow.add_edge("weather", "news")
    workflow.add_edge("news", "finance")

    # Todos convergem para agregador
    workflow.add_edge("finance", "agregador")
    workflow.add_edge("agregador", END)

    return workflow.compile()


# Testar sistema paralelo
print("\n🧪 Testando Sistema Paralelo...")

sistema_paralelo = criar_sistema_paralelo()

resultado = sistema_paralelo.invoke({
    "query": "Informações do dia",
    "resultado_weather": "",
    "resultado_news": "",
    "resultado_finance": "",
    "resultado_agregado": ""
})

print("\n" + "="*70)
print("📊 RESULTADO AGREGADO")
print("="*70)
print(resultado["resultado_agregado"])


# ===================================================================
# EXEMPLO 3: AGENTES COM COMUNICAÇÃO (HANDOFF)
# ===================================================================
print("\n\n" + "="*70)
print("EXEMPLO 3: Agentes com Handoff (Passagem de Bastão)")
print("="*70)
print("""
Cenário: Sistema de suporte ao cliente
Agentes se passam a conversa baseado em especialização
""")


class EstadoHandoff(TypedDict):
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    categoria: str
    agente_atual: str
    resolvido: bool


def agente_triagem(estado: EstadoHandoff):
    """
    Agente que classifica o problema e direciona para especialista
    """
    print("\n🎯 [AGENTE TRIAGEM] Classificando problema...")

    if not os.getenv("OPENAI_API_KEY"):
        # Versão simplificada
        ultima_msg = estado["mensagens"][-1].content.lower()
        if "senha" in ultima_msg or "login" in ultima_msg:
            categoria = "tech"
        elif "reembolso" in ultima_msg or "pagamento" in ultima_msg:
            categoria = "billing"
        else:
            categoria = "general"

        print(f"   Categoria identificada: {categoria}")
        return {
            "categoria": categoria,
            "agente_atual": categoria,
            "mensagens": [AIMessage(content=f"Direcionando para {categoria}")]
        }

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    ultima_msg = estado["mensagens"][-1].content

    prompt = f"""
Você é um agente de triagem. Classifique o problema em:
- tech (problemas técnicos)
- billing (problemas de pagamento)
- general (outros)

Problema: {ultima_msg}

Retorne APENAS: tech, billing ou general
"""

    resposta = llm.invoke([HumanMessage(content=prompt)])
    categoria = resposta.content.strip().lower()

    print(f"   Categoria identificada: {categoria}")

    return {
        "categoria": categoria,
        "agente_atual": categoria,
        "mensagens": [AIMessage(content=f"Direcionando para {categoria}")]
    }


def agente_tech(estado: EstadoHandoff):
    """Especialista em problemas técnicos"""
    print("\n💻 [AGENTE TECH] Resolvendo problema técnico...")

    return {
        "resolvido": True,
        "mensagens": [AIMessage(content="Problema técnico resolvido! Tente fazer login novamente.")]
    }


def agente_billing(estado: EstadoHandoff):
    """Especialista em billing"""
    print("\n💳 [AGENTE BILLING] Resolvendo problema de pagamento...")

    return {
        "resolvido": True,
        "mensagens": [AIMessage(content="Reembolso processado! Você receberá em 3-5 dias úteis.")]
    }


def agente_general(estado: EstadoHandoff):
    """Agente generalista"""
    print("\n👤 [AGENTE GENERAL] Atendendo...")

    return {
        "resolvido": True,
        "mensagens": [AIMessage(content="Obrigado pelo contato! Como posso ajudar mais?")]
    }


def rotear_para_especialista(estado: EstadoHandoff) -> str:
    """Router que direciona para agente especializado"""
    categoria = estado.get("categoria", "general")
    print(f"   🔀 Roteando para: {categoria}")
    return categoria


def criar_sistema_handoff():
    """Sistema com handoff entre agentes"""

    workflow = StateGraph(EstadoHandoff)

    # Adicionar agentes
    workflow.add_node("triagem", agente_triagem)
    workflow.add_node("tech", agente_tech)
    workflow.add_node("billing", agente_billing)
    workflow.add_node("general", agente_general)

    # Fluxo
    workflow.set_entry_point("triagem")

    # Roteamento condicional para especialistas
    workflow.add_conditional_edges(
        "triagem",
        rotear_para_especialista,
        {
            "tech": "tech",
            "billing": "billing",
            "general": "general"
        }
    )

    # Especialistas finalizam
    for agente in ["tech", "billing", "general"]:
        workflow.add_edge(agente, END)

    return workflow.compile()


# Testar handoff
print("\n🧪 Testando Sistema de Handoff...")

sistema_handoff = criar_sistema_handoff()

testes = [
    "Esqueci minha senha e não consigo fazer login",
    "Quero um reembolso do meu pagamento",
    "Gostaria de dar um feedback sobre o produto"
]

for teste in testes:
    print(f"\n{'='*70}")
    print(f"👤 Cliente: {teste}")
    print(f"{'='*70}")

    resultado = sistema_handoff.invoke({
        "mensagens": [HumanMessage(content=teste)],
        "categoria": "",
        "agente_atual": "",
        "resolvido": False
    })

    print(f"\n✅ Resposta: {resultado['mensagens'][-1].content}")


# ===================================================================
# RESUMO
# ===================================================================
print("\n\n" + "="*70)
print("📚 RESUMO - O QUE VOCÊ APRENDEU")
print("="*70)
print("""
✅ Multi-Agente Sequencial (Pipeline):
   - Agentes processam um após o outro
   - Cada agente adiciona informação ao estado
   - Exemplo: Tradutor → Analisador → Resumidor

✅ Multi-Agente Paralelo:
   - Múltiplos agentes trabalham simultaneamente
   - Agregador consolida resultados
   - Mais eficiente para tarefas independentes

✅ Sistema de Handoff:
   - Agente de triagem direciona para especialistas
   - Cada especialista tem seu domínio
   - Roteamento condicional baseado em classificação

✅ Quando usar cada padrão:
   - Pipeline: Quando etapas dependem umas das outras
   - Paralelo: Quando tarefas são independentes
   - Handoff: Quando precisa de especialização

🎯 PRÓXIMO PASSO: 05_agente_supervisor.py
   - Padrão mais avançado: Supervisor que gerencia agentes
   - Delegação dinâmica de tarefas
   - Agentes que podem se chamar mutuamente
""")

print("\n" + "="*70)
print("💡 EXERCÍCIO")
print("="*70)
print("""
Crie um sistema multi-agente para análise de currículo:

1. AGENTE EXTRATOR: Extrai informações (nome, skills, experiência)
2. AGENTE AVALIADOR: Avalia qualificações
3. AGENTE RECOMENDADOR: Sugere melhorias

Use o padrão sequencial (pipeline).
""")
