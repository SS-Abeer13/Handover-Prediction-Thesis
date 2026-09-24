function fig39_profile_bubble()
%FIG39  Why the gap condition cannot carry the prediction.
%   Two quantities per configuration profile that the literature never plots
%   together: how many handovers it produces, and how much of the time its own
%   entry condition is already satisfied. Bubble area is the handover count.
S = fig_style();
share = [0.7463 0.1309 0.0769];        % share of all handovers
cov   = [0.1237 0.7355 0.9136];        % fraction of samples where the gap condition holds
nho   = [553 97 57];
nm    = {'+1 dB / 320 ms','-10 dB / 640 ms','-15 dB / 160 ms'};
col   = {S.maroon, S.navy, S.grey};

newfig(1140, 760); hold on;
for k = 1:3
    r = sqrt(nho(k)) * 1.25;
    plot(cov(k), share(k), 'o', 'MarkerSize', r, 'MarkerFaceColor', col{k}, ...
         'MarkerEdgeColor', 'w', 'LineWidth', 2);
end
text(cov(1) + 0.085, share(1), {'+1 dB / 320 ms'}, 'FontSize', 15, 'Color', S.maroon);
text(cov(1) + 0.085, share(1) - 0.055, '553 handovers, 74.6 %', 'FontSize', 13, 'Color', S.maroon);
text(cov(2) - 0.150, share(2) + 0.130, '-10 dB / 640 ms', 'FontSize', 15, 'Color', S.navy);
text(cov(2) - 0.150, share(2) + 0.080, '97 handovers, 13.1 %', 'FontSize', 13, 'Color', S.navy);
text(cov(3) - 0.02, share(3) + 0.230, '-15 dB / 160 ms', 'FontSize', 15, 'Color', S.grey);
text(cov(3) - 0.02, share(3) + 0.180, '57 handovers, 7.7 %', 'FontSize', 13, 'Color', S.grey);
grid on; set(gca, 'GridColor', S.grid, 'GridAlpha', 1, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
xlim([0 1.05]); ylim([-0.05 0.95]);
xlabel('Fraction of samples on which this profile''s gap condition already holds', ...
       'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('Share of all handovers produced', 'FontSize', S.fs_lab, 'Color', S.ink);
mltext(0.215, 0.545, {'The two axes disagree. The profile that produces three quarters', ...
    'of the handovers has its entry condition satisfied on only 12 % of', ...
    'samples; the profile whose condition holds almost always produces', ...
    'fewer than one handover in twelve. Bubble area is the handover count.'}, ...
    S.ink, 14, 'left', -0.045);
savefig_png('fig39_profile_bubble');
end
