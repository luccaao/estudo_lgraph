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





# EXEMPLO AVANÇADO: MÚLTIPLAS CONDIÇÕES
class EstadoMultiCondicional(TypedDict):
    valor: int
    categoria: str
    mensagem: str
    
class ClassificarString(TypedDict):
    texto: str
    categoria: str
    mensagem: str



def analisar_string(estado: ClassificarString) -> ClassificarString:
    """Analisa o valor e determina a categoria"""
    texto = estado["texto"]
    tamanho = len(texto)

    if tamanho < 5:
        categoria = "curta"
    elif tamanho <= 10:
        categoria = "media"
    else:
        categoria = "longa"

    print(f"[ANALISAR] Texto '{texto}' -> Categoria: {categoria}")
    return {"texto": texto, "categoria": categoria, "mensagem": ""}




def processar_string_curta(estado: ClassificarString) -> ClassificarString:
    mensagem = f"String curta: '{estado['texto']}'"
    return {"texto": estado["texto"], "categoria": estado["categoria"], "mensagem": mensagem}


def processar_string_media(estado: ClassificarString) -> ClassificarString:
    
    mensagem = f"String média: '{estado['texto']}'"
    return {"texto": estado["texto"], "categoria": estado["categoria"], "mensagem": mensagem}


def processar_string_longa(estado: ClassificarString) -> ClassificarString:
    mensagem = f"String longa: '{estado['texto']}'"
    return {"texto": estado["texto"], "categoria": estado["categoria"], "mensagem": mensagem}


def processar_string_curta(estado: ClassificarString) -> ClassificarString: 
    mensagem = f"String curta: '{estado['texto']}'"
    return {"texto": estado["texto"], "categoria": estado["categoria"], "mensagem": mensagem}

def processar_string_media(estado: ClassificarString) -> ClassificarString:
    mensagem = f"String média: '{estado['texto']}'"
    return {"texto": estado["texto"], "categoria": estado["categoria"], "mensagem": mensagem}


def processar_string_longa(estado: ClassificarString) -> ClassificarString:
    mensagem = f"String longa: '{estado['texto']}'"
    return {"texto": estado["texto"], "categoria": estado["categoria"], "mensagem": mensagem}




def rotear_por_categoria(estado: EstadoMultiCondicional) -> str:
    """Roteia baseado na categoria"""
    return estado["categoria"]


def criar_grafo_multicondicional():
    """Grafo com múltiplos caminhos condicionais"""

    workflow = StateGraph(ClassificarString)

    # Nós
    workflow.add_node("analisar", analisar_string)
    workflow.add_node("curta", processar_string_curta)
    workflow.add_node("media", processar_string_media)
    workflow.add_node("longa", processar_string_longa)

    workflow.set_entry_point("analisar")

    # Roteamento condicional com múltiplos caminhos
    workflow.add_conditional_edges(
        "analisar",
        rotear_por_categoria,
        {
            "curta": "curta",
            "media": "media",
            "longa": "longa"
        
        }
    )

    # Todos convergem para o fim
    for no in ["curta", "media", "longa"]:
        workflow.add_edge(no, END)

    return workflow.compile()


# EXECUTAR EXEMPLOS
if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLO 1: Classificador Par/Ímpar")
    print("=" * 60)

    # Testar com número par
 

  
    app2 = criar_grafo_multicondicional()

    # Testar com vários valores
    valores_teste = ["Olá", "Isto é um teste", "Pequeno", "Médio", "Um texto mupassa os dez caracteres"]

    for valor in valores_teste:
        print(f"\n--- Testando valor: {valor} ---")
        resultado = app2.invoke({"texto": valor, "categoria": "", "mensagem": ""})
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
