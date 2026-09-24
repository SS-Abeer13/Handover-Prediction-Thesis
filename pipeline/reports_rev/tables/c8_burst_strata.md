| learner                             | stratum                              |   horizon_s |    n |   prevalence |   auprc |   lift |   auroc |    ece |   brier |
|:------------------------------------|:-------------------------------------|------------:|-----:|-------------:|--------:|-------:|--------:|-------:|--------:|
| Event A3 rule (deployed parameters) | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0447 | 2.1621 |  0.6714 | 0.2883 |  0.2555 |
| Event A3 rule (deployed parameters) | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.0851 | 1.9737 |  0.6813 | 0.2811 |  0.2522 |
| Event A3 rule (deployed parameters) | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.1563 | 1.8672 |  0.675  | 0.2709 |  0.2507 |
| Event A3 rule (deployed parameters) | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.2137 | 1.7469 |  0.6672 | 0.265  |  0.2526 |
| Event A3 rule (deployed parameters) | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3022 | 1.566  |  0.6562 | 0.2654 |  0.2625 |
| Event A3 rule (deployed parameters) | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.0909 | 1.361  |  0.633  | 0.4865 |  0.4473 |
| Event A3 rule (deployed parameters) | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.1469 | 1.3067 |  0.6259 | 0.4597 |  0.4313 |
| Event A3 rule (deployed parameters) | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.2534 | 1.2578 |  0.6192 | 0.4141 |  0.4052 |
| Event A3 rule (deployed parameters) | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.3319 | 1.2151 |  0.6117 | 0.3873 |  0.3905 |
| Event A3 rule (deployed parameters) | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.4462 | 1.162  |  0.6016 | 0.358  |  0.3776 |
| Logistic regression                 | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0464 | 2.2469 |  0.6622 | 0.1162 |  0.0361 |
| Logistic regression                 | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.0978 | 2.2678 |  0.6793 | 0.2043 |  0.0883 |
| Logistic regression                 | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.1696 | 2.0257 |  0.6755 | 0.2696 |  0.1549 |
| Logistic regression                 | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.2291 | 1.8727 |  0.6693 | 0.3177 |  0.2129 |
| Logistic regression                 | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3309 | 1.7145 |  0.6661 | 0.3365 |  0.2674 |
| Logistic regression                 | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.0934 | 1.3979 |  0.6011 | 0.1099 |  0.0766 |
| Logistic regression                 | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.157  | 1.3965 |  0.6084 | 0.2004 |  0.145  |
| Logistic regression                 | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.2698 | 1.3396 |  0.6065 | 0.2387 |  0.2211 |
| Logistic regression                 | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.358  | 1.3105 |  0.6118 | 0.266  |  0.2694 |
| Logistic regression                 | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.4893 | 1.2743 |  0.6188 | 0.2551 |  0.2958 |
| LightGBM                            | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0649 | 3.1435 |  0.7637 | 0.0085 |  0.0201 |
| LightGBM                            | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.1331 | 3.0854 |  0.7716 | 0.0162 |  0.0399 |
| LightGBM                            | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.2169 | 2.5905 |  0.7489 | 0.0235 |  0.0731 |
| LightGBM                            | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.2818 | 2.3036 |  0.7405 | 0.0329 |  0.1019 |
| LightGBM                            | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3833 | 1.9857 |  0.7322 | 0.0476 |  0.1455 |
| LightGBM                            | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.1309 | 1.9587 |  0.7134 | 0.0161 |  0.0605 |
| LightGBM                            | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.2118 | 1.8834 |  0.7203 | 0.0198 |  0.0949 |
| LightGBM                            | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.3307 | 1.6419 |  0.706  | 0.0301 |  0.1506 |
| LightGBM                            | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.4186 | 1.5324 |  0.6982 | 0.0413 |  0.1849 |
| LightGBM                            | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.5447 | 1.4187 |  0.69   | 0.0539 |  0.2175 |
| MLP                                 | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0731 | 3.5359 |  0.7772 | 0.0168 |  0.0204 |
| MLP                                 | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.1211 | 2.808  |  0.751  | 0.0291 |  0.0418 |
| MLP                                 | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.191  | 2.281  |  0.7263 | 0.0432 |  0.0767 |
| MLP                                 | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.2577 | 2.1067 |  0.7177 | 0.0529 |  0.1059 |
| MLP                                 | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3602 | 1.8664 |  0.7102 | 0.0609 |  0.1485 |
| MLP                                 | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.1255 | 1.8777 |  0.6714 | 0.0202 |  0.0616 |
| MLP                                 | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.214  | 1.9032 |  0.6894 | 0.031  |  0.0974 |
| MLP                                 | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.3501 | 1.738  |  0.6923 | 0.0317 |  0.151  |
| MLP                                 | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.4386 | 1.6056 |  0.6879 | 0.0437 |  0.1845 |
| MLP                                 | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.5548 | 1.4449 |  0.6853 | 0.0567 |  0.2168 |
| GRU                                 | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0451 | 2.1845 |  0.7067 | 0.0217 |  0.0229 |
| GRU                                 | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.0882 | 2.0448 |  0.6962 | 0.0361 |  0.0472 |
| GRU                                 | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.1653 | 1.9749 |  0.6944 | 0.0461 |  0.0842 |
| GRU                                 | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.2313 | 1.8912 |  0.6936 | 0.0517 |  0.1145 |
| GRU                                 | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3385 | 1.7539 |  0.6887 | 0.0586 |  0.1582 |
| GRU                                 | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.107  | 1.6021 |  0.6366 | 0.0255 |  0.0629 |
| GRU                                 | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.1717 | 1.5265 |  0.6453 | 0.0391 |  0.1018 |
| GRU                                 | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.3036 | 1.5072 |  0.652  | 0.0573 |  0.1599 |
| GRU                                 | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.4043 | 1.48   |  0.6556 | 0.0654 |  0.1941 |
| GRU                                 | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.5283 | 1.376  |  0.6528 | 0.0735 |  0.2281 |
| TCN                                 | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0749 | 3.6249 |  0.7834 | 0.0106 |  0.0201 |
| TCN                                 | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.1122 | 2.6006 |  0.7544 | 0.0196 |  0.0415 |
| TCN                                 | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.1928 | 2.3027 |  0.7417 | 0.0315 |  0.0755 |
| TCN                                 | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.2617 | 2.1393 |  0.7366 | 0.0437 |  0.1038 |
| TCN                                 | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3662 | 1.8976 |  0.7308 | 0.0497 |  0.1451 |
| TCN                                 | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.1252 | 1.8732 |  0.6773 | 0.0183 |  0.0613 |
| TCN                                 | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.2081 | 1.851  |  0.6922 | 0.0274 |  0.0965 |
| TCN                                 | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.3498 | 1.7363 |  0.6938 | 0.0353 |  0.1504 |
| TCN                                 | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.4502 | 1.6484 |  0.6941 | 0.0505 |  0.1826 |
| TCN                                 | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.5754 | 1.4987 |  0.6917 | 0.0614 |  0.2142 |
| Transformer                         | quiet (no handover in previous 10 s) |         0.5 | 5518 |       0.0207 |  0.0542 | 2.6211 |  0.7325 | 0.0131 |  0.0205 |
| Transformer                         | quiet (no handover in previous 10 s) |         1   | 5518 |       0.0431 |  0.1004 | 2.3281 |  0.7017 | 0.0212 |  0.0411 |
| Transformer                         | quiet (no handover in previous 10 s) |         2   | 5518 |       0.0837 |  0.1775 | 2.1204 |  0.703  | 0.0334 |  0.0753 |
| Transformer                         | quiet (no handover in previous 10 s) |         3   | 5518 |       0.1223 |  0.24   | 1.9616 |  0.6993 | 0.04   |  0.104  |
| Transformer                         | quiet (no handover in previous 10 s) |         5   | 5518 |       0.193  |  0.3448 | 1.7864 |  0.694  | 0.0573 |  0.1481 |
| Transformer                         | in burst (handover 2-10 s earlier)   |         0.5 | 3068 |       0.0668 |  0.1193 | 1.7853 |  0.6674 | 0.022  |  0.0616 |
| Transformer                         | in burst (handover 2-10 s earlier)   |         1   | 3068 |       0.1125 |  0.1936 | 1.7219 |  0.6795 | 0.0377 |  0.0972 |
| Transformer                         | in burst (handover 2-10 s earlier)   |         2   | 3068 |       0.2014 |  0.3171 | 1.5744 |  0.6711 | 0.0478 |  0.1545 |
| Transformer                         | in burst (handover 2-10 s earlier)   |         3   | 3068 |       0.2731 |  0.4135 | 1.5139 |  0.6731 | 0.054  |  0.1877 |
| Transformer                         | in burst (handover 2-10 s earlier)   |         5   | 3068 |       0.384  |  0.5366 | 1.3975 |  0.6668 | 0.0642 |  0.2223 |
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