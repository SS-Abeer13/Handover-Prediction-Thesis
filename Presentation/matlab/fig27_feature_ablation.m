function fig27_feature_ablation()
%FIG27_FEATURE_ABLATION  Feature representation ablation across five horizons.
%   Compares Full (RF+Mobility+History+Signalling), RF+Mobility+History, and
%   Signalling Only feature representations from stage 16 ablation.
S = fig_style();
h = [0.5 1 2 3 5];

% AUROC data from signalling_ablation.csv
auc_full = [0.9344 0.9422 0.8616 0.8237 0.7924];
auc_rf   = [0.9338 0.9401 0.8573 0.8176 0.7881];
auc_sig  = [0.8105 0.8260 0.7722 0.7508 0.7213];

% Lift over prevalence floor (AUPRC / prevalence)
lift_full = [11.05 11.07 4.80 3.28 2.30];
lift_rf   = [10.76 11.07 4.76 3.25 2.28];
lift_sig  = [5.18  5.05  2.81 2.29 1.80];

newfig(1280, 720);

% Panel 1: AUROC
subplot(1, 2, 1); hold on;
plot(h, auc_full, '-o', 'Color', S.maroon, 'LineWidth', 2.8, 'MarkerSize', 9, 'MarkerFaceColor', S.maroon);
plot(h, auc_rf,   '--s', 'Color', S.navy,   'LineWidth', 2.2, 'MarkerSize', 8, 'MarkerFaceColor', 'w');
plot(h, auc_sig,  '-.^', 'Color', S.grey,   'LineWidth', 2.0, 'MarkerSize', 8, 'MarkerFaceColor', 'w');
plot([0.3 5.5], [0.5 0.5], ':', 'Color', [0.5 0.5 0.5], 'LineWidth', 1.2);

set(gca, 'XTick', h, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1);
xlim([0.3 5.4]); ylim([0.48 1.0]);
xlabel('Prediction horizon  (s)', 'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('AUROC', 'FontSize', S.fs_lab, 'Color', S.ink);
title('Discriminative Capacity (AUROC)', 'FontSize', S.fs_lab+1, 'Color', S.maroon, 'FontWeight', 'bold');

text(1.15, 0.955, 'Full Model (0.942)', 'Color', S.maroon, 'FontSize', 13, 'FontWeight', 'bold');
text(1.15, 0.925, 'RF + Mobility + History (0.940)', 'Color', S.navy, 'FontSize', 12);
text(1.15, 0.810, 'Signalling Only (0.826)', 'Color', S.grey, 'FontSize', 12);
text(0.45, 0.525, 'Chance floor (0.50)', 'Color', [0.45 0.45 0.45], 'FontSize', 11);

% Panel 2: AUPRC Lift over Prevalence
subplot(1, 2, 2); hold on;
b = bar(1:5, [lift_full; lift_rf; lift_sig]', 0.82);
b(1).FaceColor = S.maroon; b(1).EdgeColor = 'none';
b(2).FaceColor = S.navy;   b(2).EdgeColor = 'none';
b(3).FaceColor = S.grey;   b(3).EdgeColor = 'none';

set(gca, 'XTick', 1:5, 'XTickLabel', {'0.5 s', '1.0 s', '2.0 s', '3.0 s', '5.0 s'}, ...
    'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XGrid', 'off', 'YGrid', 'on');
ylim([0 12.8]);
xlabel('Prediction horizon', 'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('Lift over prevalence  (\times)', 'FontSize', S.fs_lab, 'Color', S.ink);
title('Precision-Recall Lift over Floor', 'FontSize', S.fs_lab+1, 'Color', S.maroon, 'FontWeight', 'bold');

text(2.0, 11.7, '11.1\times lift at 1 s', 'Color', S.maroon, 'FontSize', 13, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');

leg = legend({'Full (+ Signalling)', 'RF + Mob + Hist', 'Signalling Only'}, 'Location', 'northeast');
set(leg, 'Box', 'off', 'FontSize', 12);

savefig_png('fig27_feature_ablation');
end
