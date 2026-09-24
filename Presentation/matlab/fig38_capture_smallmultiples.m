function fig38_capture_smallmultiples()
%FIG38  Leave-one-campaign-out on four metrics at once.
%   Small multiples keep the four metrics on their own scales while the eye
%   compares the same four bars across panels. The pooled value is drawn as a
%   reference line in every panel so "does the held-out campaign behave like
%   the pool?" is answerable without arithmetic.
S = fig_style();
lab  = {'urban','urban','dense','high-'; 'arterial','loop','urban','way'};
V    = [0.826 0.718 0.832 0.761;      % AUPRC
        9.9   9.4   13.2  14.9;       % lift
        0.949 0.909 0.943 0.927;      % AUROC
        0.027 0.040 0.019 0.018];     % ECE
pool = [0.784 11.7 0.933 0.024];
ttl  = {'AUPRC','Lift over the floor','AUROC','Calibration error'};
lo   = [0.60 8 0.85 0]; hi = [0.90 16 0.98 0.05];
better_low = [0 0 0 1];

newfig(1340, 640);
for m = 1:4
    axes('Position', [0.065 + 0.245*(m-1), 0.20, 0.185, 0.66]); hold on;
    for c = 1:4
        if c == 4, fc = S.maroon; else, fc = S.navy; end
        bar(c, V(m,c), 0.66, 'FaceColor', fc, 'EdgeColor', 'none');
        text(c, V(m,c) + 0.035*(hi(m)-lo(m)), sprintf('%.3g', V(m,c)), 'FontSize', 12, ...
             'Color', S.ink, 'HorizontalAlignment', 'center');
    end
    plot([0.4 4.6], [pool(m) pool(m)], '--', 'Color', [0.45 0.45 0.45], 'LineWidth', 1.8);
    set(gca, 'XTick', 1:4, 'XTickLabel', {'arterial','loop','dense','highway'}, ...
        'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top', 'FontSize', 12);
    grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XGrid', 'off', 'YGrid', 'on');
    xlim([0.4 4.6]); ylim([lo(m) hi(m)]);
    if better_low(m)
        title([ttl{m} '  (lower is better)'], 'FontSize', 13.5, 'Color', S.ink, 'FontWeight', 'normal');
    else
        title(ttl{m}, 'FontSize', 13.5, 'Color', S.ink, 'FontWeight', 'normal');
    end
end
global PRINTFIG
if isempty(PRINTFIG) || ~PRINTFIG
annotation('textbox', [0.065 0.02 0.90 0.09], 'String', ...
    'Each panel: one campaign held out entirely, trained on the other three. Dashed line = the pooled result. The highway (maroon) was driven after every modelling decision was frozen.', ...
    'EdgeColor', 'none', 'FontSize', 14, 'Color', S.ink, 'FontName', 'Arial');
end
savefig_png('fig38_capture_smallmultiples');
end
