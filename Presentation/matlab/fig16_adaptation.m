function fig16_adaptation()
%FIG16  Two zero-cost domain adaptations, both worse than doing nothing.
S = fig_style();
reg = [0.865 0.771 0.699];   % none, CORAL, per-drive z
ext = [0.642 0.534 0.567];
newfig(1200, 740); hold on;
hb = bar([reg; ext]', 1, 'grouped');
set(hb(1),'FaceColor',S.navy,'EdgeColor','none');
set(hb(2),'FaceColor',S.lgrey,'EdgeColor','none');
set(gca,'XTick',1:3,'XTickLabel',{'no adaptation','CORAL','per-drive z-scoring'}, ...
    'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1,'YGrid','on','XGrid','off');
ylabel('Transfer AUROC at 1 s','FontSize',S.fs_lab,'Color',S.ink);
ylim([0.4 1.06]);
lg = legend(hb,{'across configuration regimes','out to the public dataset'}, ...
    'Location','north','FontSize',S.fs_leg); legend boxoff; set(lg,'TextColor',S.ink);
for i=1:3
  text(i-0.16, reg(i)+0.021, sprintf('%.3f',reg(i)),'HorizontalAlignment','center','FontSize',14,'Color',S.ink);
  text(i+0.16, ext(i)+0.021, sprintf('%.3f',ext(i)),'HorizontalAlignment','center','FontSize',14,'Color',S.ink);
end
plot([0.55 3.45],[reg(1) reg(1)],'--','Color',S.maroon,'LineWidth',2);
plot([0.55 3.45],[ext(1) ext(1)],'--','Color',S.maroon,'LineWidth',1.4);
mltext(0.62, 0.985, {'Both alignments also lower MATCHED-domain accuracy', ...
  '(0.819 \rightarrow 0.796 / 0.800): this is not a robustness trade.', ...
  'They delete the absolute RF level, where the signal is.'}, S.maroon, 13.5, 'left', -0.030);
savefig_png('fig16_adaptation');
end
