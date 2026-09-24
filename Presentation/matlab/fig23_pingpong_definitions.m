function fig23_pingpong_definitions()
%FIG23  Why published ping-pong rates are not comparable.
%   The same 938 signalling-confirmed handovers, four definitions, four answers.
%   Computed in stage 16 / doc 25; every step is one stated choice.
S = fig_style();

labels = {'A \rightarrow B \rightarrow A, cell = PCI + carrier', ...
          'A \rightarrow B \rightarrow A, cell = PCI only', ...
          'any return inside the window, PCI only', ...
          'the same, ungrouped over the raw log'};
vals = [24.5 29.0 38.5 41.3];
adds = {'', '+4.5', '+9.5', '+2.8'};
cols = [S.maroon; S.navy; S.navy; S.grey];

newfig(1240, 700); hold on;
% one bar per call, padded with NaN so the bar width survives
for i = 1:numel(vals)
    v = nan(1, numel(vals)); v(i) = vals(i);
    hb = barh(1:numel(vals), v, 0.6);
    set(hb, 'EdgeColor', 'none', 'FaceColor', cols(i, :));
end

for i = 1:numel(vals)
    text(vals(i) + 1.0, i, sprintf('%.1f%%', vals(i)), 'FontSize', 15, ...
         'FontWeight', 'bold', 'Color', S.ink, 'VerticalAlignment', 'middle');
    if ~isempty(adds{i})
        text(vals(i) + 6.2, i, sprintf('(%s)', adds{i}), 'FontSize', 13, ...
             'Color', [0.45 0.45 0.45], 'VerticalAlignment', 'middle');
    end
end

set(gca, 'YTick', 1:numel(labels), 'YTickLabel', labels, 'YDir', 'reverse', ...
    'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XGrid', 'on', 'YGrid', 'off');
xlim([0 66]); ylim([0.45 numel(labels) + 0.55]);
xlabel('Ping-pong rate over the same 938 handovers  (%)', ...
       'FontSize', S.fs_lab, 'Color', S.ink);

mltext(46.5, 1.62, {'Each line changes', 'exactly one choice.', '', ...
    'None is wrong. Only the', 'top one is what the', ...
    'ping-pong literature means.'}, S.maroon, 14, 'left', 0.30);

savefig_png('fig23_pingpong_definitions');
end
