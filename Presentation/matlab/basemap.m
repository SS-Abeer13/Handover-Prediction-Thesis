function [xlim_km, ylim_km] = basemap(alpha_val, use_4camp)
%BASEMAP  Draw the OpenStreetMap background for the drive-test figures.
%   The tiles were fetched once from tile.openstreetmap.org (zoom 13) and
%   stored beside this script, so the figure regenerates offline. Coordinates
%   are Web Mercator kilometres relative to the corridor centre, scaled by
%   cos(lat0) so the axes read true ground distance at this latitude.
%   ALPHA_VAL fades the raster toward white by blending the pixels, which is
%   more portable than AlphaData across renderers.
%
%   Map data (c) OpenStreetMap contributors, ODbL.
if nargin < 1, alpha_val = 0.92; end
if nargin < 2, use_4camp = false; end
here = fileparts(mfilename('fullpath'));
if use_4camp && exist(fullfile(here, 'basemap_extent_4camp.txt'), 'file')
    E = readnum('basemap_extent_4camp.txt');
    img_name = 'osm_basemap_crop_4camp.jpg';
else
    E = readnum('basemap_extent.txt');      % lat0, lon0, xw, xe, ys, yn
    img_name = 'osm_basemap_crop.jpg';
end
xw = E(3); xe = E(4); ys = E(5); yn = E(6);
img = double(imread(fullfile(here, img_name)));
img = uint8(255 - alpha_val * (255 - img));
image([xw xe], [yn ys], img);
set(gca, 'YDir', 'normal');
xlim_km = [xw xe]; ylim_km = [ys yn];
end
