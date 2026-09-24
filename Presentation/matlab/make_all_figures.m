%MAKE_ALL_FIGURES  Regenerate every figure in the defence deck.
%   Run from this folder in MATLAB R2023a:   >> make_all_figures
%   PNGs are written to ../png next to this script.
here = fileparts(mfilename('fullpath'));
addpath(here); cd(here);
figs = {'fig01_a3_event','fig02_pipeline','fig03_map_routes','fig04_map_rsrp', ...
        'fig05_dataset','fig06_protocol_audit','fig07_config_timeline', ...
        'fig08_hazard_concept','fig09_protocol_folds','fig10_model_comparison', ...
        'fig11_tuning','fig12_leakage','fig13_hazard_results','fig14_riskcontrol', ...
        'fig15_transfer','fig16_adaptation','fig17_mechanism','fig18_hawkes', ...
        'fig19_conversion','fig20_benefit','fig21_departmental','fig22_negatives'};
fprintf('Regenerating %d figures\n', numel(figs));
for k = 1:numel(figs)
    fprintf('[%2d/%2d] %s\n', k, numel(figs), figs{k});
    feval(figs{k});
end
fprintf('Done. PNGs are in %s\n', fullfile(here,'..','png'));
