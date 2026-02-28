# Histórico de Implementações

## Rodada 1 - Base do projeto (2026-02-28)

### Entregas
- Estrutura inicial de aplicação em `src`.
- Suporte para leitura de arquivos `PDF`, `CSV` e `OFX`.
- Classificação automática inicial por palavras-chave.
- Consolidação mensal dos gastos.
- Dashboard interativo em Streamlit com:
  - gráfico mensal;
  - seleção de mês por clique no gráfico;
  - detalhamento dos lançamentos do mês;
  - distribuição por categoria.
- Política de sigilo com `Input` ignorado no versionamento.

### Próximas evoluções sugeridas
- Ajustar regras por banco/cartão para aumentar precisão do parser de PDF.
- Criar mecanismo de reclassificação manual + persistência das decisões.
- Adicionar testes automatizados para parsers.

## Como manter este arquivo atualizado
Em cada nova rodada, adicionar uma seção no formato:

`## Rodada N - Título (YYYY-MM-DD)`

com blocos:
- `Entregas`
- `Próximas evoluções sugeridas`
