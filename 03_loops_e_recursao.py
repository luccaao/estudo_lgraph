"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 3
Loops e Recursão
===========================================

Um dos superpoderes do LangGraph é permitir CICLOS no grafo,
algo que não é possível no LangChain tradicional.
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


# EXEMPLO 1: CONTADOR COM LOOP
class EstadoContador(TypedDict):
    contador: int
    limite: int
    historico: list


def incrementar(estado: EstadoContador) -> EstadoContador:
    """Incrementa o contador"""
    novo_contador = estado["contador"] + 1
    historico = estado["historico"] + [novo_contador]

    print(f"[INCREMENTAR] Contador: {novo_contador}/{estado['limite']}")

    return {
        "contador": novo_contador,
        "limite": estado["limite"],
        "historico": historico
    }


def verificar_continuar(estado: EstadoContador) -> Literal["continuar", "fim"]:
    """Decide se continua o loop ou termina"""
    if estado["contador"] < estado["limite"]:
        print(f"[DECISÃO] Continuar loop (contador={estado['contador']})")
        return "continuar"
    else:
        print(f"[DECISÃO] Finalizar loop (limite atingido)")
        return "fim"


def finalizar_contador(estado: EstadoContador) -> EstadoContador:
    """Finaliza o contador e mostra histórico"""
    print(f"[FINALIZAR] Histórico completo: {estado['historico']}")
    return estado


def criar_grafo_contador():
    """Grafo com loop que conta até um limite"""

    workflow = StateGraph(EstadoContador)

    # Nós
    workflow.add_node("incrementar", incrementar)
    workflow.add_node("finalizar", finalizar_contador)

    # Ponto de entrada
    workflow.set_entry_point("incrementar")

    # Aresta condicional que cria o LOOP
    workflow.add_conditional_edges(
        "incrementar",
        verificar_continuar,
        {
            "continuar": "incrementar",  # LOOP: volta para si mesmo!
            "fim": "finalizar"
        }
    )

    workflow.add_edge("finalizar", END)

    return workflow.compile()


# EXEMPLO 2: FATORIAL COM RECURSÃO
class EstadoFatorial(TypedDict):
    numero: int
    resultado: int
    passos: list


def calcular_fatorial(estado: EstadoFatorial) -> EstadoFatorial:
    """Calcula um passo do fatorial"""
    numero = estado["numero"]
    resultado = estado["resultado"]

    if numero > 0:
        novo_resultado = resultado * numero
        novo_numero = numero - 1
        passos = estado["passos"] + [f"{resultado} × {numero} = {novo_resultado}"]

        print(f"[FATORIAL] {resultado} × {numero} = {novo_resultado}")

        return {
            "numero": novo_numero,
            "resultado": novo_resultado,
            "passos": passos
        }
    else:
        return estado


def verificar_fatorial(estado: EstadoFatorial) -> Literal["continuar", "fim"]:
    """Verifica se o fatorial foi completamente calculado"""
    if estado["numero"] > 0:
        return "continuar"
    else:
        return "fim"


def criar_grafo_fatorial():
    """Grafo que calcula fatorial recursivamente"""

    workflow = StateGraph(EstadoFatorial)

    workflow.add_node("calcular", calcular_fatorial)
    workflow.set_entry_point("calcular")

    # Loop recursivo
    workflow.add_conditional_edges(
        "calcular",
        verificar_fatorial,
        {
            "continuar": "calcular",  # Recursão
            "fim": END
        }
    )

    return workflow.compile()


# EXEMPLO 3: FIBONACCI COM ITERAÇÃO
class EstadoFibonacci(TypedDict):
    n: int  # Quantos números gerar
    contador: int  # Contador atual
    a: int  # Penúltimo número
    b: int  # Último número
    sequencia: list  # Sequência gerada


def gerar_fibonacci(estado: EstadoFibonacci) -> EstadoFibonacci:
    """Gera o próximo número de Fibonacci"""
    a, b = estado["a"], estado["b"]
    proximo = a + b

    sequencia = estado["sequencia"] + [proximo]
    contador = estado["contador"] + 1

    print(f"[FIBONACCI] Passo {contador}: {a} + {b} = {proximo}")

    return {
        "n": estado["n"],
        "contador": contador,
        "a": b,
        "b": proximo,
        "sequencia": sequencia
    }


def verificar_fibonacci(estado: EstadoFibonacci) -> Literal["continuar", "fim"]:
    """Verifica se gerou números suficientes"""
    if estado["contador"] < estado["n"]:
        return "continuar"
    else:
        return "fim"


def criar_grafo_fibonacci():
    """Grafo que gera sequência de Fibonacci"""

    workflow = StateGraph(EstadoFibonacci)

    workflow.add_node("gerar", gerar_fibonacci)
    workflow.set_entry_point("gerar")

    workflow.add_conditional_edges(
        "gerar",
        verificar_fibonacci,
        {
            "continuar": "gerar",
            "fim": END
        }
    )

    return workflow.compile()


# EXEMPLO 4: BUSCA COM RETRY (TENTATIVAS)
class EstadoBusca(TypedDict):
    tentativas: int
    max_tentativas: int
    sucesso: bool
    resultado: str


def tentar_buscar(estado: EstadoBusca) -> EstadoBusca:
    """Simula uma busca que pode falhar"""
    import random

    tentativa = estado["tentativas"] + 1
    sucesso = random.random() > 0.6  # 40% de chance de sucesso

    print(f"[TENTATIVA {tentativa}] {'Sucesso!' if sucesso else 'Falhou...'}")

    return {
        "tentativas": tentativa,
        "max_tentativas": estado["max_tentativas"],
        "sucesso": sucesso,
        "resultado": "Dados encontrados!" if sucesso else ""
    }


def verificar_retry(estado: EstadoBusca) -> Literal["retry", "sucesso", "falha"]:
    """Decide se deve tentar novamente, se teve sucesso ou falhou definitivamente"""
    if estado["sucesso"]:
        return "sucesso"
    elif estado["tentativas"] < estado["max_tentativas"]:
        print(f"[RETRY] Tentando novamente... ({estado['tentativas']}/{estado['max_tentativas']})")
        return "retry"
    else:
        print("[FALHA] Número máximo de tentativas atingido")
        return "falha"


def sucesso_node(estado: EstadoBusca) -> EstadoBusca:
    """Processa sucesso"""
    print(f"[SUCESSO] {estado['resultado']} (após {estado['tentativas']} tentativas)")
    return estado


def falha_node(estado: EstadoBusca) -> EstadoBusca:
    """Processa falha"""
    print(f"[ERRO] Falhou após {estado['tentativas']} tentativas")
    return {**estado, "resultado": "Erro: máximo de tentativas excedido"}


def criar_grafo_retry():
    """Grafo com lógica de retry"""

    workflow = StateGraph(EstadoBusca)

    workflow.add_node("buscar", tentar_buscar)
    workflow.add_node("sucesso", sucesso_node)
    workflow.add_node("falha", falha_node)

    workflow.set_entry_point("buscar")

    workflow.add_conditional_edges(
        "buscar",
        verificar_retry,
        {
            "retry": "buscar",  # Tenta novamente
            "sucesso": "sucesso",
            "falha": "falha"
        }
    )

    workflow.add_edge("sucesso", END)
    workflow.add_edge("falha", END)

    return workflow.compile()


# EXECUTAR EXEMPLOS
if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLO 1: Contador com Loop")
    print("=" * 60)

    app1 = criar_grafo_contador()
    resultado1 = app1.invoke({
        "contador": 0,
        "limite": 5,
        "historico": []
    })
    print(f"\nContagem final: {resultado1['contador']}")
    print(f"Histórico: {resultado1['historico']}\n")

    print("=" * 60)
    print("EXEMPLO 2: Fatorial Recursivo")
    print("=" * 60)

    app2 = criar_grafo_fatorial()
    numero = 5
    print(f"\nCalculando fatorial de {numero}:")
    resultado2 = app2.invoke({
        "numero": numero,
        "resultado": 1,
        "passos": []
    })
    print(f"\nResultado: {numero}! = {resultado2['resultado']}")
    print("Passos:")
    for passo in resultado2['passos']:
        print(f"  {passo}")

    print("\n" + "=" * 60)
    print("EXEMPLO 3: Sequência de Fibonacci")
    print("=" * 60)

    app3 = criar_grafo_fibonacci()
    n = 10
    print(f"\nGerando {n} números de Fibonacci:")
    resultado3 = app3.invoke({
        "n": n,
        "contador": 0,
        "a": 0,
        "b": 1,
        "sequencia": [0, 1]
    })
    print(f"\nSequência: {resultado3['sequencia']}\n")

    print("=" * 60)
    print("EXEMPLO 4: Busca com Retry")
    print("=" * 60)

    app4 = criar_grafo_retry()
    print("\nTentando buscar dados (com retry automático):")
    resultado4 = app4.invoke({
        "tentativas": 0,
        "max_tentativas": 5,
        "sucesso": False,
        "resultado": ""
    })
    print(f"\nResultado final: {resultado4['resultado']}")
    print(f"Total de tentativas: {resultado4['tentativas']}\n")

    print("=" * 60)
    print("""
    CONCEITOS-CHAVE APRENDIDOS:
    - Loops são criados fazendo um nó condicional apontar para si mesmo
    - Sempre precisa de uma condição de saída para evitar loops infinitos
    - Útil para: iterações, tentativas, processamento de listas, etc.

    EXERCÍCIO:
    1. Crie um grafo que processa uma lista de itens um por um
    2. Adicione lógica de validação com retry
    3. Implemente um contador de sucessos e falhas

    PRÓXIMO: 04_integracao_llm.py
    """)
    print("=" * 60)
