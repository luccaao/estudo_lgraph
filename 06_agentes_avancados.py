"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 6
Agentes Avançados e Padrões Complexos
===========================================

Padrões avançados de design de agentes usando LangGraph:
- Supervisor (coordena múltiplos agentes)
- Reflexão (auto-crítica e melhoria)
- Human-in-the-Loop (aprovação humana)
- Multi-agente colaborativo
"""

from typing import TypedDict, Literal, Annotated
from langgraph.graph import StateGraph, END
import operator
from datetime import datetime


# ===========================================
# PADRÃO 1: SUPERVISOR (Orquestrador)
# ===========================================

class EstadoSupervisor(TypedDict):
    tarefa: str
    agente_atual: str
    historico_agentes: Annotated[list, operator.add]
    resultados: dict
    completo: bool


def supervisor(estado: EstadoSupervisor) -> EstadoSupervisor:
    """Supervisor que decide qual agente deve trabalhar"""
    tarefa = estado["tarefa"].lower()

    # Decide qual agente especializado chamar
    if "código" in tarefa or "programar" in tarefa:
        proximo_agente = "programador"
    elif "pesquisar" in tarefa or "buscar" in tarefa:
        proximo_agente = "pesquisador"
    elif "escrever" in tarefa or "texto" in tarefa:
        proximo_agente = "escritor"
    elif "revisar" in tarefa or "verificar" in tarefa:
        proximo_agente = "revisor"
    else:
        proximo_agente = "fim"

    print(f"[SUPERVISOR] Delegando para: {proximo_agente}")

    return {
        **estado,
        "agente_atual": proximo_agente,
        "historico_agentes": [proximo_agente]
    }


def agente_programador(estado: EstadoSupervisor) -> EstadoSupervisor:
    """Agente especializado em programação"""
    print("[PROGRAMADOR] Escrevendo código...")

    resultado = {
        "codigo": "def exemplo(): return 'Hello World'",
        "linguagem": "Python",
        "timestamp": datetime.now().isoformat()
    }

    resultados = estado.get("resultados", {})
    resultados["programador"] = resultado

    return {
        **estado,
        "resultados": resultados,
        "tarefa": "revisar código"  # Próxima tarefa
    }


def agente_pesquisador(estado: EstadoSupervisor) -> EstadoSupervisor:
    """Agente especializado em pesquisa"""
    print("[PESQUISADOR] Pesquisando informações...")

    resultado = {
        "fontes": ["doc1.pdf", "artigo2.md"],
        "resumo": "Informações coletadas sobre o tópico",
        "timestamp": datetime.now().isoformat()
    }

    resultados = estado.get("resultados", {})
    resultados["pesquisador"] = resultado

    return {
        **estado,
        "resultados": resultados,
        "tarefa": "escrever relatório"
    }


def agente_escritor(estado: EstadoSupervisor) -> EstadoSupervisor:
    """Agente especializado em escrita"""
    print("[ESCRITOR] Escrevendo documento...")

    resultado = {
        "documento": "## Relatório\n\nConteúdo baseado na pesquisa...",
        "palavras": 150,
        "timestamp": datetime.now().isoformat()
    }

    resultados = estado.get("resultados", {})
    resultados["escritor"] = resultado

    return {
        **estado,
        "resultados": resultados,
        "tarefa": "revisar documento"
    }


def agente_revisor(estado: EstadoSupervisor) -> EstadoSupervisor:
    """Agente que revisa o trabalho dos outros"""
    print("[REVISOR] Revisando trabalho...")

    resultado = {
        "aprovado": True,
        "sugestoes": ["Adicionar mais exemplos", "Corrigir formatação"],
        "timestamp": datetime.now().isoformat()
    }

    resultados = estado.get("resultados", {})
    resultados["revisor"] = resultado

    return {
        **estado,
        "resultados": resultados,
        "completo": True,
        "tarefa": "fim"
    }


def rotear_supervisor(estado: EstadoSupervisor) -> str:
    """Roteia para o próximo agente"""
    agente = estado["agente_atual"]

    if estado.get("completo"):
        return "fim"
    elif agente == "fim":
        return "fim"
    else:
        return agente


def criar_sistema_supervisor():
    """Cria sistema com supervisor e agentes especializados"""

    workflow = StateGraph(EstadoSupervisor)

    # Adicionar supervisor e agentes
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("programador", agente_programador)
    workflow.add_node("pesquisador", agente_pesquisador)
    workflow.add_node("escritor", agente_escritor)
    workflow.add_node("revisor", agente_revisor)

    workflow.set_entry_point("supervisor")

    # Roteamento condicional
    workflow.add_conditional_edges(
        "supervisor",
        rotear_supervisor,
        {
            "programador": "programador",
            "pesquisador": "pesquisador",
            "escritor": "escritor",
            "revisor": "revisor",
            "fim": END
        }
    )

    # Todos voltam para supervisor
    for agente in ["programador", "pesquisador", "escritor", "revisor"]:
        workflow.add_edge(agente, "supervisor")

    return workflow.compile()


# ===========================================
# PADRÃO 2: REFLEXÃO (Auto-crítica)
# ===========================================

class EstadoReflexao(TypedDict):
    conteudo: str
    tentativas: int
    max_tentativas: int
    qualidade_score: int
    feedback: list
    aprovado: bool


def gerar_conteudo(estado: EstadoReflexao) -> EstadoReflexao:
    """Gera conteúdo (simulado)"""
    tentativa = estado["tentativas"] + 1

    # Simula melhoria com tentativas
    qualidade = min(50 + (tentativa * 15), 95)

    conteudo = f"Versão {tentativa}: Este é um texto de qualidade {qualidade}%"

    print(f"[GERADOR] Tentativa {tentativa} - Qualidade: {qualidade}%")

    return {
        **estado,
        "conteudo": conteudo,
        "tentativas": tentativa,
        "qualidade_score": qualidade
    }


def refletir(estado: EstadoReflexao) -> EstadoReflexao:
    """Reflete sobre a qualidade do conteúdo"""
    qualidade = estado["qualidade_score"]
    feedback = []

    if qualidade < 70:
        feedback.append("Conteúdo precisa ser mais detalhado")
        feedback.append("Adicionar mais exemplos")
        aprovado = False
    elif qualidade < 85:
        feedback.append("Bom, mas pode melhorar a estrutura")
        aprovado = False
    else:
        feedback.append("Excelente! Conteúdo aprovado")
        aprovado = True

    print(f"[REFLEXÃO] Qualidade {qualidade}% - {'Aprovado' if aprovado else 'Requer melhoria'}")
    for fb in feedback:
        print(f"  - {fb}")

    return {
        **estado,
        "feedback": feedback,
        "aprovado": aprovado
    }


def decidir_reflexao(estado: EstadoReflexao) -> Literal["regenerar", "fim"]:
    """Decide se regenera ou finaliza"""
    if estado["aprovado"]:
        return "fim"
    elif estado["tentativas"] >= estado["max_tentativas"]:
        print("[REFLEXÃO] Máximo de tentativas atingido")
        return "fim"
    else:
        print("[REFLEXÃO] Tentando melhorar...")
        return "regenerar"


def criar_agente_reflexivo():
    """Cria agente com capacidade de auto-reflexão"""

    workflow = StateGraph(EstadoReflexao)

    workflow.add_node("gerar", gerar_conteudo)
    workflow.add_node("refletir", refletir)

    workflow.set_entry_point("gerar")
    workflow.add_edge("gerar", "refletir")

    workflow.add_conditional_edges(
        "refletir",
        decidir_reflexao,
        {
            "regenerar": "gerar",  # Loop de melhoria
            "fim": END
        }
    )

    return workflow.compile()


# ===========================================
# PADRÃO 3: HUMAN-IN-THE-LOOP
# ===========================================

class EstadoHumanoLoop(TypedDict):
    acao_proposta: str
    aprovacao_pendente: bool
    aprovado: bool
    feedback_humano: str
    resultado: str


def propor_acao(estado: EstadoHumanoLoop) -> EstadoHumanoLoop:
    """Agente propõe uma ação"""
    acao = "Deletar 100 registros antigos do banco de dados"

    print(f"[AGENTE] Propondo ação: {acao}")
    print("[AGENTE] Aguardando aprovação humana...")

    return {
        **estado,
        "acao_proposta": acao,
        "aprovacao_pendente": True
    }


def aguardar_humano(estado: EstadoHumanoLoop) -> EstadoHumanoLoop:
    """Simula interação humana (em produção, seria uma interrupção real)"""

    # Em produção, aqui você pausaria e esperaria input real
    # Para demonstração, vamos simular aprovação

    print("\n[SISTEMA] === INTERRUPÇÃO PARA HUMANO ===")
    print(f"Ação proposta: {estado['acao_proposta']}")
    print("[SIMULAÇÃO] Humano aprovou a ação")

    return {
        **estado,
        "aprovacao_pendente": False,
        "aprovado": True,
        "feedback_humano": "Aprovado - mas faça backup primeiro"
    }


def executar_acao(estado: EstadoHumanoLoop) -> EstadoHumanoLoop:
    """Executa a ação se aprovada"""
    if estado["aprovado"]:
        print(f"[AGENTE] Executando ação aprovada")
        print(f"[AGENTE] Feedback considerado: {estado['feedback_humano']}")
        resultado = "Ação executada com sucesso"
    else:
        print("[AGENTE] Ação rejeitada, abortando")
        resultado = "Ação cancelada pelo usuário"

    return {
        **estado,
        "resultado": resultado
    }


def criar_agente_com_humano():
    """Cria agente que requer aprovação humana"""

    workflow = StateGraph(EstadoHumanoLoop)

    workflow.add_node("propor", propor_acao)
    workflow.add_node("aguardar", aguardar_humano)
    workflow.add_node("executar", executar_acao)

    workflow.set_entry_point("propor")
    workflow.add_edge("propor", "aguardar")
    workflow.add_edge("aguardar", "executar")
    workflow.add_edge("executar", END)

    return workflow.compile()


# EXECUTAR EXEMPLOS
if __name__ == "__main__":
    print("=" * 60)
    print("PADRÃO 1: Sistema Supervisor")
    print("=" * 60)

    app1 = criar_sistema_supervisor()

    print("\n--- Tarefa 1: Programação ---")
    resultado1 = app1.invoke({
        "tarefa": "programar uma função Python",
        "agente_atual": "",
        "historico_agentes": [],
        "resultados": {},
        "completo": False
    })

    print("\n[FLUXO DE AGENTES]")
    print(f"Agentes utilizados: {resultado1['historico_agentes']}")
    print(f"\n[RESULTADOS FINAIS]")
    for agente, resultado in resultado1["resultados"].items():
        print(f"  {agente}: {list(resultado.keys())}")

    print("\n" + "=" * 60)
    print("PADRÃO 2: Agente Reflexivo")
    print("=" * 60)

    app2 = criar_agente_reflexivo()

    resultado2 = app2.invoke({
        "conteudo": "",
        "tentativas": 0,
        "max_tentativas": 5,
        "qualidade_score": 0,
        "feedback": [],
        "aprovado": False
    })

    print(f"\n[RESULTADO FINAL]")
    print(f"Tentativas: {resultado2['tentativas']}")
    print(f"Qualidade: {resultado2['qualidade_score']}%")
    print(f"Aprovado: {resultado2['aprovado']}")
    print(f"Conteúdo: {resultado2['conteudo']}")

    print("\n" + "=" * 60)
    print("PADRÃO 3: Human-in-the-Loop")
    print("=" * 60)

    app3 = criar_agente_com_humano()

    resultado3 = app3.invoke({
        "acao_proposta": "",
        "aprovacao_pendente": False,
        "aprovado": False,
        "feedback_humano": "",
        "resultado": ""
    })

    print(f"\n[RESULTADO]")
    print(f"Ação: {resultado3['acao_proposta']}")
    print(f"Status: {resultado3['resultado']}")
    print(f"Feedback: {resultado3['feedback_humano']}")

    print("\n" + "=" * 60)
    print("""
    PADRÕES AVANÇADOS DEMONSTRADOS:

    1. SUPERVISOR
       - Coordena múltiplos agentes especializados
       - Delega tarefas baseado em contexto
       - Agentes colaboram em pipeline

    2. REFLEXÃO
       - Agente critica seu próprio trabalho
       - Loop de melhoria iterativa
       - Auto-avaliação de qualidade

    3. HUMAN-IN-THE-LOOP
       - Pausas para aprovação humana
       - Decisões críticas requerem humano
       - Feedback incorporado no fluxo

    CASOS DE USO:
    - Sistemas de aprovação
    - Controle de qualidade automático
    - Workflows complexos multi-etapas
    - Agentes colaborativos

    EXERCÍCIO:
    1. Combine supervisor com reflexão
    2. Adicione mais agentes especializados
    3. Implemente votação entre múltiplos agentes
    4. Crie sistema de escalação (agente → supervisor → humano)

    PRÓXIMO: 07_casos_praticos.py
    """)
    print("=" * 60)
