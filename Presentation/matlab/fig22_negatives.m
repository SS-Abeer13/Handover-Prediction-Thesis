function fig22_negatives()
%FIG22  Five channels added in good faith; one thing that actually mattered.
S = fig_style();
left = {'Neighbour coverage 28% \rightarrow 79%', 'Explicit self-excitation features', ...
        'The full RRC signalling block', 'A dedicated ping-pong target', ...
        'Zero-cost domain adaptation', 'An equal tuning budget for every model'};
right = {'no accuracy change', 'no accuracy change', '+0.005 to +0.012 AUPRC', ...
         'at chance on 4 captures (AUROC 0.51)', 'worse, on both sides of the transfer', ...
         'ordering unchanged'};
wl = {'Reformulating as a discrete-time hazard', 'The A3 configuration regime', ...
      'Grouping the split by whole drive'};
wr = {'coherence + calibration from one fit', '\Delta AUROC 0.088 (controlled pair)', ...
      'removes a +20% to +74% inflation'};

newfig(1400, 740); hold on;
axis([0 100 0 100]); axis off;

text(4, 95, 'Added in good faith, measured, and reported as nothing', ...
     'FontSize', 17, 'FontWeight', 'bold', 'Color', S.ink, 'FontName', 'Arial');
y = 85;
for i = 1:numel(left)
    plot(6, y+0.8, 'x', 'Color', S.grey, 'MarkerSize', 13, 'LineWidth', 3);
    text(10, y, left{i}, 'FontSize', 15, 'Color', S.ink, 'FontName', 'Arial', ...
         'VerticalAlignment', 'middle');
    text(62, y, right{i}, 'FontSize', 15, 'Color', S.grey, 'FontName', 'Arial', ...
         'VerticalAlignment', 'middle');
    y = y - 8.6;
end

plot([4 96], [33 33], '-', 'Color', [0.8 0.8 0.8], 'LineWidth', 1.5);

text(4, 27.0, 'What actually moved the result', ...
     'FontSize', 17, 'FontWeight', 'bold', 'Color', S.maroon, 'FontName', 'Arial');
y = 19.0;
for i = 1:numel(wl)
    plot(6, y+0.8, 'o', 'Color', S.maroon, 'MarkerSize', 11, 'LineWidth', 3);
    text(10, y, wl{i}, 'FontSize', 15, 'Color', S.maroon, 'FontName', 'Arial', ...
         'FontWeight', 'bold', 'VerticalAlignment', 'middle');
    text(62, y, wr{i}, 'FontSize', 15, 'Color', S.maroon, 'FontName', 'Arial', ...
         'FontWeight', 'bold', 'VerticalAlignment', 'middle');
    y = y - 8.6;
end
savefig_png('fig22_negatives');
end
