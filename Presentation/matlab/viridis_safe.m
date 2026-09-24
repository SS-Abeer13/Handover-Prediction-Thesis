function c = viridis_safe(n)
%VIRIDIS_SAFE  A perceptually uniform ramp available in MATLAB and Octave.
if nargin < 1, n = 256; end
anchors = [0.267 0.005 0.329; 0.283 0.141 0.458; 0.254 0.265 0.530;
           0.207 0.372 0.553; 0.164 0.471 0.558; 0.128 0.567 0.551;
           0.135 0.659 0.518; 0.267 0.749 0.441; 0.478 0.821 0.318;
           0.741 0.873 0.150; 0.993 0.906 0.144];
x = linspace(0, 1, size(anchors,1));
xi = linspace(0, 1, n);
c = [interp1(x, anchors(:,1), xi)', interp1(x, anchors(:,2), xi)', interp1(x, anchors(:,3), xi)'];
end
