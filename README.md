Entrada: você digita um termo (o padrão é “PETR4”) e clica em “Analisar Volume e Gerar Gráfico”. Ele também roda uma análise automaticamente ao abrir.
Top 20 termos relacionados: usa o endpoint de autocompletar do Google (suggestqueries.google.com) para buscar sugestões do termo puro e do termo combinado com sufixos (a, b, c, hoje, como, dividendo, comprar, cotacao etc.). Cada sugestão ganha pontos conforme a posição em que aparece, e os pontos são somados. Os 20 maiores viram uma tabela com nota de 0 a 100.
“Sazonalidade” mensal: para cada mês (Jan a Dez), consulta o autocompletar com “termo + mês” (ex.: “petr4 jan”) e calcula um índice de volume.
Estatísticas: descobre o mês com maior índice, calcula a média dos 12 meses e mostra quantas vezes o pico é maior que a média (ex.: “1.35x, +35%”).
Gráfico: desenha um gráfico de barras com Matplotlib, com o mês de pico em verde e os demais em azul.
