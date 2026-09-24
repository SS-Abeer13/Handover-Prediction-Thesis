function fig27_necessity()
%FIG27  What the reactive rule costs, measured on this campaign.
%   Every number is counted from the four captures, not assumed.
S = fig_style();
newfig(1400, 760); hold on;
axis([0 100 0 100]); axis off;

% ---------------------------------------------------------------- left block
text(3, 95, 'What the reactive rule costs, counted on these 57 drives', ...
     'FontSize', 17, 'FontWeight', 'bold', 'Color', S.maroon, 'FontName', 'Arial');

nums = {'938', '24.5%', '341', '4,645'};
labs = {{'handovers in 2.9 hours of driving', '- one every 11 seconds, a median 3.5 s apart'}, ...
        {'go straight back to the cell just left', '- 230 of 938, within 15 seconds'}, ...
        {'RRC re-establishments', '- the link actually dropped, 159 of them in one capture'}, ...
        {'A3 reports the network declined', '- 62.9% of 7,385, each one signalling that bought nothing'}};
y = 80;
for i = 1:4
    text(4, y, nums{i}, 'FontSize', 27, 'FontWeight', 'bold', 'Color', S.maroon, ...
         'FontName', 'Arial', 'VerticalAlignment', 'middle');
    text(19, y + 2.1, labs{i}{1}, 'FontSize', 15.5, 'Color', S.ink, 'FontName', 'Arial', ...
         'VerticalAlignment', 'middle');
    text(19, y - 3.0, labs{i}{2}, 'FontSize', 13.5, 'Color', S.grey, 'FontName', 'Arial', ...
         'VerticalAlignment', 'middle');
    y = y - 17.5;
end

% divider
plot([62 62], [8 92], '-', 'Color', [0.82 0.82 0.82], 'LineWidth', 1.5);

% --------------------------------------------------------------- right block
text(65, 95, 'And nobody has built the predictor', ...
     'FontSize', 17, 'FontWeight', 'bold', 'Color', S.ink, 'FontName', 'Arial');

rl = {{'0 of 22', 'comparable papers hold out the', 'mobility unit for a per-timestep task'}, ...
      {'0 of 22', 'report a calibration curve, an ECE', 'or a Brier score'}, ...
      {'0 of 22', 'report a lead time or a false-alarm', 'rate an operator would be charged for'}};
y = 79;
for i = 1:3
    text(65, y, rl{i}{1}, 'FontSize', 21, 'FontWeight', 'bold', 'Color', S.navy, ...
         'FontName', 'Arial', 'VerticalAlignment', 'middle');
    text(65, y - 5.4, rl{i}{2}, 'FontSize', 14, 'Color', S.ink, 'FontName', 'Arial', ...
         'VerticalAlignment', 'middle');
    text(65, y - 10.0, rl{i}{3}, 'FontSize', 14, 'Color', S.ink, 'FontName', 'Arial', ...
         'VerticalAlignment', 'middle');
    y = y - 22.5;
end

patch([64 98 98 64], [6 6 17 17], [0.98 0.95 0.95], 'EdgeColor', S.maroon, 'LineWidth', 1.4);
text(81, 13.5, 'The measurement exists in the signalling.', 'FontSize', 14.5, ...
     'Color', S.maroon, 'FontName', 'Arial', 'HorizontalAlignment', 'center', ...
     'FontWeight', 'bold');
text(81, 9.0, 'Nobody has pointed a predictor at it.', 'FontSize', 14.5, ...
     'Color', S.maroon, 'FontName', 'Arial', 'HorizontalAlignment', 'center', ...
     'FontWeight', 'bold');

savefig_png('fig27_necessity');
end
