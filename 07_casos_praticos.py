"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 7
Casos Práticos e Aplicações Reais
===========================================

Exemplos práticos e completos que você pode usar como base
para seus próprios projetos.
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
import operator
from datetime import datetime
import re


# ===========================================
# CASO 1: ASSISTENTE DE ATENDIMENTO AO CLIENTE
# ===========================================

class EstadoAtendimento(TypedDict):
    mensagem_cliente: str
    categoria: str
    prioridade: str
    informacoes_coletadas: dict
    solucao: str
    satisfacao: int
    historico: Annotated[list, operator.add]


def classificar_solicitacao(estado: EstadoAtendimento) -> EstadoAtendimento:
    """Classifica a solicitação do cliente"""
    mensagem = estado["mensagem_cliente"].lower()

    # Classificação por palavras-chave
    if any(palavra in mensagem for palavra in ["urgente", "crítico", "parado"]):
        prioridade = "alta"
    elif any(palavra in mensagem for palavra in ["importante", "preciso"]):
        prioridade = "media"
    else:
        prioridade = "baixa"

    # Categorização
    if any(palavra in mensagem for palavra in ["não consigo", "erro", "problema"]):
        categoria = "tecnico"
    elif any(palavra in mensagem for palavra in ["cobrança", "pagamento", "fatura"]):
        categoria = "financeiro"
    elif any(palavra in mensagem for palavra in ["cancelar", "desistir"]):
        categoria = "cancelamento"
    else:
        categoria = "geral"

    print(f"[CLASSIFICAÇÃO] Categoria: {categoria} | Prioridade: {prioridade}")

    return {
        **estado,
        "categoria": categoria,
        "prioridade": prioridade,
        "historico": [f"Classificado como {categoria} - prioridade {prioridade}"]
    }


def coletar_informacoes(estado: EstadoAtendimento) -> EstadoAtendimento:
    """Coleta informações necessárias baseado na categoria"""
    categoria = estado["categoria"]
    mensagem = estado["mensagem_cliente"]

    info = {}

    # Extrai informações relevantes
    if categoria == "tecnico":
        # Procura por códigos de erro
        erro_match = re.search(r'erro\s*(\d+|[A-Z]+\d+)', mensagem, re.IGNORECASE)
        if erro_match:
            info["codigo_erro"] = erro_match.group(1)
        info["tipo"] = "Suporte Técnico"

    elif categoria == "financeiro":
        # Procura por valores
        valor_match = re.search(r'R?\$?\s*(\d+[.,]?\d*)', mensagem)
        if valor_match:
            info["valor"] = valor_match.group(1)
        info["tipo"] = "Financeiro"

    elif categoria == "cancelamento":
        info["tipo"] = "Retenção"
        info["motivo"] = "solicitacao_cancelamento"

    else:
        info["tipo"] = "Geral"

    print(f"[COLETA] Informações: {info}")

    return {
        **estado,
        "informacoes_coletadas": info,
        "historico": [f"Informações coletadas: {list(info.keys())}"]
    }


def gerar_solucao(estado: EstadoAtendimento) -> EstadoAtendimento:
    """Gera solução baseada na categoria"""
    categoria = estado["categoria"]
    info = estado["informacoes_coletadas"]

    # Base de conhecimento de soluções
    solucoes = {
        "tecnico": "1. Limpe o cache\n2. Reinicie o aplicativo\n3. Verifique sua conexão",
        "financeiro": "Verifique em Minha Conta > Faturas. Em caso de dúvida, contate o financeiro.",
        "cancelamento": "Entendemos sua preocupação. Podemos oferecer 20% de desconto nos próximos 3 meses.",
        "geral": "Nossa equipe irá analisar sua solicitação e retornar em até 24h."
    }

    solucao = solucoes.get(categoria, solucoes["geral"])

    print(f"[SOLUÇÃO] {categoria.upper()}")
    print(f"{solucao}")

    return {
        **estado,
        "solucao": solucao,
        "historico": [f"Solução gerada para {categoria}"]
    }


def verificar_satisfacao(estado: EstadoAtendimento) -> EstadoAtendimento:
    """Simula verificação de satisfação"""
    import random

    # Em produção, aqui você pediria feedback real
    satisfacao = random.randint(3, 5)  # Simula nota de 1-5

    print(f"[SATISFAÇÃO] Cliente avaliou com {satisfacao}/5 estrelas")

    return {
        **estado,
        "satisfacao": satisfacao,
        "historico": [f"Avaliação: {satisfacao}/5"]
    }


def decidir_escalonamento(estado: EstadoAtendimento) -> Literal["escalonar", "finalizar"]:
    """Decide se escala para humano"""
    prioridade = estado["prioridade"]
    satisfacao = estado.get("satisfacao", 5)

    if prioridade == "alta" or satisfacao <= 2:
        print("[DECISÃO] Escalonando para atendente humano")
        return "escalonar"
    else:
        return "finalizar"


def escalonar_humano(estado: EstadoAtendimento) -> EstadoAtendimento:
    """Escala para atendente humano"""
    print("[ESCALONAMENTO] Transferindo para atendente humano...")
    print(f"Contexto: {estado['categoria']} - {estado['prioridade']}")
    print(f"Histórico: {len(estado.get('historico', []))} interações")

    return {
        **estado,
        "historico": ["Escalonado para humano"]
    }


def criar_assistente_atendimento():
    """Cria assistente de atendimento ao cliente"""

    workflow = StateGraph(EstadoAtendimento)

    workflow.add_node("classificar", classificar_solicitacao)
    workflow.add_node("coletar", coletar_informacoes)
    workflow.add_node("solucao", gerar_solucao)
    workflow.add_node("satisfacao", verificar_satisfacao)
    workflow.add_node("escalonar", escalonar_humano)

    workflow.set_entry_point("classificar")
    workflow.add_edge("classificar", "coletar")
    workflow.add_edge("coletar", "solucao")
    workflow.add_edge("solucao", "satisfacao")

    workflow.add_conditional_edges(
        "satisfacao",
        decidir_escalonamento,
        {
            "escalonar": "escalonar",
            "finalizar": END
        }
    )

    workflow.add_edge("escalonar", END)

    return workflow.compile()


# ===========================================
# CASO 2: SISTEMA DE APROVAÇÃO DE CRÉDITO
# ===========================================

class EstadoCredito(TypedDict):
    cpf: str
    valor_solicitado: float
    renda_mensal: float
    score_credito: int
    dividas_ativas: float
    status: str
    limite_aprovado: float
    motivo: str
    analises: list


def validar_dados(estado: EstadoCredito) -> EstadoCredito:
    """Valida dados básicos"""
    print("[VALIDAÇÃO] Verificando dados do cliente...")

    cpf = estado["cpf"]
    renda = estado["renda_mensal"]

    # Validação simplificada
    if len(cpf) != 11 or not cpf.isdigit():
        return {
            **estado,
            "status": "recusado",
            "motivo": "CPF inválido"
        }

    if renda <= 0:
        return {
            **estado,
            "status": "recusado",
            "motivo": "Renda não informada"
        }

    print("[VALIDAÇÃO] Dados válidos ✓")
    return {
        **estado,
        "analises": ["Dados validados"]
    }


def consultar_score(estado: EstadoCredito) -> EstadoCredito:
    """Simula consulta a bureau de crédito"""
    import random

    print("[BUREAU] Consultando score de crédito...")

    # Simula score (em produção, chamaria API real)
    score = random.randint(300, 900)

    print(f"[BUREAU] Score obtido: {score}")

    return {
        **estado,
        "score_credito": score,
        "analises": estado.get("analises", []) + [f"Score: {score}"]
    }


def analisar_capacidade(estado: EstadoCredito) -> EstadoCredito:
    """Analisa capacidade de pagamento"""
    print("[ANÁLISE] Calculando capacidade de pagamento...")

    renda = estado["renda_mensal"]
    dividas = estado["dividas_ativas"]
    valor_solicitado = estado["valor_solicitado"]

    # Cálculo de capacidade (30% da renda disponível)
    renda_disponivel = renda - dividas
    capacidade = renda_disponivel * 0.3

    # Calcula parcela estimada (12 meses)
    parcela_estimada = valor_solicitado / 12

    print(f"[ANÁLISE] Capacidade: R$ {capacidade:.2f}")
    print(f"[ANÁLISE] Parcela estimada: R$ {parcela_estimada:.2f}")

    return {
        **estado,
        "analises": estado.get("analises", []) + [
            f"Capacidade: R$ {capacidade:.2f}",
            f"Parcela: R$ {parcela_estimada:.2f}"
        ]
    }


def decidir_credito(estado: EstadoCredito) -> EstadoCredito:
    """Decisão final de crédito"""
    print("[DECISÃO] Analisando solicitação...")

    score = estado["score_credito"]
    valor_solicitado = estado["valor_solicitado"]
    renda = estado["renda_mensal"]
    dividas = estado["dividas_ativas"]

    # Regras de negócio
    if score < 400:
        status = "recusado"
        limite = 0
        motivo = "Score de crédito insuficiente"

    elif dividas > renda * 0.5:
        status = "recusado"
        limite = 0
        motivo = "Endividamento elevado"

    elif valor_solicitado > renda * 3:
        status = "aprovado_parcial"
        limite = renda * 3
        motivo = f"Aprovado limite de R$ {limite:.2f} (menor que solicitado)"

    else:
        status = "aprovado"
        limite = valor_solicitado
        motivo = "Crédito aprovado conforme solicitado"

    print(f"[DECISÃO] Status: {status}")
    print(f"[DECISÃO] {motivo}")

    return {
        **estado,
        "status": status,
        "limite_aprovado": limite,
        "motivo": motivo
    }


def criar_sistema_credito():
    """Cria sistema de análise de crédito"""

    workflow = StateGraph(EstadoCredito)

    workflow.add_node("validar", validar_dados)
    workflow.add_node("score", consultar_score)
    workflow.add_node("capacidade", analisar_capacidade)
    workflow.add_node("decidir", decidir_credito)

    workflow.set_entry_point("validar")
    workflow.add_edge("validar", "score")
    workflow.add_edge("score", "capacidade")
    workflow.add_edge("capacidade", "decidir")
    workflow.add_edge("decidir", END)

    return workflow.compile()


# ===========================================
# CASO 3: PROCESSADOR DE DOCUMENTOS
# ===========================================

class EstadoDocumento(TypedDict):
    arquivo: str
    tipo_documento: str
    texto_extraido: str
    entidades: dict
    validacao: dict
    status: str


def detectar_tipo(estado: EstadoDocumento) -> EstadoDocumento:
    """Detecta tipo do documento"""
    arquivo = estado["arquivo"].lower()

    if "rg" in arquivo or "identidade" in arquivo:
        tipo = "rg"
    elif "cpf" in arquivo:
        tipo = "cpf"
    elif "comprovante" in arquivo and "renda" in arquivo:
        tipo = "comprovante_renda"
    elif "comprovante" in arquivo and "residencia" in arquivo:
        tipo = "comprovante_residencia"
    else:
        tipo = "desconhecido"

    print(f"[DETECÇÃO] Tipo identificado: {tipo}")

    return {
        **estado,
        "tipo_documento": tipo
    }


def extrair_texto(estado: EstadoDocumento) -> EstadoDocumento:
    """Simula extração de texto (OCR)"""
    print(f"[OCR] Extraindo texto de {estado['arquivo']}...")

    # Simulação de texto extraído
    textos_simulados = {
        "rg": "IDENTIDADE\nNome: JOÃO DA SILVA\nRG: 12.345.678-9\nData Nasc: 01/01/1990",
        "cpf": "CPF\n123.456.789-00\nJOÃO DA SILVA",
        "comprovante_renda": "CONTRACHEQUE\nSalário: R$ 5.000,00\nFuncionário: JOÃO DA SILVA",
        "comprovante_residencia": "CONTA DE LUZ\nEndereço: Rua A, 123\nJOÃO DA SILVA"
    }

    texto = textos_simulados.get(estado["tipo_documento"], "Texto não identificado")

    print(f"[OCR] Texto extraído: {len(texto)} caracteres")

    return {
        **estado,
        "texto_extraido": texto
    }


def extrair_entidades(estado: EstadoDocumento) -> EstadoDocumento:
    """Extrai entidades do texto"""
    print("[NER] Extraindo entidades...")

    texto = estado["texto_extraido"]
    tipo = estado["tipo_documento"]

    entidades = {}

    # Expressões regulares simples para extração
    if tipo == "rg":
        rg_match = re.search(r'RG:\s*([\d.-]+)', texto)
        nome_match = re.search(r'Nome:\s*([A-Z\s]+)', texto)
        data_match = re.search(r'Data Nasc:\s*(\d{2}/\d{2}/\d{4})', texto)

        if rg_match:
            entidades["rg"] = rg_match.group(1)
        if nome_match:
            entidades["nome"] = nome_match.group(1).strip()
        if data_match:
            entidades["data_nascimento"] = data_match.group(1)

    elif tipo == "cpf":
        cpf_match = re.search(r'(\d{3}\.\d{3}\.\d{3}-\d{2})', texto)
        if cpf_match:
            entidades["cpf"] = cpf_match.group(1)

    elif tipo == "comprovante_renda":
        salario_match = re.search(r'R?\$\s*([\d.,]+)', texto)
        if salario_match:
            entidades["renda"] = salario_match.group(1)

    print(f"[NER] Entidades extraídas: {list(entidades.keys())}")

    return {
        **estado,
        "entidades": entidades
    }


def validar_documento(estado: EstadoDocumento) -> EstadoDocumento:
    """Valida documento extraído"""
    print("[VALIDAÇÃO] Verificando documento...")

    entidades = estado["entidades"]
    tipo = estado["tipo_documento"]

    validacao = {"valido": False, "motivos": []}

    if tipo == "rg":
        if "rg" in entidades and "nome" in entidades:
            validacao["valido"] = True
        else:
            validacao["motivos"].append("Dados incompletos no RG")

    elif tipo == "cpf":
        if "cpf" in entidades:
            validacao["valido"] = True
        else:
            validacao["motivos"].append("CPF não identificado")

    elif tipo == "comprovante_renda":
        if "renda" in entidades:
            validacao["valido"] = True
        else:
            validacao["motivos"].append("Valor da renda não identificado")

    else:
        validacao["motivos"].append("Tipo de documento não suportado")

    status = "aprovado" if validacao["valido"] else "rejeitado"

    print(f"[VALIDAÇÃO] Status: {status}")
    if not validacao["valido"]:
        for motivo in validacao["motivos"]:
            print(f"  - {motivo}")

    return {
        **estado,
        "validacao": validacao,
        "status": status
    }


def criar_processador_documentos():
    """Cria processador de documentos"""

    workflow = StateGraph(EstadoDocumento)

    workflow.add_node("detectar", detectar_tipo)
    workflow.add_node("ocr", extrair_texto)
    workflow.add_node("ner", extrair_entidades)
    workflow.add_node("validar", validar_documento)

    workflow.set_entry_point("detectar")
    workflow.add_edge("detectar", "ocr")
    workflow.add_edge("ocr", "ner")
    workflow.add_edge("ner", "validar")
    workflow.add_edge("validar", END)

    return workflow.compile()


# EXECUTAR EXEMPLOS
if __name__ == "__main__":
    print("=" * 80)
    print("CASO PRÁTICO 1: Assistente de Atendimento ao Cliente")
    print("=" * 80)

    app1 = criar_assistente_atendimento()

    casos_teste = [
        "Estou com problema urgente, erro 404 no sistema",
        "Não entendi minha cobrança de R$ 150,00",
        "Quero cancelar minha assinatura"
    ]

    for i, caso in enumerate(casos_teste, 1):
        print(f"\n{'='*70}")
        print(f"CASO {i}: {caso}")
        print('='*70)

        resultado = app1.invoke({
            "mensagem_cliente": caso,
            "categoria": "",
            "prioridade": "",
            "informacoes_coletadas": {},
            "solucao": "",
            "satisfacao": 0,
            "historico": []
        })

        print(f"\n[RESUMO]")
        print(f"Categoria: {resultado['categoria']}")
        print(f"Prioridade: {resultado['prioridade']}")
        print(f"Solução: {resultado['solucao'][:50]}...")

    print("\n" + "=" * 80)
    print("CASO PRÁTICO 2: Sistema de Aprovação de Crédito")
    print("=" * 80)

    app2 = criar_sistema_credito()

    clientes_teste = [
        {"cpf": "12345678901", "valor_solicitado": 10000, "renda_mensal": 5000, "dividas_ativas": 1000},
        {"cpf": "98765432100", "valor_solicitado": 50000, "renda_mensal": 8000, "dividas_ativas": 5000},
    ]

    for i, cliente in enumerate(clientes_teste, 1):
        print(f"\n{'='*70}")
        print(f"CLIENTE {i}")
        print('='*70)
        print(f"Valor solicitado: R$ {cliente['valor_solicitado']:.2f}")
        print(f"Renda mensal: R$ {cliente['renda_mensal']:.2f}")

        resultado = app2.invoke({
            **cliente,
            "score_credito": 0,
            "status": "",
            "limite_aprovado": 0,
            "motivo": "",
            "analises": []
        })

        print(f"\n[DECISÃO FINAL]")
        print(f"Status: {resultado['status']}")
        print(f"Limite: R$ {resultado['limite_aprovado']:.2f}")
        print(f"Motivo: {resultado['motivo']}")

    print("\n" + "=" * 80)
    print("CASO PRÁTICO 3: Processador de Documentos")
    print("=" * 80)

    app3 = criar_processador_documentos()

    documentos_teste = [
        "documento_rg_frente.pdf",
        "comprovante_renda_2024.pdf",
        "comprovante_residencia.pdf"
    ]

    for doc in documentos_teste:
        print(f"\n{'='*70}")
        print(f"DOCUMENTO: {doc}")
        print('='*70)

        resultado = app3.invoke({
            "arquivo": doc,
            "tipo_documento": "",
            "texto_extraido": "",
            "entidades": {},
            "validacao": {},
            "status": ""
        })

        print(f"\n[RESULTADO]")
        print(f"Tipo: {resultado['tipo_documento']}")
        print(f"Entidades: {list(resultado['entidades'].keys())}")
        print(f"Status: {resultado['status']}")

    print("\n" + "=" * 80)
    print("""
    CASOS PRÁTICOS IMPLEMENTADOS:

    1. ATENDIMENTO AO CLIENTE
       - Classificação automática
       - Roteamento inteligente
       - Escalonamento quando necessário

    2. ANÁLISE DE CRÉDITO
       - Validação de dados
       - Consulta a bureaus
       - Decisão automatizada

    3. PROCESSAMENTO DE DOCUMENTOS
       - OCR (extração de texto)
       - NER (extração de entidades)
       - Validação automática

    PRÓXIMOS PASSOS:
    - Integre com APIs reais
    - Adicione persistência
    - Implemente logging
    - Crie dashboards de monitoramento

    PARABÉNS! Você completou o estudo guiado de LangGraph!
    """)
    print("=" * 80)
