function M = readnum(fname)
%READNUM  Read a numeric CSV that may carry a one-line header.
%   Portable across MATLAB and Octave: dlmread is fussy about headers, so the
%   first line is skipped when it does not parse as a row of numbers.
here = fileparts(mfilename('fullpath'));
p = fullfile(here, fname);
if ~exist(p, 'file'), p = fname; end
fid = fopen(p, 'r'); first = fgetl(fid); fclose(fid);
hdr = 0;
v = sscanf(strrep(first, ',', ' '), '%f');
if isempty(v), hdr = 1; end
M = dlmread(p, ',', hdr, 0);
end
