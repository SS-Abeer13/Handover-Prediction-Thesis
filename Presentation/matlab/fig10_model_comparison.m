function fig10_model_comparison()
%FIG10  AUPRC against the prevalence floor, seven models, five horizons.
S = fig_style();
h   = [0.5 1 2 3 5];
prev= [0.037 0.067 0.125 0.175 0.259];
lgbm= [0.416 0.784 0.627 0.598 0.606];
logr= [0.402 0.728 0.607 0.586 0.602];
mlp = [0.411 0.677 0.584 0.574 0.602];
tran= [0.367 0.567 0.470 0.463 0.512];
tcn = [0.353 0.574 0.515 0.514 0.555];
gru = [0.269 0.475 0.443 0.470 0.528];
rule= [0.065 0.118 0.221 0.298 0.411];

newfig(1180, 760); hold on;
a = area(h, prev, 'FaceColor', S.lgrey, 'EdgeColor', 'none');
try set(a, 'FaceAlpha', 0.75); end
plot(h, prev, '--', 'Color', [0.45 0.45 0.45], 'LineWidth', 1.6);

p3 = plot(h, gru,  '-^', 'Color', S.grey, 'LineWidth', 1.6, 'MarkerSize', 7, 'MarkerFaceColor', 'w');
p4 = plot(h, tcn,  '-v', 'Color', S.grey, 'LineWidth', 1.6, 'MarkerSize', 7, 'MarkerFaceColor', 'w');
p5 = plot(h, tran, '-d', 'Color', S.grey, 'LineWidth', 1.6, 'MarkerSize', 7, 'MarkerFaceColor', 'w');
p6 = plot(h, mlp,  '-s', 'Color', S.navy, 'LineWidth', 1.8, 'MarkerSize', 8, 'MarkerFaceColor', 'w');
p2 = plot(h, logr, '-o', 'Color', S.navy, 'LineWidth', 2.2, 'MarkerSize', 8, 'MarkerFaceColor', S.navy);
p1 = plot(h, lgbm, '-o', 'Color', S.maroon, 'LineWidth', 3.2, 'MarkerSize', 10, 'MarkerFaceColor', S.maroon);
p7 = plot(h, rule, '-x', 'Color', [0.35 0.35 0.35], 'LineWidth', 1.6, 'MarkerSize', 9);

set(gca, 'XTick', h, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1);
xlim([0.3 6.35]); ylim([0 0.92]);
xlabel('Prediction horizon  (s)', 'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('AUPRC', 'FontSize', S.fs_lab, 'Color', S.ink);

plot([1 1], [prev(2) lgbm(2)], '-', 'Color', S.maroon, 'LineWidth', 1.2);
text(1.12, 0.845, '11.7\times the prevalence floor', 'Color', S.maroon, ...
     'FontSize', S.fs_ann, 'FontWeight', 'bold');
text(3.1, 0.135, 'prevalence floor', 'Color', [0.35 0.35 0.35], 'FontSize', S.fs_ann);

% Direct line labels beat a seven-entry legend box, but six curves finish
% within 0.10 AUPRC of each other, so the labels are spread to a minimum
% separation and joined back to their curve with a leader.
names = {' LightGBM', ' Logistic', ' MLP', ' TCN', ' GRU', ' Transformer', ' A3 rule'};
ends  = [lgbm(5) logr(5) mlp(5) tcn(5) gru(5) tran(5) rule(5)];
cols  = [S.maroon; S.navy; S.navy; S.grey; S.grey; S.grey; 0.35 0.35 0.35];
bold  = [1 0 0 0 0 0 0];
[sv, si] = sort(ends, 'descend');
lab = sv; gap = 0.047;
for k = 2:numel(lab)
    if lab(k-1) - lab(k) < gap, lab(k) = lab(k-1) - gap; end
end
for k = 1:numel(lab)
    j = si(k);
    plot([5.02 5.16], [ends(j) lab(k)], '-', 'Color', [0.72 0.72 0.72], 'LineWidth', 0.9);
    if bold(j)
        text(5.18, lab(k), names{j}, 'Color', cols(j,:), 'FontSize', 15, 'FontWeight', 'bold', ...
             'VerticalAlignment', 'middle');
    else
        text(5.18, lab(k), names{j}, 'Color', cols(j,:), 'FontSize', 14, ...
             'VerticalAlignment', 'middle');
    end
end
set(gca,'Position',[0.085 0.135 0.775 0.83]);

savefig_png('fig10_model_comparison');
end
