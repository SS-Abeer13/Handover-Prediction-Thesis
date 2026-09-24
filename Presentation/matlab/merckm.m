function [x, y] = merckm(lat, lon, lat0, lon0)
%MERCKM  Web Mercator kilometres relative to (lat0, lon0), scaled to true
%   ground distance at lat0. Keeps the drive traces geometrically consistent
%   with the OpenStreetMap basemap, which is itself Web Mercator.
R = 6378.137;
k = cosd(lat0);
mercy = @(p) log(tan(pi/4 + deg2rad(p)/2));
x = R * deg2rad(lon - lon0) * k;
y = R * (mercy(lat) - mercy(lat0)) * k;
end
