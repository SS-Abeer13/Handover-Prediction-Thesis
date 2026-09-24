function fig40_signalling_ablation()
%FIG40  What the signalling block is and is not worth.
%   A dot plot with every seed drawn: three feature sets, the same folds. It
%   answers two questions a reviewer asks in sequence - does signalling help,
%   and is signalling on its own enough?
S = fig_style();
sets = {'Radio + mobility + history', 'The same, plus signalling', 'Signalling only'};
A    = { [0.8114 0.8113 0.8090], [0.8109 0.8134 0.8074], [0.3612 0.3752 0.3723] };
col  = {S.navy, S.maroon, S.grey};

newfig(1200, 640); hold on;
prev = 0.0732;
plot([prev prev], [0.4 3.6], '-', 'Color', S.lgrey, 'LineWidth', 2.4);
text(prev + 0.012, 3.45, 'prevalence floor', 'FontSize', 13, 'Color', [0.45 0.45 0.45]);
for k = 1:3
    y = 4 - k;
    v = A{k};
    plot([min(v) max(v)], [y y], '-', 'Color', [0.72 0.72 0.72], 'LineWidth', 6);
    plot(v, y*ones(size(v)), 'o', 'MarkerSize', 10, 'MarkerFaceColor', col{k}, 'MarkerEdgeColor', 'w');
    text(mean(v), y + 0.28, sprintf('%.3f', mean(v)), 'FontSize', 14, 'Color', col{k}, ...
         'HorizontalAlignment', 'center');
end
set(gca, 'YTick', 1:3, 'YTickLabel', fliplr(sets), 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XGrid', 'on', 'YGrid', 'off');
xlim([0.02 0.92]); ylim([0.4 3.6]);
xlabel('AUPRC at the 1 s horizon, one marker per seed', 'FontSize', S.fs_lab, 'Color', S.ink);
mltext(0.10, 2.55, {'Adding the signalling block to the radio features changes nothing', ...
    '(0.811 against 0.811). Signalling alone still reaches 0.37, five times', ...
    'the floor - so it carries real information that the radio features', ...
    'already contain.'}, S.ink, 14, 'left', -0.20);
savefig_png('fig40_signalling_ablation');
end
