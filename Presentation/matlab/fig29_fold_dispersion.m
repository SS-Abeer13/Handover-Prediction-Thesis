function fig29_fold_dispersion()
%FIG29  What the mean hides: the per-fold spread of AUPRC at the 1 s horizon.
%   Reviewers in every empirical field now expect the distribution behind a
%   reported mean. Eight grouped-drive folds are few enough that every one can
%   be drawn, so this is a box plot with the folds themselves overlaid rather
%   than a bar chart with an error bar.
S = fig_style();

lbl = {'Hazard', 'Multi-head', 'Multi-head', 'Hazard', 'Multi-head'};
sub = {'LightGBM', 'LightGBM', '+ isotonic', 'MLP', 'MLP'};
A = { [0.8554 0.7554 0.7209 0.7595 0.7815 0.7979 0.7421 0.8258], ...
      [0.8608 0.7889 0.7957 0.7715 0.8149 0.8349 0.7711 0.8258], ...
      [0.8227 0.6914 0.7457 0.7344 0.7766 0.7856 0.7374 0.7956], ...
      [0.7136 0.6268 0.5513 0.5273 0.5783 0.6570 0.5370 0.6642], ...
      [0.8036 0.7157 0.7342 0.6363 0.7098 0.7446 0.6771 0.7413] };
col = {S.maroon, S.navy, S.grey, S.maroon, S.navy};
fc  = {[0.95 0.88 0.88], [0.88 0.92 0.96], [0.93 0.93 0.93], [0.95 0.88 0.88], [0.88 0.92 0.96]};

newfig(1240, 760); hold on;
for k = 1:numel(A)
    drawbox(k, A{k}, 0.28, fc{k}, col{k}, S);
end

set(gca, 'XTick', 1:5, 'XTickLabel', lbl, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
for k = 1:5
    text(k, 0.455, sub{k}, 'FontSize', 13, 'Color', [0.42 0.42 0.42], ...
         'HorizontalAlignment', 'center');
end
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XGrid', 'off', 'YGrid', 'on');
xlim([0.3 5.7]); ylim([0.44 0.92]);
ylabel('AUPRC at the 1 s horizon, per fold', 'FontSize', S.fs_lab, 'Color', S.ink);
mltext(0.42, 0.660, {'Eight grouped-drive folds per arm, every fold drawn.', ...
    'The spread inside an arm exceeds the gap between the two', ...
    'LightGBM arms, which is why the paired fold-by-fold test,', ...
    'and not the ordering of the means, decides between them.'}, S.ink, 14, 'left', -0.026);
savefig_png('fig29_fold_dispersion');
end
