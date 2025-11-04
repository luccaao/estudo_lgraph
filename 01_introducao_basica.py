"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 1
Introdução: Agentes de IA com LangGraph
===========================================

LangGraph é uma biblioteca para construir AGENTES DE IA stateful e multi-agente.
Um agente é um sistema que pode:
- Pensar e raciocinar
- Usar ferramentas (tools)
- Tomar decisões
- Manter contexto/memória
- Executar tarefas complexas de forma autônoma

CONCEITOS FUNDAMENTAIS PARA AGENTES:
- State: Armazena o histórico de mensagens e contexto
- LLM: Modelo de linguagem que "pensa" e decide
- Tools: Ferramentas que o agente pode usar
- Memory: Capacidade de lembrar conversas anteriores
- ReAct Pattern: Raciocínio + Ação em loop
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator


# ===================================================================
# EXEMPLO 1: AGENTE MAIS SIMPLES POSSÍVEL (SEM LLM)
# ===================================================================
print("\n" + "="*70)
print("EXEMPLO 1: Anatomia Básica de um Agente")
print("="*70)

class EstadoAgenteSimples(TypedDict):
    """Estado mínimo para um agente"""
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    proxima_acao: str


def no_raciocinio(estado: EstadoAgenteSimples):
    """Simula o 'pensamento' do agente"""
    ultima_msg = estado["mensagens"][-1].content
    print(f"\n🤔 [AGENTE PENSANDO]: Recebi '{ultima_msg}'")
    print("   Decisão: Vou processar essa informação")

    return {
        "mensagens": [AIMessage(content=f"Processando: {ultima_msg}")],
        "proxima_acao": "responder"
    }


def no_acao(estado: EstadoAgenteSimples):
    """Executa a ação decidida"""
    print(f"\n🎯 [AGENTE AGINDO]: Ação = {estado['proxima_acao']}")

    return {
        "mensagens": [AIMessage(content="Tarefa concluída!")],
        "proxima_acao": "fim"
    }


# Construir o agente simples
workflow = StateGraph(EstadoAgenteSimples)
workflow.add_node("pensar", no_raciocinio)
workflow.add_node("agir", no_acao)
workflow.set_entry_point("pensar")
workflow.add_edge("pensar", "agir")
workflow.add_edge("agir", END)

agente_simples = workflow.compile()

# Executar
resultado = agente_simples.invoke({
    "mensagens": [HumanMessage(content="Olá agente!")],
    "proxima_acao": ""
})

print("\n📋 HISTÓRICO COMPLETO:")
for msg in resultado["mensagens"]:
    tipo = "👤 HUMANO" if isinstance(msg, HumanMessage) else "🤖 AGENTE"
    print(f"{tipo}: {msg.content}")


# ===================================================================
# EXEMPLO 2: PADRÃO ReAct (REASON + ACT)
# ===================================================================
print("\n\n" + "="*70)
print("EXEMPLO 2: Padrão ReAct - O Coração dos Agentes")
print("="*70)
print("""
O padrão ReAct é o mais comum para agentes:
1. OBSERVE (observação do input)
2. THINK (raciocínio sobre o que fazer)
3. ACT (executar ação ou usar ferramenta)
4. REPEAT (voltar ao passo 1 se necessário)
""")


class EstadoReAct(TypedDict):
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    pensamento: str
    acao_executada: str
    iteracao: int


def react_observar(estado: EstadoReAct):
    """OBSERVE: Analisa a situação atual"""
    ultima = estado["mensagens"][-1].content
    iteracao = estado.get("iteracao", 0)

    print(f"\n👁️  OBSERVAÇÃO (iter {iteracao}):")
    print(f"   Input do usuário: '{ultima}'")

    return {"iteracao": iteracao + 1}


def react_pensar(estado: EstadoReAct):
    """THINK: Decide o que fazer"""
    ultima = estado["mensagens"][-1].content

    print(f"\n🧠 PENSAMENTO:")
    if "clima" in ultima.lower():
        pensamento = "Usuário perguntou sobre clima. Preciso usar ferramenta de clima."
        acao = "buscar_clima"
    elif "calcular" in ultima.lower() or any(op in ultima for op in ["+", "-", "*", "/"]):
        pensamento = "Usuário quer cálculo. Preciso usar calculadora."
        acao = "calcular"
    else:
        pensamento = "Posso responder diretamente."
        acao = "responder"

    print(f"   💭 {pensamento}")
    print(f"   🎯 Ação escolhida: {acao}")

    return {
        "pensamento": pensamento,
        "acao_executada": acao
    }


def react_agir(estado: EstadoReAct):
    """ACT: Executa a ação/tool"""
    acao = estado["acao_executada"]
    ultima = estado["mensagens"][-1].content

    print(f"\n⚡ AÇÃO:")

    # Simular execução de ferramentas
    if acao == "buscar_clima":
        resultado = "🌤️ Clima: 25°C, ensolarado"
        print(f"   [TOOL: weather_api] Consultando clima...")
    elif acao == "calcular":
        # Tentar extrair números da mensagem
        import re
        numeros = re.findall(r'\d+', ultima)
        if len(numeros) >= 2:
            resultado = f"📊 Resultado: {int(numeros[0]) + int(numeros[1])}"
        else:
            resultado = "📊 Calculadora pronta"
        print(f"   [TOOL: calculator] Calculando...")
    else:
        resultado = "✅ Entendido! Como posso ajudar mais?"
        print(f"   [DIRECT_RESPONSE] Respondendo...")

    print(f"   📤 Resultado: {resultado}")

    return {
        "mensagens": [AIMessage(content=resultado)]
    }


# Construir agente ReAct
workflow_react = StateGraph(EstadoReAct)
workflow_react.add_node("observar", react_observar)
workflow_react.add_node("pensar", react_pensar)
workflow_react.add_node("agir", react_agir)

workflow_react.set_entry_point("observar")
workflow_react.add_edge("observar", "pensar")
workflow_react.add_edge("pensar", "agir")
workflow_react.add_edge("agir", END)

agente_react = workflow_react.compile()

# Testar com diferentes inputs
testes = [
    "Qual o clima hoje?",
    "Quanto é 15 + 27?",
    "Olá, tudo bem?"
]

for teste in testes:
    print(f"\n{'='*70}")
    print(f"🧪 TESTE: '{teste}'")
    print(f"{'='*70}")

    resultado = agente_react.invoke({
        "mensagens": [HumanMessage(content=teste)],
        "pensamento": "",
        "acao_executada": "",
        "iteracao": 0
    })


# ===================================================================
# RESUMO E PRÓXIMOS PASSOS
# ===================================================================
print("\n\n" + "="*70)
print("📚 RESUMO - O QUE VOCÊ APRENDEU")
print("="*70)
print("""
✅ O que é um agente de IA:
   - Sistema autônomo que pensa, decide e age
   - Usa o padrão ReAct (Reason + Act)

✅ Componentes essenciais:
   - State: Mantém contexto (mensagens, pensamentos)
   - Nodes: Representam as etapas do agente (observar, pensar, agir)
   - Messages: Histórico de interações

✅ Padrão ReAct:
   OBSERVE → THINK → ACT → (repeat if needed)

🎯 PRÓXIMO PASSO: 02_agente_com_llm.py
   - Vamos adicionar um LLM REAL (OpenAI/Anthropic)
   - O agente vai realmente PENSAR sozinho
   - Vai decidir quais ferramentas usar dinamicamente
""")


print("\n" + "="*70)
print("💡 EXERCÍCIO")
print("="*70)
print("""
Modifique o agente ReAct para:
1. Adicionar uma nova ferramenta "tradutor"
2. Detectar quando usuário pede tradução
3. Simular a tradução no nó de ação
4. Testar com: "Traduza 'hello' para português"
""")
