function fig26_literature_headtohead()
%FIG26  The only two comparisons with the literature that are actually fair.
%   Left : the nearest published method on this network, reimplemented and run
%          on the SAME rows under the SAME protocol (stage 20, four captures).
%   Right: why the headline accuracies quoted across the audited set cannot be
%          compared - on this task, saying "no" forever scores 93.3%.
S = fig_style();

newfig(1460, 700);

% ------------------------------------------------ left: same rows, same rules
subplot(1, 2, 1); hold on;
names = {'their agent', 'their reward, ranked', 'our learner, their 5 inputs', 'this work'};
v = [0.489 0.624 0.766 0.921];
cols = [S.grey; S.grey; S.navy; S.maroon];
for i = 1:4
    vv = nan(1, 4); vv(i) = v(i);
    hb = barh(1:4, vv, 0.6);
    set(hb, 'EdgeColor', 'none', 'FaceColor', cols(i, :));
end
plot([0.5 0.5], [0.42 1.55], '-', 'Color', [0.15 0.15 0.15], 'LineWidth', 2.2);
text(0.508, 1.52, 'chance', 'FontSize', 13, 'Color', [0.15 0.15 0.15]);
for i = 1:4
    text(v(i) + 0.012, i, sprintf('%.3f', v(i)), 'FontSize', 15, 'FontWeight', 'bold', ...
         'Color', S.ink, 'VerticalAlignment', 'middle');
end
set(gca, 'YTick', 1:4, 'YTickLabel', names, 'YDir', 'reverse', ...
    'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XGrid', 'on', 'YGrid', 'off');
xlim([0.42 1.03]); ylim([0.45 4.6]);
xlabel('AUROC at 1 s, same 654 rows, same grouped protocol', ...
       'FontSize', 15, 'Color', S.ink);
title('Reimplemented, not quoted', 'FontSize', S.fs_lab, 'FontWeight', 'bold', 'Color', S.ink);

% ------------------------------------- right: the floor under a headline number
subplot(1, 2, 2); hold on;
n2 = {'accuracy of a model that', 'AUPRC of that same model', 'AUPRC, this work'};
v2 = [93.3 6.7 78.4];
c2 = [S.grey; S.amber; S.maroon];
for i = 1:3
    vv = nan(1, 3); vv(i) = v2(i);
    hb = bar(1:3, vv, 0.55);
    set(hb, 'EdgeColor', 'none', 'FaceColor', c2(i, :));
end
for i = 1:3
    text(i, v2(i) + 2.4, sprintf('%.1f%%', v2(i)), 'HorizontalAlignment', 'center', ...
         'FontSize', 17, 'FontWeight', 'bold', 'Color', S.ink);
end
set(gca, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
set(gca, 'XTick', []);          % the renderer ignores XTickLabel after bar()
xlim([0.45 3.55]);
lab = {'a model that', 'the same model,', 'this work,'};
lab2 = {'always says no', 'AUPRC not accuracy', 'AUPRC'};
for i = 1:3
    text(i, -5.0, lab{i}, 'HorizontalAlignment', 'center', 'FontSize', 14, 'Color', S.ink);
    text(i, -11.5, lab2{i}, 'HorizontalAlignment', 'center', 'FontSize', 14, 'Color', S.ink);
end
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'YGrid', 'on', 'XGrid', 'off');
ylim([-15 112]);
ylabel('score on the 1 s task  (%)', 'FontSize', S.fs_lab, 'Color', S.ink);
title('Same model, two metrics', 'FontSize', S.fs_lab, 'FontWeight', 'bold', 'Color', S.ink);
mltext(2.05, 108, {'7 of the 22 audited papers report a headline accuracy', ...
    'on an imbalanced task. Two report a ranking metric that', ...
    'survives the imbalance.'}, S.maroon, 14, 'center', -6.5);

savefig_png('fig26_literature_headtohead');
end
