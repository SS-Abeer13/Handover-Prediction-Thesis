function fig18_hawkes()
%FIG18  Handovers are strongly self-exciting, and the exponential kernel is
%       a calibrated description rather than a generative truth.
S = fig_style();
newfig(1440, 700);

subplot(1,2,1); hold on;
t = 0:0.02:60;
mu = 0.06; alpha = 0.55; beta = 0.9;
ev = [6 8.4 9.1 20 33 34.2 47 48.1 49.4];
lamb = mu*ones(size(t));
for e = ev, lamb = lamb + alpha*exp(-beta*(t-e)).*(t>=e); end
area(t, lamb, 'FaceColor', [0.93 0.95 0.98], 'EdgeColor','none');
plot(t, lamb, '-', 'Color', S.navy, 'LineWidth', 2.4);
plot([0 60],[mu mu],'--','Color',[0.45 0.45 0.45],'LineWidth',1.5);
for e = ev, plot([e e],[0 0.08],'-','Color',S.maroon,'LineWidth',2.5); end
set(gca,'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1);
xlim([0 60]); ylim([0 0.85]);
xlabel('Time  (s)','FontSize',S.fs_lab,'Color',S.ink);
ylabel('Conditional intensity  \lambda(t)','FontSize',S.fs_lab,'Color',S.ink);
text(2, mu+0.05,'background \mu','FontSize',13,'Color',[0.45 0.45 0.45]);
text(21, 0.72,'each handover raises the chance of the next one', ...
     'FontSize',14,'Color',S.maroon,'HorizontalAlignment','center');
title('Self-excitation, illustrated','FontSize',15,'FontWeight','bold','Color',S.ink);

subplot(1,2,2); hold on;
n = 0.605; lo = 0.524; hi = 0.673;
plot([0 1.15],[3 3],'-','Color',[0.93 0.93 0.93],'LineWidth',1);
plot([lo hi],[3 3],'-','Color',S.maroon,'LineWidth',4);
plot([lo lo],[2.82 3.18],'-','Color',S.maroon,'LineWidth',4);
plot([hi hi],[2.82 3.18],'-','Color',S.maroon,'LineWidth',4);
plot(n, 3, 'o','MarkerSize',15,'MarkerFaceColor',S.maroon,'MarkerEdgeColor','w','LineWidth',2);
plot([1 1],[2.3 3.7],'--','Color',[0.4 0.4 0.4],'LineWidth',1.8);
text(n, 3.45, '0.605   [0.524, 0.673]','HorizontalAlignment','center', ...
     'FontSize',17,'FontWeight','bold','Color',S.maroon,'FontName','Arial');
text(1.0, 3.85, 'critical, n = 1','HorizontalAlignment','center','FontSize',13,'Color',[0.4 0.4 0.4]);
text(0.02, 2.55, 'Six in ten handovers are triggered by a previous handover.', ...
     'FontSize',14,'Color',S.ink,'FontName','Arial');
set(gca,'YTick',[],'XColor',S.ink,'YColor','w','Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1,'XGrid','on','YGrid','off');
xlim([0 1.15]); ylim([0.2 4.1]);
xlabel('Branching ratio  n = \alpha / \beta','FontSize',S.fs_lab,'Color',S.ink);
mltext(0.02, 1.95, {'vs homogeneous Poisson:   p \approx 5 \times 10^{-58}', ...
   'vs gamma renewal:   shape 0.78 < 1', ...
   'Ogata residual KS:   p = 7 \times 10^{-4}'}, S.ink, 13.5, 'left', -0.30);
mltext(0.02, 0.85, {'The kernel itself is rejected, so 0.61 is a calibrated', ...
   'measure of clustering strength under a stated kernel,', 'not a generative claim.'}, ...
   S.maroon, 13, 'left', -0.26);
title('Clustering strength, with its goodness of fit','FontSize',15,'FontWeight','bold','Color',S.ink);
savefig_png('fig18_hawkes');
end
