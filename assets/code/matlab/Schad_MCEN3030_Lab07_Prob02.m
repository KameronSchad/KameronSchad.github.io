%% Part a)

clc, clear, close all

format shortG

% Tensile Test Data
A = load('01Tensile.txt');

% Stress and Strain
strain = A(:,3) / 25.4;
stress = A(:,4) / (4 * 12.5); 

% Assume the 15 mm width shown in Lab 7 is a typo. A width of
% 12.5 mm is used to remain consistent with Lab 6.

% Two-Point Central Difference
n = length(strain);

for i = 2:n-1
    der(i) = (stress(i+1) - stress(i-1)) / (strain(i+1) - strain(i-1));
end

% Average Modulus in Elastic Region
E = mean(der(5:22)) / 1000  % GPa

% Comparison with Lab 6 and Textbook
ELab6 = 74.127;      % GPa
Etextbook = 69;      % GPa

errorLab6 = abs(E - ELab6) / ELab6 * 100             % Percent
errorTextbook = abs(E - Etextbook) / Etextbook * 100 % Percent

% The numerical derivative gives a modulus of approximately 74.09 GPa,
% which closely agrees with the 74.127 GPa obtained in Lab 6.
% The textbook value for aluminum is 69 GPa, giving a difference
% of approximately 7.37%. This difference may be due to experimental
% uncertainty, material variations, and measurement noise.

% Reference:
% Callister, W. D., and Rethwisch, D. G., Materials Science and
% Engineering: An Introduction, 8th ed., Wiley, 2010, Table 6.1.


%% Part b)

% Results from Lab 6
Efit = 74127;        % MPa
yieldStress = 245.7; % MPa

% Elastic Strain at Yield
elasticStrain = yieldStress / Efit;

% Resilience (Triangular Approximation)
resilience = 0.5 * yieldStress * elasticStrain  % MJ/m^3


%% Part c)

% Experimental Data in Elastic Region
strainElastic = [0; strain(1:33)];
stressElastic = [0; stress(1:33)];

% Resilience Using Trapezoidal Integration
resilienceTrapz = trapz(strainElastic,stressElastic)  % MJ/m^3

errorResilience = abs(resilienceTrapz - resilience) / resilience * 100  % Percent

% The trapezoidal method gives a slightly higher resilience than the
% triangular approximation because the experimental curve is not
% perfectly linear.


%% Part d)

% Toughness Using Trapezoidal Integration
toughness = trapz(strain,stress)  % MJ/m^3

% Comparison with Resilience from Part c)
toughnessRatio = toughness / resilienceTrapz

% Toughness is approximately 16.1 times greater than resilience
% because it includes energy absorbed during plastic deformation.


%% Part e)

% Energy Required to Break Sample
energy = trapz(A(:,2),A(:,4)) / 1000  % J
