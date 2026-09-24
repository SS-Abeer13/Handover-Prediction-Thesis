function mltext(x, y, lines, col, fs, align, dy)
%MLTEXT  Multi-line annotation drawn one line per text object.
%   Suppressed in the print variant: a printed figure should not carry a
%   paragraph of prose, because the caption already carries it and the prose
%   is what forces the plot itself to be small.
global PRINTFIG
if ~isempty(PRINTFIG) && PRINTFIG, return; end
if nargin < 4 || isempty(col),   col = [0.16 0.16 0.16]; end
if nargin < 5 || isempty(fs),    fs = 15; end
if nargin < 6 || isempty(align), align = 'left'; end
if nargin < 7 || isempty(dy)
    yl = ylim; dy = -0.055 * (yl(2) - yl(1));
end
for k = 1:numel(lines)
    text(x, y + (k-1)*dy, lines{k}, 'Color', col, 'FontSize', fs, ...
         'HorizontalAlignment', align, 'FontName', 'Arial');
end
end
