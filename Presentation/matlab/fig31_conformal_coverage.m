function fig31_conformal_coverage()
%FIG31  Does the guarantee hold, and what does it cost?
%   Conformal papers report realised risk against the nominal level with the
%   diagonal drawn, because the claim is exactly "the point sits on or below
%   the line". The alarm rate is carried on a second axis because the cost of
%   the guarantee is the other half of the story.
S = fig_style();
alpha  = [0.05 0.10 0.15 0.20 0.30 0.40];
fnr    = [0.0348 0.0740 0.0913 0.1263 0.2198 0.3692];
alarm  = [0.6054 0.3713 0.2778 0.2346 0.0937 0.0421];
amin   = 0.0345;

newfig(1180, 780);
ax1 = axes('Position', [0.10 0.13 0.80 0.78]); hold on;
patch([0 amin amin 0], [0 0 0.45 0.45], [0.95 0.95 0.95], 'EdgeColor', 'none');
text(amin/2, 0.415, {'not'}, 'FontSize', 12, 'Color', [0.5 0.5 0.5], 'HorizontalAlignment', 'center');
text(amin/2, 0.385, {'reachable'}, 'FontSize', 12, 'Color', [0.5 0.5 0.5], 'HorizontalAlignment', 'center');
plot([0 0.45], [0 0.45], '--', 'Color', [0.55 0.55 0.55], 'LineWidth', 1.6);
text(0.405, 0.425, 'guarantee boundary', 'FontSize', 13, 'Color', [0.45 0.45 0.45], ...
     'HorizontalAlignment', 'right');
plot(alpha, fnr, '-o', 'Color', S.maroon, 'LineWidth', 2.6, 'MarkerSize', 9, ...
     'MarkerFaceColor', S.maroon, 'MarkerEdgeColor', 'w');
plot([amin amin], [0 0.45], ':', 'Color', S.ink, 'LineWidth', 1.6);
mltext(0.055, 0.305, {'feasibility floor', '\alpha \geq 0.0345 with n = 28 drives'}, S.ink, 13, 'left', -0.028);
set(ax1, 'XColor', S.ink, 'YColor', S.maroon, 'Layer', 'top');
grid on; set(ax1, 'GridColor', S.grid, 'GridAlpha', 1);
xlim([0 0.45]); ylim([0 0.45]);
xlabel('Certified target \alpha  (bound on the per-drive miss rate)', 'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('Realised miss rate on held-out drives', 'FontSize', S.fs_lab, 'Color', S.maroon);

ax2 = axes('Position', get(ax1,'Position'), 'Color', 'none', ...
           'YAxisLocation', 'right', 'XTick', [], 'XColor', 'none', 'YColor', S.navy);
hold(ax2, 'on');
plot(ax2, alpha, alarm, '-s', 'Color', S.navy, 'LineWidth', 2.2, 'MarkerSize', 8, ...
     'MarkerFaceColor', S.navy, 'MarkerEdgeColor', 'w');
xlim(ax2, [0 0.45]); ylim(ax2, [0 0.70]);
ylabel(ax2, 'Fraction of samples alarmed', 'FontSize', S.fs_lab, 'Color', S.navy);
text(0.090, 0.640, 'alarm rate 61 % at \alpha = 0.05', 'FontSize', 14, 'Color', S.navy, 'Parent', ax2);
text(0.215, 0.275, '23 % at \alpha = 0.20', 'FontSize', 14, 'Color', S.navy, 'Parent', ax2);
savefig_png('fig31_conformal_coverage');
end
