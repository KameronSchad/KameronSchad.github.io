%% Part a)

clc, clear, close all

%Constants
m = 40;   %Mass (kg)
r = 0.3;  %Radius (m)
p = 1030; %Density (kg/m^3)

function val = heightEQ(d)
    %Constants
    m = 40;   %Mass (kg)
    r = 0.3;  %Radius (m)
    p = 1030; %Density (kg/m^3)

    val = (2 * m) / (p * pi() * d^2) + (2 * d) / 3 - 2 * r; %Equation used to solve for d
end

%% Part b)

function val = deriv(d)
    %Constants
    m = 40;   %Mass (kg)
    r = 0.3;  %Radius (m)
    p = 1030; %Density (kg/m^3)

    val = (-4 * m) / (p * pi() * d^3) + 2 / 3; %derivative
end

Guess = 0.3;
tolMax = 1e-4;
tol = 1;

i = 0;
while tol > tolMax  %Newton's Method
    i = i + 1;

    New = Guess - heightEQ(Guess) / deriv(Guess);

    tol = abs((New - Guess) / New);

    resv(i,:) = [i Guess New tol];

    Guess = New;
end

dNewton = New; %d
hNewton = 2*r - dNewton %h
resv

%% Part c)

x0 = 0.3;

dFzero = fzero(@heightEQ, x0); %d

hFzero = 2*r - dFzero %h

%% Part d)

%   The result is possible because the height h (0.3636) is less than twice
%   the radius (0.6). The results agree because both Newton's method and
%   fzero gave the same answer. 