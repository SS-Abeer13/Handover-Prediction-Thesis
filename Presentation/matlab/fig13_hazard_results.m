function fig13_hazard_results()
%FIG13  The hazard model buys coherence; isotonic calibration buys ECE and
%       destroys coherence. Left: ECE by horizon. Right: monotonicity.
S = fig_style();
h    = [0.5 1 2 3 5];
haz  = [0.015 0.014 0.034 0.054 0.084];
raw  = [0.023 0.022 0.055 0.077 0.111];
iso  = [0.012 0.010 0.022 0.033 0.046];
mono = [0.012 0.012 0.021 0.033 0.047];

newfig(1440, 700);

subplot(1,2,1); hold on;
p2 = plot(h, raw,  '-s', 'Color', S.grey,  'LineWidth', 2.0, 'MarkerSize', 8, 'MarkerFaceColor', 'w');
p3 = plot(h, iso,  '-d', 'Color', S.navy,  'LineWidth', 2.0, 'MarkerSize', 8, 'MarkerFaceColor', 'w');
p4 = plot(h, mono, '-v', 'Color', S.navy,  'LineWidth', 1.4, 'MarkerSize', 7, 'MarkerFaceColor', S.navy);
p1 = plot(h, haz,  '-o', 'Color', S.maroon,'LineWidth', 3.0, 'MarkerSize', 10,'MarkerFaceColor', S.maroon);
set(gca,'XTick',h,'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1);
xlim([0.3 5.3]); ylim([0 0.130]);
xlabel('Horizon  (s)','FontSize',S.fs_lab,'Color',S.ink);
ylabel('Expected calibration error','FontSize',S.fs_lab,'Color',S.ink);
title('Calibration  (lower is better)','FontSize',S.fs_lab,'FontWeight','bold','Color',S.ink);
lg = legend([p1 p2 p3 p4], {'hazard (one fit)','multi-head, raw', ...
     'multi-head + isotonic','+ isotonic + monotone'},'Location','southeast','FontSize',12.5);
legend boxoff; set(lg,'TextColor',S.ink);
mltext(0.45, 0.124, {'the hazard model is beaten on ECE only by', ...
     'spending a held-out calibration split'}, S.navy, 12.5, 'left', -0.0085);

subplot(1,2,2); hold on;
viol = [0 43.6 48.7 0];
hb = bar(viol, 0.6);
set(hb,'EdgeColor','none','FaceColor','flat');
try set(hb,'CData',[S.maroon; S.grey; S.navy; S.navy]); catch, set(hb,'FaceColor',S.navy); end
set(gca,'XTick',1:4,'XTickLabel',{'hazard','5 heads','+ iso','+ iso+mon'}, ...
    'XColor',S.ink,'YColor',S.ink,'Layer','top');
try set(gca,'XTickLabelRotation',20); end
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1,'YGrid','on','XGrid','off');
ylim([0 62]);
ylabel('Rows with a non-monotone horizon sequence  (%)','FontSize',14,'Color',S.ink);
title('Coherence across horizons','FontSize',S.fs_lab,'FontWeight','bold','Color',S.ink);
for i=1:4
    text(i, viol(i)+2.6, sprintf('%.1f%%', viol(i)), 'HorizontalAlignment','center', ...
         'FontSize',14,'FontWeight','bold','Color',S.ink);
end
mltext(2.5, 58, {'per-horizon isotonic makes coherence WORSE', ...
     '(max violation 0.495 \rightarrow 0.596)'}, S.maroon, 13, 'center', -3.6);
mltext(1, 9, {'0% by', 'construction'}, S.maroon, 13, 'center', -3.6);

savefig_png('fig13_hazard_results');
end
