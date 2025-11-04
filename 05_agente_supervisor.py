"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 5
Padrão Supervisor: Agente que Gerencia Outros Agentes
===========================================

O padrão SUPERVISOR é um dos mais poderosos para agentes:

                    ┌──────────────┐
                    │  SUPERVISOR  │ ← Decide quem fazer o quê
                    │   (Manager)  │
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
       ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
       │ AGENTE  │   │ AGENTE  │   │ AGENTE  │
       │PESQUISA │   │ CÓDIGO  │   │ESCRITOR │
       └─────────┘   └─────────┘   └─────────┘

O supervisor:
- Recebe a tarefa do usuário
- Decide qual agente é melhor para cada subtarefa
- Delega trabalho
- Monitora progresso
- Pode pedir para agentes colaborarem
"""

import os
from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import operator
import json


# ===================================================================
# PARTE 1: DEFINIR AGENTES ESPECIALIZADOS
# ===================================================================
print("\n" + "="*70)
print("PARTE 1: Criando Agentes Especializados")
print("="*70)


class EstadoSupervisor(TypedDict):
    """Estado compartilhado do sistema supervisor"""
    mensagens: Annotated[Sequence[BaseMessage], operator.add]
    proximo_agente: str
    tarefa_completa: bool
    iteracao: int


def agente_pesquisador(estado: EstadoSupervisor):
    """
    Agente especialista em pesquisa e coleta de informações.
    """
    print("\n🔍 [AGENTE PESQUISADOR] Coletando informações...")

    if not os.getenv("OPENAI_API_KEY"):
        resposta = "Pesquisei sobre o tópico e encontrei informações relevantes [simulado]."
        print(f"   {resposta}")
        return {
            "mensagens": [AIMessage(content=f"Pesquisador: {resposta}", name="pesquisador")]
        }

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    system_prompt = """
Você é um PESQUISADOR especializado.
Seu trabalho é coletar e organizar informações sobre o tópico solicitado.
Seja objetivo e factual.
"""

    mensagens = [SystemMessage(content=system_prompt)] + list(estado["mensagens"])
    resposta = llm.invoke(mensagens)

    print(f"   Pesquisa concluída")

    return {
        "mensagens": [AIMessage(content=resposta.content, name="pesquisador")]
    }


def agente_programador(estado: EstadoSupervisor):
    """
    Agente especialista em código.
    """
    print("\n💻 [AGENTE PROGRAMADOR] Escrevendo código...")

    if not os.getenv("OPENAI_API_KEY"):
        resposta = "```python\ndef exemplo():\n    return 'código aqui'\n```"
        print(f"   Código gerado")
        return {
            "mensagens": [AIMessage(content=f"Programador: {resposta}", name="programador")]
        }

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    system_prompt = """
Você é um PROGRAMADOR especializado.
Seu trabalho é escrever código limpo, eficiente e bem documentado.
Use boas práticas e padrões de código.
"""

    mensagens = [SystemMessage(content=system_prompt)] + list(estado["mensagens"])
    resposta = llm.invoke(mensagens)

    print(f"   Código gerado")

    return {
        "mensagens": [AIMessage(content=resposta.content, name="programador")]
    }


def agente_escritor(estado: EstadoSupervisor):
    """
    Agente especialista em escrita e documentação.
    """
    print("\n✍️  [AGENTE ESCRITOR] Criando conteúdo...")

    if not os.getenv("OPENAI_API_KEY"):
        resposta = "Criei um texto bem estruturado sobre o tópico [simulado]."
        print(f"   {resposta}")
        return {
            "mensagens": [AIMessage(content=f"Escritor: {resposta}", name="escritor")]
        }

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    system_prompt = """
Você é um ESCRITOR especializado.
Seu trabalho é criar conteúdo claro, envolvente e bem estruturado.
Use linguagem apropriada para o público-alvo.
"""

    mensagens = [SystemMessage(content=system_prompt)] + list(estado["mensagens"])
    resposta = llm.invoke(mensagens)

    print(f"   Conteúdo criado")

    return {
        "mensagens": [AIMessage(content=resposta.content, name="escritor")]
    }


# ===================================================================
# PARTE 2: CRIAR O AGENTE SUPERVISOR
# ===================================================================
print("\n" + "="*70)
print("PARTE 2: Criando o Agente Supervisor (Manager)")
print("="*70)


def agente_supervisor(estado: EstadoSupervisor):
    """
    SUPERVISOR: Gerencia os outros agentes.

    Responsabilidades:
    1. Analisar a tarefa
    2. Decidir qual agente deve trabalhar
    3. Determinar se a tarefa está completa
    """
    print(f"\n👔 [SUPERVISOR] Gerenciando (iteração {estado.get('iteracao', 0)})...")

    if not os.getenv("OPENAI_API_KEY"):
        # Versão simplificada sem LLM
        ultima_msg = estado["mensagens"][-1].content.lower()

        if estado.get("iteracao", 0) >= 2:
            print("   Decisão: Tarefa completa")
            return {
                "proximo_agente": "FINISH",
                "tarefa_completa": True,
                "iteracao": estado.get("iteracao", 0) + 1
            }

        if "pesquis" in ultima_msg or "informação" in ultima_msg:
            proximo = "pesquisador"
        elif "código" in ultima_msg or "programar" in ultima_msg:
            proximo = "programador"
        elif "escrever" in ultima_msg or "texto" in ultima_msg:
            proximo = "escritor"
        else:
            proximo = "pesquisador"

        print(f"   Decisão: Delegar para {proximo}")

        return {
            "proximo_agente": proximo,
            "tarefa_completa": False,
            "iteracao": estado.get("iteracao", 0) + 1
        }

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    system_prompt = """
Você é um SUPERVISOR que gerencia uma equipe de agentes especializados:

- pesquisador: Coleta informações e dados
- programador: Escreve e revisa código
- escritor: Cria documentação e textos

Sua tarefa:
1. Analise a conversa
2. Decida qual agente deve trabalhar a seguir
3. Ou determine se a tarefa está completa

Responda APENAS com JSON no formato:
{
    "proximo_agente": "pesquisador" | "programador" | "escritor" | "FINISH",
    "raciocinio": "Breve explicação da decisão"
}

Use FINISH quando a tarefa estiver completa e satisfatória.
"""

    mensagens = [SystemMessage(content=system_prompt)] + list(estado["mensagens"])

    resposta = llm.invoke(mensagens)

    try:
        # Tentar extrair JSON da resposta
        content = resposta.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        decisao = json.loads(content.strip())

        proximo = decisao.get("proximo_agente", "FINISH")
        raciocinio = decisao.get("raciocinio", "")

        print(f"   💭 Raciocínio: {raciocinio}")
        print(f"   🎯 Próximo: {proximo}")

        tarefa_completa = proximo == "FINISH"

        return {
            "proximo_agente": proximo,
            "tarefa_completa": tarefa_completa,
            "iteracao": estado.get("iteracao", 0) + 1,
            "mensagens": [AIMessage(
                content=f"Supervisor: {raciocinio}",
                name="supervisor"
            )]
        }

    except json.JSONDecodeError:
        print("   ⚠️  Erro ao parsear decisão, finalizando...")
        return {
            "proximo_agente": "FINISH",
            "tarefa_completa": True,
            "iteracao": estado.get("iteracao", 0) + 1
        }


# ===================================================================
# PARTE 3: CONSTRUIR O GRAFO SUPERVISOR
# ===================================================================
print("\n" + "="*70)
print("PARTE 3: Montando o Sistema Supervisor")
print("="*70)


def rotear_supervisor(estado: EstadoSupervisor) -> str:
    """
    Router que direciona para o próximo agente ou finaliza.
    """
    proximo = estado.get("proximo_agente", "FINISH")

    # Limite de segurança
    if estado.get("iteracao", 0) > 10:
        print("   ⚠️  Limite de iterações atingido")
        return "FINISH"

    return proximo


def criar_sistema_supervisor():
    """
    Cria sistema com padrão supervisor.

    O supervisor está no centro e decide qual agente trabalhar.
    Cada agente retorna para o supervisor após completar.
    """

    workflow = StateGraph(EstadoSupervisor)

    # Adicionar supervisor
    workflow.add_node("supervisor", agente_supervisor)

    # Adicionar agentes trabalhadores
    workflow.add_node("pesquisador", agente_pesquisador)
    workflow.add_node("programador", agente_programador)
    workflow.add_node("escritor", agente_escritor)

    # Supervisor é o ponto de entrada
    workflow.set_entry_point("supervisor")

    # Roteamento condicional do supervisor
    workflow.add_conditional_edges(
        "supervisor",
        rotear_supervisor,
        {
            "pesquisador": "pesquisador",
            "programador": "programador",
            "escritor": "escritor",
            "FINISH": END
        }
    )

    # Todos os agentes retornam para o supervisor
    for agente in ["pesquisador", "programador", "escritor"]:
        workflow.add_edge(agente, "supervisor")

    return workflow.compile()


print("\n✅ Sistema supervisor criado!")
print("""
Arquitetura do Sistema:

         ┌─────────────┐
    ┌───►│ SUPERVISOR  │◄───┐
    │    └──────┬──────┘    │
    │           │           │
    │     ┌─────┴─────┐     │
    │     │           │     │
    │  ┌──▼──┐     ┌──▼──┐  │
    └──┤ AGT │     │ AGT │──┘
       └─────┘     └─────┘
""")


# ===================================================================
# PARTE 4: TESTAR O SISTEMA SUPERVISOR
# ===================================================================
if __name__ == "__main__":
    print("\n\n" + "="*70)
    print("PARTE 4: TESTANDO SISTEMA SUPERVISOR")
    print("="*70)

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Executando em modo simulado (sem OPENAI_API_KEY)")

    sistema = criar_sistema_supervisor()

    # Testes de diferentes tipos de tarefas
    tarefas = [
        "Pesquise sobre LangGraph e me dê um resumo",
        "Escreva uma função Python que calcula fibonacci",
        "Crie um tutorial sobre como usar agentes de IA",
    ]

    for i, tarefa in enumerate(tarefas, 1):
        print(f"\n{'='*70}")
        print(f"🎯 TAREFA {i}: {tarefa}")
        print(f"{'='*70}")

        resultado = sistema.invoke({
            "mensagens": [HumanMessage(content=tarefa)],
            "proximo_agente": "",
            "tarefa_completa": False,
            "iteracao": 0
        })

        print(f"\n{'='*70}")
        print(f"📊 RESULTADO DA TAREFA {i}")
        print(f"{'='*70}")
        print(f"Total de iterações: {resultado['iteracao']}")
        print(f"Total de mensagens: {len(resultado['mensagens'])}")

        print(f"\n📜 Fluxo de trabalho:")
        for msg in resultado["mensagens"]:
            if hasattr(msg, "name") and msg.name:
                print(f"  • {msg.name}: {msg.content[:60]}...")


# ===================================================================
# RESUMO
# ===================================================================
print("\n\n" + "="*70)
print("📚 RESUMO - O QUE VOCÊ APRENDEU")
print("="*70)
print("""
✅ Padrão Supervisor:
   - Um agente gerente coordena múltiplos agentes
   - Supervisor decide qual agente trabalha quando
   - Cada agente retorna para o supervisor após completar
   - Supervisor decide quando tarefa está completa

✅ Vantagens do Padrão:
   - Flexibilidade: Supervisor decide dinamicamente
   - Especialização: Cada agente foca em sua expertise
   - Reutilização: Agentes podem ser chamados múltiplas vezes
   - Controle: Um ponto central de decisão

✅ Quando usar:
   - Tarefas complexas que requerem múltiplas habilidades
   - Quando ordem de execução não é fixa
   - Quando agentes precisam colaborar dinamicamente
   - Sistemas que precisam de orquestração inteligente

✅ Implementação:
   - Supervisor usa LLM para tomar decisões
   - Conditional edges para roteamento dinâmico
   - Cada agente tem system prompt especializado
   - Loop até supervisor decidir FINISH

🎯 PRÓXIMO PASSO: 06_human_in_the_loop.py
   - Adicionar aprovação humana no fluxo
   - Interromper execução para input
   - Editar planos antes de executar
   - Supervisão humana de agentes
""")

print("\n" + "="*70)
print("💡 EXERCÍCIO AVANÇADO")
print("="*70)
print("""
Crie um sistema supervisor para análise de código:

AGENTES:
1. analisador_estatico: Verifica sintaxe e estilo
2. analisador_seguranca: Busca vulnerabilidades
3. analisador_performance: Identifica gargalos
4. revisor: Consolida findings e sugere melhorias

SUPERVISOR:
- Decide ordem de análise
- Pode pedir múltiplas revisões
- Finaliza quando código está OK

Teste com um código Python real!
""")
