function fig09_protocol_folds()
%FIG09  Grouped rotation: every drive is tested exactly once, and a random-row
%       split would put a window's own neighbours in the training set.
S = fig_style();
newfig(1420, 700); hold on;
axis([0 52 -1.2 7.9]); axis off;

for f = 0:4
    y = 6 - f*1.15;
    for d = 1:43
        if mod(d-1, 5) == f, c = S.maroon; else, c = [0.86 0.86 0.86]; end
        rectangle('Position', [d*0.86, y, 0.72, 0.8], 'FaceColor', c, 'EdgeColor','none');
    end
    text(0.55, y+0.4, sprintf('fold %d', f), 'HorizontalAlignment','right', ...
         'FontSize',14,'Color',S.ink,'FontName','Arial');
end
text(19.5, -0.62, '43 drives', 'HorizontalAlignment','center','FontSize',15,'Color',S.ink,'FontName','Arial');
rectangle('Position',[0.86, -0.15, 37.5, 0.06],'FaceColor',[0.5 0.5 0.5],'EdgeColor','none');

rectangle('Position',[1.0, 7.0, 0.72, 0.5],'FaceColor',S.maroon,'EdgeColor','none');
text(2.1, 7.25, 'test','FontSize',14,'Color',S.ink,'FontName','Arial');
rectangle('Position',[6.0, 7.0, 0.72, 0.5],'FaceColor',[0.86 0.86 0.86],'EdgeColor','none');
text(7.1, 7.25, 'train / val / calib','FontSize',14,'Color',S.ink,'FontName','Arial');

mltext(38.6, 6.6, {'Out-of-fold predictions', 'are pooled and scored', 'once over all 43 drives.'}, S.ink, 14, 'left', -0.62);
mltext(38.6, 3.4, {'Nothing from a test fold', 'is ever fitted: scalers,', 'thresholds, temperature', 'and calibrators are all', 'fitted inside the fold.'}, S.maroon, 14, 'left', -0.62);
savefig_png('fig09_protocol_folds');
end
