%% Part a)
clc, clear, close all

function valN1 = N1(JH, TH, JC, TC) %Row 1 function Newton
    valN1 = 5.67e-8 * TC^4 + 17.41 * TC - JC - 5000;
end

function valN2 = N2(JH, TH, JC, TC) %Row 2 function Newton
    valN2 = JC - 0.71 * JH + 7.46 * TC - 2300;
end

function valN3 = N3(JH, TH, JC, TC) %Row 3 function Newton
    valN3 = 5.67e-8 * TH^4 + 1.865 * TH - JH - 2500;
end

function valN4 = N4(JH, TH, JC, TC) %Row 4 function Newton
    valN4 = JH - 0.71 * JC + 7.46 * TH - 12000;
end

%% Part b)

function Jacobian = J(JH, TH, JC, TC)
Jacobian = [0,      0,                       -1,     4*5.67e-8*TC^3 + 17.41;
    -0.71,   0,                        1,     7.46;
    -1,      4*5.67e-8*TH^3 + 1.865,   0,     0;
    1,      7.46,                    -0.71,  0];
end

guessN = [5000;  % JH
         300;    % TH
         3000;   % JC
         300];   % TC

maxTol = 1e-4;
tol = 1;
i = 2;

resvN(1,:) = [0 guessN' tol]; %[iteration JH TH JC TC error]

while tol >= maxTol
    Jac = J(guessN(1), guessN(2), guessN(3), guessN(4));

    functionValues = [N1(guessN(1), guessN(2), guessN(3), guessN(4));
                      N2(guessN(1), guessN(2), guessN(3), guessN(4));
                      N3(guessN(1), guessN(2), guessN(3), guessN(4));
                      N4(guessN(1), guessN(2), guessN(3), guessN(4))];

     NewN = guessN - Jac \ functionValues;

     errorJH = abs((NewN(1) - guessN(1)) / NewN(1));
     errorTH = abs((NewN(2) - guessN(2)) / NewN(2));
     errorJC = abs((NewN(3) - guessN(3)) / NewN(3));
     errorTC = abs((NewN(4) - guessN(4)) / NewN(4));

     tol = max([errorJH errorTH errorJC errorTC]);

     resvN(i,:) = [i-1 NewN' tol];

     guessN = NewN;
     i = i + 1;
end

format shortG

solution = guessN
resvN

%% Part d)

function valfFP1 = FP1(JH, TH, JC, TC) %TC
    valfFP1 = ((JC - 17.41 * TC + 5000) / (5.67e-8)) ^ (1/4);
end

function valfFP2 = FP2(JH, TH, JC, TC) %JC
    valfFP2 = 2300 + 0.71 * JH - 7.46 * TC;
end

function valfFP3 = FP3(JH, TH, JC, TC) %JH
    valfFP3 = 12000 + 0.71 * JC - 7.46 * TH;
end

function valfFP4 = FP4(JH, TH, JC, TC) %TH
    valfFP4 = ((JH - 1.865 * TH + 2500) / (5.67e-8)) ^ (1/4);
end

guessFP = [5000; %JH
           300;  %TH
           3000; %JC
           300]; %TC

maxTol = 1e-4;
tol = 1;
i = 2;

resvFP(1,:) = [0 guessFP' tol]; %[iteration JH TH JC TC error]

while tol >= maxTol

    NewFP = [FP3(guessFP(1), guessFP(2), guessFP(3), guessFP(4));
             FP4(guessFP(1), guessFP(2), guessFP(3), guessFP(4));
             FP2(guessFP(1), guessFP(2), guessFP(3), guessFP(4));
             FP1(guessFP(1), guessFP(2), guessFP(3), guessFP(4))];

    errorJH = abs((NewFP(1) - guessFP(1)) / NewFP(1));
    errorTH = abs((NewFP(2) - guessFP(2)) / NewFP(2));
    errorJC = abs((NewFP(3) - guessFP(3)) / NewFP(3));
    errorTC = abs((NewFP(4) - guessFP(4)) / NewFP(4));

    tol = max([errorJH errorTH errorJC errorTC]);

    resvFP(i,:) = [i-1 NewFP' tol];

    guessFP = NewFP;
    i = i + 1;
end

solution = guessFP
resvFP

%% Part e)

% Radiosities
figure
plot(resvN(:,1), resvN(:,2), '-o')
hold on
plot(resvN(:,1), resvN(:,4), '-o')
plot(resvFP(:,1), resvFP(:,2), ':o')
plot(resvFP(:,1), resvFP(:,4), ':o')

xlabel('Iteration')
ylabel('Radiosity (W/m^2)')
title('Radiosity Convergence')
legend('J_H Newton', 'J_C Newton', 'J_H Fixed-Point', 'J_C Fixed-Point')
grid on


% Temperatures
figure
plot(resvN(:,1), resvN(:,3), '-o')
hold on
plot(resvN(:,1), resvN(:,5), '-o')
plot(resvFP(:,1), resvFP(:,3), ':o')
plot(resvFP(:,1), resvFP(:,5), ':o')

xlabel('Iteration')
ylabel('Temperature (K)')
title('Temperature Convergence')
legend('T_H Newton', 'T_C Newton', 'T_H Fixed-Point', 'T_C Fixed-Point')
grid on

%% Part f)

% Both Newton and fixed-point iteration converged to approximately
% the same solution. Newton converged much faster, requiring about
% 6 iterations, while fixed-point iteration required 31 iterations.
% However, Newton requires calculating the Jacobian, while
% fixed-point iteration required solving each equation for a variable.
% Depending on the complexity of the equations, it could be beneficial to
% do either.