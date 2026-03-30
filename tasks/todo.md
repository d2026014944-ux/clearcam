# Todo Tatico

## Filtro Feynman (2 frases)
Problema: Precisamos integrar uma camada OSINT profissional ao ClearCAM sem quebrar o fluxo atual de captura, inferencia e eventos.
Solucao: Implementar uma arquitetura de plugins e fila assincrona com hooks de qualidade para garantir seguranca, testes e evolucao controlada.

## Subtarefas
- [x] Materializar Matriz Omega no workspace.
- [x] Criar testes para pipeline OSINT MVP.
- [x] Integrar endpoints OSINT MVP no servidor HTTP.
- [x] Conectar gatilho de enriquecimento no pos-evento.
- [x] Validar gates (lint e testes do modulo novo) e registrar evidencias.
- [x] Criar testes de endpoint para rotas OSINT e refatorar handler para testabilidade.
- [x] Integrar painel OSINT na web com filtros e ações de triagem conectadas aos endpoints.
- [x] Adicionar navegação direta (View Event / View Camera) no card OSINT.
- [x] Criar testes de integração HTTP para ciclo completo (listar → confirmar/descartar → refletir).
- [x] Evoluir visual com badges de score (verde/amarelo/vermelho) e origen de plugins.

## Ciclo Atual - Deploy Free

## Filtro Feynman (2 frases)
Problema: Precisamos colocar o ClearCAM em producao sem custo e com operacao estavel para desenvolvimento autonomo.
Solucao: Implementar um pacote de deploy free com configuracao de servico, proxy HTTPS e guia operacional validado por gates locais.

## Subtarefas Deploy
- [x] Criar guia de deploy free para Oracle Cloud Always Free.
- [x] Adicionar exemplo de variaveis de ambiente para producao.
- [x] Adicionar unidade systemd para execucao em boot e restart automatico.
- [x] Adicionar configuracao Nginx para reverse proxy e TLS.
- [x] Adicionar script de bootstrap para provisionamento inicial da VM.
- [x] Atualizar README com referencia para o novo fluxo de deploy.
- [x] Validar artefatos de deploy (shell + unit systemd).
- [x] Adicionar smoke test pos-deploy para validacao operacional da VM.
- [ ] Validar gates locais (ruff, pytest e safety hook).

Observacao: Gate executado, mas bloqueado por erros de lint legados fora do escopo do ciclo de deploy free.
