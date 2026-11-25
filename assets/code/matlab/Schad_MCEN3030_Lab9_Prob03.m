%% Part b)

clc, clear, close all

format shortG

% Initial Conditions and Parameters
m = 80;
g = 9.81;
rho = 1.225;

% Wind and Airplane Velocity
wind = 5;
vx0 = 45 + wind;
vy0 = 0;
x0 = 0;
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

% Time Step
N = 13200;
h = (tf - t0) / N;
t = t0:h:tf;

% Preallocating
vx = 0*t;
vy = 0*t;
x = 0*t;
y = 0*t;
CdA = 0*t;

vx(1) = vx0;
vy(1) = vy0;
x(1) = x0;
y(1) = y0;

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

    % Velocity Relative to the Air
    vrx = vx(i) - wind;
    V = sqrt(vrx^2 + vy(i)^2);

    % Differential Equations of Motion
    ax = -(rho*CdA(i)/(2*m))*V*vrx;
    ay = -g - (rho*CdA(i)/(2*m))*V*vy(i);

    % Explicit Euler Method
    vx(i+1) = vx(i) + ax*h;
    vy(i+1) = vy(i) + ay*h;

    % Position
    x(i+1) = x(i) + vx(i)*h;
    y(i+1) = y(i) + vy(i)*h;

end

CdA(end) = Cd2*A2;

% Plotting
figure
plot(t,vx,'-b')
hold on
plot(t,vy,'-r')
hold off

xlabel('Time (s)')
ylabel('Velocity (m/s)')
title('Horizontal and Vertical Velocity vs. Time')
legend('Horizontal','Vertical')
grid on


%% Part c)

% Drag Force
D = 0*t;

for i = 1:length(t)
    vrx = vx(i) - wind;
    V = sqrt(vrx^2 + vy(i)^2);

    D(i) = 0.5*rho*CdA(i)*V^2;
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


%% Part d)

% Final Landing Speed
landingVx = vx(end)
landingVy = vy(end)

landingSpeed = sqrt(vx(end)^2 + vy(end)^2)
landingSpeedMph = landingSpeed*2.23694


%% Part e)

% Initial Height
H0 = -y(end)
H0ft = H0*3.28084;

height = H0 + y;


%% Part g)

% Horizontal Distance
horizontalDistance = x(end)

% Additional Distance Due to Wind
extraDistance = wind*(tf - t0)


%% Part h)

% Trajectory
figure
plot(x,height,'-b')

xlabel('Horizontal Distance (m)')
ylabel('Height Above Ground (m)')
title('Skydiver Trajectory with Wind')
grid on
