# ClassificadorGastos

Aplicação para processar faturas de cartão de crédito em `PDF`, `CSV` e `OFX`, classificar gastos por categoria e analisar a evolução mensal com visão detalhada por mês.

## Estrutura do projeto

```text
ClassificadorGastos/
├── Input/                  # faturas (ignorado no Git)
├── src/
│   ├── app.py              # dashboard Streamlit
│   ├── pipeline.py         # ingestão e consolidação
│   ├── classifier.py       # classificação por categorias
│   ├── analytics.py        # análises mensais
│   └── parsers/            # leitores PDF/CSV/OFX
├── docs/
│   └── IMPLEMENTACOES.md   # histórico das rodadas
├── requirements.txt
└── .gitignore
```

## Preparação do ambiente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Como usar

1. Coloque os arquivos da fatura dentro da pasta `Input` (`.pdf`, `.csv`, `.ofx`).
2. Execute:

```bash
streamlit run src/app.py
```

3. No dashboard:
	- veja o gráfico de evolução mensal;
	- clique em um mês para ver os detalhes;
	- analise distribuição por categoria e lançamentos individuais.

## Sigilo dos dados

O `.gitignore` está configurado para **não versionar os arquivos da pasta `Input`**. Assim, as faturas e os gastos permanecem locais.

## Documentação contínua

O histórico de evolução é mantido em `docs/IMPLEMENTACOES.md`.
A cada nova rodada, adicionaremos uma seção com data, entregas e próximos passos.
