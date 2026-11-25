%% Part a)

clc, clear, close all

format shortG

% A power function is expected because the gas undergoes an
% approximately reversible adiabatic process.
% The equation is:
%
%   Pabs = C * V^(-k)
%
% where:
%   C is a constant and k is the specific heat ratio (cp/cv).


%% Part b)

% Experimental Data
A = load('03Process.txt');

Pgauge = A(:,1);
volume = A(:,2);

% Absolute Pressure
Pabs = Pgauge + 1;  % atm

% Power Regression
cc = polyfit(log(volume),log(Pabs),1);

k = -cc(1)
C = exp(cc(2))

% Fitted Curve
volumeFit = linspace(min(volume),max(volume),100);
pressureFit = C*volumeFit.^(-k);

figure
plot(volume,Pabs,'bo')
hold on
plot(volumeFit,pressureFit,'--r','LineWidth',2)
hold off

xlabel('Volume (mm^3)')
ylabel('Absolute Pressure (atm)')
title('Absolute Pressure vs. Volume with Power Fit')
legend('Experimental Data','Power Fit','Location','best')
grid on


%% Part c)

% Based on the fitted specific heat ratio of k = 1.1253, the gas is
% most likely propane (C3H8), which has a specific heat ratio of
% k = 1.126 according to Table A-2.