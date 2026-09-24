function fig02_pipeline()
%FIG02  The measurement-to-prediction pipeline, and where each guard sits.
S = fig_style();
newfig(1460, 720); hold on;
axis([0 100 0 54]); axis off;

dbox(1, 38, 19, 12, {'XCAL wide CSV','1 Hz serving RF','GPS  /  speed'}, [0.96 0.96 0.96], [0.4 0.4 0.4], 13);
dbox(1, 20, 19, 12, {'RRC signalling','measConfig  /  reports','HO commands  /  RLF'}, [0.96 0.96 0.96], [0.4 0.4 0.4], 13);

dbox(25, 20, 19, 12, {'Configuration','timeline','from measConfig'}, [1 0.93 0.93], S.maroon, 13, S.maroon);
dbox(25, 38, 19, 12, {'QC  /  drive','segmentation'}, [0.96 0.96 0.96], [0.4 0.4 0.4], 13);

dbox(49, 38, 20, 12, {'Labels','0.5 / 1 / 2 / 3 / 5 s','+ hazard bins'}, [0.93 0.95 0.98], S.navy, 13, S.navy);
dbox(49, 20, 20, 12, {'Features 107','RF  /  mobility','history  /  signalling'}, [0.93 0.95 0.98], S.navy, 13, S.navy);

dbox(74, 29, 24, 13, {'Grouped 5-fold rotation','every drive tested once','models fitted inside the fold'}, [1 0.93 0.93], S.maroon, 13, S.maroon);
dbox(74, 8, 24, 13, {'AUPRC + prevalence floor','ECE  /  FA/hour  /  lead time','conformal risk control'}, [0.96 0.96 0.96], [0.4 0.4 0.4], 13);

darrow(20, 44, 25, 44, [0.4 0.4 0.4]);
darrow(20, 26, 25, 26, [0.4 0.4 0.4]);
darrow(34.5, 32, 34.5, 37.5, [0.4 0.4 0.4]);
darrow(44, 44, 49, 44, [0.4 0.4 0.4]);
darrow(44, 26, 49, 26, [0.4 0.4 0.4]);
darrow(69, 44, 74, 40, S.maroon);
darrow(69, 26, 74, 32, S.maroon);
darrow(86, 29, 86, 21.5, [0.4 0.4 0.4]);

text(50, 2.5, ['Invariants:  grouping is by whole drive, never by row   /   scalers, thresholds ' ...
     'and calibrators fitted inside the fold   /   handover truth from signalling'], ...
     'HorizontalAlignment','center','FontSize',14,'Color',S.maroon,'FontName','Arial');
savefig_png('fig02_pipeline');
end
