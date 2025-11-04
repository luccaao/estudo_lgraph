"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 1
Introdução Básica: Criando seu Primeiro Grafo
===========================================

LangGraph é uma biblioteca para construir aplicações stateful e multi-agente
usando grafos. Ele estende o LangChain para permitir ciclos e persistência de estado.

CONCEITOS FUNDAMENTAIS:
- Nodes (Nós): Funções que processam dados
- Edges (Arestas): Conexões entre nós que determinam o fluxo
- State (Estado): Dados compartilhados que fluem pelo grafo
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END


# 1. DEFINIR O ESTADO
# O estado é compartilhado entre todos os nós do grafo
class EstadoSimples(TypedDict):
    mensagem: str
    contador: int


# 2. CRIAR FUNÇÕES DE NÓS
# Cada nó recebe o estado atual e retorna atualizações
def no_inicial(estado: EstadoSimples) -> EstadoSimples:
    """Primeiro nó: inicializa a mensagem"""
    print(f"[NO INICIAL] Mensagem recebida: {estado.get('mensagem', 'Nenhuma')}")
    return {
        "mensagem": "Olá do LangGraph!",
        "contador": estado.get("contador", 0) + 1
    }


def no_processamento(estado: EstadoSimples) -> EstadoSimples:
    """Segundo nó: processa a mensagem"""
    mensagem = estado["mensagem"]
    print(f"[PROCESSAMENTO] Processando: {mensagem}")
    return {
        "mensagem": mensagem.upper(),
        "contador": estado["contador"] + 1
    }


def no_final(estado: EstadoSimples) -> EstadoSimples:
    """Terceiro nó: finaliza o processo"""
    print(f"[NO FINAL] Resultado: {estado['mensagem']}")
    print(f"[NO FINAL] Passou por {estado['contador']} nós")
    return estado


# 3. CONSTRUIR O GRAFO
def criar_grafo_simples():
    """Cria e retorna um grafo simples e linear"""

    # Inicializar o grafo com o tipo de estado
    workflow = StateGraph(EstadoSimples)

    # Adicionar nós
    workflow.add_node("inicio", no_inicial)
    workflow.add_node("processar", no_processamento)
    workflow.add_node("finalizar", no_final)

    # Definir o ponto de entrada
    workflow.set_entry_point("inicio")

    # Adicionar arestas (conexões entre nós)
    workflow.add_edge("inicio", "processar")
    workflow.add_edge("processar", "finalizar")
    workflow.add_edge("finalizar", END)  # END marca o fim do grafo

    # Compilar o grafo
    app = workflow.compile()
    return app


# 4. EXECUTAR O GRAFO
if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLO 1: Grafo Linear Simples")
    print("=" * 60)

    # Criar o grafo
    app = criar_grafo_simples()

    # Estado inicial
    estado_inicial = {
        "mensagem": "Iniciando...",
        "contador": 0
    }

    # Executar o grafo
    resultado = app.invoke(estado_inicial)

    print("\n" + "=" * 60)
    print("RESULTADO FINAL:")
    print(f"Mensagem: {resultado['mensagem']}")
    print(f"Contador: {resultado['contador']}")
    print("=" * 60)

    """
    EXERCÍCIO:
    1. Adicione um novo nó que inverte a mensagem
    2. Conecte esse nó entre 'processar' e 'finalizar'
    3. Execute e observe o resultado

    PRÓXIMO: 02_condicionais_e_branches.py
    """
