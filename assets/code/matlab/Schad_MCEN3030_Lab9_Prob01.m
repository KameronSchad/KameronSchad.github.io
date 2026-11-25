%% Part a)

clc, clear, close all

format shortG

% Initial Conditions and Parameters
m = 80;
g = 9.81;
rho = 1.225;
v0 = 0;
y0 = 0;

% Freefall
Cd1 = 1.0;
A1 = 0.70;

% Parachute Deployed (Spectre-135)
Cd2 = 1.3;
A2 = 12.54;

% Times from Problem 0
t0 = 0;
tStart = 15;
tDeploy = 18;
tf = 132;

% Number of Intervals
N = 13200;
h = (tf - t0) / N;
t = t0:h:tf;

% Preallocating
v = 0*t;
y = 0*t;
CdA = 0*t;
D = 0*t;

v(1) = v0;
y(1) = y0;


%% Part d)

% Explicit Euler Method
for i = 1:N

    % Effective Drag Area
    if t(i) < tStart
        CdA(i) = Cd1*A1;

    elseif t(i) < tDeploy
        CdA(i) = Cd1*A1 + (Cd2*A2 - Cd1*A1)*(t(i) - tStart)/(tDeploy - tStart);

    else
        CdA(i) = Cd2*A2;
    end

    % Drag Constant
    c = 0.5*rho*CdA(i);

    % Differential Equation of Motion
    slope = -g - (c/m)*v(i)*abs(v(i));

    % Explicit Euler Method
    v(i+1) = v(i) + slope*h;

    % Vertical Displacement
    y(i+1) = y(i) + v(i)*h;

end

CdA(end) = Cd2*A2;

% Plotting
figure
plot(t,v,'-b')

xlabel('Time (s)')
ylabel('Vertical Velocity (m/s)')
title('Vertical Velocity vs. Time')
grid on


%% Part e)

% Final Landing Speed
landingSpeed = abs(v(end))
landingSpeedMph = landingSpeed*2.23694


%% Part f)

% Drag Force
for i = 1:length(t)
    D(i) = 0.5*rho*CdA(i)*v(i)^2;
end

landingDrag = D(end)
maxDrag = max(D)

% Plotting
figure
plot(t,D,'-r')

xlabel('Time (s)')
ylabel('Drag Force (N)')
title('Drag Force vs. Time')
grid on


%% Part h)

% Initial Height from Numerical Integration
H0 = -y(end);
height = H0 + y;

H0
H0ft = H0*3.28084

% Plotting
figure
plot(t,height,'-g')

xlabel('Time (s)')
ylabel('Height Above Ground (m)')
title('Height vs. Time')
grid on
