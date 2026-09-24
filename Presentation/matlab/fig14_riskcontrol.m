function fig14_riskcontrol()
%FIG14  The distribution-free guarantee is expensive below alpha = 0.15.
S = fig_style();
alpha = [0.05 0.10 0.15 0.20 0.30 0.40];
alarm = [60.5 37.1 27.8 23.5  9.4  3.7];   % certified alarm rate, %
fnr   = [3.5  7.4   9.1 12.6 22.0 36.9];   % realised test FNR, %

newfig(1180, 760); hold on;
plot(alpha*100, alpha*100, ':', 'Color', [0.45 0.45 0.45], 'LineWidth', 1.8);
p1 = plot(alpha*100, alarm, '-o', 'Color', S.maroon, 'LineWidth', 3.0, ...
          'MarkerSize', 10, 'MarkerFaceColor', S.maroon);
p2 = plot(alpha*100, fnr, '-s', 'Color', S.navy, 'LineWidth', 2.2, ...
          'MarkerSize', 9, 'MarkerFaceColor', 'w');

set(gca,'XTick',alpha*100,'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1);
xlim([2 43]); ylim([0 90]);
xlabel('Target per-drive miss rate  \alpha  (%)','FontSize',S.fs_lab,'Color',S.ink);
ylabel('Percent','FontSize',S.fs_lab,'Color',S.ink);

% usable operating point
plot(20, 23.5, 'o', 'MarkerSize', 20, 'Color', S.amber, 'LineWidth', 2.5);
mltext(21.8, 52, {'usable operating point', ...
     'alarms on 23% of samples,', 'misses 12.6% of handovers'}, S.ink, S.fs_ann, 'left');
mltext(5.2, 86, {'the guarantee is expensive below \alpha = 0.15'}, S.maroon, S.fs_ann, 'left');
mltext(41.5, 14, {'feasibility floor: 28 calibration', 'drives put \alpha \geq 0.034'}, [0.35 0.35 0.35], 13, 'right');

lg = legend([p1 p2], {'certified alarm rate', 'realised test miss rate'}, ...
            'Location','northeast','FontSize',S.fs_leg);
legend boxoff; set(lg,'TextColor',S.ink);
text(30.5, 31.5, '\alpha  (the bound)', 'FontSize', 13, 'Color', [0.45 0.45 0.45], 'Rotation', 22);

savefig_png('fig14_riskcontrol');
end
