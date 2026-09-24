function fig36_ece_ribbon()
%FIG36  Calibration degrades with the horizon, and by how much.
%   A median line inside an inter-quartile ribbon is the compact way to show a
%   distribution that moves along an axis. The gap between the two ribbons is
%   the calibration benefit of the hazard formulation, horizon by horizon.
S = fig_style();
h   = [0.5 1 2 3 5];
hq1 = [0.0176 0.0140 0.0423 0.0634 0.0704];
hmd = [0.0194 0.0181 0.0447 0.0685 0.1041];
hq3 = [0.0239 0.0199 0.0503 0.0800 0.1173];
mq1 = [0.0236 0.0204 0.0556 0.0861 0.1013];
mmd = [0.0258 0.0231 0.0599 0.0898 0.1279];
mq3 = [0.0308 0.0245 0.0701 0.1026 0.1447];

newfig(1140, 740); hold on;
patch([h fliplr(h)], [mq1 fliplr(mq3)], [0.88 0.92 0.96], 'EdgeColor', 'none');
patch([h fliplr(h)], [hq1 fliplr(hq3)], [0.95 0.88 0.88], 'EdgeColor', 'none');
plot(h, mmd, '-s', 'Color', S.navy,   'LineWidth', 2.6, 'MarkerSize', 8, ...
     'MarkerFaceColor', S.navy, 'MarkerEdgeColor', 'w');
plot(h, hmd, '-o', 'Color', S.maroon, 'LineWidth', 2.6, 'MarkerSize', 8, ...
     'MarkerFaceColor', S.maroon, 'MarkerEdgeColor', 'w');
text(5.08, mmd(5), 'Five independent heads', 'FontSize', 14, 'Color', S.navy);
text(5.08, hmd(5), 'One hazard model',      'FontSize', 14, 'Color', S.maroon);
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
set(gca, 'XTick', h);
xlim([0.3 6.9]); ylim([0 0.16]);
xlabel('Look-ahead horizon (s)', 'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('Expected calibration error  (median, IQR band)', 'FontSize', S.fs_lab, 'Color', S.ink);
mltext(0.45, 0.152, {'The hazard model is better calibrated at every horizon,', ...
    'and both degrade steeply beyond 2 s. That degradation bounds', ...
    'the horizon at which the output may be read as a probability', ...
    'rather than as a ranking.'}, S.ink, 14, 'left', -0.0115);
savefig_png('fig36_ece_ribbon');
end
