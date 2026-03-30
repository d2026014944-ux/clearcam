# Plan Node Command

## Objetivo
Forcar planejamento antes de codigo de producao.

## Passos obrigatorios
1. Ler CLAUDE.md e .mcp.json.
2. Escrever em tasks/todo.md:
- problema em 2 frases simples
- solucao em 2 frases simples
- subtarefas objetivas
3. Criar ou atualizar testes em tests/.
4. Rodar gate local: `bash .claude/hooks/precommit-gate.sh`.
5. Somente depois editar src/ ou codigo de producao.

## Criterio de bloqueio
Se tasks/todo.md nao tiver as frases de Feynman e subtarefas, a implementacao nao deve continuar.
