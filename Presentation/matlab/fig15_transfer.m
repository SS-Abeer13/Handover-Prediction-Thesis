function fig15_transfer()
%FIG15  Real-to-real transfer holds; the curated export is a different world.
S = fig_style();
M = [0.933 0.895 0.933 0.381;
     0.918 0.914 0.926 0.616;
     0.931 0.883 0.919 0.433;
     0.553 0.652 0.578 0.833];
lab = {'1st Campaign','2nd Campaign','3rd Campaign','curated'};

newfig(1440, 720);

subplot(1,2,1);
imagesc(M, [0.35 0.95]); hold on;
colormap(flipud(bone(256)));
set(gca,'XTick',1:4,'XTickLabel',lab,'YTick',1:4,'YTickLabel',lab, ...
    'XColor',S.ink,'YColor',S.ink,'Layer','top');
xlabel('tested on','FontSize',S.fs_lab,'Color',S.ink);
ylabel('trained on','FontSize',S.fs_lab,'Color',S.ink);
for i=1:4, for j=1:4
    if M(i,j) > 0.72, c = [1 1 1]; else, c = [0.05 0.05 0.05]; end
    text(j, i, sprintf('%.2f', M(i,j)), 'HorizontalAlignment','center', ...
         'FontSize',17,'FontWeight','bold','Color',c,'FontName','Arial');
end, end
plot([3.5 3.5],[0.5 4.5],'-','Color',S.maroon,'LineWidth',2.5);
plot([0.5 4.5],[3.5 3.5],'-','Color',S.maroon,'LineWidth',2.5);
title('AUROC at 1 s, whole drives held out','FontSize',15,'FontWeight','bold','Color',S.ink);

subplot(1,2,2); hold on;
hh = [1 2 3 5];
ours = [0.752 0.745 0.712 0.705];
theirs = [0.745 0.737 0.686 0.708];
hb = bar([ours; theirs]', 1, 'grouped');
set(hb(1),'FaceColor',S.maroon,'EdgeColor','none');
set(hb(2),'FaceColor',S.lgrey,'EdgeColor','none');
set(gca,'XTick',1:4,'XTickLabel',{'1 s','2 s','3 s','5 s'}, ...
    'XColor',S.ink,'YColor',S.ink,'Layer','top');
grid on; set(gca,'GridColor',S.grid,'GridAlpha',1,'YGrid','on','XGrid','off');
ylabel('AUROC on the public dataset','FontSize',S.fs_lab,'Color',S.ink);
ylim([0.5 0.86]);
lg = legend(hb,{'ours, never trained on it','trained on that dataset'}, ...
    'Location','north','FontSize',12.5); legend boxoff; set(lg,'TextColor',S.ink);
ylim([0.5 0.95]);
mltext(4.45, 0.855, {'matches or beats the dataset''s own', 'in-domain ceiling at 3 of 4 horizons'}, ...
    S.maroon, 13, 'right', -0.019);
title('External validation, independent dataset','FontSize',15,'FontWeight','bold','Color',S.ink);
savefig_png('fig15_transfer');
end
