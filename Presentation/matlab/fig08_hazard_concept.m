function fig08_hazard_concept()
%FIG08  One fit gives a hazard per bin; survival and incidence follow by identity.
S = fig_style();
lam = [0.042 0.033 0.070 0.065 0.110];
h   = [0.5 1 2 3 5];
Sv = cumprod(1 - lam); F = 1 - Sv;

newfig(1420, 700);

subplot(1,2,1); hold on;
hb = bar(lam, 0.6); set(hb,'FaceColor',S.navy,'EdgeColor','none');
set(gca,'XTick',1:5,'XTickLabel',{'(0,0.5]','(0.5,1]','(1,2]','(2,3]','(3,5]'}, ...
    'XColor',S.ink,'YColor',S.ink,'Layer','top');
try set(gca,'XTickLabelRotation',18); end
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1,'YGrid','on','XGrid','off');
ylabel('Discrete hazard  \lambda_k(x)','FontSize',S.fs_lab,'Color',S.ink);
xlabel('Time bin  (s)','FontSize',S.fs_lab,'Color',S.ink);
ylim([0 0.145]);
title('One model, one output per bin','FontSize',15,'FontWeight','bold','Color',S.ink);

subplot(1,2,2); hold on;
p1 = plot(h, F,  '-o','Color',S.maroon,'LineWidth',3.0,'MarkerSize',10,'MarkerFaceColor',S.maroon);
p2 = plot(h, Sv, '-s','Color',S.navy,  'LineWidth',2.2,'MarkerSize',8, 'MarkerFaceColor','w');
set(gca,'XTick',h,'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1);
xlim([0.3 5.4]); ylim([0 1]);
xlabel('Horizon  (s)','FontSize',S.fs_lab,'Color',S.ink);
ylabel('Probability','FontSize',S.fs_lab,'Color',S.ink);
lg = legend([p1 p2],{'incidence  F_k = 1 - S_k','survival  S_k = \Pi (1-\lambda_j)'}, ...
     'Location','east','FontSize',13); legend boxoff; set(lg,'TextColor',S.ink);
title('Coherent across horizons by construction','FontSize',15,'FontWeight','bold','Color',S.ink);
mltext(0.55, 0.30, {'F_k is non-decreasing in k for every row,', ...
    'so a 1 s alarm can never exceed a 2 s alarm.', 'A multi-head baseline violates this on 43.6% of rows.'}, ...
    S.maroon, 13, 'left', -0.07);
savefig_png('fig08_hazard_concept');
end
