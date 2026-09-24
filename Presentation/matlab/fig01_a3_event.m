function fig01_a3_event()
%FIG01  What event A3 actually does, and why it is reactive.
S = fig_style();
t = 0:0.02:20;
serv = -78 - 1.35*t + 1.2*sin(0.9*t);
nbr  = -101 + 1.55*t + 1.0*sin(1.3*t + 1);
off = 1; hys = 1;
cond = nbr > serv + off + hys;
i0 = find(cond, 1);
ttt = 0.32;                      % 320 ms, the deployed profile
t_fire = t(i0) + ttt;
t_ho   = t_fire + 0.18;

newfig(1180, 740); hold on;
ylim([-112 -62]); xlim([0 20]);
yl = ylim;
ix = find(t >= t(i0) & t <= t_fire);
patch([t(ix) fliplr(t(ix))], [yl(1)*ones(size(ix)) yl(2)*ones(size(ix))], ...
      S.amber, 'FaceAlpha', 0.18, 'EdgeColor', 'none');

p1 = plot(t, serv, '-', 'Color', S.navy,  'LineWidth', 3.0);
p2 = plot(t, nbr,  '-', 'Color', S.maroon,'LineWidth', 3.0);
p3 = plot(t, serv + off + hys, ':', 'Color', [0.4 0.4 0.4], 'LineWidth', 2.0);

plot([t(i0) t(i0)], yl, '--', 'Color', [0.35 0.35 0.35], 'LineWidth', 1.4);
plot([t_ho t_ho],   yl, '-',  'Color', S.green, 'LineWidth', 2.2);

set(gca,'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1);
xlabel('Time  (s)','FontSize',S.fs_lab,'Color',S.ink);
ylabel('RSRP  (dBm)','FontSize',S.fs_lab,'Color',S.ink);

mltext(t(i0)-0.3, -66, {'entering condition', 'M_n > M_s + Off + Hys'}, [0.3 0.3 0.3], 14, 'right');
mltext(t_ho+0.3, -95, {'handover', 'command'}, S.green, 14, 'left');
text(mean([t(i0) t_fire]), -104.5, 'TTT', 'Color', S.amber, 'FontSize', 15, ...
     'FontWeight','bold','HorizontalAlignment','center');
text(1.2, -80.5, 'serving cell', 'Color', S.navy, 'FontSize', 16, 'FontWeight','bold');
text(14.6, -73.5, 'neighbour cell', 'Color', S.maroon, 'FontSize', 16, 'FontWeight','bold');
mltext(0.4, -64.2, {'The rule acts on conditions that have', ...
      'ALREADY happened \rightarrow everything', 'downstream of it is a reaction.'}, S.ink, 15, 'left', -2.7);
savefig_png('fig01_a3_event');
end
