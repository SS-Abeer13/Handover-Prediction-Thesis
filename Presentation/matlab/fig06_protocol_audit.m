function fig06_protocol_audit()
%FIG06  Protocol audit of 22 comparable papers: the gap this thesis occupies.
%   Counts recounted from protocol_audit.csv after the pass-3 widening
%   (doc 22 section 3). Counting rules are stated in that document.
S = fig_style();
labels = {'Splits by drive or route','Split coarser than a random row', ...
          'States a split protocol at all','Prevalence-aware ranking metric', ...
          'Calibration curve, ECE or Brier','Lead time or false alarms/hour', ...
          'Releases code','Releases data'};
counts = [0 5 12 2 0 0 2 1];
N = 22;

newfig(1240, 760); hold on;
hb = barh(100*counts/N, 0.55);
set(hb,'FaceColor',S.grey,'EdgeColor','none');
for i = 1:numel(counts)
    plot([100 100], [i-0.28 i+0.28], '-', 'Color', S.maroon, 'LineWidth', 9);
    text(100*counts(i)/N + 2, i, sprintf('%d of %d', counts(i), N), ...
         'FontSize', 14, 'Color', S.ink, 'VerticalAlignment','middle');
end
set(gca,'YTick',1:numel(labels),'YTickLabel',labels,'YDir','reverse', ...
    'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1,'XGrid','on','YGrid','off');
xlim([0 118]); ylim([0.4 numel(labels)+0.6]);
xlabel('Share of the 22 audited papers  (%)','FontSize',S.fs_lab,'Color',S.ink);
text(104, 0.72, 'this work', 'Color', S.maroon, 'FontSize', 15, 'FontWeight','bold', ...
     'HorizontalAlignment','center');
mltext(31, 5.6, {'7 of 22 report headline accuracy on an imbalanced', ...
     'task, where a constant no scores 89-99%'}, S.maroon, 14, 'left', 0.36);
mltext(31, 7.3, {'The survey widened from 17 papers to 22 and these', ...
     'two rows did not move at all.'}, [0.35 0.35 0.35], 13, 'left', 0.34);
savefig_png('fig06_protocol_audit');
end
