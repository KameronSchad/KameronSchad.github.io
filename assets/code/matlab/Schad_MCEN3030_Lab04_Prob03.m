%% Part a)

clc, clear, close all

format shortG

A = [9.5 -2.5  0    -2   0;
    -2.5  11  -3.5   0  -5;
     0   -3.5  15.5  0  -4;
    -2    0    0     7  -3;
     0   -5   -4    -3   12];

b = [10;
    -16;
     20;
     12;
    -30];

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

I_GaussJordan = zeros(R,1);

for i = 1:R
    I_GaussJordan(i,1) = ab(i,C);
end

I_GaussJordan

% Pivoting is not necessary

%% Part b)

% Jacobi Method

guessJ = [1;
         1;
         1;
         1;
         1];

maxerr = 1e-6;
error = 1;
i = 0;

resvJ(1,:) = [i guessJ' error];

while error > maxerr

    i = i + 1;

    Inew = [(10 + 2.5*guessJ(2) + 2*guessJ(4))/9.5;
            (-16 + 2.5*guessJ(1) + 3.5*guessJ(3) + 5*guessJ(5))/11;
            (20 + 3.5*guessJ(2) + 4*guessJ(5))/15.5;
            (12 + 2*guessJ(1) + 3*guessJ(5))/7;
            (-30 + 5*guessJ(2) + 4*guessJ(3) + 3*guessJ(4))/12];

    error = norm(Inew-guessJ,2)/norm(Inew,2);

    resvJ(i+1,:) = [i Inew' error];

    guessJ = Inew;
end

I_Jacobi = Inew
errorJ = error
iterationsJ = i

% Gauss-Seidel Method

guessGS = [1;
          1;
          1;
          1;
          1];

maxerr = 1e-6;
error = 1;
i = 0;

resvGS(1,:) = [i guessGS' error];

while error > maxerr

    i = i + 1;

    Inew(1,1) = (10 + 2.5*guessGS(2) + 2*guessGS(4))/9.5;

    Inew(2,1) = (-16 + 2.5*Inew(1) + 3.5*guessGS(3) ...
        + 5*guessGS(5))/11;

    Inew(3,1) = (20 + 3.5*Inew(2) + 4*guessGS(5))/15.5;

    Inew(4,1) = (12 + 2*Inew(1) + 3*guessGS(5))/7;

    Inew(5,1) = (-30 + 5*Inew(2) + 4*Inew(3) ...
        + 3*Inew(4))/12;

    error = norm(Inew-guessGS,2)/norm(Inew,2);

    resvGS(i+1,:) = [i Inew' error];

    guessGS = Inew;
end

I_GaussSeidel = Inew
errorGS = error
iterationsGS = i

%% Part c)

% Jacobi Method
figure
plot(resvJ(:,1),resvJ(:,2),'-')
hold on
plot(resvJ(:,1),resvJ(:,3),'-')
plot(resvJ(:,1),resvJ(:,4),'-')
plot(resvJ(:,1),resvJ(:,5),'-')
plot(resvJ(:,1),resvJ(:,6),'-')

xlabel('Iteration')
ylabel('Current (A)')
title('Jacobi Method Convergence')
legend('i_1','i_2','i_3','i_4','i_5')
grid on


% Gauss-Seidel Method
figure
plot(resvGS(:,1),resvGS(:,2),'-')
hold on
plot(resvGS(:,1),resvGS(:,3),'-')
plot(resvGS(:,1),resvGS(:,4),'-')
plot(resvGS(:,1),resvGS(:,5),'-')
plot(resvGS(:,1),resvGS(:,6),'-')

xlabel('Iteration')
ylabel('Current (A)')
title('Gauss-Seidel Method Convergence')
legend('i_1','i_2','i_3','i_4','i_5')
grid on

%% Part d)

I_Matlab = A\b