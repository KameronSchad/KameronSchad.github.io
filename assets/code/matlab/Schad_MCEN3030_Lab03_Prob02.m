%% Part a)
clc, clear, close all

function val = G(w)
    m = 2000;   %kg
    k = 160000; %N/m
    c = 30000;  %Ns/m
    R = 0.25;   %X/Y

    val = (1 / c) * sqrt(((w^2 * c + k^2) / R^2) - (k - m * w^2));
end

%% Part b)
errorMax = 1e-4;
error = 1;
guess = 10;

resv(1,:) = [0 guess guess 0];
i = 2;

while error >= errorMax
    New = G(guess);

    error = abs((New - guess) / New);

    resv(i,:) = [i-1 guess New error];

    guess = New;

    i = i + 1;
end

solution = guess
resv

%% Part c)
figure
plot(resv(:,1), resv(:,3), '-o')
xlabel('Iteration')
ylabel('Angular Frequency (rad/s)')
grid on

%% Part d)
w = linspace(0,25,100);

i = 1;
while i <= length(w)
    Gw(i) = G(w(i));
    i = i + 1;
end

figure
plot(w,w)
hold on
plot(w,Gw)

i = 1;
while i <= length(resv(:,1))
    old = resv(i,2);
    new = resv(i,3);

    % Vertical line
    plot([old old],[old new],'r')

    % Horizontal line
    plot([old new],[new new],'r')

    i = i + 1;
end

xlabel('w (rad/s)')
ylabel('G(w)')
legend('y = w','y = G(w)','Iterations')
grid on

%% Part e)

%  The fixed-point iteration converged to an angular frequency of 
%  approximately 21.399 rad/s. The iteration plot shows the solution 
%  approaching a constant value, and the G(w) vs w plot also shows the 
%  iterations converging toward the intersection of the two functions.