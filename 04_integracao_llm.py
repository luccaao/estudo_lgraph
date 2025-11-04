"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 4
Integração com LLMs (Language Models)
===========================================

Agora vamos integrar LangGraph com modelos de linguagem!
Este é o verdadeiro poder do LangGraph.

NOTA: Este exemplo requer uma chave de API (OpenAI, Anthropic, etc.)
Configure sua chave antes de executar.
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
import operator

# Importações do LangChain (descomente quando tiver as chaves configuradas)
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
# from langchain.schema import HumanMessage, AIMessage, SystemMessage


# EXEMPLO 1: ESTADO PARA CONVERSAÇÃO
class EstadoConversa(TypedDict):
    mensagens: Annotated[list, operator.add]  # Acumula mensagens
    contador_rodadas: int
    resumo: str


# Simulação de LLM para demonstração (substitua por LLM real)
class LLMSimulado:
    """Simula um LLM para fins de demonstração"""

    def invoke(self, mensagens):
        ultima = mensagens[-1] if mensagens else ""

        # Simula respostas baseadas na mensagem
        if "olá" in str(ultima).lower():
            return "Olá! Como posso ajudar você hoje?"
        elif "nome" in str(ultima).lower():
            return "Meu nome é AssistenteLangGraph, um agente criado com LangGraph!"
        elif "python" in str(ultima).lower():
            return "Python é uma linguagem excelente! Posso ajudar com código Python."
        elif "tchau" in str(ultima).lower() or "adeus" in str(ultima).lower():
            return "Até logo! Foi um prazer conversar com você."
        else:
            return f"Interessante! Você disse: '{ultima}'. Posso elaborar mais sobre isso."


# EXEMPLO 2: AGENTE SIMPLES COM LLM
class EstadoAgente(TypedDict):
    entrada: str
    pensamento: str
    resposta: str
    historico: list


def pensar(estado: EstadoAgente) -> EstadoAgente:
    """Nó que 'pensa' sobre a entrada usando um LLM"""
    entrada = estado["entrada"]

    # Simulação de pensamento (em produção, use um LLM real)
    print(f"[PENSAR] Analisando: '{entrada}'")

    # Aqui você usaria algo como:
    # llm = ChatOpenAI(model="gpt-4")
    # resposta = llm.invoke([
    #     SystemMessage(content="Você é um assistente prestativo."),
    #     HumanMessage(content=entrada)
    # ])

    pensamento = f"Interpretação: '{entrada}' é uma pergunta/afirmação que requer análise."

    return {
        **estado,
        "pensamento": pensamento
    }


def responder(estado: EstadoAgente) -> EstadoAgente:
    """Nó que gera uma resposta baseada no pensamento"""
    pensamento = estado["pensamento"]
    entrada = estado["entrada"]

    print(f"[RESPONDER] Gerando resposta...")

    # Simulação de geração de resposta
    llm_simulado = LLMSimulado()
    resposta = llm_simulado.invoke([entrada])

    historico = estado.get("historico", []) + [
        {"entrada": entrada, "resposta": resposta}
    ]

    return {
        **estado,
        "resposta": resposta,
        "historico": historico
    }


def criar_agente_simples():
    """Cria um agente simples com LLM"""

    workflow = StateGraph(EstadoAgente)

    workflow.add_node("pensar", pensar)
    workflow.add_node("responder", responder)

    workflow.set_entry_point("pensar")
    workflow.add_edge("pensar", "responder")
    workflow.add_edge("responder", END)

    return workflow.compile()


# EXEMPLO 3: AGENTE COM FERRAMENTAS (TOOL CALLING)
class EstadoComFerramentas(TypedDict):
    entrada: str
    usa_ferramenta: bool
    ferramenta_usada: str
    resultado_ferramenta: str
    resposta_final: str


# Ferramentas simuladas
def calcular(expressao: str) -> str:
    """Calcula uma expressão matemática"""
    try:
        resultado = eval(expressao)
        return f"O resultado de {expressao} é {resultado}"
    except:
        return f"Não consegui calcular: {expressao}"


def buscar_informacao(termo: str) -> str:
    """Simula busca de informação"""
    base_conhecimento = {
        "python": "Python é uma linguagem de programação de alto nível.",
        "langgraph": "LangGraph é uma biblioteca para construir agentes com grafos.",
        "ia": "Inteligência Artificial é o campo de estudo de sistemas inteligentes."
    }
    return base_conhecimento.get(termo.lower(), f"Não encontrei informação sobre '{termo}'")


def decidir_ferramenta(estado: EstadoComFerramentas) -> EstadoComFerramentas:
    """Decide se precisa usar uma ferramenta"""
    entrada = estado["entrada"].lower()

    usa_ferramenta = False
    ferramenta = ""

    if any(op in entrada for op in ['+', '-', '*', '/', 'calcular', 'quanto é']):
        usa_ferramenta = True
        ferramenta = "calculadora"
        print("[DECISÃO] Usar calculadora")
    elif any(palavra in entrada for palavra in ['o que é', 'sobre', 'informação']):
        usa_ferramenta = True
        ferramenta = "busca"
        print("[DECISÃO] Usar busca")
    else:
        print("[DECISÃO] Responder diretamente (sem ferramenta)")

    return {
        **estado,
        "usa_ferramenta": usa_ferramenta,
        "ferramenta_usada": ferramenta
    }


def executar_ferramenta(estado: EstadoComFerramentas) -> EstadoComFerramentas:
    """Executa a ferramenta escolhida"""
    ferramenta = estado["ferramenta_usada"]
    entrada = estado["entrada"]

    if ferramenta == "calculadora":
        # Extrai expressão (simplificado)
        for palavra in entrada.split():
            if any(op in palavra for op in ['+', '-', '*', '/']):
                resultado = calcular(palavra)
                break
        else:
            resultado = "Não encontrei uma expressão para calcular"

    elif ferramenta == "busca":
        # Extrai termo de busca (simplificado)
        if "o que é" in entrada:
            termo = entrada.split("o que é")[-1].strip().rstrip("?")
        else:
            termo = entrada
        resultado = buscar_informacao(termo)

    else:
        resultado = ""

    print(f"[FERRAMENTA] Executando {ferramenta}: {resultado}")

    return {
        **estado,
        "resultado_ferramenta": resultado
    }


def gerar_resposta_final(estado: EstadoComFerramentas) -> EstadoComFerramentas:
    """Gera resposta final, com ou sem ferramenta"""
    if estado["usa_ferramenta"]:
        resposta = f"Usei a ferramenta '{estado['ferramenta_usada']}': {estado['resultado_ferramenta']}"
    else:
        llm = LLMSimulado()
        resposta = llm.invoke([estado["entrada"]])

    print(f"[RESPOSTA] {resposta}")

    return {
        **estado,
        "resposta_final": resposta
    }


def rotear_ferramenta(estado: EstadoComFerramentas):
    """Roteia baseado se usa ferramenta ou não"""
    if estado["usa_ferramenta"]:
        return "executar_ferramenta"
    else:
        return "responder"


def criar_agente_com_ferramentas():
    """Cria agente que pode usar ferramentas"""

    workflow = StateGraph(EstadoComFerramentas)

    workflow.add_node("decidir", decidir_ferramenta)
    workflow.add_node("executar_ferramenta", executar_ferramenta)
    workflow.add_node("responder", gerar_resposta_final)

    workflow.set_entry_point("decidir")

    workflow.add_conditional_edges(
        "decidir",
        rotear_ferramenta,
        {
            "executar_ferramenta": "executar_ferramenta",
            "responder": "responder"
        }
    )

    workflow.add_edge("executar_ferramenta", "responder")
    workflow.add_edge("responder", END)

    return workflow.compile()


# EXECUTAR EXEMPLOS
if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLO 1: Agente Simples")
    print("=" * 60)

    app1 = criar_agente_simples()

    perguntas = [
        "Olá, tudo bem?",
        "Qual é o seu nome?",
        "Me ajude com Python"
    ]

    for pergunta in perguntas:
        print(f"\n>>> {pergunta}")
        resultado = app1.invoke({
            "entrada": pergunta,
            "pensamento": "",
            "resposta": "",
            "historico": []
        })
        print(f"<<< {resultado['resposta']}")

    print("\n" + "=" * 60)
    print("EXEMPLO 2: Agente com Ferramentas")
    print("=" * 60)

    app2 = criar_agente_com_ferramentas()

    consultas = [
        "Quanto é 15+27?",
        "O que é Python?",
        "Olá, como vai?",
        "O que é LangGraph?",
        "Calcule 100*5"
    ]

    for consulta in consultas:
        print(f"\n{'='*50}")
        print(f">>> {consulta}")
        resultado = app2.invoke({
            "entrada": consulta,
            "usa_ferramenta": False,
            "ferramenta_usada": "",
            "resultado_ferramenta": "",
            "resposta_final": ""
        })
        print(f"<<< {resultado['resposta_final']}")

    print("\n" + "=" * 60)
    print("""
    CONFIGURAÇÃO PARA LLM REAL:

    # 1. Instalar dependências:
    pip install langchain-openai  # Para OpenAI
    # ou
    pip install langchain-anthropic  # Para Claude

    # 2. Configurar chave API:
    export OPENAI_API_KEY="sua-chave"
    # ou
    export ANTHROPIC_API_KEY="sua-chave"

    # 3. Usar no código:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    # ou
    from langchain_anthropic import ChatAnthropic
    llm = ChatAnthropic(model="claude-3-sonnet-20240229")

    EXERCÍCIO:
    1. Configure uma chave de API (OpenAI ou Anthropic)
    2. Substitua o LLMSimulado por um LLM real
    3. Adicione novas ferramentas (clima, hora, etc.)
    4. Teste o agente com perguntas complexas

    PRÓXIMO: 05_persistencia_memoria.py
    """)
    print("=" * 60)
