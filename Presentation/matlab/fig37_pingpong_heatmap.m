function fig37_pingpong_heatmap()
%FIG37  One measurement sequence, nine published numbers.
%   A heatmap over the definitional grid is the honest way to report a quantity
%   whose value is set by unstated conventions: the reader sees the whole
%   surface instead of the one cell an author chose.
S = fig_style();
% rows: return window (5s, 10s, 15s); columns: cell identity & return rule
R = [21.0 24.8 31.2;      % 5 s
     24.9 29.6 39.5;      % 10 s
     26.3 31.2 43.8];     % 15 s
rows = {'5 s', '10 s', '15 s'};
cols = {'Previous cell (PCI + carrier)', ...
        'Previous cell (PCI only)', ...
        'Any recent cell (PCI + carrier)'};

newfig(1160, 720);
imagesc(R); hold on;
cmap = zeros(64,3);
for k = 1:64
    f = (k-1)/63;
    cmap(k,:) = [1 1 1]*(1-f) + [0.537 0.075 0.075]*f;
end
colormap(cmap); caxis([18 45]);

for r = 1:3
    for c = 1:3
        if R(r,c) > 33, tc = [1 1 1]; else, tc = S.ink; end
        text(c, r, sprintf('%.1f %%', R(r,c)), 'FontSize', 18, 'Color', tc, ...
             'HorizontalAlignment', 'center', 'FontWeight', 'bold');
    end
end

% Outline 3GPP baseline (5 s, Previous cell PCI+carrier)
plot([0.5 0.5 1.5 1.5 0.5], [0.5 1.5 1.5 0.5 0.5], '-', 'Color', [0.1 0.1 0.1], 'LineWidth', 3);
text(1, 1.32, '(3GPP baseline)', 'FontSize', 11, 'Color', S.ink, ...
     'HorizontalAlignment', 'center', 'FontWeight', 'normal');

axis([0.5 3.5 0.5 3.5]);
set(gca, 'XTickMode', 'manual', 'YTickMode', 'manual', 'TickLength', [0 0], ...
    'XColor', S.ink, 'YColor', S.ink);
set(gca, 'XTick', 1:3); set(gca, 'XTickLabel', cols);
xtickangle(15);
set(gca, 'FontSize', 13);
set(gca, 'YTick', 1:3); set(gca, 'YTickLabel', rows);
ylabel('Return window', 'FontSize', S.fs_lab, 'Color', S.ink);
cb = colorbar; set(cb, 'FontSize', 13);
ylabel(cb, 'Ping-pong rate (%)', 'FontSize', 14);
title('Same 957 handover commands: the outlined cell is the 3GPP definition', ...
      'FontSize', 14, 'Color', S.ink, 'FontWeight', 'normal');
savefig_png('fig37_pingpong_heatmap');
end
