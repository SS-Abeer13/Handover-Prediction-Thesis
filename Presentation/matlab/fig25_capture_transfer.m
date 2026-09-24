function fig25_capture_transfer()
%FIG25  Leave-one-capture-out: hold out a whole day, corridor and speed regime.
%   Stage 21 on the four measured captures. Replaces the curated-vs-measured
%   transfer matrix, which described a dataset this thesis no longer uses.
S = fig_style();

names = {'1st Campaign', '2nd Campaign', '3rd Campaign', '4th Campaign'};
sub   = {'urban arterial', 'urban loop', 'dense urban', 'HIGHWAY'};
auroc = [0.949 0.909 0.943 0.927];
lift  = [9.9   9.4   13.2  14.9];
cols  = [S.navy; S.navy; S.navy; S.maroon];

newfig(1300, 720); hold on;

for i = 1:4
    v = nan(1, 4); v(i) = auroc(i);
    hb = bar(1:4, v, 0.58);
    set(hb, 'EdgeColor', 'none', 'FaceColor', cols(i, :));
end

% the within-dataset reference: every drive tested once, all four captures
plot([0.35 4.65], [0.933 0.933], '--', 'Color', [0.35 0.35 0.35], 'LineWidth', 2);
text(0.42, 0.9385, 'pooled, drives rotated within the dataset:  0.933', ...
     'FontSize', 14, 'Color', [0.3 0.3 0.3]);

for i = 1:4
    text(i, auroc(i) + 0.006, sprintf('%.3f', auroc(i)), 'HorizontalAlignment', 'center', ...
         'FontSize', 17, 'FontWeight', 'bold', 'Color', S.ink);
    text(i, 0.700, sprintf('%.1f\\times lift', lift(i)), 'HorizontalAlignment', 'center', ...
         'FontSize', 15, 'FontWeight', 'bold', 'Color', [1 1 1]);
    text(i, 0.676, sub{i}, 'HorizontalAlignment', 'center', ...
         'FontSize', 13, 'Color', [1 1 1]);
end

set(gca, 'XTick', 1:4, 'XTickLabel', names, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'YGrid', 'on', 'XGrid', 'off');
xlim([0.35 4.65]); ylim([0.65 1.022]);
ylabel('AUROC at the 1 s horizon, capture held out whole', ...
       'FontSize', S.fs_lab, 'Color', S.ink);
xlabel('capture withheld from training', 'FontSize', S.fs_lab, 'Color', S.ink);

mltext(2.50, 1.007, {['The highway capture was driven after every modelling decision was frozen. ' ...
    'Held out whole it scores 0.927,'], ...
    'with the highest lift and the lowest calibration error of the four.'}, ...
    S.maroon, S.fs_ann, 'center', -0.0215);

savefig_png('fig25_capture_transfer');
end
