%% Part a)

clc, clear, close all

format shortG

% Initial Guess
x = 1;
y = 1;

% Function Values
f1 = y - 0.5*(exp(x/2) + exp(-x/2))
f2 = 9*x^2 + 25*y^2 - 225


%% Part b)

% Step Size
h = 0.0001;

% Original Function Values
F = [f1; f2];

% Function Values at x + h
Fx = [y - 0.5*(exp((x+h)/2) + exp(-(x+h)/2));
    9*(x+h)^2 + 25*y^2 - 225];

% Function Values at y + h
Fy = [(y+h) - 0.5*(exp(x/2) + exp(-x/2));
    9*x^2 + 25*(y+h)^2 - 225];

% Jacobian Matrix
J = [(Fx-F)/h (Fy-F)/h]


%% Part c)

% Newton's Method
for i = 1:20

    % Function Values
    F = [y - 0.5*(exp(x/2) + exp(-x/2));
        9*x^2 + 25*y^2 - 225];

    % Function Values at x + h
    Fx = [y - 0.5*(exp((x+h)/2) + exp(-(x+h)/2));
        9*(x+h)^2 + 25*y^2 - 225];

    % Function Values at y + h
    Fy = [(y+h) - 0.5*(exp(x/2) + exp(-x/2));
        9*x^2 + 25*(y+h)^2 - 225];

    % Jacobian Matrix
    J = [(Fx-F)/h (Fy-F)/h];

    % Newton's Method
    delta = J\(-F);

    x = x + delta(1);
    y = y + delta(2);

    % Convergence Check
    if max(abs(delta)) < 0.000001
        break
    end

end

% Results
x
y
iterations = i