# Lessons Learned

## Regras acumuladas
- Sempre inicializar tarefas com Filtro Feynman em tasks/todo.md.
- Nunca implementar producao antes de testes falhando (Red).
- Integracoes externas devem ter modo passivo/fallback para nao interromper operacao local.
- Validar e instalar toolchain minima (pytest, ruff) antes de executar gates automatizados.
- Para testar endpoints BaseHTTPRequestHandler com baixo acoplamento, extrair logica de negocio para metodos internos puros no handler.
- Em validacao de HTML com script externo, contar tags `<script` (com atributos) e compilar script inline para checagem real de sintaxe.

## Workflow Autônomo de Testes e Correção (Estratégia Cloudflare)

**Princípio**: O teste não avisa o humano que errou. O teste é o volante que dirige a IA. A IA só para quando a luz verde acende.

### 🔄 5 Fases Sequenciais

```
[Início] IA gera bloco de código em src/
   │
   ▼
🟢 FASE 1: Validação de Contrato & Ambiente (O Guardião)
   ├─ O código usa dependências proibidas?
   ├─ A API pública é idêntica à especificada?
   │    ├─ [FALHA] ➔ Rejeita. Envia erro de arquitetura para IA.
   │    └─ [PASSA] ➔ Continua.
   ▼
🔵 FASE 2: O Loop Rápido (Testes Unitários - pytest)
   ├─ Testa lógica pura, estado e funções isoladas.
   │    ├─ [FALHA] ➔ Captura log (stderr).
   │    │            Gatilho: Agente Corretor recebe prompt com erro.
   │    │            (Volta ao início)
   │    └─ [PASSA] ➔ Continua.
   ▼
🟣 FASE 3: O Loop de Integração (Testes E2E - Playwright/Selenium)
   ├─ Sobe servidor + simula navegador real.
   ├─ Testa navegação, cliques, renderização e integração.
   │    ├─ [FALHA] ➔ Captura log + screenshot.
   │    │            Gatilho: Agente Corretor focado em UI.
   │    │            (Volta ao início)
   │    └─ [PASSA] ➔ Funcionalidade válida!
   ▼
🟠 FASE 4: Code Review Multi-Agente (O Tribunal)
   ├─ [AGENTE 1: REVISOR] Busca: gargalos, redundância, segurança.
   │    ├─ [ENCONTRA] ➔ Relatório de críticas.
   │    │    └─ [AGENTE 2: CORRETOR] Refatora + volta à FASE 2.
   │    └─ [APROVA] ➔ Código limpo e seguro.
   ▼
✅ FASE 5: Merge Automático & Relatório
   └─ Integra branch principal. Humano recebe notificação.
```

### Implementação Técnica

**FASE 1 - TDD Reverso**
- Script verifica se classes/funções têm nomes e tipos do framework alvo.
- Linter ESLint: quebra build se IA importar bibliotecas pesadas proibidas.
- Força programação para Web API nativa (Edge Computing).

**FASE 2 - Micro-Loop (pytest em watch mode)**
- Executa em segundos.
- Gatilho: bash script pega stderr e joga de volta no prompt da IA.
- Feedback: "O teste X quebrou por Y. Stack trace: Z. Conserte."

**FASE 3 - Macro-Loop (Playwright/Selenium headless)**
- Abre browser simulado, clica em links, verifica SSR e hidratação.
- Erro E2E volta para IA analisar contexto frontend+backend.
- Detalhe: screenshot visualmente documentado do erro.

**FASE 4 - Code Review Automatizado**
- **Revisor** (lê, não programa): busca ineficiências, bundle size, segurança.
- **Corretor** (programa): refatora, minifica, segue Clean Architecture de CLAUDE.md.
- **Detalhe crítico**: após refatoração, código volta às FASES 2 & 3.

### Por que funciona (Lição Cloudflare)

> Você não precisa confiar que a IA acertará de primeira. Crie um labirinto elétrico (testes) onde ela toma choques (erros) até encontrar a única saída: código perfeito, performático e em conformidade exata com a especificação.

**Ciclo de sucesso**:
1. Erro no teste → feedback imediato.
2. IA aprende padrão → refatora.
3. Ciclo repete até luz verde.
4. Nenhuma confiança cega. Apenas validação.

---

## Template de dissecacao
- Incidente:
- Causa raiz:
- Evidencia:
- Correcao aplicada:
- Nova regra:
