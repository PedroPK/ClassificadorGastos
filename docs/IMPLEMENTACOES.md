# Histórico de Implementações

## Rodada 4 - Encerramento facilitado da aplicação (2026-02-28)

### Entregas
- Criado launcher em `src/run_app.py` para iniciar o Streamlit.
- Tratamento explícito de sinal `SIGINT` (`Ctrl + C`) com encerramento limpo.
- Finalização do processo filho e subprocessos associados para evitar app "presa" no terminal.
- README atualizado para usar `python src/run_app.py` como comando padrão.

### Próximas evoluções sugeridas
- Adicionar um script de atalho (`make run`) para simplificar ainda mais o comando.

## Rodada 3 - Controle de duplicidade mensal (2026-02-28)

### Entregas
- Regra de seleção automática do melhor formato por mês (`OFX/CSV/PDF`) com base em volume e riqueza descritiva.
- Garantia de uso de apenas uma fonte principal por mês para evitar contagem dupla entre formatos.
- Deduplicação adicional de lançamentos repetidos entre arquivos do mesmo mês.
- README atualizado com o comportamento de deduplicação.

### Próximas evoluções sugeridas
- Expor no dashboard qual formato foi selecionado em cada mês.
- Permitir override manual da fonte por mês para auditoria.

## Rodada 2 - Suporte a ZIP (2026-02-28)

### Entregas
- Pipeline atualizado para aceitar arquivos `.zip` na pasta `Input`.
- Extração temporária dos conteúdos do ZIP sem persistir dados fora da execução.
- Processamento dos arquivos internos `PDF`, `CSV` e `OFX` automaticamente.
- Rastreabilidade da origem no campo `source_file` no formato `arquivo.zip!caminho/interno.ext`.
- README atualizado com o novo formato suportado.

### Próximas evoluções sugeridas
- Tratar ZIP aninhado (`zip` dentro de `zip`) de forma opcional.
- Exibir no dashboard um filtro por arquivo de origem.

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
