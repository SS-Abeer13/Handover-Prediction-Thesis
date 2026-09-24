function fig35_operating_points()
%FIG35  Where the model sits on the ROC and PR planes, horizon by horizon.
%   Full curves would need the per-sample scores; what the frozen result tables
%   carry is a set of certified operating points, so they are plotted as points
%   rather than interpolated into a curve that was never measured.
S = fig_style();
h    = [0.5 1 2 3 5];
prev = [0.0368 0.0670 0.1248 0.1749 0.2592];
r01  = [0.301 0.695 0.381 0.277 0.172];    % recall at FPR 1 %
r05  = [0.732 0.747 0.513 0.395 0.322];    % recall at FPR 5 %
r10  = [0.776 0.796 0.597 0.532 0.437];    % recall at FPR 10 %
p50  = [0.563 0.983 0.620 0.551 0.564];    % precision at recall 0.5
p80  = [0.203 0.360 0.289 0.326 0.407];    % precision at recall 0.8
cols = [0.72 0.78 0.86; 0.537 0.075 0.075; 0.45 0.55 0.66; 0.30 0.42 0.56; 0.16 0.28 0.40];

newfig(1320, 700);
axA = axes('Position', [0.07 0.14 0.40 0.76]); hold on;
plot([0 1], [0 1], '--', 'Color', [0.7 0.7 0.7], 'LineWidth', 1.4);
for k = 1:5
    plot([0.01 0.05 0.10], [r01(k) r05(k) r10(k)], '-o', 'Color', cols(k,:), ...
         'LineWidth', 2.2, 'MarkerSize', 7, 'MarkerFaceColor', cols(k,:), 'MarkerEdgeColor', 'w');
    text(0.104, r10(k), sprintf('%g s', h(k)), 'FontSize', 13, 'Color', cols(k,:));
end
grid on; set(axA, 'GridColor', S.grid, 'GridAlpha', 1, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
xlim([0 0.13]); ylim([0 1]);
xlabel('False positive rate', 'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('Recall', 'FontSize', S.fs_lab, 'Color', S.ink);
title('Low-false-positive region of the ROC plane', 'FontSize', 15, 'Color', S.ink, 'FontWeight', 'normal');

axB = axes('Position', [0.57 0.14 0.40 0.76]); hold on;
for k = 1:5
    plot([0 1], [prev(k) prev(k)], ':', 'Color', cols(k,:), 'LineWidth', 1.4);
    plot([0.5 0.8], [p50(k) p80(k)], '-o', 'Color', cols(k,:), 'LineWidth', 2.2, ...
         'MarkerSize', 7, 'MarkerFaceColor', cols(k,:), 'MarkerEdgeColor', 'w');
    text(0.815, p80(k), sprintf('%g s', h(k)), 'FontSize', 13, 'Color', cols(k,:));
end
text(0.06, 0.30, 'dotted lines: the prevalence floor at each horizon', ...
     'FontSize', 13, 'Color', [0.45 0.45 0.45]);
grid on; set(axB, 'GridColor', S.grid, 'GridAlpha', 1, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
xlim([0.4 0.9]); ylim([0 1]);
xlabel('Recall', 'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('Precision', 'FontSize', S.fs_lab, 'Color', S.ink);
title('Precision at two fixed recall levels', 'FontSize', 15, 'Color', S.ink, 'FontWeight', 'normal');
savefig_png('fig35_operating_points');
end
