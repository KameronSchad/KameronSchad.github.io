%% Part a)

clc, clear, close all

format shortG

% Aluminum Properties
E = 73e9;     % Pa
rho = 2800;   % kg/m^3       %Material: Aluminum Alloy 2014

% Dimensions
D1 = 1 * 0.0254;     % m
D2 = 0.7 * 0.0254;   % m
D3 = 0.9 * 0.0254;   % m
H  = 0.5 * 0.0254;   % m

% Spring Constants
k1 = E * pi * D1^2 / (4 * H);
k2 = E * pi * D2^2 / (4 * H);
k3 = E * pi * D3^2 / (4 * H);

% Coefficient Matrix
A = [k1+k2  -k2       0;
    -k2      k2+k3   -k3;
     0      -k3       k3];

b = [60000;
     40000;
     20000];

% Gaussian Elimination
ab = [A b];
[R,C] = size(ab);

% Forward Elimination
for j = 1:R-1 
     for i = j+1:R
        ab(i,j:C) = ab(i,j:C) - (ab(i,j)/ab(j,j))*ab(j,j:C);
    end
end

% Back Substitution
x = zeros(R,1);

x(R) = ab(R,C)/ab(R,R);

for i = R-1:-1:1
    x(i) = (ab(i,C) - ab(i,i+1:R)*x(i+1:R))/ab(i,i);
end

displacements = x

%% Part b)

% Masses
m1 = rho * pi * D1^2 * H / 4;
m2 = rho * pi * D2^2 * H / 4;
m3 = rho * pi * D3^2 * H / 4;

% Equivalent Masses
m1eq = (m1 + m2) / 3;
m2eq = m2 / 3 + m3 / 3;
m3eq = m3 / 3;

% Eigenvalue Matrix
A = [(k1 + k2) / m1eq  -k2 / m1eq          0;
    -k2 / m2eq         (k2 + k3) / m2eq   -k3 / m2eq;
     0                 -k3 / m3eq          k3 / m3eq];

maxerr = 1e-8;
errtype = 1;

guess = [1;
         1;
         1];

% Power Method (Largest Eigenvalue)
[lamres,uv3] = powerm(A,guess,errtype,maxerr);

lambda3 = lamres;

% Inverse Power Method (Smallest Eigenvalue)
B = inv(A);

[lamres,uv1] = powerm(B,guess,errtype,maxerr);

lambda1 = 1 / lamres;

% Shifted Inverse Power Method (Middle Eigenvalue)
shift = 4e11;
C = inv(A - shift * eye(3));

[lamres,uv2] = powerm(C,guess,errtype,maxerr);

lambda2 = shift + 1 / lamres;

% Natural Frequencies
eigenvalues = [lambda1;
               lambda2;
               lambda3]

naturalFrequencies = (sqrt(eigenvalues) / (2 * pi))


function [lambdag,ug] = powerm(A,ug,errtype,maxerr)
    error = 1;
    lambdag = 0;

    while error > maxerr
        p = A * ug;
        lambda = norm(p);
        unew = p / lambda;

        errorlam = abs((lambda - lambdag) / lambda);
        erroruve = norm(unew - ug) / norm(unew);

        if errtype == 1
            error = erroruve;
        end

        if errtype == 2
            error = errorlam;
        end

        ug = unew;
        lambdag = lambda;
    end
end

%% Part c)

[V,D] = eig(A);
V
D

%% Part e)

% The natural frequencies calculated using the power methods in Part (b) 
% were compared with the eigenvalues obtained using the eig command
% in Part (c). After taking the square root of the eigenvalues and
% dividing by 2pi, the natural frequencies were found to be close enough
% for all three modes. They are within the same order of magnitude.