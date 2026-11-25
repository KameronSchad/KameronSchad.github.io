%% Part a)

clc, clear, close all

format shortG

A = [-1  0 -0.342  0  0     0  0      0  0      0  0      0  0      0  0      0  0;       % 1
      0  0  0.342  0  1     0  0      0  0      0  0      0  0      0  0      0  0;       % 2
      0  0  0      0 -1     0 -0.7071 0  0      0  0      0  0      0  0      0  0;       % 3
      0  0  0.94   1  0     0  0      0  0      0  0      0  0      0  0      0  0;       % 4
      0 -1 -0.94   0  0     1  0      0  0      0  0      0  0      0  0      0  0;       % 5
      0  0  0     -1  0     0  0.707  1  0      0  0      0  0      0  0      0  0;       % 6
      0  0  0      0  0.707 0  0      0  0.707  0 -0.5   -1  0      0  0      0  0;       % 7
      0  0  0      0  0     1 -0.707  0  0.7071 0  0.866  0  0      0  0      0  0;       % 8
      0  0  0      0  0     0  0      0 -0.707 -1  0      0  0      0  0      0  0;       % 9
      0  0  0      0  0     0  0     -1 -0.707  0  0      0  0      0  0      0  0;       % 10
      0  0  0      0  0     0  0      0  0      1  0.5    0 -0.5   -1  0      0  0;       % 11
      0  0  0      0  0     0  0      0  0      0 -0.866  0 -0.866  0  0      0  0;       % 12
      0  0  0      0  0     0  0      0  0      0  0      1  0.5    0 -0.5   -1  0;       % 13
      0  0  0      0  0     0  0      0  0      0  0      0  0.866  0  0.866  0  0;       % 14
      0  0  0      0  0     0  0      0  0      0  0      0  0      0  0      1  0.5;     % 15
      0  0  0      0  0     0  0      0  0      0  0      0  0      1  0.5    0 -0.5;     % 16
      0  0  0      0  0     0  0      0  0      0  0      0  0      0 -0.866  0 -0.866];  % 17

b = [0;       % 1
    0;       % 2
    0;       % 3
    54000;   % 4
    0;       % 5
    0;       % 6
    0;       % 7
    0;       % 8
    -2000;    % 9
    0;       % 10
    0;       % 11
    5000;    % 12
    0;       % 13
    6000;    % 14
    0;       % 15
    0;       % 16
    0];      % 17

% Gaussian Elimination
ab = [A b];
[R,C] = size(ab);

    % Forward Elimination
    for j = 1:R-1
    
        % Pivoting
        [~,k] = max(abs(ab(j:R,j)));
        k = k + j - 1;
    
        if k ~= j
            temp = ab(j,:);
            ab(j,:) = ab(k,:);
            ab(k,:) = temp;
        end
    
        for i = j+1:R
            ab(i,:) = ab(i,:) - ab(i,j)/ab(j,j)*ab(j,:);
        end
    end

    % Back Substitution
    F_Gauss = zeros(R,1);

    F_Gauss(R) = ab(R,C) / ab(R,R);

    for i = R-1:-1:1
        F_Gauss(i) = (ab(i,C) - ab(i,i+1:R)*F_Gauss(i+1:R)) / ab(i,i);
    end

F_Gauss

% Pivoting is necessary because values of zero are encountered in the
% pivot positions during forward elimination.

%% Part b)

% Gauss-Jordan Elimination

ab = [A b];
[R,C] = size(ab);

for j = 1:R

    % Pivoting
    [~,k] = max(abs(ab(j:R,j)));
    k = k + j - 1;

    if k ~= j
        temp = ab(j,:);
        ab(j,:) = ab(k,:);
        ab(k,:) = temp;
    end

    % Make pivot equal to 1
    ab(j,:) = ab(j,:) / ab(j,j);

    % Eliminate above and below pivot
    for i = 1:R
        if i ~= j
            ab(i,:) = ab(i,:) - ab(i,j)*ab(j,:);
        end
    end
end

F_GaussJordan = zeros(R,1);

for i = 1:R
    F_GaussJordan(i,1) = ab(i,C);
end

F_GaussJordan

%% Part c)

F_Matlab = A\b

%% Part d)

% Member 1  - compression
% Member 2  - tension
% Member 3  - tension
% Member 4  - tension
% Member 5  - compression
% Member 6  - tension
% Member 7  - tension
% Member 8  - tension
% Member 9  - compression
% Member 10 - tension
% Member 11 - compression
% Member 12 - compression
% Member 13 - tension
% Member 14 - tension
% Member 15 - compression
% Member 16 - compression
% Member 17 - tension