function fig32_operating_plane()
%FIG32  The cost plane an operator actually cares about.
%   Detection-versus-false-alarm planes are standard in event-detection work
%   and absent from every model in the audit of Chapter 2. Each track is one
%   model walked across the five look-ahead times; marker size grows with the
%   horizon, so both axes and the horizon are readable at once.
S = fig_style();
h   = [0.5 1 2 3 5];
det = [0.0362 0.0554 0.1269 0.1748 0.2793;   % deployed A3 rule
       0.4168 0.4467 0.5394 0.6418 0.6514;   % LightGBM
       0.3785 0.4520 0.5352 0.6407 0.7026;   % logistic regression
       0.2846 0.3188 0.3795 0.4733 0.5384];  % GRU
fah = [54.15 65.80 69.57 61.61 57.33;
       42.49 63.92 63.52 62.75 41.56;
       39.86 61.29 61.25 57.43 55.41;
       42.87 53.77 51.05 52.48 50.02];
nm  = {'Event A3 rule (deployed)','LightGBM','Logistic regression','GRU'};
col = {S.grey, S.maroon, S.navy, [0.55 0.45 0.65]};

newfig(1200, 800); hold on;
for m = 1:4
    plot(fah(m,:), det(m,:), '-', 'Color', col{m}, 'LineWidth', 2.0);
    for k = 1:5
        plot(fah(m,k), det(m,k), 'o', 'MarkerSize', 5 + 2.1*k, ...
             'MarkerFaceColor', col{m}, 'MarkerEdgeColor', 'w', 'LineWidth', 1.2);
    end
    yl = 0.88 - 0.062*m;
    plot([68.0 71.0], [yl yl], '-', 'Color', col{m}, 'LineWidth', 2.6);
    text(72.0, yl, nm{m}, 'FontSize', 14, 'Color', col{m});
end
for k = 1:5
    text(fah(2,k), det(2,k) + 0.036, sprintf('%g s', h(k)), 'FontSize', 12, ...
         'Color', S.maroon, 'HorizontalAlignment', 'center');
end
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
xlim([32 88]); ylim([0 0.98]);
xlabel('False alarm episodes per hour of driving', 'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('Fraction of handover events detected', 'FontSize', S.fs_lab, 'Color', S.ink);
plot([32 88], [0.905 0.905], '--', 'Color', S.lgrey, 'LineWidth', 2.2);
text(33, 0.925, 'ceiling imposed by the 1 Hz grid: 90.5 % of events', 'FontSize', 13, 'Color', [0.45 0.45 0.45]);
mltext(33, 0.175, {'Marker size grows with the look-ahead time.', ...
    'Moving right buys detection with false alarms;', ...
    'the deployed rule buys almost none of it.'}, S.ink, 14, 'left', -0.045);
savefig_png('fig32_operating_plane');
end
