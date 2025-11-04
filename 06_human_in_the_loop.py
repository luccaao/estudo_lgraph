"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 6
Human-in-the-Loop: Supervisão Humana
===========================================

Um dos recursos mais importantes do LangGraph:
PAUSAR a execução para aprovação/input humano.

Casos de uso:
- Aprovar ações críticas (deletar, enviar email, fazer pagamento)
- Revisar planos antes de executar
- Fornecer informações adicionais
- Supervisionar decisões do agente

Este é ESSENCIAL para agentes em produção!
"""

import os
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import operator


# ===================================================================
# EXEMPLO 1: APROVAÇÃO SIMPLES
# ===================================================================
print("\n" + "="*70)
print("EXEMPLO 1: Aprovação Humana para Ações Críticas")
print("="*70)


class EstadoComAprovacao(TypedDict):
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    acao_proposta: str
    aprovado: bool


def agente_propor_acao(estado: EstadoComAprovacao):
    """
    Agente propõe uma ação que precisa de aprovação.
    """
    print("\n🤖 [AGENTE] Analisando situação e propondo ação...")

    # Simular análise
    acao = "Deletar 1.5GB de arquivos temporários"

    print(f"   💡 Ação proposta: {acao}")
    print("   ⏸️  PAUSANDO para aprovação humana...")

    return {
        "acao_proposta": acao,
        "mensagens": [AIMessage(content=f"Propondo: {acao}")]
    }


def aguardar_aprovacao(estado: EstadoComAprovacao):
    """
    Nó que representa a aprovação humana.

    No LangGraph real, você usaria interrupt_before ou interrupt_after
    para pausar aqui e aguardar input do usuário.
    """
    print("\n⏸️  [AGUARDANDO] Esperando aprovação humana...")
    print(f"   Ação: {estado['acao_proposta']}")

    # Em produção, aqui o grafo PAUSA
    # O usuário vê a ação e aprova/rejeita
    # Por enquanto, simularemos aprovação automática

    print("   [SIMULADO] Usuário aprovou!")

    return {"aprovado": True}


def executar_acao(estado: EstadoComAprovacao):
    """
    Executa a ação após aprovação.
    """
    if not estado.get("aprovado", False):
        print("\n❌ [EXECUÇÃO] Ação não aprovada, cancelando...")
        return {
            "mensagens": [AIMessage(content="Ação cancelada pelo usuário.")]
        }

    print("\n✅ [EXECUÇÃO] Executando ação aprovada...")
    print(f"   {estado['acao_proposta']}")

    return {
        "mensagens": [AIMessage(content=f"Ação executada: {estado['acao_proposta']}")]
    }


def criar_fluxo_com_aprovacao():
    """Fluxo que requer aprovação humana"""

    workflow = StateGraph(EstadoComAprovacao)

    workflow.add_node("propor", agente_propor_acao)
    workflow.add_node("aprovar", aguardar_aprovacao)
    workflow.add_node("executar", executar_acao)

    workflow.set_entry_point("propor")
    workflow.add_edge("propor", "aprovar")
    workflow.add_edge("aprovar", "executar")
    workflow.add_edge("executar", END)

    # Com checkpointer, podemos pausar e retomar
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


print("\n🧪 Testando fluxo com aprovação...")

app = criar_fluxo_com_aprovacao()

resultado = app.invoke(
    {
        "mensagens": [HumanMessage(content="Limpe arquivos temporários")],
        "acao_proposta": "",
        "aprovado": False
    },
    {"configurable": {"thread_id": "teste-1"}}
)

print(f"\n✅ Resultado: {resultado['mensagens'][-1].content}")


# ===================================================================
# EXEMPLO 2: EDIÇÃO DE PLANO
# ===================================================================
print("\n\n" + "="*70)
print("EXEMPLO 2: Humano Pode Editar o Plano do Agente")
print("="*70)


class EstadoPlanejamento(TypedDict):
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    plano: list[str]
    plano_aprovado: bool


def criar_plano(estado: EstadoPlanejamento):
    """
    Agente cria um plano de ação.
    """
    print("\n🤖 [AGENTE] Criando plano de ação...")

    if not os.getenv("OPENAI_API_KEY"):
        # Plano simulado
        plano = [
            "1. Analisar requisitos",
            "2. Desenhar arquitetura",
            "3. Implementar features",
            "4. Testar",
            "5. Deploy"
        ]
    else:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

        ultima_msg = estado["mensagens"][-1].content

        prompt = f"""
Crie um plano detalhado para: {ultima_msg}

Retorne como uma lista numerada de passos.
Máximo 5 passos.
"""

        resposta = llm.invoke([HumanMessage(content=prompt)])
        plano = resposta.content.strip().split("\n")

    print("\n📋 PLANO CRIADO:")
    for passo in plano:
        print(f"   {passo}")

    print("\n⏸️  PAUSANDO para revisão humana...")
    print("   (Humano pode editar/aprovar o plano)")

    return {
        "plano": plano,
        "mensagens": [AIMessage(content="Plano criado, aguardando aprovação")]
    }


def revisar_plano(estado: EstadoPlanejamento):
    """
    Ponto de interrupção para humano revisar/editar plano.
    """
    print("\n👤 [HUMANO REVISANDO] ...")

    # Simular aprovação
    print("   ✅ Plano aprovado!")

    # Humano poderia editar o plano aqui:
    # plano_editado = estado["plano"] + ["6. Documentar"]

    return {"plano_aprovado": True}


def executar_plano(estado: EstadoPlanejamento):
    """
    Executa o plano aprovado.
    """
    print("\n⚡ [EXECUÇÃO] Executando plano...")

    for i, passo in enumerate(estado["plano"], 1):
        print(f"   ✓ Executando: {passo}")

    return {
        "mensagens": [AIMessage(content="Plano executado com sucesso!")]
    }


def criar_sistema_planejamento():
    """Sistema com planejamento aprovado por humano"""

    workflow = StateGraph(EstadoPlanejamento)

    workflow.add_node("criar_plano", criar_plano)
    workflow.add_node("revisar", revisar_plano)
    workflow.add_node("executar", executar_plano)

    workflow.set_entry_point("criar_plano")
    workflow.add_edge("criar_plano", "revisar")
    workflow.add_edge("revisar", "executar")
    workflow.add_edge("executar", END)

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


print("\n🧪 Testando sistema de planejamento...")

app_plan = criar_sistema_planejamento()

resultado = app_plan.invoke(
    {
        "mensagens": [HumanMessage(content="Criar um sistema de autenticação")],
        "plano": [],
        "plano_aprovado": False
    },
    {"configurable": {"thread_id": "plan-1"}}
)


# ===================================================================
# EXEMPLO 3: INTERRUPÇÃO EM QUALQUER PONTO (REAL)
# ===================================================================
print("\n\n" + "="*70)
print("EXEMPLO 3: Interrupção Real com interrupt_before")
print("="*70)
print("""
No LangGraph, você pode usar:

1. interrupt_before=["nome_do_no"]
   - Pausa ANTES de executar esse nó
   - Permite revisar estado antes da ação

2. interrupt_after=["nome_do_no"]
   - Pausa DEPOIS de executar esse nó
   - Permite revisar resultado

Exemplo de código real:
""")

print("""
```python
from langgraph.checkpoint.memory import MemorySaver

def criar_agente_com_interrupcao():
    workflow = StateGraph(Estado)

    workflow.add_node("analisar", analisar)
    workflow.add_node("executar", executar)  # Ação crítica

    workflow.set_entry_point("analisar")
    workflow.add_edge("analisar", "executar")
    workflow.add_edge("executar", END)

    memory = MemorySaver()

    # 🔑 CHAVE: interrupt_before pausa antes de executar
    app = workflow.compile(
        checkpointer=memory,
        interrupt_before=["executar"]  # Pausa aqui!
    )

    return app


# Usar o agente
config = {"configurable": {"thread_id": "user-123"}}

# Primeira execução: vai parar em "executar"
for event in app.stream(input_inicial, config):
    print(event)
    # ... grafo pausou!

# Humano revisa o estado
state = app.get_state(config)
print(f"Estado atual: {state.values}")
print(f"Próximo nó: {state.next}")  # ["executar"]

# Humano pode:
# 1. Continuar: app.stream(None, config)
# 2. Modificar estado: app.update_state(config, novo_estado)
# 3. Cancelar: não chamar stream novamente

# Continuar execução
for event in app.stream(None, config):
    print(event)
    # ... agora executa "executar" e termina
```
""")


# ===================================================================
# EXEMPLO 4: MODIFICAR ESTADO DURANTE INTERRUPÇÃO
# ===================================================================
print("\n\n" + "="*70)
print("EXEMPLO 4: Humano Modifica Estado Durante Pausa")
print("="*70)
print("""
Durante a interrupção, você pode modificar o estado:

```python
# Agente parou para aprovação
config = {"configurable": {"thread_id": "user-123"}}

# Ver estado atual
state = app.get_state(config)
print(state.values["acao_proposta"])  # "Deletar tudo"

# Humano modifica a ação
novo_estado = {
    "acao_proposta": "Deletar apenas arquivos .tmp",
    "aprovado": True
}

# Atualizar estado
app.update_state(config, novo_estado)

# Continuar execução com novo estado
for event in app.stream(None, config):
    print(event)
    # Executa a ação MODIFICADA
```
""")


# ===================================================================
# EXEMPLO PRÁTICO: AGENTE QUE ENVIA EMAIL
# ===================================================================
print("\n\n" + "="*70)
print("EXEMPLO PRÁTICO: Agente que Envia Email (com aprovação)")
print("="*70)


class EstadoEmail(TypedDict):
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    email_draft: str
    destinatario: str
    aprovado: bool


def redigir_email(estado: EstadoEmail):
    """Agente redige um email"""
    print("\n✍️  [AGENTE] Redigindo email...")

    if not os.getenv("OPENAI_API_KEY"):
        draft = """
Olá [Nome],

Espero que esteja bem. Gostaria de agendar uma reunião para
discutir o projeto. Você tem disponibilidade esta semana?

Atenciosamente,
Seu nome
"""
        destinatario = "cliente@empresa.com"
    else:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        contexto = estado["mensagens"][-1].content

        prompt = f"""
Redija um email profissional para: {contexto}

Retorne apenas o corpo do email.
"""

        resposta = llm.invoke([HumanMessage(content=prompt)])
        draft = resposta.content
        destinatario = "cliente@empresa.com"

    print(f"\n📧 DRAFT CRIADO:")
    print(f"Para: {destinatario}")
    print(f"{draft[:100]}...")

    return {
        "email_draft": draft,
        "destinatario": destinatario,
        "mensagens": [AIMessage(content="Email redigido")]
    }


def revisar_email(estado: EstadoEmail):
    """Humano revisa o email"""
    print("\n👤 [HUMANO] Revisando email...")
    print("   (Aqui você poderia mostrar uma UI para editar)")

    # Simular aprovação
    print("   ✅ Aprovado!")

    return {"aprovado": True}


def enviar_email(estado: EstadoEmail):
    """Envia o email (simulado)"""
    if not estado.get("aprovado", False):
        print("\n❌ Email não enviado (não aprovado)")
        return {"mensagens": [AIMessage(content="Email cancelado")]}

    print("\n📤 [ENVIANDO EMAIL]...")
    print(f"   Para: {estado['destinatario']}")
    print(f"   ✅ Email enviado!")

    return {"mensagens": [AIMessage(content="Email enviado com sucesso")]}


def criar_agente_email():
    """Agente de email com aprovação humana"""

    workflow = StateGraph(EstadoEmail)

    workflow.add_node("redigir", redigir_email)
    workflow.add_node("revisar", revisar_email)
    workflow.add_node("enviar", enviar_email)

    workflow.set_entry_point("redigir")
    workflow.add_edge("redigir", "revisar")
    workflow.add_edge("revisar", "enviar")
    workflow.add_edge("enviar", END)

    memory = MemorySaver()

    # Em produção, usaríamos:
    # return workflow.compile(checkpointer=memory, interrupt_before=["enviar"])

    return workflow.compile(checkpointer=memory)


print("\n🧪 Testando agente de email...")

agente_email = criar_agente_email()

resultado = agente_email.invoke(
    {
        "mensagens": [HumanMessage(content="Agendar reunião com cliente")],
        "email_draft": "",
        "destinatario": "",
        "aprovado": False
    },
    {"configurable": {"thread_id": "email-1"}}
)


# ===================================================================
# RESUMO
# ===================================================================
print("\n\n" + "="*70)
print("📚 RESUMO - O QUE VOCÊ APRENDEU")
print("="*70)
print("""
✅ Human-in-the-Loop é ESSENCIAL para:
   - Ações críticas (deletar, enviar, pagar)
   - Revisão de planos antes de executar
   - Fornecer informações que agente não tem
   - Supervisionar decisões importantes

✅ Como implementar:
   - interrupt_before=["nó"]: Pausa antes do nó
   - interrupt_after=["nó"]: Pausa depois do nó
   - Checkpointer: Necessário para pausar/retomar
   - thread_id: Mantém estado entre pausas

✅ Durante a pausa, você pode:
   - Ver estado atual: app.get_state(config)
   - Modificar estado: app.update_state(config, novo)
   - Continuar: app.stream(None, config)
   - Cancelar: simplesmente não continuar

✅ Casos de uso reais:
   - Chatbots que precisam confirmação
   - Agentes que fazem mudanças no sistema
   - Workflows que requerem aprovação
   - Sistemas de automação com supervisão

🎯 PRÓXIMO PASSO: 07_casos_praticos.py
   - RAG Agent: Agente que consulta documentos
   - Code Agent: Agente que escreve e executa código
   - Research Agent: Agente que pesquisa na web
   - Data Analysis Agent: Agente que analisa dados
""")

print("\n" + "="*70)
print("💡 EXERCÍCIO")
print("="*70)
print("""
Crie um agente de aprovação de despesas:

1. Agente analisa a despesa e categoria
2. Se < R$100: aprova automaticamente
3. Se >= R$100: pausa para aprovação humana
4. Humano pode aprovar, rejeitar ou modificar valor
5. Agente processa a decisão

Use interrupt_before para pausar na aprovação!
""")
