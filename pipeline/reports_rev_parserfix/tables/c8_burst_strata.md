| learner                             | stratum                              |   horizon_s |    n |   prevalence |   auprc |   lift |   auroc |    ece |   brier |
|:------------------------------------|:-------------------------------------|------------:|-----:|-------------:|--------:|-------:|--------:|-------:|--------:|
| Event A3 rule (deployed parameters) | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0407 | 1.9698 |  0.6693 | 0.3106 |  0.2778 |
| Event A3 rule (deployed parameters) | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.0798 | 1.8507 |  0.678  | 0.3026 |  0.2733 |
| Event A3 rule (deployed parameters) | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.1454 | 1.7368 |  0.6706 | 0.2918 |  0.2692 |
| Event A3 rule (deployed parameters) | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.1982 | 1.6204 |  0.6633 | 0.2854 |  0.2689 |
| Event A3 rule (deployed parameters) | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.28   | 1.4509 |  0.6493 | 0.2771 |  0.2761 |
| Event A3 rule (deployed parameters) | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.0953 | 1.4268 |  0.6349 | 0.5186 |  0.4776 |
| Event A3 rule (deployed parameters) | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.1477 | 1.3137 |  0.621  | 0.4906 |  0.4604 |
| Event A3 rule (deployed parameters) | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.2579 | 1.2806 |  0.6225 | 0.437  |  0.4251 |
| Event A3 rule (deployed parameters) | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.3386 | 1.2395 |  0.6179 | 0.3998 |  0.4042 |
| Event A3 rule (deployed parameters) | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.4615 | 1.2018 |  0.6153 | 0.3541 |  0.3776 |
| Logistic regression                 | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0471 | 2.2791 |  0.635  | 0.1092 |  0.0362 |
| Logistic regression                 | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.0972 | 2.2524 |  0.6471 | 0.1912 |  0.089  |
| Logistic regression                 | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.17   | 2.0301 |  0.6495 | 0.2535 |  0.1567 |
| Logistic regression                 | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.2329 | 1.9035 |  0.6466 | 0.2997 |  0.2165 |
| Logistic regression                 | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3382 | 1.7522 |  0.6524 | 0.3189 |  0.273  |
| Logistic regression                 | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.0865 | 1.2949 |  0.5649 | 0.1028 |  0.077  |
| Logistic regression                 | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.1443 | 1.2831 |  0.564  | 0.1842 |  0.1465 |
| Logistic regression                 | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.2511 | 1.2466 |  0.5697 | 0.2234 |  0.2253 |
| Logistic regression                 | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.3395 | 1.2428 |  0.5767 | 0.2495 |  0.2759 |
| Logistic regression                 | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.4746 | 1.2361 |  0.5912 | 0.2452 |  0.3033 |
| LightGBM                            | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0597 | 2.891  |  0.7722 | 0.0117 |  0.0204 |
| LightGBM                            | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.1287 | 2.9833 |  0.7698 | 0.0191 |  0.0406 |
| LightGBM                            | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.208  | 2.4837 |  0.7441 | 0.032  |  0.075  |
| LightGBM                            | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.272  | 2.2235 |  0.7318 | 0.0436 |  0.1052 |
| LightGBM                            | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3685 | 1.9093 |  0.7219 | 0.06   |  0.1511 |
| LightGBM                            | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.1238 | 1.8529 |  0.7103 | 0.0213 |  0.0608 |
| LightGBM                            | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.1983 | 1.7638 |  0.7145 | 0.0239 |  0.096  |
| LightGBM                            | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.3103 | 1.5405 |  0.6999 | 0.0381 |  0.1535 |
| LightGBM                            | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.395  | 1.4463 |  0.6933 | 0.0467 |  0.1884 |
| LightGBM                            | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.5216 | 1.3585 |  0.6869 | 0.0544 |  0.2205 |
| MLP                                 | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0757 | 3.6639 |  0.7975 | 0.0091 |  0.02   |
| MLP                                 | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.1156 | 2.6811 |  0.7611 | 0.0167 |  0.0412 |
| MLP                                 | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.2063 | 2.4645 |  0.7433 | 0.0261 |  0.074  |
| MLP                                 | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.2803 | 2.2911 |  0.7381 | 0.0351 |  0.1012 |
| MLP                                 | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3853 | 1.9964 |  0.728  | 0.0489 |  0.1429 |
| MLP                                 | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.1138 | 1.7038 |  0.68   | 0.0207 |  0.0617 |
| MLP                                 | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.2066 | 1.8372 |  0.6977 | 0.0299 |  0.0967 |
| MLP                                 | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.3603 | 1.7888 |  0.7057 | 0.0374 |  0.1487 |
| MLP                                 | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.4584 | 1.6784 |  0.7028 | 0.042  |  0.1804 |
| MLP                                 | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.5821 | 1.516  |  0.6969 | 0.0628 |  0.2135 |
| GRU                                 | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0473 | 2.288  |  0.7018 | 0.0246 |  0.0225 |
| GRU                                 | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.0901 | 2.0897 |  0.685  | 0.0404 |  0.0463 |
| GRU                                 | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.1697 | 2.0266 |  0.684  | 0.0529 |  0.0826 |
| GRU                                 | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.2356 | 1.9263 |  0.6787 | 0.0637 |  0.1131 |
| GRU                                 | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3369 | 1.7457 |  0.6701 | 0.0733 |  0.1586 |
| GRU                                 | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.1039 | 1.5557 |  0.6314 | 0.0237 |  0.0628 |
| GRU                                 | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.1674 | 1.4887 |  0.6415 | 0.0434 |  0.1016 |
| GRU                                 | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.3081 | 1.5295 |  0.6531 | 0.0535 |  0.159  |
| GRU                                 | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.4129 | 1.5118 |  0.6591 | 0.0642 |  0.193  |
| GRU                                 | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.5441 | 1.4172 |  0.6614 | 0.0706 |  0.2251 |
| TCN                                 | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0808 | 3.9134 |  0.7911 | 0.0093 |  0.02   |
| TCN                                 | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.1165 | 2.7009 |  0.7606 | 0.0185 |  0.0412 |
| TCN                                 | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.2023 | 2.4163 |  0.7455 | 0.0308 |  0.0748 |
| TCN                                 | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.2746 | 2.2451 |  0.7402 | 0.0392 |  0.1026 |
| TCN                                 | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3774 | 1.9554 |  0.7321 | 0.0485 |  0.1437 |
| TCN                                 | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.1204 | 1.8017 |  0.6714 | 0.0237 |  0.0617 |
| TCN                                 | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.1976 | 1.7574 |  0.6858 | 0.0353 |  0.0977 |
| TCN                                 | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.3414 | 1.695  |  0.6919 | 0.0512 |  0.1521 |
| TCN                                 | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.4418 | 1.6175 |  0.6906 | 0.0595 |  0.1848 |
| TCN                                 | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.5742 | 1.4953 |  0.6926 | 0.0577 |  0.2147 |
| Transformer                         | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0597 | 2.8898 |  0.7597 | 0.0152 |  0.0204 |
| Transformer                         | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.0971 | 2.2506 |  0.705  | 0.0242 |  0.0415 |
| Transformer                         | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.1783 | 2.1295 |  0.711  | 0.038  |  0.0755 |
| Transformer                         | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.2411 | 1.9708 |  0.7091 | 0.0514 |  0.1044 |
| Transformer                         | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.342  | 1.772  |  0.7026 | 0.0586 |  0.1491 |
| Transformer                         | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.1211 | 1.812  |  0.6727 | 0.0257 |  0.0615 |
| Transformer                         | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.1905 | 1.6941 |  0.6802 | 0.0353 |  0.0975 |
| Transformer                         | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.3182 | 1.5798 |  0.6747 | 0.0542 |  0.1547 |
| Transformer                         | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.4099 | 1.5005 |  0.6732 | 0.0615 |  0.1889 |
| Transformer                         | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.5345 | 1.3921 |  0.6707 | 0.0807 |  0.2234 |
| Dwell time only (LightGBM)          | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0265 | 1.2811 |  0.529  | 0.0102 |  0.0203 |
| Dwell time only (LightGBM)          | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.0571 | 1.3229 |  0.5498 | 0.0155 |  0.0414 |
| Dwell time only (LightGBM)          | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.1085 | 1.2958 |  0.5551 | 0.0259 |  0.0769 |
| Dwell time only (LightGBM)          | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.1533 | 1.2528 |  0.5565 | 0.0369 |  0.1079 |
| Dwell time only (LightGBM)          | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.2407 | 1.2473 |  0.5634 | 0.0421 |  0.1562 |
| Dwell time only (LightGBM)          | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.0714 | 1.0685 |  0.5249 | 0.0175 |  0.0627 |
| Dwell time only (LightGBM)          | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.1204 | 1.0706 |  0.5171 | 0.0269 |  0.1005 |
| Dwell time only (LightGBM)          | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.2172 | 1.078  |  0.5277 | 0.0449 |  0.1619 |
| Dwell time only (LightGBM)          | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.2945 | 1.0784 |  0.5322 | 0.0468 |  0.1999 |
| Dwell time only (LightGBM)          | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.4161 | 1.0838 |  0.542  | 0.0512 |  0.2377 |
| History block only (LightGBM)       | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0269 | 1.3013 |  0.5588 | 0.0109 |  0.0204 |
| History block only (LightGBM)       | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.0609 | 1.4123 |  0.5664 | 0.0183 |  0.0415 |
| History block only (LightGBM)       | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.1133 | 1.3537 |  0.5636 | 0.0318 |  0.0771 |
| History block only (LightGBM)       | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.156  | 1.2754 |  0.5614 | 0.0425 |  0.1082 |
| History block only (LightGBM)       | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.2362 | 1.224  |  0.5601 | 0.0444 |  0.1565 |
| History block only (LightGBM)       | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.0785 | 1.1745 |  0.5623 | 0.016  |  0.0623 |
| History block only (LightGBM)       | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.133  | 1.1828 |  0.5615 | 0.0248 |  0.0996 |
| History block only (LightGBM)       | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.2386 | 1.1848 |  0.5742 | 0.0296 |  0.1596 |
| History block only (LightGBM)       | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.3301 | 1.2087 |  0.5889 | 0.0406 |  0.1952 |
| History block only (LightGBM)       | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.4786 | 1.2464 |  0.6147 | 0.0341 |  0.2277 |
| Hawkes-kernel intensity (LR)        | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0241 | 1.1687 |  0.5499 | 0.009  |  0.0203 |
| Hawkes-kernel intensity (LR)        | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.0599 | 1.3887 |  0.5922 | 0.0142 |  0.0412 |
| Hawkes-kernel intensity (LR)        | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.1156 | 1.3804 |  0.594  | 0.0248 |  0.0763 |
| Hawkes-kernel intensity (LR)        | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.1666 | 1.3623 |  0.596  | 0.0349 |  0.1065 |
| Hawkes-kernel intensity (LR)        | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.2629 | 1.3623 |  0.5996 | 0.0468 |  0.1533 |
| Hawkes-kernel intensity (LR)        | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.0847 | 1.2682 |  0.5761 | 0.0175 |  0.0625 |
| Hawkes-kernel intensity (LR)        | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.1423 | 1.2655 |  0.5827 | 0.0239 |  0.1    |
| Hawkes-kernel intensity (LR)        | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.246  | 1.2213 |  0.585  | 0.04   |  0.1612 |
| Hawkes-kernel intensity (LR)        | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.3329 | 1.2189 |  0.5954 | 0.05   |  0.198  |
| Hawkes-kernel intensity (LR)        | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.4676 | 1.2179 |  0.6134 | 0.0569 |  0.2321 |