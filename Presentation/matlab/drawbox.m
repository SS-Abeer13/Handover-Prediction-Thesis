function drawbox(x, v, w, fc, ec, S)
%DRAWBOX  One box-and-whisker drawn from primitives, with the sample points
%   overlaid. Octave's boxplot lives in a package that may not be installed,
%   and a hand-drawn box also lets the individual folds stay visible, which is
%   the point of showing a distribution over only eight paired observations.
v = sort(v(:));
q1 = prctile_(v, 25); q2 = prctile_(v, 50); q3 = prctile_(v, 75);
iqr = q3 - q1;
lo = min(v(v >= q1 - 1.5*iqr)); hi = max(v(v <= q3 + 1.5*iqr));
patch([x-w x+w x+w x-w], [q1 q1 q3 q3], fc, 'EdgeColor', ec, 'LineWidth', 1.4);
line([x-w x+w], [q2 q2], 'Color', ec, 'LineWidth', 2.4);
line([x x], [q3 hi], 'Color', ec, 'LineWidth', 1.2);
line([x x], [lo q1], 'Color', ec, 'LineWidth', 1.2);
line([x-w/2 x+w/2], [hi hi], 'Color', ec, 'LineWidth', 1.2);
line([x-w/2 x+w/2], [lo lo], 'Color', ec, 'LineWidth', 1.2);
jit = linspace(-w*0.55, w*0.55, numel(v));
plot(x + jit(randperm(numel(v))), v, 'o', 'MarkerSize', 4.5, ...
     'MarkerFaceColor', ec, 'MarkerEdgeColor', 'none');
end

function q = prctile_(v, p)
v = sort(v(:)); n = numel(v);
idx = (p/100) * (n - 1) + 1;
lo = floor(idx); hi = ceil(idx);
if lo == hi, q = v(lo); else, q = v(lo) + (idx - lo) * (v(hi) - v(lo)); end
end
