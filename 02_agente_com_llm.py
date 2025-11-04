"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 2
Agente Real com LLM e Ferramentas
===========================================

Agora vamos criar um AGENTE DE VERDADE que:
- Usa um LLM real (OpenAI/Anthropic) para pensar
- Decide automaticamente quais ferramentas usar
- Executa múltiplas ações em sequência
- Mantém contexto da conversa

Este é o padrão que você usará em 90% dos casos reais!
"""

import os
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import operator


# ===================================================================
# PARTE 1: DEFINIR FERRAMENTAS (TOOLS)
# ===================================================================
print("\n" + "="*70)
print("PARTE 1: Criando Ferramentas para o Agente")
print("="*70)

@tool
def calculadora(expressao: str) -> str:
    """
    Calcula expressões matemáticas simples.

    Args:
        expressao: A expressão matemática (ex: "2 + 2", "10 * 5")
    """
    try:
        # ATENÇÃO: Em produção, use uma biblioteca segura!
        resultado = eval(expressao)
        print(f"🔢 [TOOL: calculadora] Calculando '{expressao}' = {resultado}")
        return f"Resultado: {resultado}"
    except Exception as e:
        return f"Erro ao calcular: {e}"


@tool
def buscar_clima(cidade: str) -> str:
    """
    Busca informações de clima para uma cidade.

    Args:
        cidade: Nome da cidade
    """
    # Simulando API de clima
    print(f"🌤️  [TOOL: buscar_clima] Consultando clima de {cidade}...")

    climas_fake = {
        "são paulo": "25°C, parcialmente nublado",
        "rio de janeiro": "30°C, ensolarado",
        "brasília": "28°C, céu limpo",
    }

    resultado = climas_fake.get(cidade.lower(), "22°C, clima agradável")
    return f"Clima em {cidade}: {resultado}"


@tool
def buscar_na_web(query: str) -> str:
    """
    Busca informações na internet.

    Args:
        query: Termo de busca
    """
    print(f"🔍 [TOOL: buscar_na_web] Buscando '{query}'...")

    # Simulando resultados de busca
    resultados_fake = {
        "python": "Python é uma linguagem de programação de alto nível, interpretada...",
        "langgraph": "LangGraph é uma biblioteca para construir agentes de IA stateful...",
        "default": f"Informações sobre '{query}': [simulação de resultados da web]"
    }

    for key in resultados_fake:
        if key in query.lower():
            return resultados_fake[key]

    return resultados_fake["default"]


# Lista de todas as ferramentas disponíveis
ferramentas = [calculadora, buscar_clima, buscar_na_web]

print("\n✅ Ferramentas criadas:")
for f in ferramentas:
    print(f"   - {f.name}: {f.description}")


# ===================================================================
# PARTE 2: DEFINIR O ESTADO DO AGENTE
# ===================================================================
print("\n" + "="*70)
print("PARTE 2: Definindo o Estado do Agente")
print("="*70)

class EstadoAgente(TypedDict):
    """
    Estado que mantém toda a conversa e contexto do agente.

    - mensagens: Histórico completo (humano, AI, ferramentas)
    - iteracoes: Contador de iterações (evita loops infinitos)
    """
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    iteracoes: int


# ===================================================================
# PARTE 3: NÓ QUE CHAMA O LLM
# ===================================================================
print("\n" + "="*70)
print("PARTE 3: Criando o Nó de Raciocínio (LLM)")
print("="*70)

def no_agente(estado: EstadoAgente):
    """
    Este é o CÉREBRO do agente.
    O LLM analisa a conversa e decide:
    1. Usar uma ferramenta, OU
    2. Responder diretamente ao usuário
    """
    print(f"\n🧠 [AGENTE] Pensando... (iteração {estado.get('iteracoes', 0)})")

    # Inicializar o LLM com as ferramentas
    # NOTA: Você precisa ter OPENAI_API_KEY no .env
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_com_tools = llm.bind_tools(ferramentas)

    # LLM analisa todas as mensagens e decide o que fazer
    resposta = llm_com_tools.invoke(estado["mensagens"])

    # Verificar se o LLM quer usar ferramentas
    if resposta.tool_calls:
        print(f"   🎯 Decisão: Usar ferramenta '{resposta.tool_calls[0]['name']}'")
    else:
        print(f"   💬 Decisão: Responder diretamente")

    return {
        "mensagens": [resposta],
        "iteracoes": estado.get("iteracoes", 0) + 1
    }


# ===================================================================
# PARTE 4: NÓ QUE EXECUTA FERRAMENTAS
# ===================================================================
print("\n" + "="*70)
print("PARTE 4: Criando o Nó de Ação (Execução de Tools)")
print("="*70)

def no_ferramentas(estado: EstadoAgente):
    """
    Executa as ferramentas que o LLM decidiu usar.
    """
    print(f"\n⚡ [FERRAMENTAS] Executando ações...")

    ultima_mensagem = estado["mensagens"][-1]

    # Executar cada ferramenta solicitada
    resultados = []
    for tool_call in ultima_mensagem.tool_calls:
        # Encontrar a ferramenta correspondente
        ferramenta = next((f for f in ferramentas if f.name == tool_call["name"]), None)

        if ferramenta:
            # Executar a ferramenta
            resultado = ferramenta.invoke(tool_call["args"])

            # Criar mensagem com o resultado
            resultados.append(
                ToolMessage(
                    content=str(resultado),
                    tool_call_id=tool_call["id"]
                )
            )

    return {"mensagens": resultados}


# ===================================================================
# PARTE 5: FUNÇÃO DE ROTEAMENTO (DECIDIR PRÓXIMO PASSO)
# ===================================================================
print("\n" + "="*70)
print("PARTE 5: Criando Lógica de Roteamento")
print("="*70)

def should_continue(estado: EstadoAgente) -> str:
    """
    Decide se o agente deve:
    - Continuar (executar ferramentas)
    - Terminar (já respondeu ao usuário)
    """
    ultima_mensagem = estado["mensagens"][-1]
    iteracoes = estado.get("iteracoes", 0)

    # Segurança: limite de iterações
    if iteracoes > 10:
        print("   ⚠️  Limite de iterações atingido")
        return "end"

    # Se o LLM chamou ferramentas, continuar
    if hasattr(ultima_mensagem, "tool_calls") and ultima_mensagem.tool_calls:
        print("   ➡️  Roteamento: Executar ferramentas")
        return "continue"

    # Caso contrário, terminar
    print("   ✅ Roteamento: Finalizar")
    return "end"


# ===================================================================
# PARTE 6: CONSTRUIR O GRAFO DO AGENTE
# ===================================================================
print("\n" + "="*70)
print("PARTE 6: Montando o Grafo do Agente")
print("="*70)

def criar_agente():
    """
    Cria o grafo completo do agente ReAct.

    Fluxo:
    1. START → agente (LLM pensa e decide)
    2. Se decidiu usar ferramenta → ferramentas → volta para agente
    3. Se decidiu responder → END
    """
    workflow = StateGraph(EstadoAgente)

    # Adicionar nós
    workflow.add_node("agente", no_agente)
    workflow.add_node("ferramentas", no_ferramentas)

    # Ponto de entrada
    workflow.set_entry_point("agente")

    # Roteamento condicional
    workflow.add_conditional_edges(
        "agente",
        should_continue,
        {
            "continue": "ferramentas",
            "end": END
        }
    )

    # Depois de executar ferramentas, volta para o agente pensar novamente
    workflow.add_edge("ferramentas", "agente")

    return workflow.compile()


print("\n✅ Grafo do agente construído!")
print("""
Fluxo do agente:
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────┐
│ AGENTE  │ ◄──────┐
│  (LLM)  │        │
└────┬────┘        │
     │             │
     ▼             │
  Precisa         │
ferramenta?       │
     │             │
  ┌──┴──┐         │
  │ SIM │ NÃO     │
  └──┬──┘  │      │
     │     ▼      │
     │   [END]    │
     │            │
     ▼            │
┌──────────┐     │
│FERRAMENTAS├─────┘
└──────────┘
""")


# ===================================================================
# PARTE 7: TESTAR O AGENTE
# ===================================================================
if __name__ == "__main__":
    print("\n\n" + "="*70)
    print("PARTE 7: TESTANDO O AGENTE")
    print("="*70)

    # Verificar se tem API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  ATENÇÃO: Configure OPENAI_API_KEY no arquivo .env")
        print("   Sem a chave, o agente não funcionará.\n")
        exit(1)

    agente = criar_agente()

    # Testes
    testes = [
        "Qual o clima em São Paulo?",
        "Quanto é 25 * 4 + 10?",
        "Me explique o que é LangGraph",
        "Qual o clima no Rio e quanto é 100 dividido por 5?",  # Múltiplas ferramentas!
    ]

    for i, pergunta in enumerate(testes, 1):
        print(f"\n{'='*70}")
        print(f"🧪 TESTE {i}: {pergunta}")
        print(f"{'='*70}")

        resultado = agente.invoke({
            "mensagens": [HumanMessage(content=pergunta)],
            "iteracoes": 0
        })

        # Mostrar a resposta final
        print(f"\n💬 RESPOSTA FINAL:")
        resposta_final = resultado["mensagens"][-1]
        if hasattr(resposta_final, "content"):
            print(f"   {resposta_final.content}")

        print(f"\n📊 Total de iterações: {resultado['iteracoes']}")
        print(f"📊 Total de mensagens: {len(resultado['mensagens'])}")


# ===================================================================
# RESUMO E PRÓXIMOS PASSOS
# ===================================================================
print("\n\n" + "="*70)
print("📚 RESUMO - O QUE VOCÊ APRENDEU")
print("="*70)
print("""
✅ Como criar um agente REAL com LLM:
   - Definir ferramentas com @tool decorator
   - Bind ferramentas ao LLM com .bind_tools()
   - LLM decide automaticamente quais ferramentas usar

✅ Padrão ReAct em ação:
   AGENTE (pensa) → decide ferramenta → FERRAMENTAS (executa)
   → volta para AGENTE → decide responder → END

✅ Tool calling:
   - LLM retorna tool_calls quando quer usar ferramenta
   - Executamos a ferramenta e devolvemos ToolMessage
   - LLM vê o resultado e decide próximo passo

✅ Roteamento condicional:
   - should_continue decide se continua ou termina
   - Permite loops (ReAct) com segurança (limite de iterações)

🎯 PRÓXIMO PASSO: 03_agente_conversacional.py
   - Adicionar memória persistente
   - Manter contexto entre múltiplas conversas
   - Implementar checkpoints para salvar estado
""")

print("\n" + "="*70)
print("💡 EXERCÍCIO")
print("="*70)
print("""
Adicione uma nova ferramenta ao agente:

@tool
def converter_moeda(valor: float, de: str, para: str) -> str:
    \"\"\"Converte valores entre moedas\"\"\"
    # Implemente conversão simulada
    pass

Teste com: "Quanto é 100 dólares em reais?"
""")
