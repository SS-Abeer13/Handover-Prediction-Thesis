%MAKE_NEW_FIGURES  Regenerate the twelve figures added in the second figure pass.
%   Run from this folder in MATLAB R2023a or GNU Octave:  >> make_new_figures
%   Every number in these scripts is transcribed from the frozen result tables
%   in pipeline/reports_xcal/tables; none is illustrative.
here = fileparts(mfilename('fullpath'));
addpath(here); cd(here);
figs = {'fig29_fold_dispersion', 'fig30_paired_ece', 'fig31_conformal_coverage', ...
        'fig32_operating_plane', 'fig33_dose_response', 'fig34_forest_hawkes', ...
        'fig35_operating_points', 'fig36_ece_ribbon', 'fig37_pingpong_heatmap', ...
        'fig38_capture_smallmultiples', 'fig39_profile_bubble', 'fig40_signalling_ablation'};
fprintf('Regenerating %d figures\n', numel(figs));
for k = 1:numel(figs)
    fprintf('[%2d/%2d] %s\n', k, numel(figs), figs{k});
    feval(figs{k});
end
fprintf('Done. PNGs are in %s\n', fullfile(here,'png'));
