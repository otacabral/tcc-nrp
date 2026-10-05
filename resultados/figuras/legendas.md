# Tabelas e figuras do capítulo de resultados

Geradas por `src/figuras_tcc.py`. Nenhum número digitado à mão. Tempo é limite operacional desta máquina, uma medição por tamanho.

## tab_p1_curva (.csv, .md)

Curva de escalabilidade com o objetivo da ferramenta, caso sem folga (demanda igual à capacidade de N pessoas a 168 h): estado, prova e tempo de cada etapa, por tamanho.

*Origem: resultados/escalabilidade_objetivo.csv (gravado em 03/10/2026). Máquina: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel | Windows-10-10.0.26200-SP0 | Python 3.11.9. Solver: appsi_highs (highspy 1.15.1 instalado ao gerar esta figura).*

## tab_p1_folga (.csv, .md)

Rodada com folga (mesma demanda, equipe 10% maior): etapas 1 e 2 e amplitude da fração do contrato por categoria, antes e depois da etapa 2.

*Origem: resultados/escalabilidade_objetivo_folga.csv (gravado em 05/10/2026). Máquina: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel | Windows-10-10.0.26200-SP0 | Python 3.11.9. Solver: appsi_highs (highspy 1.15.1 instalado ao gerar esta figura).*

## fig_p1_tempos_etapa1.png

Tempo de relógio da etapa 1 e tempo até a primeira escala legal, por tamanho; marcados os tamanhos em que a etapa 1 terminou sem prova de otimalidade.

*Origem: resultados/escalabilidade_objetivo.csv (gravado em 03/10/2026). Máquina: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel | Windows-10-10.0.26200-SP0 | Python 3.11.9. Solver: appsi_highs (highspy 1.15.1 instalado ao gerar esta figura).*

## fig_folga_amplitude.png

Amplitude da fração do contrato cumprida, por categoria, na escala da etapa 1 e na da etapa 2, por tamanho da rodada com folga.

*Origem: resultados/escalabilidade_objetivo_folga.csv (gravado em 05/10/2026). Máquina: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel | Windows-10-10.0.26200-SP0 | Python 3.11.9. Solver: appsi_highs (highspy 1.15.1 instalado ao gerar esta figura).*

## fig_folga_tempo_etapa2.png

Etapa 2 da rodada com folga: tempo até 90% da redução final da amplitude e tempo de relógio total, por tamanho.

*Origem: resultados/escalabilidade_objetivo_folga.csv (gravado em 05/10/2026). Máquina: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel | Windows-10-10.0.26200-SP0 | Python 3.11.9. Solver: appsi_highs (highspy 1.15.1 instalado ao gerar esta figura).*
