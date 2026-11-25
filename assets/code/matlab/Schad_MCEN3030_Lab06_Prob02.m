%% Part a)

clc, clear, close all

format shortG

% An exponential decay function should be used to fit the data. The
% equation is:

%   Tmod = C * exp(-alpha*t)

% where:
%   C is the initial temperature difference and alpha is the
%   cooling rate constant.


%% Part b)

% Cooling Data
A = load('02Cooling.txt');

time = A(:,1);
temperature = A(:,2);

% Room Temperature
Tair = 22;  % Celsius

% Temperature Difference
Tmod = temperature - Tair;


%% Part c)

figure
plot(time,Tmod,'b')
xlabel('Time (s)')
ylabel('Temperature Difference (°C)')
title('Temperature Difference vs. Time')
grid on


%% Part d)

% Exponential Regression
cc = polyfit(time,log(Tmod),1);

alpha = -cc(1)
C = exp(cc(2))

% Fitted Curve
timeFit = linspace(min(time),max(time),100);
TmodFit = C*exp(-alpha*timeFit);

figure
plot(time,Tmod,'b')
hold on
plot(timeFit,TmodFit,'--r','LineWidth',2)
hold off

xlabel('Time (s)')
ylabel('Temperature Difference (°C)')
title('Temperature Difference vs. Time with Exponential Fit')
legend('Experimental Data','Exponential Fit','Location','best')
grid on

%% Part e)

TB = Tair + C*exp(-alpha*time);


%% Part f)

figure
plot(time,temperature,'b')
hold on
plot(time,TB,'--r','LineWidth',2)
hold off

xlabel('Time (s)')
ylabel('Temperature (°C)')
title('Measured vs. Predicted Block Temperature')
legend('Measured Temperature','Predicted Temperature','Location','best')
grid on


%% Part g)

% Estimated Initial Temperature
Te = Tair + C

% Measured Initial Temperature
Tm = temperature(1)

% Error
ri = Tm - Te

% The estimated and measured initial temperatures are not equal.
% The estimated temperature is approximately 4.53°C lower.


%% Part h)

% Given Values
mB = 5;               % kg
CB = 0.897 * 1000;    % J/(kg*K)
AB = 0.30 * 0.40;     % m^2

% Convection Coefficient
h = alpha * mB * CB / AB  % W/(m^2*K)


%% Part i)

% Assumed Handling Temperature
THandling = 40;  % Celsius

% Cooling Time
coolingTime = -log((THandling - Tair) / C) / alpha  % seconds

% A handling temperature of 40°C was assumed since the problem
% does not specify a required safe handling temperature.