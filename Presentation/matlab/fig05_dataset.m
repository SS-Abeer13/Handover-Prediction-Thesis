function fig05_dataset()
%FIG05  Composition of the pooled dataset, all four campaigns.
%   Rebuilt 16 Sept 2026: the previous version was a three-capture render
%   (43 drives / 7,740 samples / 761 handovers) and contradicted Table 3.2.
%   Laid out for print: no subplot titles and no second label row, because both
%   collide once the canvas is shrunk for a 12 pt document. The caption carries
%   what the titles used to say.
S = fig_style();
lab  = {'1st Campaign', '2nd Campaign', '3rd Campaign', '4th Campaign'};
ho   = [290 174 297 177];
dr   = [15 8 20 14];
mins = [46 24 60 43];
rate = ho ./ mins;

newfig(1500, 640);

subplot(1,2,1); hold on;
bar(1:4, ho, 0.58, 'FaceColor', S.navy, 'EdgeColor', 'none');
bar(4, ho(4), 0.58, 'FaceColor', S.maroon, 'EdgeColor', 'none');
for k = 1:4
    text(k, ho(k) + 14, sprintf('%d', ho(k)), 'HorizontalAlignment', 'center', ...
         'FontSize', 16, 'FontWeight', 'bold', 'Color', S.ink);
end
set(gca, 'XTick', 1:4, 'XTickLabel', lab, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'YGrid', 'on', 'XGrid', 'off');
xlim([0.4 4.6]); ylim([0 360]);
ylabel('Signalling-confirmed handovers', 'FontSize', S.fs_lab, 'Color', S.ink);

subplot(1,2,2); hold on;
bar(1:4, rate, 0.58, 'FaceColor', S.navy, 'EdgeColor', 'none');
bar(4, rate(4), 0.58, 'FaceColor', S.maroon, 'EdgeColor', 'none');
for k = 1:4
    text(k, rate(k) + 0.30, sprintf('%.1f', rate(k)), 'HorizontalAlignment', 'center', ...
         'FontSize', 16, 'FontWeight', 'bold', 'Color', S.ink);
    text(k, 0.32, sprintf('%d dr', dr(k)), 'HorizontalAlignment', 'center', ...
         'FontSize', 13, 'Color', [1 1 1]);
end
set(gca, 'XTick', 1:4, 'XTickLabel', lab, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'YGrid', 'on', 'XGrid', 'off');
xlim([0.4 4.6]); ylim([0 8.6]);
ylabel('Handovers per minute', 'FontSize', S.fs_lab, 'Color', S.ink);
savefig_png('fig05_dataset');
end
