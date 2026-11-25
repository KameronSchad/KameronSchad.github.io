%% Part a)
clc, clear, close all

function val = G1(f)
    Q = 5e-3; %e/D
    Re = 2e5; %Reynolds Number

    val = (1 / (-2 * log10((Q / 3.7) + (2.51 / (Re * sqrt(f)))))) ^ 2;
end

errorMax = 1e-4;
error = 1;
guess = 0.2;

while error >= errorMax
    New = G1(guess);

    error = abs((New - guess) / New);

    guess = New;
end

solution1 = guess

%% Part b)

function val = G2(f)
Q = 1e-4; %e/D
Re = 5e6; %Reynolds Number

val = (1 / (-2 * log10((Q / 3.7) + (2.51 / (Re * sqrt(f)))))) ^ 2;
end

errorMax = 1e-4;
error = 1;
guess = 0.2;

while error >= errorMax
    New = G2(guess);

    error = abs((New - guess) / New);

    guess = New;
end

solution2 = guess

%% Part c)

function val = G3(f)
Q = 5e-5; %e/D
Re = 7e7; %Reynolds Number

val = (1 / (-2 * log10((Q / 3.7) + (2.51 / (Re * sqrt(f)))))) ^ 2;
end

errorMax = 1e-4;
error = 1;
guess = 0.2;

while error >= errorMax
    New = G3(guess);

    error = abs((New - guess) / New);

    guess = New;
end

solution3 = guess


%% Part d)

function val = F1(f)
    Q = 5e-3;
    Re = 2e5;

    val = 1/sqrt(f) + 2*log10((Q/3.7) + (2.51/(Re*sqrt(f))));
end
function val = F2(f)
    Q = 1e-4;
    Re = 5e6;
    
    val = 1/sqrt(f) + 2*log10((Q/3.7) + (2.51/(Re*sqrt(f))));
end
function val = F3(f)
    Q = 5e-5;
    Re = 7e7;
    
    val = 1/sqrt(f) + 2*log10((Q/3.7) + (2.51/(Re*sqrt(f))));
end

guess = 0.02;

fzero1 = fzero(@F1, guess)
fzero2 = fzero(@F2, guess)
fzero3 = fzero(@F3, guess)

%% Part e)

%   From the Moody diagram, the friction factors are approximately 0.031,
%   0.012, and 0.011 for parts a, b, and c, respectively. These values
%   agree closely with the results from the fixed-point iteration and
%   fzero methods. The small differences are expected because the Moody
%   diagram only allows the values to be estimated graphically.