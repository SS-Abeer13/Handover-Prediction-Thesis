function S = fig_style()
%FIG_STYLE  Shared look-and-feel for every defence figure.
%   Institution palette taken from the IUT presentation template:
%   maroon 891313 is the emphasis colour, navy is the neutral data colour.
%   Runs unchanged in MATLAB R2023a and in GNU Octave.

S.maroon  = [0.537 0.075 0.075];   % #891313  our method / the key finding
S.navy    = [0.122 0.306 0.475];   % #1F4E79  comparator series
S.grey    = [0.55  0.55  0.55];    % context series
S.lgrey   = [0.82  0.82  0.82];    % floors, reference bars
S.amber   = [0.85  0.60  0.00];    % callouts
S.green   = [0.13  0.45  0.27];    % "good" markers
S.ink     = [0.16  0.16  0.16];    % text
S.grid    = [0.90  0.90  0.90];

S.fs_axis  = 15;   % tick labels
S.fs_lab   = 16;   % axis labels
S.fs_ann   = 15;   % on-chart annotation
S.fs_leg   = 14;

set(0,'DefaultAxesFontName','Arial');
set(0,'DefaultTextFontName','Arial');
set(0,'DefaultAxesFontSize',S.fs_axis);
set(0,'DefaultTextFontSize',S.fs_ann);
end
