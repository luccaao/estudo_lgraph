"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 3
Agente Conversacional com Memória
===========================================

Aprenda a criar agentes que:
- Mantêm memória entre conversas
- Usam checkpoints para persistência
- Funcionam como chatbots inteligentes
- Lembram do contexto anterior
"""

import os
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import operator


# ===================================================================
# PARTE 1: FERRAMENTAS PARA O AGENTE CONVERSACIONAL
# ===================================================================
print("\n" + "="*70)
print("PARTE 1: Ferramentas do Agente Conversacional")
print("="*70)

@tool
def salvar_nota(titulo: str, conteudo: str) -> str:
    """
    Salva uma nota/lembrete do usuário.

    Args:
        titulo: Título da nota
        conteudo: Conteúdo da nota
    """
    print(f"📝 [TOOL: salvar_nota] Salvando '{titulo}'...")
    # Em produção, salvaria em banco de dados
    return f"Nota '{titulo}' salva com sucesso!"


@tool
def buscar_informacao_usuario(campo: str) -> str:
    """
    Busca informações sobre o usuário (simulado).

    Args:
        campo: Campo a buscar (nome, email, cidade, etc)
    """
    print(f"👤 [TOOL: buscar_informacao] Buscando {campo}...")

    # Simulando banco de dados de usuário
    dados_usuario = {
        "nome": "João Silva",
        "email": "joao@email.com",
        "cidade": "São Paulo",
        "profissao": "Desenvolvedor"
    }

    return dados_usuario.get(campo.lower(), "Informação não encontrada")


@tool
def agendar_lembrete(quando: str, mensagem: str) -> str:
    """
    Agenda um lembrete para o usuário.

    Args:
        quando: Quando o lembrete deve disparar (ex: "amanhã 14h")
        mensagem: Mensagem do lembrete
    """
    print(f"⏰ [TOOL: agendar_lembrete] Agendando para {quando}...")
    return f"Lembrete agendado: '{mensagem}' para {quando}"


ferramentas = [salvar_nota, buscar_informacao_usuario, agendar_lembrete]


# ===================================================================
# PARTE 2: ESTADO COM SISTEMA DE MENSAGENS
# ===================================================================
print("\n" + "="*70)
print("PARTE 2: Estado do Agente Conversacional")
print("="*70)

class EstadoConversacional(TypedDict):
    """
    Estado completo do agente conversacional.

    A diferença aqui é que usaremos checkpoints para
    salvar o estado entre diferentes conversas.
    """
    mensagens: Annotated[Sequence[BaseMessage], operator.add]


# ===================================================================
# PARTE 3: NÓS DO AGENTE
# ===================================================================

def no_agente_conversacional(estado: EstadoConversacional):
    """
    Agente que mantém contexto da conversa.
    """
    print(f"\n🤖 [AGENTE] Analisando conversa ({len(estado['mensagens'])} mensagens no histórico)...")

    # Sistema de mensagem que define o comportamento
    system_message = SystemMessage(content="""
Você é um assistente pessoal prestativo e amigável.

Características:
- Você lembra de tudo que o usuário disse anteriormente
- Você é proativo em oferecer ajuda
- Você usa as ferramentas disponíveis quando necessário
- Você chama o usuário pelo nome quando souber

Ferramentas disponíveis:
- salvar_nota: Para salvar informações importantes
- buscar_informacao_usuario: Para buscar dados do usuário
- agendar_lembrete: Para criar lembretes
""")

    # Adicionar system message se for a primeira interação
    mensagens = estado["mensagens"]
    if not any(isinstance(m, SystemMessage) for m in mensagens):
        mensagens = [system_message] + mensagens

    # LLM com ferramentas
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    llm_com_tools = llm.bind_tools(ferramentas)

    resposta = llm_com_tools.invoke(mensagens)

    return {"mensagens": [resposta]}


def no_executar_ferramentas(estado: EstadoConversacional):
    """
    Executa ferramentas solicitadas pelo agente.
    """
    print("\n⚡ [EXECUTANDO FERRAMENTAS]")

    from langchain_core.messages import ToolMessage

    ultima_mensagem = estado["mensagens"][-1]
    resultados = []

    for tool_call in ultima_mensagem.tool_calls:
        ferramenta = next((f for f in ferramentas if f.name == tool_call["name"]), None)

        if ferramenta:
            resultado = ferramenta.invoke(tool_call["args"])
            resultados.append(
                ToolMessage(
                    content=str(resultado),
                    tool_call_id=tool_call["id"]
                )
            )

    return {"mensagens": resultados}


def should_continue(estado: EstadoConversacional) -> str:
    """Decide se continua executando ferramentas ou termina."""
    ultima_mensagem = estado["mensagens"][-1]

    if hasattr(ultima_mensagem, "tool_calls") and ultima_mensagem.tool_calls:
        return "ferramentas"

    return "fim"


# ===================================================================
# PARTE 4: CONSTRUIR AGENTE COM MEMÓRIA
# ===================================================================
print("\n" + "="*70)
print("PARTE 4: Construindo Agente com Memória Persistente")
print("="*70)

def criar_agente_conversacional():
    """
    Cria agente com memória usando checkpoints.

    A grande diferença aqui é o MemorySaver, que permite
    que o agente lembre de conversas anteriores!
    """
    workflow = StateGraph(EstadoConversacional)

    # Adicionar nós
    workflow.add_node("agente", no_agente_conversacional)
    workflow.add_node("ferramentas", no_executar_ferramentas)

    # Fluxo
    workflow.set_entry_point("agente")

    workflow.add_conditional_edges(
        "agente",
        should_continue,
        {
            "ferramentas": "ferramentas",
            "fim": END
        }
    )

    workflow.add_edge("ferramentas", "agente")

    # 🔑 CHAVE: Adicionar memória com checkpointer
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app


print("\n✅ Agente conversacional criado com memória!")


# ===================================================================
# PARTE 5: TESTAR CONVERSAÇÃO COM MEMÓRIA
# ===================================================================
if __name__ == "__main__":
    print("\n\n" + "="*70)
    print("PARTE 5: TESTANDO CONVERSAÇÃO COM MEMÓRIA")
    print("="*70)

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Configure OPENAI_API_KEY no .env")
        exit(1)

    agente = criar_agente_conversacional()

    # 🔑 IMPORTANTE: thread_id mantém a memória entre conversas
    config = {"configurable": {"thread_id": "conversa-123"}}

    print("\n📱 Simulando uma conversa contínua...")
    print("="*70)

    # CONVERSA PARTE 1
    print("\n👤 Usuário: Olá! Meu nome é Maria e sou designer.")
    resultado = agente.invoke({
        "mensagens": [HumanMessage(content="Olá! Meu nome é Maria e sou designer.")]
    }, config)

    print(f"🤖 Agente: {resultado['mensagens'][-1].content}")

    # CONVERSA PARTE 2 - Agente deve lembrar do nome!
    print("\n👤 Usuário: Você lembra qual é minha profissão?")
    resultado = agente.invoke({
        "mensagens": [HumanMessage(content="Você lembra qual é minha profissão?")]
    }, config)

    print(f"🤖 Agente: {resultado['mensagens'][-1].content}")

    # CONVERSA PARTE 3 - Usando ferramentas
    print("\n👤 Usuário: Salva uma nota lembrando que tenho reunião amanhã às 10h")
    resultado = agente.invoke({
        "mensagens": [HumanMessage(content="Salva uma nota lembrando que tenho reunião amanhã às 10h")]
    }, config)

    print(f"🤖 Agente: {resultado['mensagens'][-1].content}")

    # CONVERSA PARTE 4 - Referência ao passado
    print("\n👤 Usuário: O que você salvou pra mim?")
    resultado = agente.invoke({
        "mensagens": [HumanMessage(content="O que você salvou pra mim?")]
    }, config)

    print(f"🤖 Agente: {resultado['mensagens'][-1].content}")

    # Mostrar estatísticas
    print("\n" + "="*70)
    print("📊 ESTATÍSTICAS DA CONVERSA")
    print("="*70)
    print(f"Total de mensagens no histórico: {len(resultado['mensagens'])}")
    print("\nHistórico completo:")
    for i, msg in enumerate(resultado['mensagens'], 1):
        tipo = type(msg).__name__
        conteudo = getattr(msg, 'content', '')[:50]
        print(f"  {i}. [{tipo}] {conteudo}...")


    # ===================================================================
    # DEMONSTRAÇÃO: MÚLTIPLAS THREADS (USUÁRIOS DIFERENTES)
    # ===================================================================
    print("\n\n" + "="*70)
    print("DEMONSTRAÇÃO: Múltiplos Usuários (Threads Separadas)")
    print("="*70)

    # Usuário 1
    config_user1 = {"configurable": {"thread_id": "usuario-1"}}
    print("\n🧑 Usuário 1: Meu nome é Carlos")
    agente.invoke({
        "mensagens": [HumanMessage(content="Meu nome é Carlos")]
    }, config_user1)

    # Usuário 2
    config_user2 = {"configurable": {"thread_id": "usuario-2"}}
    print("👩 Usuário 2: Meu nome é Ana")
    agente.invoke({
        "mensagens": [HumanMessage(content="Meu nome é Ana")]
    }, config_user2)

    # Testar memória separada
    print("\n🧑 Usuário 1 pergunta: Qual é o meu nome?")
    resultado1 = agente.invoke({
        "mensagens": [HumanMessage(content="Qual é o meu nome?")]
    }, config_user1)
    print(f"   Resposta: {resultado1['mensagens'][-1].content}")

    print("\n👩 Usuário 2 pergunta: Qual é o meu nome?")
    resultado2 = agente.invoke({
        "mensagens": [HumanMessage(content="Qual é o meu nome?")]
    }, config_user2)
    print(f"   Resposta: {resultado2['mensagens'][-1].content}")

    print("\n✅ Cada thread mantém sua própria memória!")


# ===================================================================
# RESUMO
# ===================================================================
print("\n\n" + "="*70)
print("📚 RESUMO - O QUE VOCÊ APRENDEU")
print("="*70)
print("""
✅ Memória Persistente:
   - MemorySaver() permite salvar estado entre conversas
   - Cada thread_id é uma conversa separada
   - Perfeito para chatbots com múltiplos usuários

✅ Checkpoints:
   - workflow.compile(checkpointer=memory)
   - Estado é automaticamente salvo e restaurado
   - Permite pausar/continuar conversas

✅ Configuração por Thread:
   - config = {"configurable": {"thread_id": "..."}}
   - Cada usuário tem seu próprio histórico
   - Memórias não se misturam

✅ Sistema de Mensagens:
   - SystemMessage: Define comportamento do agente
   - HumanMessage: Mensagens do usuário
   - AIMessage: Respostas do agente
   - ToolMessage: Resultados de ferramentas

🎯 PRÓXIMO PASSO: 04_multi_agentes.py
   - Criar múltiplos agentes especializados
   - Agentes que colaboram entre si
   - Padrão de orquestração
""")

print("\n" + "="*70)
print("💡 EXERCÍCIO")
print("="*70)
print("""
Modifique o agente para:
1. Adicionar ferramenta de "contar_piada"
2. Sistema deve ser mais descontraído
3. Testar múltiplas conversas mantendo contexto
4. Experimentar diferentes thread_ids
""")
