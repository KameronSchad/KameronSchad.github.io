%% Part b)

clc, clear, close all

format shortG

% Fourier Series Approximation
a = 0;
b = 6;
L = (b - a) / 2;
dx = (b - a) / 1000;
x = a:dx:b;
terms = 10;

for i = 1:length(x)
    sum = 4;

    for k = 1:terms
        Amp(k) = 0;
        Bmp(k) = -18 * (1 - cos(2 * pi * k / 3)) / (pi^2 * k^2);

        term(i,k) = Amp(k) * sin(pi * k * x(i) / L) + Bmp(k) * cos(pi * k * x(i) / L);

        sum = sum + term(i,k);
    end

    y(i) = sum;
end


%% Part c)

% Original Piecewise Function
for i = 1:length(x)
    if x(i) < 2
        f(i) = 3*x(i);
    elseif x(i) < 4
        f(i) = 6;
    else
        f(i) = 18 - 3*x(i);
    end
end

% Fourier Series for 100 and 200 Terms
Nvalues = [100 200];

for j = 1:length(Nvalues)
    for i = 1:length(x)
        sum = 4;

        for k = 1:Nvalues(j)
            Amp(k) = 0;
            Bmp(k) = -18 * (1 - cos(2*pi*k/3)) / (pi^2*k^2);

            sum = sum + Amp(k)*sin(pi*k*x(i)/L) + Bmp(k)*cos(pi*k*x(i)/L);
        end

        yMore(i,j) = sum;
    end
end

% Plotting
figure
plot(x,y,'-b')
hold on
plot(x,yMore(:,1),'-r')
plot(x,yMore(:,2),'-g')
plot(x,f,'-k','LineWidth',2)
hold off

xlabel('x')
ylabel('f(x)')
title('Fourier Series Approximation')
legend('N = 10','N = 100','N = 200','Original Function')
grid on

% Increasing the number of terms improves the approximation,
% especially near x = 2 and x = 4 where the slope changes.
% Unlike Problem 1, the function is continuous, so there is
% no Gibbs overshoot associated with a jump discontinuity.


%% Part d)

% Amplitude and Spatial Frequency for N = 10
N = 10;

% Constant Component
frequency(1) = 0;
amplitude(1) = 4;

% Harmonic Components
for k = 1:N
    frequency(k+1) = k / (2*L);
    amplitude(k+1) = sqrt(Amp(k)^2 + Bmp(k)^2);
end

% Plotting
figure
stem(frequency,amplitude)

xlabel('Spatial Frequency (cycles/unit x)')
ylabel('Amplitude')
title('Amplitude vs. Spatial Frequency (N = 10)')
grid on

% The largest amplitude is the constant component at frequency 0.
% The largest oscillatory amplitude occurs at the fundamental
% frequency of 1/6 cycles/unit x. Every third harmonic has zero
% amplitude due to the cosine coefficient becoming zero.


%% Part e)

% Plot First 4 Fourier Terms
figure
plot(x,y,'-k','LineWidth',2)
hold on

for k = 1:4
    plot(x,term(:,k))
end

hold off

xlabel('x')
ylabel('f(x)')
title('First 4 Fourier Terms (N = 10)')
legend('N = 10 Approximation','Term 1','Term 2','Term 3','Term 4')
grid on

% The first harmonic has the largest amplitude of the four terms.
% Higher harmonics generally have smaller amplitudes and higher
% frequencies. The third harmonic has zero amplitude.
% Together, these terms contribute to the overall approximation.