function savefig_png(name)
%SAVEFIG_PNG  Write the current figure to png/ (slides) or png_print/ (thesis).
global PRINTFIG
here = fileparts(mfilename('fullpath'));
if ~isempty(PRINTFIG) && PRINTFIG, sub = 'png_print'; else, sub = 'png'; end
outdirs = {fullfile(here, sub), ...
           fullfile(here, '..', sub), ...
           fullfile(here, '..', '..', 'pipeline', 'reports_rev', 'figures'), ...
           fullfile(here, '..', '..', 'latex', 'figures')};

for i = 1:numel(outdirs)
    od = outdirs{i};
    if ~exist(od, 'dir'), mkdir(od); end
    print(gcf, fullfile(od, [name '.png']), '-dpng', '-r300');
end
close(gcf);
end
