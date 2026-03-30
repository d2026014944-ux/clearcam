---
name: omega-enforcement
description: "Use quando precisar executar tarefas no modo anti-vibe coding com planejamento, TDD, hooks de seguranca e memoria de licoes." 
---

# Omega Enforcement Skill

## Workflow
1. Portao 1: confirmar entendimento em tasks/todo.md com linguagem simples.
2. Portao 2: escrever testes em tests/ antes de alterar producao.
3. Portao 3: executar hooks de seguranca e so aceitar mudancas com tudo verde.
4. Portao 4: registrar licoes em tasks/lessons.md quando houver erro real.

## Regras
- Nao escrever codigo de producao sem teste previo.
- Nao aprovar mudanca com lint/testes/secrets falhando.
- Priorizar simplicidade e baixo acoplamento.
- Se o contexto estiver acima de 70%, compactar resumindo fatos uteis; acima de 80%, reduzir memoria operacional.

## Deliverables minimos por tarefa
- tasks/todo.md atualizado.
- testes criados/ajustados.
- gate local executado.
- lessons atualizada quando aplicavel.
