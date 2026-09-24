function fig07_config_timeline()
%FIG07  measId and reportConfigId are message-scoped indices, not identifiers.
S = fig_style();
newfig(1440, 700);

subplot(1,2,1); hold on;
ev = {'A1','A2','A3','A5','A6'};
raw = [1424 1401 1309 195 506];
hb = bar(raw, 0.6); set(hb,'FaceColor',S.navy,'EdgeColor','none');
set(gca,'XTick',1:5,'XTickLabel',ev,'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1,'YGrid','on','XGrid','off');
ylabel('Configurations in one 60-minute capture','FontSize',14,'Color',S.ink);
ylim([0 1750]);
title('What the log actually contains','FontSize',15,'FontWeight','bold','Color',S.ink);
mltext(1.4, 1650, {'1,057 measConfig updates in one capture.', ...
    '29 of 30 reportConfigIds change event type.'}, S.ink, 13.5, 'left', -130);

subplot(1,2,2); hold on;
vals = [99.4 100-99.4; 43.2 56.8];
hb2 = bar([1 2], vals, 0.55, 'stacked');
set(hb2(1),'FaceColor',S.maroon,'EdgeColor','none');
set(hb2(2),'FaceColor',S.lgrey,'EdgeColor','none');
set(gca,'XTick',[1 2],'XTickLabel',{'flat parse','configuration timeline'}, ...
    'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1,'YGrid','on','XGrid','off');
ylabel('Measurement reports resolved to an A3 rule  (%)','FontSize',13.5,'Color',S.ink);
ylim([0 118]); xlim([0.4 2.6]);
text(1, 102, '99.4%','HorizontalAlignment','center','FontSize',16,'FontWeight','bold','Color',S.maroon);
text(2, 46.5, '43.2%','HorizontalAlignment','center','FontSize',16,'FontWeight','bold','Color',S.maroon);
mltext(2.55, 112, {'impossible: 43% of reports', 'carry no neighbour at all'}, S.ink, 13.5, 'right', -7);
title('Attribution before and after the fix','FontSize',15,'FontWeight','bold','Color',S.ink);
savefig_png('fig07_config_timeline');
end
