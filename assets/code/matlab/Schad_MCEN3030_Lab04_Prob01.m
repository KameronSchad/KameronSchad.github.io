%% Part a)

clc, clear, close all

format shortG

A = [ 0.707  1  0  0      0      0  0  0      0      0  0  0       0;       % 1
     -0.707  0  1  0      0      0  0  0      0      0  0  0       0;       % 2
      0.7071 0  0  1      0      0  0  0      0      0  0  0       0;       % 3
      0     -1  0  0      0.659  1  0  0      0      0  0  0       0;       % 4
      0      0  0 -1     -0.753  0  0  0      0      0  0  0       0;       % 5
      0      0 -1  0     -0.659  0  1  0      0      0  0  0       0;       % 6
      0      0  0  0      0.753  0  0  1      0      0  0  0       0;       % 7
      0      0  0  0      0     -1  0  0      0.659  1  0  0       0;       % 8
      0      0  0  0      0      0  0  0      0.753  0  0  1       0;       % 9
      0      0  0  0      0      0  0 -1     -0.753  0  0  0       0;       % 10
      0      0  0  0      0      0 -1  0     -0.659  0  1  0       0;       % 11
      0      0  0  0      0      0  0  0      0     -1  0  0       0.707;   % 12
      0      0  0  0      0      0  0  0      0      0  0 -1      -0.7071]; % 13

b = [0;     % 1
     3000;  % 2
    -6229;  % 3
     0;     % 4
     600;   % 5
     0;     % 6
     0;     % 7
     0;     % 8
     2429;  % 9
     800;   % 10
     0;     % 11
     0;     % 12
     600];  % 13


% Gaussian Elimination
ab = [A b];
[R,C] = size(ab);

    % Forward Elimination
    for j = 1:R-1
        for i = j+1:R
            ab(i,:) = ab(i,:) - ab(i,j)/ab(j,j)*ab(j,:);
        end
    end

    % Back Substitution
    F = zeros(R,1);
    
    F(R) = ab(R,C) / ab(R,R);
    
    for i = R-1:-1:1
        F(i) = (ab(i,C) - ab(i,i+1:R)*F(i+1:R)) / ab(i,i);
    end

F

% Pivoting is not necessary

%% Part b)

F_Matlab = A\b

%% Part c)

% Member 1  - compression
% Member 2  - tension
% Member 3  - tension
% Member 4  - compression
% Member 5  - tension
% Member 6  - tension
% Member 7  - tension
% Member 8  - compression
% Member 9  - tension
% Member 10 - compression
% Member 11 - tension
% Member 12 - tension
% Member 13 - compression