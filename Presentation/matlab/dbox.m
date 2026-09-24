function dbox(x, y, w, h, label, face, edge, fs, txtcol)
%DBOX  Rounded-ish block for the architecture diagrams (axis units).
if nargin < 6 || isempty(face),  face = [1 1 1]; end
if nargin < 7 || isempty(edge),  edge = [0.35 0.35 0.35]; end
if nargin < 8 || isempty(fs),    fs = 14; end
if nargin < 9 || isempty(txtcol),txtcol = [0.16 0.16 0.16]; end
rectangle('Position', [x y w h], 'FaceColor', face, 'EdgeColor', edge, ...
          'LineWidth', 1.6, 'Curvature', 0.12);
if iscell(label)
    n = numel(label);
    for k = 1:n
        yy = y + h/2 + (n-1)/2*0.052*h*n - (k-1)*0.30*h;
        text(x + w/2, yy, label{k}, 'HorizontalAlignment','center', ...
             'VerticalAlignment','middle','FontSize',fs,'Color',txtcol,'FontName','Arial');
    end
else
    text(x + w/2, y + h/2, label, 'HorizontalAlignment','center', ...
         'VerticalAlignment','middle','FontSize',fs,'Color',txtcol,'FontName','Arial');
end
end
