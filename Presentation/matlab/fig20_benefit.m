function fig20_benefit()
%FIG20  Against a same-rate random alarm, the generic ranker earns its budget
%       only up to about 20% of samples - and the dedicated model never does.
S = fig_style();
budget = [5 10 20 40];
gen = [0.335 0.248 0.044 -0.027];
ded = [-0.227 -0.343 -0.387 -0.217];

newfig(1220, 740); hold on;
plot([3 45],[0 0],'-','Color',[0.4 0.4 0.4],'LineWidth',1.6);
p1 = plot(budget, gen, '-o','Color',S.maroon,'LineWidth',3.0,'MarkerSize',11,'MarkerFaceColor',S.maroon);
p2 = plot(budget, ded, '-s','Color',S.navy,'LineWidth',2.2,'MarkerSize',9,'MarkerFaceColor','w');
set(gca,'XTick',budget,'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1);
xlim([3 45]); ylim([-0.45 0.40]);
xlabel('Alarm budget  (% of samples alarmed)','FontSize',S.fs_lab,'Color',S.ink);
ylabel('Excess ping-pong coverage over a same-rate random alarm','FontSize',14,'Color',S.ink);
lg = legend([p1 p2],{'generic handover model','dedicated ping-pong model'}, ...
    'Location','northeast','FontSize',S.fs_leg); legend boxoff; set(lg,'TextColor',S.ink);
plot(20, 0.044,'o','MarkerSize',20,'Color',S.amber,'LineWidth',2.5);
mltext(21.5, 0.20, {'positive up to a 20% budget', '(+0.044); negative above it'}, S.ink, 14, 'left', -0.028);
text(6, -0.155, 'a coverage figure without a chance reference', 'FontSize',13.5,'Color',S.maroon);
text(6, -0.185, 'overstates the benefit by two thirds at a 10% budget', 'FontSize',13.5,'Color',S.maroon);
mltext(44, -0.075, {'the dedicated model is far', 'worse - it is at chance', 'on four captures'}, S.navy, 13, 'right', -0.028);
savefig_png('fig20_benefit');
end
