%% Part a)

clc, clear, close all

function val = yDeriv(x)
    %Constants
    E = 210000;   %Young's Modulus (MPa)
    L = 12000;    %Length (mm)
    w0 = 25;      %Load Intensity (N/mm)
    I = 4.545e7;  %Moment of Inertia (mm^4)
    
    %x in (mm)

    val = (w0 / (360 * L * E * I)) * (15*x^4 - 30*L^2*x^2 + 7*L^4);
end

%% Part b)

X = linspace(0, 12000, 10000);

i = 1;
while i <= numel(X)
    Y(i) = yDeriv(X(i));
    i = i + 1;
end

plot (X, Y)
yline(0, 'LineWidth', 2)
grid on
ylim([-0.11 0.1])
xlabel('Position x (mm)')
ylabel('dy/dx')

pause %Wait for approval to continue
close all 
%% Part c)

aBisect = 6000; %Lower bound
bBisect = 7000; %Upper bound
cBisect = (aBisect + bBisect) / 2;
tolBisect = 1;

tolMaxBisect = 1e-4;

j = 0;
while tolBisect > tolMaxBisect
    j = j + 1;

    tolBisect = (bBisect - aBisect) / 2;
    cBisect = (aBisect + bBisect) / 2;

    resvBisect(j,:) = [j aBisect bBisect cBisect tolBisect];

    if yDeriv(aBisect) * yDeriv(cBisect) < 0
        bBisect = cBisect; %Update upper bound
    else
        aBisect = cBisect; %Update lower bound
    end
end

xBisect = cBisect
resvBisect

%% Part d)

function val = yDeriv2(x)
    %Constants
    E = 210000;   %Young's Modulus (MPa)
    L = 12000;    %Length (mm)
    w0 = 25;      %Load Intensity (N/mm)
    I = 4.545e7;  %Moment of Inertia (mm^4)

    val = (w0 / (360 * L * E * I)) * (60*x^3 - 60*L^2*x);
end

xGuess = 6000;
tolNewton = 1;
tolMaxNewton = 1e-4;

k=0
while tolNewton > tolMaxNewton
    k = k + 1;
    
    xNew = xGuess - yDeriv(xGuess) / yDeriv2(xGuess);

    tolNewton = abs((xNew - xGuess) / xNew);

    resvNewton(k,:) = [k xGuess xNew tolNewton];

    xGuess = xNew;

end

xNewton = xNew
resvNewton

%% Part e)

plot(resvBisect(:,1), resvBisect(:,4))
hold on
plot(resvNewton(:,1), resvNewton(:,3))
hold off

xlabel('Number of Iterations')
ylabel('Position of Maximum Beam Deflection (mm)')
legend('Bisect Method','Newton Method')
grid on

%% Part f)

%Constants
E = 210000;   %Young's Modulus (MPa)
L = 12000;    %Length (mm)
w0 = 25;      %Load Intensity (N/mm)
I = 4.545e7;  %Moment of Inertia (mm^4)

maxDeflectionBisect = ((w0 * xBisect) / (360 * L * E * I)) * (3 * xBisect^4 - 10 * L^2 * xBisect^2 + 7 * L^4)  %Maximum Deflection
maxDeflectionNewton = ((w0 * xNewton) / (360 * L * E * I)) * (3 * xNewton^4 - 10 * L^2 * xNewton^2 + 7 * L^4)  %Maximum Deflection

%% Part g)

%   While both options eventually lead you to the same result, generally
%   Newton's method is much quicker. However, Newton's method is only usable
%   when a derivative can be found for the function. HSince this is the case 
%   for this problem, Newton's method is the method that should be chosen.