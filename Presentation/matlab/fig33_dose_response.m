function fig33_dose_response()
%FIG33  Handover probability against the quantity the rule thresholds on.
%   A binned dose-response curve with binomial confidence intervals, drawn
%   over a bar of bin counts so that a wide interval is visibly a small-sample
%   interval. This is the figure that shows the A3 gap is a weak signal, not
%   merely that a model outperforms it.
S = fig_style();
gap = [-8.75 -6.25 -3.75 -1.25 1.25 3.75 6.25 8.75 11.25 13.75 16.25 21.25];
n   = [49 54 163 243 584 530 603 279 309 98 77 35];
p   = [0.2245 0.1667 0.2147 0.1893 0.1387 0.1038 0.1095 0.0860 0.0809 0.0918 0.1299 0.0857];
z = 1.96; ph = (p.*n + z^2/2) ./ (n + z^2);                 % Wilson centre
w = z ./ (n + z^2) .* sqrt(p.*(1-p).*n + z^2/4);            % Wilson half-width

newfig(1200, 820);
axB = axes('Position', [0.10 0.10 0.85 0.20]); hold on;
bar(gap, n, 0.62, 'FaceColor', S.lgrey, 'EdgeColor', 'none');
set(axB, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
xlim([-11 24]); ylim([0 700]);
xlabel('Serving-to-neighbour gap at the prediction instant (dB)', 'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('samples', 'FontSize', 13, 'Color', S.ink);

axT = axes('Position', [0.10 0.36 0.85 0.57]); hold on;
for k = 1:numel(gap)
    plot([gap(k) gap(k)], [ph(k)-w(k) ph(k)+w(k)], '-', 'Color', [0.72 0.72 0.72], 'LineWidth', 1.6);
end
plot(gap, p, '-o', 'Color', S.maroon, 'LineWidth', 2.4, 'MarkerSize', 8, ...
     'MarkerFaceColor', S.maroon, 'MarkerEdgeColor', 'w');
plot([-2 -2], [0 0.30], ':', 'Color', S.navy, 'LineWidth', 2);
text(-1.6, 0.288, 'the dominant profile fires here', 'FontSize', 13, 'Color', S.navy);
grid on; set(axT, 'GridColor', S.grid, 'GridAlpha', 1, 'XColor', S.ink, 'YColor', S.ink, ...
    'Layer', 'top', 'XTickLabel', []);
xlim([-11 24]); ylim([0 0.32]);
ylabel('P(handover within 1 s)', 'FontSize', S.fs_lab, 'Color', S.ink);
mltext(8.0, 0.285, {'The response is shallow and not monotone.', ...
    'Across a 30 dB sweep of the rule''s own quantity the', ...
    'handover probability moves between 0.08 and 0.22:', ...
    'necessary, nowhere near sufficient.'}, S.ink, 14, 'left', -0.026);
savefig_png('fig33_dose_response');
end
