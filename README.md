# Eleições

Modelo para clusterização do voto a partir da estratégia de voto e rede neural para predição.

A base pode ser útil para agrupar os eleitores por outras estratégias / realizar outras análises, bem como testar outros modelos.

Há uma deficiência no modelo atual. Por causa da geração sequencial, é possível que o modelo esteja com um bootstrap inadequado (por começar analisando a urna do Acre).

Fora isso, é preciso otimizar ou repensar estratégias de normalização.

Para executar, coloque na pasta `urnas` os arquivos do TSE (como `bu_imgbu_logjez_rdv_vscmr_2022_1t_AC.zip`).

É preciso instalar o `scikit-learn`, `asn1crypto` e `py7zr`.

Para executar: `python leitor_urnas.py`.

---

Resultados iniciais apontaram uma silhueta de ~0.225 para o melhor agrupamento, além de uma predição que não teve efeito (igual ou próximo do erro ao comparar com a média).
