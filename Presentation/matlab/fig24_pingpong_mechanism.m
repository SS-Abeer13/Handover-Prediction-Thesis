function fig24_pingpong_mechanism()
%FIG24  Where the ping-pong actually is: one carrier layer, one A3 profile.
%   Left: rate split by whether the handover changes carrier.
%   Right: rate by the deployed time-to-trigger, with the number of handovers
%   each profile carries printed on the bar.
S = fig_style();

newfig(1440, 680);

% ---------------------------------------------------- left: carrier layer
subplot(1, 2, 1); hold on;
v = [31.0 6.5]; n = [690 248];
hb = bar(v, 0.55);
set(hb, 'EdgeColor', 'none', 'FaceColor', 'flat');
try set(hb, 'CData', [S.maroon; S.navy]); catch, set(hb, 'FaceColor', S.navy); end
for i = 1:2
    text(i, v(i) + 1.4, sprintf('%.1f%%', v(i)), 'HorizontalAlignment', 'center', ...
         'FontSize', 16, 'FontWeight', 'bold', 'Color', S.ink);
    text(i, 1.8, sprintf('%d handovers', n(i)), 'HorizontalAlignment', 'center', ...
         'FontSize', 13, 'Color', [1 1 1], 'FontWeight', 'bold');
end
set(gca, 'XTick', 1:2, 'XTickLabel', {'stays on the carrier', 'changes carrier'}, ...
    'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'YGrid', 'on', 'XGrid', 'off');
ylim([0 40]);
ylabel('Ping-pong rate  (%)', 'FontSize', S.fs_lab, 'Color', S.ink);
title('Ping-pong is an intra-carrier effect', 'FontSize', S.fs_lab, ...
      'FontWeight', 'bold', 'Color', S.ink);
mltext(1.5, 37.5, {'Five times the rate when the', 'handover stays on one carrier.'}, ...
       S.maroon, S.fs_ann, 'center', -3.0);

% ---------------------------------------- right: deployed time-to-trigger
subplot(1, 2, 2); hold on;
ttt = [160 320 640];
v2 = [12.5 28.8 11.0]; n2 = [72 702 136];
hb = bar(v2, 0.55);
set(hb, 'EdgeColor', 'none', 'FaceColor', 'flat');
try set(hb, 'CData', [S.navy; S.maroon; S.navy]); catch, set(hb, 'FaceColor', S.navy); end
for i = 1:3
    text(i, v2(i) + 1.4, sprintf('%.1f%%', v2(i)), 'HorizontalAlignment', 'center', ...
         'FontSize', 16, 'FontWeight', 'bold', 'Color', S.ink);
    text(i, 1.8, sprintf('n=%d', n2(i)), 'HorizontalAlignment', 'center', ...
         'FontSize', 13, 'Color', [1 1 1], 'FontWeight', 'bold');
end
set(gca, 'XTick', 1:3, 'XTickLabel', {'160 ms', '320 ms', '640 ms'}, ...
    'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'YGrid', 'on', 'XGrid', 'off');
ylim([0 40]);
xlabel('Deployed time-to-trigger of the profile that fired', ...
       'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('Ping-pong rate  (%)', 'FontSize', S.fs_lab, 'Color', S.ink);
title('One profile carries it', 'FontSize', S.fs_lab, 'FontWeight', 'bold', 'Color', S.ink);
mltext(2.55, 37.5, {'The 320 ms profile fires 3 of every', ...
    '4 handovers and is the only one', 'that oscillates.'}, S.maroon, S.fs_ann, 'center', -3.0);

savefig_png('fig24_pingpong_mechanism');
end
