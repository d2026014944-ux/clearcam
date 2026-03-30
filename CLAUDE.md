# Matriz Omega - ClearCAM

## Missao
Construir e evoluir ClearCAM com engenharia inviolavel: entendimento antes de sintaxe, TDD antes de codigo de producao, seguranca por default e memoria de aprendizado apos cada incidente.

## Dominio em 2 frases (Filtro Feynman)
ClearCAM captura streams de cameras, roda deteccao/rastreamento e gera eventos com clips e notificacoes. O sistema agora ganha uma camada OSINT assincroma para enriquecer eventos sem degradar FPS nem expor dados sensiveis por padrao.

## Stack Atual
- Python 3.11+
- Tinygrad, OpenCV, NumPy
- SQLite local (WAL)
- API HTTP em clearcam.py

## Regras de Ouro
1. Nenhum codigo de producao antes de testes falhando (Red).
2. Toda mudanca passa por lint, testes e varredura de segredos.
3. Integracoes externas devem ser opcionais, com fallback local.
4. Dados biometricos e correlacao identitaria sao opt-in por camera/cliente.
5. Todo erro relevante gera aprendizado em tasks/lessons.md.

## Portoes Obrigatorios
### Portao 1 - Entendimento
- Ler .mcp.json e este arquivo antes de implementar.
- Registrar no tasks/todo.md o problema e a solucao em 2 frases simples.

### Portao 2 - Planejamento + TDD
- Quebrar o trabalho em subtarefas no tasks/todo.md.
- Criar testes em tests/ antes de src/.

### Portao 3 - Anti-Vibe Coding
- Implementar com simplicidade extrema e sem acoplamento indevido.
- Passar nos hooks: lint, testes, segredos, verificacao de contexto.

### Portao 4 - Disseccao + Memoria
- Se falhar, documentar causa raiz e regra nova em tasks/lessons.md.
- Atualizar este CLAUDE.md quando arquitetura/processo mudar.

## Convencoes de Projeto
- Codigo novo deve privilegiar src/.
- Legado em raiz/test/ permanece ativo e nao deve ser quebrado.
- APIs novas devem ser backwards compatible sempre que possivel.
