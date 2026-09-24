function fig04_map_rsrp()
%FIG04  The same corridor, banded by serving RSRP, with ping-pong handovers,
%   over an OpenStreetMap background.
%   Discrete bands rather than a continuous colourbar: a scaled colour axis
%   and a true-colour raster cannot share one renderer palette, and bands
%   read better at projector distance anyway.
%   Map data (c) OpenStreetMap contributors, ODbL.
S = fig_style();
% the map is portrait, so it lands small on a landscape slide: scale the type up
S.fs_axis = 22; S.fs_lab = 24; S.fs_ann = 21; S.fs_leg = 19;
R = readnum('map_route.csv');
H = readnum('map_handovers.csv');
E = readnum('basemap_extent.txt');
lat0 = E(1); lon0 = E(2);

newfig(820, 1060);
[xl, yl] = basemap(0.45);          % faded, so the RSRP bands read clearly
hold on;

[rx, ry] = merckm(R(:,3), R(:,4), lat0, lon0);
[hx, hy] = merckm(H(:,2), H(:,3), lat0, lon0);
rsrp = R(:,5);
pp = H(:,4) == 1;

% viridis, sampled at five levels; dark end = weak signal
edges = [-Inf -105 -95 -85 -75 Inf];
cols  = [0.267 0.005 0.329;
         0.229 0.322 0.545;
         0.128 0.567 0.551;
         0.369 0.789 0.383;
         0.780 0.760 0.110];
names = {'RSRP < -105 dBm', '-105 to -95', '-95 to -85', '-85 to -75', 'RSRP \geq -75 dBm'};

hb = zeros(1,5); keep = true(1,5);
for k = 1:5
    m = rsrp >= edges(k) & rsrp < edges(k+1);
    if ~any(m), keep(k) = false; hb(k) = plot(NaN, NaN, '.'); continue; end
    hb(k) = plot(rx(m), ry(m), '.', 'Color', cols(k,:), 'MarkerSize', 13);
end

h1 = plot(hx(~pp), hy(~pp), 'o', 'MarkerSize', 3.4, 'MarkerEdgeColor', [0.12 0.12 0.12], 'LineWidth', 0.7);
h2 = plot(hx(pp),  hy(pp),  'o', 'MarkerSize', 6.2, 'MarkerEdgeColor', S.maroon, ...
          'MarkerFaceColor', S.maroon, 'LineWidth', 0.8);

axis equal; xlim(xl); ylim(yl); box on;
set(gca, 'XColor', S.ink, 'YColor', S.ink, 'Layer', 'top');
xlabel('East of corridor centre  (km)', 'FontSize', S.fs_lab, 'Color', S.ink);
ylabel('North of corridor centre  (km)', 'FontSize', S.fs_lab, 'Color', S.ink);

% A drawn key rather than legend(): the renderer gives legend boxes no opaque
% backing, and at this type size a seven-row legend covers the corridor.
keyx = 2.75; keyw = 6.30; keytop = -1.55; dy = 0.80;
rows = [names(keep), {'handover  (546)', 'ping-pong  (215, 28.3%)'}];
nrow = numel(rows);
keybot = keytop - nrow*dy - 0.20;
patch([keyx keyx+keyw keyx+keyw keyx], [keytop keytop keybot keybot], [1 1 1], ...
      'EdgeColor', [0.68 0.68 0.68], 'LineWidth', 1.0);
kc = cols(keep, :);
for k = 1:nrow
    yy = keytop - 0.55 - (k-1)*dy;
    if k <= size(kc,1)
        plot(keyx+0.45, yy, '.', 'Color', kc(k,:), 'MarkerSize', 34);
    elseif k == nrow-1
        plot(keyx+0.45, yy, 'o', 'MarkerSize', 6, 'MarkerEdgeColor', [0.12 0.12 0.12], 'LineWidth', 1.2);
    else
        plot(keyx+0.45, yy, 'o', 'MarkerSize', 11, 'MarkerEdgeColor', S.maroon, ...
             'MarkerFaceColor', S.maroon, 'LineWidth', 1.2);
    end
    text(keyx+0.95, yy, rows{k}, 'FontSize', S.fs_leg, 'Color', S.ink, ...
         'VerticalAlignment', 'middle');
end

text(xl(2) - 0.15, yl(2) - 0.32, 'Map data \copyright OpenStreetMap contributors', ...
     'FontSize', 16, 'Color', [0.2 0.2 0.2], 'HorizontalAlignment', 'right', ...
     'VerticalAlignment', 'top', 'BackgroundColor', [1 1 1], 'Margin', 2);

savefig_png('fig04_map_rsrp');
end
