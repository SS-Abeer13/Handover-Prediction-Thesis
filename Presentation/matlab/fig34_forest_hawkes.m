function fig34_forest_hawkes()
%FIG34  Self-excitation, per campaign, with its uncertainty.
%   A forest plot is the standard way to show one effect estimated on several
%   samples together with the pooled value. Here it also carries the finding
%   that the highway is the least clustered corridor.
S = fig_style();
lab = {'1st Campaign (urban arterial)','2nd Campaign (urban loop)','3rd Campaign (dense urban)', ...
       '4th Campaign (highway)','Pooled'};
br  = [0.6492 0.6091 0.5671 0.5125 0.6054];
lo  = [0.4538 0.4433 0.3628 0.3354 0.5237];
hi  = [0.7762 0.7402 0.6877 0.6290 0.6729];
nev = [288 172 294 176 930];

newfig(1200, 720); hold on;
plot([br(5) br(5)], [0.35 5.7], ':', 'Color', [0.65 0.65 0.65], 'LineWidth', 1.6);
for k = 1:4
    y = 6 - k;
    plot([lo(k) hi(k)], [y y], '-', 'Color', [0.6 0.6 0.6], 'LineWidth', 2.0);
    plot(br(k), y, 's', 'MarkerSize', 12, 'MarkerFaceColor', S.navy, 'MarkerEdgeColor', 'w');
    text(1.00, y, sprintf('%.3f  [%.3f, %.3f]   n = %d', br(k), lo(k), hi(k), nev(k)), ...
         'FontSize', 13, 'Color', S.ink, 'HorizontalAlignment', 'right');
end
y = 1;   % pooled, drawn as a diamond in the usual convention
dx = [lo(5) br(5) hi(5) br(5)]; dy = [y y+0.22 y y-0.22];
patch(dx, dy, S.maroon, 'EdgeColor', 'none');
text(1.00, y, sprintf('%.3f  [%.3f, %.3f]   n = %d', br(5), lo(5), hi(5), nev(5)), ...
     'FontSize', 13, 'Color', S.maroon, 'HorizontalAlignment', 'right', 'FontWeight', 'bold');
set(gca, 'YTick', 1:5, 'YTickLabel', fliplr(lab), 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XGrid', 'on', 'YGrid', 'off');
xlim([0.28 1.02]); ylim([0.35 6.75]);
xlabel('Hawkes branching ratio  (expected further handovers triggered by one handover)', ...
       'FontSize', 14, 'Color', S.ink);
mltext(0.30, 6.55, {'Every campaign clusters. The highway clusters least,', ...
    'consistent with fewer cell boundaries per minute rather', ...
    'than with a different mechanism.'}, S.ink, 14, 'left', -0.26);
savefig_png('fig34_forest_hawkes');
end
