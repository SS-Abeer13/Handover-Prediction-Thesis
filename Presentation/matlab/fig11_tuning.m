function fig11_tuning()
%FIG11  Equal tuning budget: the deep models gain a lot and still lose.
S = fig_style();
names = {'LightGBM','Logistic','MLP','Transformer','TCN','GRU'};
def   = [0.800 0.741 0.689 0.570 0.531 0.486];
tun   = [0.779 0.770 0.693 0.679 0.633 0.536];

newfig(1180, 760);
hb = bar([def; tun]', 1, 'grouped');
set(hb(1), 'FaceColor', S.lgrey, 'EdgeColor', 'none');
set(hb(2), 'FaceColor', S.navy,  'EdgeColor', 'none');
hold on;

set(gca, 'XTick', 1:6, 'XTickLabel', names, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
try set(gca, 'XTickLabelRotation', 20); end
ylim([0 0.95]); grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'YGrid', 'on', 'XGrid', 'off');
ylabel('AUPRC at the 1 s horizon', 'FontSize', S.fs_lab, 'Color', S.ink);

for i = 1:6
    d = tun(i) - def(i);
    if d >= 0, s = sprintf('+%.3f', d); c = S.green; else, s = sprintf('%.3f', d); c = S.maroon; end
    text(i + 0.16, tun(i) + 0.035, s, 'FontSize', 14, 'Color', c, ...
         'FontWeight', 'bold', 'HorizontalAlignment', 'center');
end

% the line the deep models still fail to cross
plot([0.4 6.6], [def(2) def(2)], '--', 'Color', S.maroon, 'LineWidth', 2);
text(2.9, def(2) + 0.032, 'untuned logistic regression = 0.741', ...
     'Color', S.maroon, 'FontSize', S.fs_ann, 'FontWeight', 'bold');
mltext(6.45, 0.30, {'no tuned sequence model', 'crosses this line'}, ...
     S.maroon, S.fs_ann, 'right', -0.045);

lg = legend(hb, {'coded defaults', 'tuned: 20 Optuna trials, nested grouped CV'}, ...
            'Location', 'northeast', 'FontSize', S.fs_leg);
legend boxoff; set(lg, 'TextColor', S.ink);

savefig_png('fig11_tuning');
end
