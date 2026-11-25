%% Part a)

clc, clear, close all

format shortG

% Composite Rectangle Method
a = 0;
b = 1;
N = 10;

h = (b-a) / N;
x = a:h:b;

sum = 0;
for i = 1:N
    sum = sum + fun(x(i));
end

phi_1_a = sum * h


%% Part b)

% Composite Rectangle Method
a = 0;
b = 1;
N = 40;

h = (b-a) / N;
x = a:h:b;

sum = 0;
for i = 1:N
    sum = sum + fun(x(i));
end

phi_1_b = sum * h


%% Part c)

% Composite Simpson's 1/3 Rule
a = 0;
b = 1;
N = 30;

h = (b-a) / N;
x = a:h:b;

sum = fun(x(1)) + fun(x(N+1));

% Coefficients of 4
for i = 2:2:N
    sum = sum + 4 * fun(x(i));
end

% Coefficients of 2
for i = 3:2:N-1
    sum = sum + 2 * fun(x(i));
end

phi_1_c = sum * h / 3


%% Part d)

% Composite Simpson's 3/8 Rule
a = 0;
b = 1;
N = 30;

h = (b-a) / N;
x = a:h:b;

sum = fun(x(1)) + fun(x(N+1));

% Coefficients of 3
for i = 2:3:N
    sum = sum + 3 * fun(x(i));
end

for i = 3:3:N
    sum = sum + 3 * fun(x(i));
end

% Coefficients of 2
for i = 4:3:N-2
    sum = sum + 2 * fun(x(i));
end

phi_1_d = sum * 3 * h / 8

% Simpson's 3/8 Rule agrees closely with Simpson's 1/3 Rule
% and is more accurate than the rectangle methods.


%% Part e)

% Reference Value from NIST Table
phiRef = 0.34134;

% Relative Errors
error_a = abs(phi_1_a - phiRef) / phiRef * 100
error_b = abs(phi_1_b - phiRef) / phiRef * 100
error_c = abs(phi_1_c - phiRef) / phiRef * 100
error_d = abs(phi_1_d - phiRef) / phiRef * 100

% Increasing the number of rectangles reduces the relative error.
% Both Simpson's methods are significantly more accurate than the
% rectangle methods, with Simpson's 1/3 Rule having the lowest error.


%% Part f)

% Composite Simpson's 1/3 Rule
z = 0.1:0.1:3.9;
N = 30;

for j = 1:length(z)
    a = 0;
    b = z(j);

    h = (b-a) / N;
    x = a:h:b;

    sum = fun(x(1)) + fun(x(N+1));

    % Coefficients of 4
    for i = 2:2:N
        sum = sum + 4 * fun(x(i));
    end

    % Coefficients of 2
    for i = 3:2:N-1
        sum = sum + 2 * fun(x(i));
    end

    phi_1_f(j) = sum * h / 3;
end

% Results Table: Column 1 = z, Column 2 = Phi(z)
results = [z' phi_1_f']

% Simpson's 1/3 Rule was selected because it produced the lowest
% relative error in Part e). The calculated values agree with the
% NIST reference table to five decimal places.

% Function Definition
function val = fun(x)
    val = 1 / sqrt(2 * pi) * exp(-x^2 / 2);
end