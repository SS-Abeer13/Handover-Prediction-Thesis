| arm        | learner                             |   columns_lagged |   horizon_s |    n |   prevalence |   auprc |   lift |   auroc |
|:-----------|:------------------------------------|-----------------:|------------:|-----:|-------------:|--------:|-------:|--------:|
| none       | Event A3 rule (deployed parameters) |                0 |         0.5 | 8586 |       0.0372 |  0.0599 | 1.611  |  0.6708 |
| neighbour  | Event A3 rule (deployed parameters) |               31 |         0.5 | 8586 |       0.0372 |  0.0683 | 1.8395 |  0.6937 |
| serving    | Event A3 rule (deployed parameters) |               56 |         0.5 | 8586 |       0.0372 |  0.0599 | 1.611  |  0.6708 |
| assignment | Event A3 rule (deployed parameters) |               92 |         0.5 | 8586 |       0.0372 |  0.0683 | 1.8395 |  0.6937 |
| all        | Event A3 rule (deployed parameters) |              109 |         0.5 | 8586 |       0.0372 |  0.0683 | 1.8395 |  0.6937 |
| none       | Event A3 rule (deployed parameters) |                0 |         1   | 8586 |       0.0679 |  0.1136 | 1.6736 |  0.6834 |
| neighbour  | Event A3 rule (deployed parameters) |               31 |         1   | 8586 |       0.0679 |  0.1143 | 1.6828 |  0.6849 |
| serving    | Event A3 rule (deployed parameters) |               56 |         1   | 8586 |       0.0679 |  0.1136 | 1.6736 |  0.6834 |
| assignment | Event A3 rule (deployed parameters) |               92 |         1   | 8586 |       0.0679 |  0.1143 | 1.6828 |  0.6849 |
| all        | Event A3 rule (deployed parameters) |              109 |         1   | 8586 |       0.0679 |  0.1143 | 1.6828 |  0.6849 |
| none       | Event A3 rule (deployed parameters) |                0 |         2   | 8586 |       0.1258 |  0.2111 | 1.6782 |  0.694  |
| neighbour  | Event A3 rule (deployed parameters) |               31 |         2   | 8586 |       0.1258 |  0.2011 | 1.5989 |  0.6817 |
| serving    | Event A3 rule (deployed parameters) |               56 |         2   | 8586 |       0.1258 |  0.2111 | 1.6782 |  0.694  |
| assignment | Event A3 rule (deployed parameters) |               92 |         2   | 8586 |       0.1258 |  0.2011 | 1.5989 |  0.6817 |
| all        | Event A3 rule (deployed parameters) |              109 |         2   | 8586 |       0.1258 |  0.2011 | 1.5989 |  0.6817 |
| none       | Event A3 rule (deployed parameters) |                0 |         3   | 8586 |       0.1762 |  0.2832 | 1.6073 |  0.6929 |
| neighbour  | Event A3 rule (deployed parameters) |               31 |         3   | 8586 |       0.1762 |  0.2681 | 1.5213 |  0.6757 |
| serving    | Event A3 rule (deployed parameters) |               56 |         3   | 8586 |       0.1762 |  0.2832 | 1.6073 |  0.6929 |
| assignment | Event A3 rule (deployed parameters) |               92 |         3   | 8586 |       0.1762 |  0.2681 | 1.5213 |  0.6757 |
| all        | Event A3 rule (deployed parameters) |              109 |         3   | 8586 |       0.1762 |  0.2681 | 1.5213 |  0.6757 |
| none       | Event A3 rule (deployed parameters) |                0 |         5   | 8586 |       0.2612 |  0.3859 | 1.4772 |  0.6828 |
| neighbour  | Event A3 rule (deployed parameters) |               31 |         5   | 8586 |       0.2612 |  0.3703 | 1.4174 |  0.6666 |
| serving    | Event A3 rule (deployed parameters) |               56 |         5   | 8586 |       0.2612 |  0.3859 | 1.4772 |  0.6828 |
| assignment | Event A3 rule (deployed parameters) |               92 |         5   | 8586 |       0.2612 |  0.3703 | 1.4174 |  0.6666 |
| all        | Event A3 rule (deployed parameters) |              109 |         5   | 8586 |       0.2612 |  0.3703 | 1.4174 |  0.6666 |
| none       | LightGBM                            |                0 |         0.5 | 8586 |       0.0372 |  0.35   | 9.4191 |  0.9106 |
| neighbour  | LightGBM                            |               31 |         0.5 | 8586 |       0.0372 |  0.3401 | 9.1547 |  0.9052 |
| serving    | LightGBM                            |               56 |         0.5 | 8586 |       0.0372 |  0.1052 | 2.8313 |  0.7728 |
| assignment | LightGBM                            |               92 |         0.5 | 8586 |       0.0372 |  0.0843 | 2.2681 |  0.7418 |
| all        | LightGBM                            |              109 |         0.5 | 8586 |       0.0372 |  0.0841 | 2.2648 |  0.7407 |
| none       | LightGBM                            |                0 |         1   | 8586 |       0.0679 |  0.6038 | 8.892  |  0.9106 |
| neighbour  | LightGBM                            |               31 |         1   | 8586 |       0.0679 |  0.6011 | 8.8529 |  0.9051 |
| serving    | LightGBM                            |               56 |         1   | 8586 |       0.0679 |  0.1816 | 2.6742 |  0.7721 |
| assignment | LightGBM                            |               92 |         1   | 8586 |       0.0679 |  0.1564 | 2.304  |  0.7434 |
| all        | LightGBM                            |              109 |         1   | 8586 |       0.0679 |  0.1565 | 2.3042 |  0.7437 |
| none       | LightGBM                            |                0 |         2   | 8586 |       0.1258 |  0.5205 | 4.1377 |  0.837  |
| neighbour  | LightGBM                            |               31 |         2   | 8586 |       0.1258 |  0.5153 | 4.0965 |  0.8322 |
| serving    | LightGBM                            |               56 |         2   | 8586 |       0.1258 |  0.2678 | 2.1289 |  0.7475 |
| assignment | LightGBM                            |               92 |         2   | 8586 |       0.1258 |  0.2529 | 2.0109 |  0.7307 |
| all        | LightGBM                            |              109 |         2   | 8586 |       0.1258 |  0.2514 | 1.9985 |  0.731  |
| none       | LightGBM                            |                0 |         3   | 8586 |       0.1762 |  0.519  | 2.9451 |  0.8023 |
| neighbour  | LightGBM                            |               31 |         3   | 8586 |       0.1762 |  0.514  | 2.9166 |  0.7977 |
| serving    | LightGBM                            |               56 |         3   | 8586 |       0.1762 |  0.3384 | 1.9206 |  0.7352 |
| assignment | LightGBM                            |               92 |         3   | 8586 |       0.1762 |  0.3253 | 1.8463 |  0.7205 |
| all        | LightGBM                            |              109 |         3   | 8586 |       0.1762 |  0.325  | 1.8442 |  0.7221 |
| none       | LightGBM                            |                0 |         5   | 8586 |       0.2612 |  0.5562 | 2.1289 |  0.767  |
| neighbour  | LightGBM                            |               31 |         5   | 8586 |       0.2612 |  0.5546 | 2.123  |  0.7648 |
| serving    | LightGBM                            |               56 |         5   | 8586 |       0.2612 |  0.4434 | 1.6975 |  0.7204 |
| assignment | LightGBM                            |               92 |         5   | 8586 |       0.2612 |  0.4353 | 1.6662 |  0.7105 |
| all        | LightGBM                            |              109 |         5   | 8586 |       0.2612 |  0.4352 | 1.6657 |  0.7133 |