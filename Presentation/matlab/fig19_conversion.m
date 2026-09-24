function fig19_conversion()
%FIG19  Most A3 reports are never acted on, and the rate rises with cell size.
%   Rebuilt 16 Sept 2026. The previous version reported 60.9 % of 6,354 reports,
%   a three-capture figure that contradicted Table 5.9, and carried a second
%   panel of report-conversion predictor scores that are known to be stale on
%   four captures. Both are removed. Values here are the four-capture figures.
S = fig_style();
lab = {'1st Campaign','2nd Campaign','3rd Campaign','4th Campaign'};
sub = {'urban arterial','urban loop','dense urban','highway'};
dec = [57.2 60.1 63.3 71.9];
pool = 62.9;

newfig(1320, 720); hold on;
hb = bar(1:4, dec, 0.55, 'FaceColor', S.navy, 'EdgeColor', 'none');
bar(4, dec(4), 0.55, 'FaceColor', S.maroon, 'EdgeColor', 'none');
for k = 1:4
    text(k, dec(k) + 2.2, sprintf('%.1f%%', dec(k)), 'HorizontalAlignment', 'center', ...
         'FontSize', 17, 'FontWeight', 'bold', 'Color', S.ink);
    text(k, -4.2, sub{k}, 'HorizontalAlignment', 'center', 'FontSize', 12.5, ...
         'Color', [0.42 0.42 0.42]);
end
plot([0.4 4.6], [pool pool], '--', 'Color', [0.35 0.35 0.35], 'LineWidth', 2.2);
text(0.5, 78.5, sprintf('dashed line: pooled %.1f%% of 7,385 A3 reports', pool), ...
     'HorizontalAlignment', 'left', 'FontSize', 14, 'Color', [0.35 0.35 0.35]);
set(gca, 'XTick', 1:4, 'XTickLabel', lab, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'YGrid', 'on', 'XGrid', 'off');
xlim([0.4 4.6]); ylim([-7 82]);
ylabel('A3 reports not followed by a handover within 2 s  (%)', ...
       'FontSize', S.fs_lab, 'Color', S.ink);
savefig_png('fig19_conversion');
end
