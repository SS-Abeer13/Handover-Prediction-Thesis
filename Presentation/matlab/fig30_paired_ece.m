function fig30_paired_ece()
%FIG30  The paired comparison behind the calibration claim.
%   A difference of means says nothing when the folds are paired. This is the
%   slope chart used for paired designs: one line per fold, so both the
%   direction and the consistency of the effect are visible at once.
S = fig_style();
haz = [0.0140 0.0264 0.0132 0.0199 0.0183 0.0180 0.0189 0.0130];
mhd = [0.0204 0.0326 0.0203 0.0233 0.0235 0.0228 0.0245 0.0183];

newfig(1080, 780); hold on;
for k = 1:numel(haz)
    plot([1 2], [mhd(k) haz(k)], '-', 'Color', [0.72 0.72 0.72], 'LineWidth', 1.3);
end
plot(ones(1,8)*2, haz, 'o', 'MarkerSize', 8, 'MarkerFaceColor', S.maroon, 'MarkerEdgeColor', 'w');
plot(ones(1,8)*1, mhd, 'o', 'MarkerSize', 8, 'MarkerFaceColor', S.navy,   'MarkerEdgeColor', 'w');
plot([0.86 1.14], [mean(mhd) mean(mhd)], '-', 'Color', S.navy,   'LineWidth', 3);
plot([1.86 2.14], [mean(haz) mean(haz)], '-', 'Color', S.maroon, 'LineWidth', 3);
text(0.84, mean(mhd), sprintf('mean %.4f', mean(mhd)), 'FontSize', 14, ...
     'Color', S.navy, 'HorizontalAlignment', 'right');
text(2.16, mean(haz), sprintf('mean %.4f', mean(haz)), 'FontSize', 14, 'Color', S.maroon);

set(gca, 'XTick', [1 2], 'XTickLabel', {'Five independent heads', 'One hazard model'}, ...
    'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XGrid', 'off', 'YGrid', 'on');
xlim([0.55 2.45]); ylim([0.010 0.036]);
ylabel('Expected calibration error at 1 s, per fold', 'FontSize', S.fs_lab, 'Color', S.ink);
mltext(1.5, 0.0348, {'Every one of the eight folds improves.', ...
    'Wilcoxon signed-rank p = 0.0078; lower is better.'}, S.ink, 14, 'center', -0.0022);
savefig_png('fig30_paired_ece');
end
