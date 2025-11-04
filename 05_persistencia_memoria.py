"""
===========================================
ESTUDO GUIADO LANGGRAPH - PARTE 5
Persistência e Memória
===========================================

LangGraph pode salvar e restaurar o estado entre execuções,
permitindo criar agentes com memória de longo prazo.
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import operator
import json
from datetime import datetime


# EXEMPLO 1: CONVERSAÇÃO COM MEMÓRIA
class EstadoComMemoria(TypedDict):
    mensagens: Annotated[list, operator.add]
    nome_usuario: str
    preferencias: dict
    historico_completo: Annotated[list, operator.add]


def cumprimentar(estado: EstadoComMemoria) -> EstadoComMemoria:
    """Cumprimenta o usuário usando memória"""
    nome = estado.get("nome_usuario", "")

    if nome:
        mensagem = f"Olá novamente, {nome}! Lembro de você."
    else:
        mensagem = "Olá! Qual é o seu nome?"

    print(f"[AGENTE] {mensagem}")

    return {
        "mensagens": [mensagem],
        "nome_usuario": nome,
        "preferencias": estado.get("preferencias", {}),
        "historico_completo": [{"timestamp": datetime.now().isoformat(), "mensagem": mensagem}]
    }


def processar_entrada(estado: EstadoComMemoria) -> EstadoComMemoria:
    """Processa entrada do usuário e atualiza memória"""
    mensagens = estado.get("mensagens", [])
    ultima_mensagem = mensagens[-1] if mensagens else ""

    nome = estado.get("nome_usuario", "")
    preferencias = estado.get("preferencias", {})

    # Detecta nome
    if not nome and "meu nome é" in ultima_mensagem.lower():
        nome = ultima_mensagem.lower().split("meu nome é")[-1].strip()
        resposta = f"Prazer em conhecê-lo, {nome}! Vou lembrar do seu nome."

    # Detecta preferências
    elif "gosto de" in ultima_mensagem.lower():
        interesse = ultima_mensagem.lower().split("gosto de")[-1].strip()
        if "interesses" not in preferencias:
            preferencias["interesses"] = []
        preferencias["interesses"].append(interesse)
        resposta = f"Anotado! Você gosta de {interesse}."

    else:
        resposta = f"Entendi. Você disse: '{ultima_mensagem}'"

    print(f"[AGENTE] {resposta}")

    return {
        "mensagens": [resposta],
        "nome_usuario": nome,
        "preferencias": preferencias,
        "historico_completo": [{"timestamp": datetime.now().isoformat(), "mensagem": resposta}]
    }


def criar_agente_com_memoria():
    """Cria agente com memória persistente"""

    workflow = StateGraph(EstadoComMemoria)

    workflow.add_node("cumprimentar", cumprimentar)
    workflow.add_node("processar", processar_entrada)

    workflow.set_entry_point("cumprimentar")
    workflow.add_edge("cumprimentar", "processar")
    workflow.add_edge("processar", END)

    # Adicionar checkpointer para persistência
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app


# EXEMPLO 2: SISTEMA DE TAREFAS COM PERSISTÊNCIA
class EstadoTarefas(TypedDict):
    tarefas: list
    concluidas: list
    em_andamento: str
    estatisticas: dict


def adicionar_tarefa(estado: EstadoTarefas, nova_tarefa: str) -> EstadoTarefas:
    """Adiciona uma nova tarefa"""
    tarefas = estado.get("tarefas", [])
    tarefa_obj = {
        "id": len(tarefas) + 1,
        "titulo": nova_tarefa,
        "criada_em": datetime.now().isoformat(),
        "status": "pendente"
    }

    tarefas.append(tarefa_obj)

    print(f"[TAREFA ADICIONADA] #{tarefa_obj['id']}: {nova_tarefa}")

    return {
        **estado,
        "tarefas": tarefas
    }


def listar_tarefas(estado: EstadoTarefas) -> EstadoTarefas:
    """Lista todas as tarefas"""
    tarefas = estado.get("tarefas", [])
    concluidas = estado.get("concluidas", [])

    print("\n[TAREFAS PENDENTES]")
    for tarefa in tarefas:
        print(f"  #{tarefa['id']}: {tarefa['titulo']}")

    print(f"\n[TAREFAS CONCLUÍDAS] {len(concluidas)} tarefas")
    for tarefa in concluidas:
        print(f"  ✓ #{tarefa['id']}: {tarefa['titulo']}")

    return estado


def concluir_tarefa(estado: EstadoTarefas, tarefa_id: int) -> EstadoTarefas:
    """Marca uma tarefa como concluída"""
    tarefas = estado.get("tarefas", [])
    concluidas = estado.get("concluidas", [])

    for i, tarefa in enumerate(tarefas):
        if tarefa["id"] == tarefa_id:
            tarefa["concluida_em"] = datetime.now().isoformat()
            tarefa["status"] = "concluida"
            concluidas.append(tarefa)
            tarefas.pop(i)
            print(f"[TAREFA CONCLUÍDA] #{tarefa_id}: {tarefa['titulo']}")
            break

    return {
        **estado,
        "tarefas": tarefas,
        "concluidas": concluidas
    }


# EXEMPLO 3: SALVAR/CARREGAR ESTADO MANUALMENTE
class GerenciadorEstado:
    """Gerencia salvamento e carregamento de estado"""

    def __init__(self, arquivo: str = "estado_agente.json"):
        self.arquivo = arquivo

    def salvar(self, estado: dict):
        """Salva estado em arquivo JSON"""
        with open(self.arquivo, 'w', encoding='utf-8') as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)
        print(f"[ESTADO SALVO] {self.arquivo}")

    def carregar(self) -> dict:
        """Carrega estado do arquivo JSON"""
        try:
            with open(self.arquivo, 'r', encoding='utf-8') as f:
                estado = json.load(f)
            print(f"[ESTADO CARREGADO] {self.arquivo}")
            return estado
        except FileNotFoundError:
            print("[NOVO ESTADO] Arquivo não encontrado, criando novo")
            return {}

    def limpar(self):
        """Limpa o estado salvo"""
        import os
        if os.path.exists(self.arquivo):
            os.remove(self.arquivo)
            print(f"[ESTADO LIMPO] {self.arquivo} removido")


# EXEMPLO 4: CHECKPOINT E ROLLBACK
class EstadoVersionado(TypedDict):
    versao: int
    dados: dict
    historico_versoes: list


def criar_checkpoint(estado: EstadoVersionado) -> EstadoVersionado:
    """Cria um checkpoint do estado atual"""
    versao = estado.get("versao", 0) + 1
    dados = estado.get("dados", {})
    historico = estado.get("historico_versoes", [])

    checkpoint = {
        "versao": versao,
        "timestamp": datetime.now().isoformat(),
        "dados": dados.copy()
    }

    historico.append(checkpoint)

    print(f"[CHECKPOINT] Versão {versao} salva")

    return {
        "versao": versao,
        "dados": dados,
        "historico_versoes": historico
    }


def rollback(estado: EstadoVersionado, versao_alvo: int) -> EstadoVersionado:
    """Volta para uma versão anterior"""
    historico = estado.get("historico_versoes", [])

    for checkpoint in historico:
        if checkpoint["versao"] == versao_alvo:
            print(f"[ROLLBACK] Voltando para versão {versao_alvo}")
            return {
                "versao": checkpoint["versao"],
                "dados": checkpoint["dados"],
                "historico_versoes": historico
            }

    print(f"[ERRO] Versão {versao_alvo} não encontrada")
    return estado


# EXECUTAR EXEMPLOS
if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLO 1: Agente com Memória")
    print("=" * 60)

    app = criar_agente_com_memoria()

    # Configuração de thread para manter memória entre chamadas
    config = {"configurable": {"thread_id": "usuario_123"}}

    print("\n--- Primeira Conversa ---")
    resultado1 = app.invoke({
        "mensagens": ["Olá!"],
        "nome_usuario": "",
        "preferencias": {},
        "historico_completo": []
    }, config)

    print("\n--- Segunda Conversa (menciona nome) ---")
    resultado2 = app.invoke({
        "mensagens": ["Meu nome é João"],
        "nome_usuario": resultado1.get("nome_usuario", ""),
        "preferencias": resultado1.get("preferencias", {}),
        "historico_completo": []
    }, config)

    print("\n--- Terceira Conversa (menciona preferência) ---")
    resultado3 = app.invoke({
        "mensagens": ["Eu gosto de programação Python"],
        "nome_usuario": resultado2.get("nome_usuario", ""),
        "preferencias": resultado2.get("preferencias", {}),
        "historico_completo": []
    }, config)

    print("\n[MEMÓRIA PERSISTIDA]")
    print(f"Nome: {resultado3.get('nome_usuario')}")
    print(f"Preferências: {resultado3.get('preferencias')}")

    print("\n" + "=" * 60)
    print("EXEMPLO 2: Sistema de Tarefas")
    print("=" * 60)

    estado_tarefas = {
        "tarefas": [],
        "concluidas": [],
        "em_andamento": "",
        "estatisticas": {}
    }

    # Adicionar tarefas
    estado_tarefas = adicionar_tarefa(estado_tarefas, "Estudar LangGraph")
    estado_tarefas = adicionar_tarefa(estado_tarefas, "Implementar agente")
    estado_tarefas = adicionar_tarefa(estado_tarefas, "Testar em produção")

    # Listar
    listar_tarefas(estado_tarefas)

    # Concluir uma tarefa
    estado_tarefas = concluir_tarefa(estado_tarefas, 1)

    # Listar novamente
    print()
    listar_tarefas(estado_tarefas)

    print("\n" + "=" * 60)
    print("EXEMPLO 3: Salvar/Carregar Manualmente")
    print("=" * 60)

    gerenciador = GerenciadorEstado("teste_estado.json")

    # Salvar estado
    estado_para_salvar = {
        "usuario": "Maria",
        "pontos": 150,
        "nivel": 5,
        "conquistas": ["primeira_vitoria", "explorador"]
    }

    print("\n[SALVANDO]")
    gerenciador.salvar(estado_para_salvar)

    print("\n[CARREGANDO]")
    estado_carregado = gerenciador.carregar()
    print(f"Estado recuperado: {estado_carregado}")

    # Limpar
    print()
    gerenciador.limpar()

    print("\n" + "=" * 60)
    print("EXEMPLO 4: Versionamento com Checkpoint")
    print("=" * 60)

    estado_v = {
        "versao": 0,
        "dados": {"contador": 0},
        "historico_versoes": []
    }

    print("\n[Criando checkpoints]")
    for i in range(3):
        estado_v["dados"]["contador"] += 10
        estado_v = criar_checkpoint(estado_v)
        print(f"Dados atuais: {estado_v['dados']}")

    print(f"\n[Histórico de versões]")
    for cp in estado_v["historico_versoes"]:
        print(f"  Versão {cp['versao']}: {cp['dados']}")

    print(f"\n[Fazendo rollback para versão 2]")
    estado_v = rollback(estado_v, 2)
    print(f"Dados após rollback: {estado_v['dados']}")

    print("\n" + "=" * 60)
    print("""
    CONCEITOS-CHAVE:

    1. MemorySaver: Checkpointer em memória do LangGraph
    2. Thread ID: Identifica sessões/usuários únicos
    3. Persistência Manual: Salvar em JSON/BD quando necessário
    4. Versionamento: Manter histórico de mudanças

    USO EM PRODUÇÃO:
    - Use SQLite/PostgreSQL para persistência durável
    - Implemente limpeza de dados antigos
    - Adicione autenticação para threads de usuário
    - Monitore uso de memória

    EXERCÍCIO:
    1. Implemente um chatbot que lembra conversas anteriores
    2. Adicione sistema de perfil de usuário persistente
    3. Crie funcionalidade de "desfazer" última ação
    4. Implemente backup automático do estado

    PRÓXIMO: 06_agentes_avancados.py
    """)
    print("=" * 60)
