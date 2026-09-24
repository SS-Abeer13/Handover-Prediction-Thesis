function fig21_departmental()
%FIG21  The nearest published method on this network, reimplemented and
%       measured on the same rows.
S = fig_style();
names = {'This work (107 features)','Our learner on THEIR 5-D state', ...
         'Their reward ranked directly','Their Q-learning agent','Their HOM/TTT gate alone'};
auroc = [0.921 0.766 0.614 0.505 0.523];
cols  = [S.maroon; S.navy; S.grey; S.grey; S.lgrey];

newfig(1300, 740); hold on;
for i = 1:numel(auroc)
    barh(i, auroc(i), 0.6, 'FaceColor', cols(i,:), 'EdgeColor','none');
    text(auroc(i)+0.008, i, sprintf('%.3f', auroc(i)), 'FontSize',16, ...
        'FontWeight','bold','Color',S.ink,'VerticalAlignment','middle','FontName','Arial');
end
plot([0.5 0.5],[0.4 5.6],'-','Color',[0.4 0.4 0.4],'LineWidth',1.8);
set(gca,'YTick',1:numel(names),'YTickLabel',names,'YDir','reverse', ...
    'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1,'XGrid','on','YGrid','off');
xlim([0.45 1.0]); ylim([0.4 5.7]);
xlabel('AUROC at 1 s, same rows, same labels','FontSize',S.fs_lab,'Color',S.ink);
text(0.455, 5.55,'chance','FontSize',13,'Color',[0.4 0.4 0.4]);
mltext(0.995, 3.45, {'Ranking by their own reward function,', ...
   'with no reinforcement learning at all,', 'beats the agent trained on it.'}, S.maroon, 14, 'right', 0.32);
savefig_png('fig21_departmental');
end
