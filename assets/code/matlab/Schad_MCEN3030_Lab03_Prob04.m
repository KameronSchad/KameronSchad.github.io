%% Part a)
clc, clear, close all

function val1 = f1(x, y, z) %Row 1 function
    val1 = cos(x) + y^4 + log(z) - 4;
end

function val2 = f2(x, y, z) %Row 2 function
    val2 = 3*x + 2*y - z^3 + 2;
end

function val3 = f3(x, y, z) %Row 3 function
    val3 = x + y + 2*z - 10;
end

function Jacobian = J(x, y, z) %Jacobian
    Jacobian = [-sin(x), 4*y^3,  1/z;
                3,       2,     -3*z^2;
                1,       1,      2];
end

%% Part b)

guess = [1;
         1;
         1];

maxTol = 1e-5;
tol = 1;
i = 2;

resv(1,:) = [1 guess' 1];

while tol >= maxTol
    Jac = J(guess(1), guess(2), guess(3));
    
    functionValues = [f1(guess(1), guess(2), guess(3));
                      f2(guess(1), guess(2), guess(3));
                      f3(guess(1), guess(2), guess(3))];

    New = guess - Jac \ functionValues;

    errorX = abs((New(1) - guess(1)) / New(1));
    errorY = abs((New(2) - guess(2)) / New(2));
    errorZ = abs((New(3) - guess(3)) / New(3));

    tol = max([errorX errorY errorZ]);
    
    resv(i,:) = [i New' tol];

    guess = New;
    i = i + 1;
end

format shortG

solution = guess
resv

%% Part c)

figure
plot(resv(:,1), resv(:,2), '-o')
hold on
plot(resv(:,1), resv(:,3), '-o')
plot(resv(:,1), resv(:,4), '-o')

xlabel('Iteration')
ylabel('Solution Values')
legend('x', 'y', 'z')
grid on

%% Part d)

% All three variables converge to their solutions after approximately
% 6 iterations.