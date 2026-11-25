%% Part a)

clc, clear, close all

format shortG

A = [1  0  0  1;
     1  1  0  0;
     0  1  1  0;
     0  0  1  1];

b = [1100;
     700;
     400;
    -100];

ab = [A b];
[R,C] = size(ab);

% Gaussian Elimination
for j = 1:R-1
    for i = j+1:R
        ab(i,:) = ab(i,:) - ab(i,j)/ab(j,j)*ab(j,:);
    end
end

ab

% No, the system cannot be solved because Gaussian elimination produces
% a row equivalent to 0 = -900. This is a contradiction, so the system
% of equations is inconsistent and has no solution.

%% Part b)

A = [1  0  0  1;
     1  1  0  0;
     0  1  1  0;
     0  0  0  1];

b = [1100;
     700;
     400;
     400];

ab = [A b];
[R,C] = size(ab);

% Gaussian Elimination
for j = 1:R-1
    for i = j+1:R
        ab(i,:) = ab(i,:) - ab(i,j)/ab(j,j)*ab(j,:);
    end
end

% Back Substitution
n = zeros(R,1);

n(R) = ab(R,C)/ab(R,R);

for i = R-1:-1:1
    n(i) = (ab(i,C) - ab(i,i+1:R)*n(i+1:R))/ab(i,i);
end

n

%% Part c)

% Yes, the city should authorize the event because all of the traffic
% flows from part b are less than 1000 cars per hour.

%% Part d)

A = [1  0  0  1;
    1  1  0  0;
    0  1  1  0;
    0  0  0  1];

b = [1100;
    700;
    400;
    80];

ab = [A b];
[R,C] = size(ab);

% Gaussian Elimination
for j = 1:R-1
    for i = j+1:R
        ab(i,:) = ab(i,:) - ab(i,j)/ab(j,j)*ab(j,:);
    end
end

% Back Substitution
n = zeros(R,1);

n(R) = ab(R,C)/ab(R,R);

for i = R-1:-1:1
    n(i) = (ab(i,C) - ab(i,i+1:R)*n(i+1:R))/ab(i,i);
end

n

% No, the event should not be authorized. Reducing n4 to 80 cars per hour
% results in n1 = 1020 cars per hour, which exceeds the maximum capacity
% of 1000 cars per hour. It also results in n2 = -320 cars per hour,
% which is not possible with the defined one-way traffic direction.