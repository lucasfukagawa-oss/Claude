# Economia de uso (plano de assinatura)

No plano de assinatura o limite é por janela de uso, e o Opus consome o limite muito mais rápido que Sonnet/Haiku. O que mais gasta é **contexto grande no modelo caro**, não a pergunta em si.

## Delegação por modelo

| Tarefa | Quem faz |
|---|---|
| Achar arquivo, varrer pasta, ler PDF/planilha/lei/log longo, pesquisar na web e resumir | subagente `explorador` (Haiku) |
| Executar algo já decidido: edições em lote, boilerplate, formatar dados, rodar e corrigir testes | subagente `executor` (Sonnet) |
| Decidir: estratégia, arquitetura, parecer jurídico/técnico, viabilidade, revisão final | agente principal |

Regras para o agente principal:
- Antes de ler mais de 2–3 arquivos ou qualquer documento longo, delegue ao `explorador` e trabalhe só com o resumo.
- Depois de decidir o que fazer, se a execução for mecânica, delegue ao `executor` com instruções completas (arquivos, o que mudar, como validar).
- Não delegue tarefas de uma linha — o custo de abrir o subagente supera a economia.

## Hábitos do usuário (maior ganho)
- `/clear` ao trocar de assunto; `/compact` em sessões longas.
- `/model sonnet` como padrão do dia a dia; `/model opus` (ou `opusplan`) só para decisões difíceis.
- Não colar arquivos inteiros no chat — aponte o caminho e deixe o `explorador` ler.
