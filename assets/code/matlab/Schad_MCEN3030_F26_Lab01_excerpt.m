% Student-authored problem sections from the original lab file.
% Course-provided examples omitted.
%% Problem 3
clc, clear, close all

Number = 643; %Input Number

%Find sign
if Number > 0
    numberSign = 0;
elseif Number < 0
    numberSign = 1;
    Number = abs(Number)
elseif Number == 0;
    doublePrecisionFormat = [0]
    return
end

%Calculate mantissa
j = 0;
while Number >= 2
    j = j + 1;
    a(j) = mod(Number, 2);
    Number = floor(Number/2);
end   
mantissaZeros = zeros(1, 52-numel(a));
mantissa = [fliplr(a) mantissaZeros];

%Calculate bias and exponent
exponent = j;
bias = exponent + 1023;
k = 0;
while bias >= 2
    k = k + 1;
    b(k) = mod(bias, 2);
    bias = floor(bias/2);
end
biasZeros = zeros(1, 10-numel(b));
biasVector = [bias fliplr(b) biasZeros];

%Final Vector
doublePrecisionFormat = [numberSign biasVector mantissa]
%% Problem 4
clc, clear, close all

%Define Terms
Terms = [5 10 15 20];
x = linspace(0, 4*pi(), 1000); %1000 steps between 0 and 4 PI
sum = zeros(4, numel(x));

%Calculate terms
i = 1;
while i <= 4
    k = 1;
    while k <= numel(x)
        j = 0;
        while j < Terms(i)
            term = (-1)^(j)*x(k)^(2*j)/factorial(2*j); %cos
            sum(i,k) = term + sum(i,k);
            j = j + 1;
        end
        k = k + 1;
    end
    i = i + 1;
end

%Plotting graphs
plot(x, sum(1,:))
hold on
plot(x, sum(2,:))
plot(x, sum(3,:))
plot(x, sum(4,:))
hold off

ylim([-10 10])
legend('5 Terms','10 Terms','15 Terms','20 Terms')

%Calculating error
xError = 2*pi();
i = 1;
while i <= 4
    j = 0;
    errorSum = 0;

    while j < Terms(i)
        term = (-1)^j*xError^(2*j)/factorial(2*j);
        errorSum = term + errorSum;
        j = j + 1;
    end

    truncationError(i) = abs(cos(xError) - errorSum);
    i = i + 1;
end

format short e
truncationError