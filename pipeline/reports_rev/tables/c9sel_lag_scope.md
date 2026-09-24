| arm        | learner                             |   columns_lagged |   horizon_s |    n |   prevalence |   auprc |   lift |   auroc |
|:-----------|:------------------------------------|-----------------:|------------:|-----:|-------------:|--------:|-------:|--------:|
| none       | Event A3 rule (deployed parameters) |                0 |         0.5 | 8586 |       0.0372 |  0.0621 | 1.6721 |  0.6732 |
| neighbour  | Event A3 rule (deployed parameters) |               31 |         0.5 | 8586 |       0.0372 |  0.0675 | 1.8175 |  0.6942 |
| serving    | Event A3 rule (deployed parameters) |               56 |         0.5 | 8586 |       0.0372 |  0.0621 | 1.6721 |  0.6732 |
| assignment | Event A3 rule (deployed parameters) |               92 |         0.5 | 8586 |       0.0372 |  0.0675 | 1.8175 |  0.6942 |
| all        | Event A3 rule (deployed parameters) |              109 |         0.5 | 8586 |       0.0372 |  0.0675 | 1.8175 |  0.6942 |
| none       | Event A3 rule (deployed parameters) |                0 |         1   | 8586 |       0.0679 |  0.1168 | 1.7205 |  0.6824 |
| neighbour  | Event A3 rule (deployed parameters) |               31 |         1   | 8586 |       0.0679 |  0.1163 | 1.7135 |  0.6888 |
| serving    | Event A3 rule (deployed parameters) |               56 |         1   | 8586 |       0.0679 |  0.1168 | 1.7205 |  0.6824 |
| assignment | Event A3 rule (deployed parameters) |               92 |         1   | 8586 |       0.0679 |  0.1163 | 1.7135 |  0.6888 |
| all        | Event A3 rule (deployed parameters) |              109 |         1   | 8586 |       0.0679 |  0.1163 | 1.7135 |  0.6888 |
| none       | Event A3 rule (deployed parameters) |                0 |         2   | 8586 |       0.1258 |  0.2157 | 1.7149 |  0.6936 |
| neighbour  | Event A3 rule (deployed parameters) |               31 |         2   | 8586 |       0.1258 |  0.2038 | 1.6206 |  0.6825 |
| serving    | Event A3 rule (deployed parameters) |               56 |         2   | 8586 |       0.1258 |  0.2157 | 1.7149 |  0.6936 |
| assignment | Event A3 rule (deployed parameters) |               92 |         2   | 8586 |       0.1258 |  0.2038 | 1.6206 |  0.6825 |
| all        | Event A3 rule (deployed parameters) |              109 |         2   | 8586 |       0.1258 |  0.2038 | 1.6206 |  0.6825 |
| none       | Event A3 rule (deployed parameters) |                0 |         3   | 8586 |       0.1762 |  0.2878 | 1.6331 |  0.6911 |
| neighbour  | Event A3 rule (deployed parameters) |               31 |         3   | 8586 |       0.1762 |  0.272  | 1.5437 |  0.6752 |
| serving    | Event A3 rule (deployed parameters) |               56 |         3   | 8586 |       0.1762 |  0.2878 | 1.6331 |  0.6911 |
| assignment | Event A3 rule (deployed parameters) |               92 |         3   | 8586 |       0.1762 |  0.272  | 1.5437 |  0.6752 |
| all        | Event A3 rule (deployed parameters) |              109 |         3   | 8586 |       0.1762 |  0.272  | 1.5437 |  0.6752 |
| none       | Event A3 rule (deployed parameters) |                0 |         5   | 8586 |       0.2612 |  0.3918 | 1.4998 |  0.6805 |
| neighbour  | Event A3 rule (deployed parameters) |               31 |         5   | 8586 |       0.2612 |  0.3743 | 1.4329 |  0.666  |
| serving    | Event A3 rule (deployed parameters) |               56 |         5   | 8586 |       0.2612 |  0.3918 | 1.4998 |  0.6805 |
| assignment | Event A3 rule (deployed parameters) |               92 |         5   | 8586 |       0.2612 |  0.3743 | 1.4329 |  0.666  |
| all        | Event A3 rule (deployed parameters) |              109 |         5   | 8586 |       0.2612 |  0.3743 | 1.4329 |  0.666  |
| none       | LightGBM                            |                0 |         0.5 | 8586 |       0.0372 |  0.3551 | 9.5573 |  0.9093 |
| neighbour  | LightGBM                            |               31 |         0.5 | 8586 |       0.0372 |  0.3337 | 8.9828 |  0.9024 |
| serving    | LightGBM                            |               56 |         0.5 | 8586 |       0.0372 |  0.1018 | 2.739  |  0.7646 |
| assignment | LightGBM                            |               92 |         0.5 | 8586 |       0.0372 |  0.0875 | 2.3548 |  0.7435 |
| all        | LightGBM                            |              109 |         0.5 | 8586 |       0.0372 |  0.0859 | 2.3117 |  0.7439 |
| none       | LightGBM                            |                0 |         1   | 8586 |       0.0679 |  0.6067 | 8.9356 |  0.9109 |
| neighbour  | LightGBM                            |               31 |         1   | 8586 |       0.0679 |  0.5954 | 8.7685 |  0.9049 |
| serving    | LightGBM                            |               56 |         1   | 8586 |       0.0679 |  0.1784 | 2.6278 |  0.7684 |
| assignment | LightGBM                            |               92 |         1   | 8586 |       0.0679 |  0.1589 | 2.3397 |  0.7478 |
| all        | LightGBM                            |              109 |         1   | 8586 |       0.0679 |  0.1596 | 2.351  |  0.7498 |
| none       | LightGBM                            |                0 |         2   | 8586 |       0.1258 |  0.5212 | 4.1432 |  0.8372 |
| neighbour  | LightGBM                            |               31 |         2   | 8586 |       0.1258 |  0.5125 | 4.0742 |  0.8314 |
| serving    | LightGBM                            |               56 |         2   | 8586 |       0.1258 |  0.2696 | 2.1432 |  0.7501 |
| assignment | LightGBM                            |               92 |         2   | 8586 |       0.1258 |  0.2567 | 2.041  |  0.7363 |
| all        | LightGBM                            |              109 |         2   | 8586 |       0.1258 |  0.2591 | 2.0598 |  0.7377 |
| none       | LightGBM                            |                0 |         3   | 8586 |       0.1762 |  0.5204 | 2.9534 |  0.8046 |
| neighbour  | LightGBM                            |               31 |         3   | 8586 |       0.1762 |  0.5101 | 2.8946 |  0.7972 |
| serving    | LightGBM                            |               56 |         3   | 8586 |       0.1762 |  0.345  | 1.9578 |  0.74   |
| assignment | LightGBM                            |               92 |         3   | 8586 |       0.1762 |  0.3322 | 1.8852 |  0.7266 |
| all        | LightGBM                            |              109 |         3   | 8586 |       0.1762 |  0.3345 | 1.8983 |  0.7282 |
| none       | LightGBM                            |                0 |         5   | 8586 |       0.2612 |  0.5585 | 2.1379 |  0.7694 |
| neighbour  | LightGBM                            |               31 |         5   | 8586 |       0.2612 |  0.5503 | 2.1066 |  0.764  |
| serving    | LightGBM                            |               56 |         5   | 8586 |       0.2612 |  0.4508 | 1.7255 |  0.7269 |
| assignment | LightGBM                            |               92 |         5   | 8586 |       0.2612 |  0.4386 | 1.679  |  0.716  |
| all        | LightGBM                            |              109 |         5   | 8586 |       0.2612 |  0.4453 | 1.7047 |  0.7189 |