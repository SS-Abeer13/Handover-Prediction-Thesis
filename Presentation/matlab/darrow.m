function darrow(x1, y1, x2, y2, col, lw)
%DARROW  Straight arrow drawn inside the axes (annotation() is unreliable
%   across MATLAB/Octave, so the head is an explicit patch).
if nargin < 5 || isempty(col), col = [0.35 0.35 0.35]; end
if nargin < 6 || isempty(lw),  lw = 1.8; end
plot([x1 x2], [y1 y2], '-', 'Color', col, 'LineWidth', lw);
d = [x2-x1, y2-y1]; L = norm(d);
if L == 0, return; end
u = d / L; p = [-u(2) u(1)];
xl = xlim; yl = ylim;
hl = 0.020 * (xl(2)-xl(1));  hw = 0.016 * (yl(2)-yl(1));
sx = hl; sy = hw;
tipx = x2; tipy = y2;
bx = tipx - u(1)*sx; by = tipy - u(2)*sy;
patch([tipx, bx + p(1)*sx*0.55, bx - p(1)*sx*0.55], ...
      [tipy, by + p(2)*sy*0.55, by - p(2)*sy*0.55], col, 'EdgeColor', col);
end
