function fig17_mechanism()
%FIG17  The quantity the rule thresholds on is the weakest predictor there is.
S = fig_style();
feat = {'Serving dwell time','Serving SINR','Time since last A3 report', ...
        'A3 reports, previous 3 s','Time since previous handover', ...
        'A3 hold time (TTT clock)','Serving-to-neighbour gap'};
auc  = [0.874 0.830 0.703 0.685 0.652 0.615 0.566];
src  = [1 1 2 2 1 2 3];   % 1 history/RF, 2 signalling, 3 the rule's own quantity

newfig(1280, 760); hold on;
for i = 1:numel(auc)
    switch src(i)
        case 1, c = S.navy;
        case 2, c = S.grey;
        case 3, c = S.maroon;
    end
    barh(i, auc(i), 0.62, 'FaceColor', c, 'EdgeColor', 'none');
    text(auc(i) + 0.008, i, sprintf('%.3f', auc(i)), 'FontSize', 15, ...
         'Color', S.ink, 'VerticalAlignment','middle','FontName','Arial');
end
plot([0.5 0.5], [0.4 7.6], '-', 'Color', [0.45 0.45 0.45], 'LineWidth', 1.6);
set(gca,'YTick',1:numel(feat),'YTickLabel',feat,'YDir','reverse', ...
    'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1,'XGrid','on','YGrid','off');
xlim([0.5 0.95]); ylim([0.4 7.6]);
xlabel('Single-feature AUROC at the 1 s horizon','FontSize',S.fs_lab,'Color',S.ink);
text(0.505, 7.5, 'chance', 'FontSize', 13, 'Color', [0.45 0.45 0.45]);
mltext(0.735, 4.55, {'How long the phone has already been on the', ...
    'cell beats the quantity the deployed rule', 'thresholds on by 0.31 AUROC.'}, S.maroon, 14, 'left', 0.42);
savefig_png('fig17_mechanism');
end
