function fig03_map_routes()
%FIG03  Drive-test geography on an OpenStreetMap background, all 4 campaigns.
%   Map data (c) OpenStreetMap contributors, ODbL.
S = fig_style();
S.fs_axis = 12; S.fs_lab = 13; S.fs_ann = 11; S.fs_leg = 10.5;

if exist('map_route_4camp.csv', 'file')
    R = readnum('map_route_4camp.csv');
    H = readnum('map_handovers_4camp.csv');
    use_4camp = true;
else
    R = readnum('map_route.csv');
    H = readnum('map_handovers.csv');
    use_4camp = false;
end

if use_4camp && exist('basemap_extent_4camp.txt', 'file')
    E = readnum('basemap_extent_4camp.txt');
else
    E = readnum('basemap_extent.txt');
end
lat0 = E(1); lon0 = E(2);

newfig(1050, 1380);
[xl, yl] = basemap(0.72, use_4camp);
hold on;

[rx, ry] = merckm(R(:,3), R(:,4), lat0, lon0);
[hx, hy] = merckm(H(:,2), H(:,3), lat0, lon0);

cols = [S.navy; S.amber; S.green; [0.72 0.20 0.20]];
names = {'1st Campaign  (15 drives, 290 HO)', ...
         '2nd Campaign  ( 8 drives, 174 HO)', ...
         '3rd Campaign  (20 drives, 297 HO)', ...
         '4th Campaign  (14 drives, 177 HO)'};

n_caps = max(R(:,1));
for c = 1:n_caps
    m = R(:,1) == c;
    plot(rx(m), ry(m), '-', 'Color', cols(c,:), 'LineWidth', 2.4);
    plot(rx(m), ry(m), '.', 'Color', cols(c,:), 'MarkerSize', 5.5);
end

% Plot handover locations as crisp circles
hho = plot(hx, hy, 'o', 'MarkerSize', 2.8, 'MarkerEdgeColor', [0.15 0.15 0.15], ...
           'MarkerFaceColor', 'none', 'LineWidth', 0.65);

axis equal; xlim(xl); ylim(yl); box on;
set(gca, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
xlabel('East of corridor centre  (km)', 'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('North of corridor centre  (km)', 'FontSize', S.fs_lab, 'Color', S.ink);

% Compact legend placed in the open Southeast quadrant (clear of all routes)
if use_4camp
    keyx = 4.20; keyw = 10.40; keytop = -1.20; dy = 1.15;
    rows = [names, {'938 signalling handovers'}];
else
    keyx = 1.20; keyw = 7.70; keytop = -3.20; dy = 0.82;
    rows = [names(1:3), {'761 signalling handovers'}];
end

nrow = numel(rows);
keybot = keytop - nrow*dy - 0.25;
patch([keyx keyx+keyw keyx+keyw keyx], [keytop keytop keybot keybot], [1 1 1], ...
      'EdgeColor', [0.65 0.65 0.65], 'LineWidth', 0.9);

for k = 1:nrow
    yy = keytop - 0.70 - (k-1)*dy;
    if k <= n_caps
        plot([keyx+0.35 keyx+1.20], [yy yy], '-', 'Color', cols(k,:), 'LineWidth', 3.8);
    else
        plot(keyx+0.75, yy, 'o', 'MarkerSize', 5.5, 'MarkerEdgeColor', [0.15 0.15 0.15], ...
             'MarkerFaceColor', 'none', 'LineWidth', 1.2);
    end
    text(keyx+1.55, yy, rows{k}, 'FontSize', S.fs_leg, 'Color', S.ink, ...
         'VerticalAlignment', 'middle');
end

text(xl(2) - 0.25, yl(2) - 0.50, 'Map data \copyright OpenStreetMap contributors', ...
     'FontSize', 10.5, 'Color', [0.2 0.2 0.2], 'HorizontalAlignment', 'right', ...
     'VerticalAlignment', 'top', 'BackgroundColor', [1 1 1], 'Margin', 2);

if use_4camp
    mltext(xl(1) + 0.35, yl(1) + 2.5, {'Uttara - Gazipur & Dhaka Corridors', ...
        '57 drives  /  10,220 samples at 1 Hz'}, S.ink, S.fs_ann, 'left', -0.85);
else
    mltext(xl(1) + 0.2, yl(1) + 1.9, {'Uttara - BRAC corridor, Dhaka', ...
        '43 drives  /  7,740 samples at 1 Hz'}, S.ink, S.fs_ann, 'left', -0.62);
end

savefig_png('fig03_map_routes');
end
