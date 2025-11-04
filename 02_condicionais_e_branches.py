"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 2
Condicionais e Branches (Ramificações)
===========================================

Aprenda a criar grafos com lógica condicional que escolhem
diferentes caminhos baseados no estado.
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


# ESTADO COM MAIS INFORMAÇÕES
class EstadoCondicional(TypedDict):
    numero: int
    tipo: str
    resultado: str


# NÓS DO GRAFO
def classificar_numero(estado: EstadoCondicional) -> EstadoCondicional:
    """Classifica o número como par ou ímpar"""
    numero = estado["numero"]
    tipo = "par" if numero % 2 == 0 else "impar"
    print(f"[CLASSIFICADOR] Número {numero} é {tipo}")
    return {"tipo": tipo, "numero": numero, "resultado": ""}


def processar_par(estado: EstadoCondicional) -> EstadoCondicional:
    """Processa números pares"""
    numero = estado["numero"]
    resultado = f"Número {numero} é PAR - dividido por 2 = {numero // 2}"
    print(f"[PROCESSAR PAR] {resultado}")
    return {"resultado": resultado, "tipo": estado["tipo"], "numero": numero}


def processar_impar(estado: EstadoCondicional) -> EstadoCondicional:
    """Processa números ímpares"""
    numero = estado["numero"]
    resultado = f"Número {numero} é ÍMPAR - multiplicado por 3 + 1 = {numero * 3 + 1}"
    print(f"[PROCESSAR ÍMPAR] {resultado}")
    return {"resultado": resultado, "tipo": estado["tipo"], "numero": numero}


def finalizar_processamento(estado: EstadoCondicional) -> EstadoCondicional:
    """Finaliza o processamento"""
    print(f"[FINALIZAR] {estado['resultado']}")
    return estado


# FUNÇÃO DE ROTEAMENTO (CONDICIONAL)
def decidir_caminho(estado: EstadoCondicional) -> Literal["par", "impar"]:
    """
    Esta função decide qual caminho seguir baseado no estado.
    IMPORTANTE: Retorna o NOME do próximo nó, não o estado!
    """
    tipo = estado["tipo"]
    print(f"[DECISÃO] Direcionando para caminho: {tipo}")
    return "par" if tipo == "par" else "impar"


# CONSTRUIR GRAFO COM CONDICIONAL
def criar_grafo_condicional():
    """Cria um grafo com ramificação condicional"""

    workflow = StateGraph(EstadoCondicional)

    # Adicionar nós
    workflow.add_node("classificar", classificar_numero)
    workflow.add_node("par", processar_par)
    workflow.add_node("impar", processar_impar)
    workflow.add_node("finalizar", finalizar_processamento)

    # Ponto de entrada
    workflow.set_entry_point("classificar")

    # ARESTA CONDICIONAL - a mágica acontece aqui!
    workflow.add_conditional_edges(
        "classificar",  # Nó de origem
        decidir_caminho,  # Função que decide o caminho
        {
            "par": "par",  # Se retornar "par", vai para nó "par"
            "impar": "impar"  # Se retornar "impar", vai para nó "impar"
        }
    )

    # Ambos os caminhos convergem para finalizar
    workflow.add_edge("par", "finalizar")
    workflow.add_edge("impar", "finalizar")
    workflow.add_edge("finalizar", END)

    return workflow.compile()


# EXEMPLO AVANÇADO: MÚLTIPLAS CONDIÇÕES
class EstadoMultiCondicional(TypedDict):
    valor: int
    categoria: str
    mensagem: str


def analisar_valor(estado: EstadoMultiCondicional) -> EstadoMultiCondicional:
    """Analisa o valor e determina a categoria"""
    valor = estado["valor"]

    if valor < 0:
        categoria = "negativo"
    elif valor == 0:
        categoria = "zero"
    elif valor < 10:
        categoria = "pequeno"
    elif valor < 100:
        categoria = "medio"
    else:
        categoria = "grande"

    print(f"[ANALISAR] Valor {valor} -> Categoria: {categoria}")
    return {"valor": valor, "categoria": categoria, "mensagem": ""}


def processar_negativo(estado: EstadoMultiCondicional) -> EstadoMultiCondicional:
    mensagem = f"Valor negativo: {estado['valor']} convertido para {abs(estado['valor'])}"
    return {"mensagem": mensagem, "categoria": estado["categoria"], "valor": estado["valor"]}


def processar_zero(estado: EstadoMultiCondicional) -> EstadoMultiCondicional:
    mensagem = "Valor é zero - neutro"
    return {"mensagem": mensagem, "categoria": estado["categoria"], "valor": estado["valor"]}


def processar_pequeno(estado: EstadoMultiCondicional) -> EstadoMultiCondicional:
    mensagem = f"Valor pequeno: {estado['valor']} (um dígito)"
    return {"mensagem": mensagem, "categoria": estado["categoria"], "valor": estado["valor"]}


def processar_medio(estado: EstadoMultiCondicional) -> EstadoMultiCondicional:
    mensagem = f"Valor médio: {estado['valor']} (dois dígitos)"
    return {"mensagem": mensagem, "categoria": estado["categoria"], "valor": estado["valor"]}


def processar_grande(estado: EstadoMultiCondicional) -> EstadoMultiCondicional:
    mensagem = f"Valor grande: {estado['valor']} (três ou mais dígitos)"
    return {"mensagem": mensagem, "categoria": estado["categoria"], "valor": estado["valor"]}


def rotear_por_categoria(estado: EstadoMultiCondicional) -> str:
    """Roteia baseado na categoria"""
    return estado["categoria"]


def criar_grafo_multicondicional():
    """Grafo com múltiplos caminhos condicionais"""

    workflow = StateGraph(EstadoMultiCondicional)

    # Nós
    workflow.add_node("analisar", analisar_valor)
    workflow.add_node("negativo", processar_negativo)
    workflow.add_node("zero", processar_zero)
    workflow.add_node("pequeno", processar_pequeno)
    workflow.add_node("medio", processar_medio)
    workflow.add_node("grande", processar_grande)

    workflow.set_entry_point("analisar")

    # Roteamento condicional com múltiplos caminhos
    workflow.add_conditional_edges(
        "analisar",
        rotear_por_categoria,
        {
            "negativo": "negativo",
            "zero": "zero",
            "pequeno": "pequeno",
            "medio": "medio",
            "grande": "grande"
        }
    )

    # Todos convergem para o fim
    for no in ["negativo", "zero", "pequeno", "medio", "grande"]:
        workflow.add_edge(no, END)

    return workflow.compile()


# EXECUTAR EXEMPLOS
if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLO 1: Classificador Par/Ímpar")
    print("=" * 60)

    app1 = criar_grafo_condicional()

    # Testar com número par
    print("\n--- Testando número PAR (42) ---")
    resultado1 = app1.invoke({"numero": 42, "tipo": "", "resultado": ""})
    print(f"Resultado: {resultado1['resultado']}\n")

    # Testar com número ímpar
    print("--- Testando número ÍMPAR (37) ---")
    resultado2 = app1.invoke({"numero": 37, "tipo": "", "resultado": ""})
    print(f"Resultado: {resultado2['resultado']}\n")

    print("\n" + "=" * 60)
    print("EXEMPLO 2: Múltiplas Categorias")
    print("=" * 60)

    app2 = criar_grafo_multicondicional()

    # Testar com vários valores
    valores_teste = [-5, 0, 7, 55, 999]

    for valor in valores_teste:
        print(f"\n--- Testando valor: {valor} ---")
        resultado = app2.invoke({"valor": valor, "categoria": "", "mensagem": ""})
        print(f"Resultado: {resultado['mensagem']}")

    print("\n" + "=" * 60)
    print("""
    EXERCÍCIO:
    1. Crie um grafo que classifica strings por tamanho (curta, média, longa)
    2. Adicione processamento diferente para cada categoria
    3. Teste com strings de diferentes tamanhos

    PRÓXIMO: 03_loops_e_recursao.py
    """)
    print("=" * 60)
