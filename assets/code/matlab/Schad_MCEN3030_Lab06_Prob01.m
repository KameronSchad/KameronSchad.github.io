%% Part a)

clc, clear, close all

format shortG

% Tensile Test Data
A = load('01Tensile.txt');

time = A(:,1);
crosshead = A(:,2);
extensometer = A(:,3);
force = A(:,4);

% Specimen Dimensions
length = 150;         % mm
lengthGuage = 25.4;   % mm
area = 4*12.5;        % mm^2

% Strain Calculations
strainCrosshead = crosshead / length;
strainExtensometer = extensometer / lengthGuage;

% Stress Calculation
stress = force / area;  % MPa


%% Part b)

figure
plot(strainExtensometer,stress,'b')
xlabel('Strain (mm/mm)')
ylabel('Stress (MPa)')
title('Stress vs. Strain')
grid on

% The linear regression should be performed on the initial straight-line
% portion of the stress-strain curve, corresponding to the elastic region.
% This region occurs before the material begins to yield.

% The selected elastic region is approximately 0.0004 to 0.0025 strain.


%% Part c)

% A linear function is recommended to fit the elastic region of the 
% stress-strain curve. The equation is:

%   stress = a1 * strain + a0

% where:
%   a1 is the slope of the line and represents the modulus of elasticity.
%   a0 is the y-intercept, representing the stress at zero strain.


%% Part d)

% Select Linear Region
x = strainExtensometer(4:23);
y = stress(4:23);

% Linear Regression
cc = polyfit(x,y,1);

a1 = cc(1)
a0 = cc(2)

% Fitted Curve
xFit = linspace(0,0.0035,100);
stressFit = a1*xFit + a0;

% 0.2% Offset Line
xOffset = linspace(0.002,0.006,100);
stressOffset = a1 * (xOffset - 0.002) + a0;

figure
plot(strainExtensometer,stress,'b')
hold on
plot(xFit,stressFit,'--r','LineWidth',2)
plot(xOffset,stressOffset,'--g','LineWidth',2)
hold off

xlabel('Strain (mm/mm)')
ylabel('Stress (MPa)')
title('Stress vs. Strain with Linear Fit and 0.2% Offset')
legend('Experimental Data','Linear Fit','0.2% Offset','Location','best')
%xlim([0 0.007])
ylim([0 300])
grid on


%% Part e)

% Modulus of Elasticity
modulusElasticity = a1 / 1000 % GPa

% Yield Point (estimated graphically using 0.2% offset)
yieldStress = 245.7      % MPa
yieldStrain = 0.00527    % mm/mm


%% Part f)

% Based on the modulus of elasticity and yield stress, the material is 
% most likely an aluminum alloy such as 6061-T6. 