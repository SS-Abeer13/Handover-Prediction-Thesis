function h = newfig(w, hgt)
%NEWFIG  White figure of a given pixel size, ready for print().
%   With the global PRINTFIG set, the canvas is shrunk by PRINTSCALE while the
%   font sizes in every figure script stay as authored. That is what raises the
%   on-figure text from about 5 pt to about 9 pt once the image is placed in a
%   12 pt document. The slide versions are produced with PRINTFIG unset.
global PRINTFIG PRINTSCALE
if nargin < 1, w = 1080; end
if nargin < 2, hgt = 760; end
if ~isempty(PRINTFIG) && PRINTFIG
    k = 0.60; if ~isempty(PRINTSCALE), k = PRINTSCALE; end
    w = round(w * k); hgt = round(hgt * k);
end
h = figure('Color','w','Position',[80 80 w hgt]);
set(h,'PaperPositionMode','auto');
set(h,'InvertHardcopy','off');
end
