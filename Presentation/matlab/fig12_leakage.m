function fig12_leakage()
%FIG12  Random-row splitting inflates AUPRC, and it inflates by architecture.
S = fig_style();
names = {'GRU','Transformer','TCN','MLP','LightGBM','Logistic'};
infl  = [71 62 82 84 73;      % GRU        0.5, 1, 2, 3, 5 s
         44 27 44 53 52;      % Transformer
         35 20 27 25 26;      % TCN
         26  5  3  6 10;      % MLP
         41 -1  3 20 37;      % LightGBM
         21 -3 -3  0  4];     % Logistic
mn = mean(infl, 2);

newfig(1180, 760); hold on;
hb = barh(mn, 0.62);
set(hb, 'EdgeColor', 'none', 'FaceColor', 'flat');
cols = [S.maroon; S.maroon; S.maroon; S.navy; S.navy; S.navy];
try
    set(hb, 'CData', cols);
catch
    set(hb, 'FaceColor', S.navy);
end
for i = 1:6
    plot([min(infl(i,:)) max(infl(i,:))], [i i], '-', 'Color', [0.3 0.3 0.3], 'LineWidth', 1.4);
    plot(infl(i,:), i*ones(1,5), '.', 'Color', [0.3 0.3 0.3], 'MarkerSize', 11);
    text(max(infl(i,:)) + 3, i, sprintf('%.0f%%', mn(i)), 'FontSize', 14, ...
         'Color', S.ink, 'VerticalAlignment', 'middle');
end

set(gca, 'YTick', 1:6, 'YTickLabel', names, 'YDir', 'reverse', ...
    'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XGrid', 'on', 'YGrid', 'off');
xlim([-8 105]);
xlabel('AUPRC inflation from random-row splitting  (%, mean over 5 horizons)', ...
       'FontSize', S.fs_lab, 'Color', S.ink);

mltext(58, 4.5, {'Sequence models leak most: a 10 s window', ...
     'straddling a random split shares rows', 'with its own training set.'}, ...
     S.maroon, S.fs_ann, 'left', 0.34);
mltext(58, 6.4, {'dots: the five individual horizons'}, [0.35 0.35 0.35], 13, 'left', 0.34);

savefig_png('fig12_leakage');
end
