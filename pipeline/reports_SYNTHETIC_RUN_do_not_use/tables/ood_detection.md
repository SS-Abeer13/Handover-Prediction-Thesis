| shift    | score                 | part   |   auroc |   detection_rate |   threshold |   fpr_in_distribution |   n_in |   n_out |
|:---------|:----------------------|:-------|--------:|-----------------:|------------:|----------------------:|-------:|--------:|
| temporal | ensemble_disagreement | val    |  0.5072 |           0.0451 |      0.0489 |                0.0501 |   5467 |    4612 |
| temporal | mahalanobis           | val    |  0.5307 |           0.0694 |    205.9657 |                0.0501 |   5467 |    4612 |
| temporal | knn                   | val    |  0.4900 |           0.0484 |      0.4783 |                0.0501 |   5467 |    4612 |
| mobility | ensemble_disagreement | val    |  0.4984 |           0.0608 |      0.0461 |                0.0501 |   7350 |    2729 |
| mobility | mahalanobis           | val    |  0.4948 |           0.0484 |    216.7718 |                0.0501 |   7350 |    2729 |
| mobility | knn                   | val    |  0.5205 |           0.0583 |      0.4754 |                0.0501 |   7350 |    2729 |