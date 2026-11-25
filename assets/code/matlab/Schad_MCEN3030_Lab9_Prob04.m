%% Part a)

clc, clear, close all

format shortG

% Initial Conditions and Parameters
m = 118;
g0 = 9.80665;
Re = 6371000;

% Altitude Above Sea Level
Hvideo = 38969.4;
groundASL = 1042;

% Initial Velocity and Position
wind = 5;
vx0 = wind;
vy0 = 0;
x0 = 0;
y0 = 0;

% Freefall
Cd1 = 1.0;
A1 = 0.70;

% Parachute Deployed (270 ft^2)
Cd2 = 1.6;
A2 = 25.08;

% Times from Video
t0 = 0;
tStart = 260;
tDeploy = 263;
tf = 553;

% Air Density (US Standard Atmosphere)
zTable = 0:5000:40000;
rhoTable = [1.225 0.73643 0.41351 0.19476 0.08891 0.040084 0.018410 0.0084634 0.0039957];

% Initial Altitude Comparison
altitudeRatio = 100*Hvideo/Re
gExit = g0*(Re/(Re + Hvideo))^2

% Time Step
N = 55300;
h = (tf - t0)/N;
t = t0:h:tf;


%% Part d)

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

last = N + 1;

% Explicit Euler Method
for i = 1:N

    % Current Altitude
    z = max(groundASL,Hvideo + y(i));

    % Variable Air Density and Gravity
    rho = interp1(zTable,rhoTable,z);
    g = g0*(Re/(Re + z))^2;

    % Effective Drag Area
    if t(i) < tStart
        CdA(i) = Cd1*A1;

    elseif t(i) < tDeploy
        CdA(i) = Cd1*A1 + (Cd2*A2 - Cd1*A1)*(t(i) - tStart)/(tDeploy - tStart);

    else
        CdA(i) = Cd2*A2;
    end

    % Velocity Relative to Air
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

    % Stop at Ground Level
    if Hvideo + y(i+1) <= groundASL
        last = i + 1;
        break
    end

end

% Remove Unused Time Steps
t = t(1:last);
vx = vx(1:last);
vy = vy(1:last);
x = x(1:last);
y = y(1:last);
CdA = CdA(1:last);

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


%% Part e)

% Drag Force
D = 0*t;

for i = 1:length(t)

    % Variable Air Density
    z = max(groundASL,Hvideo + y(i));
    rho = interp1(zTable,rhoTable,z);

    % Velocity Relative to Air
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


%% Part f)

% Landing Speed
landingSpeed = sqrt(vx(end)^2 + vy(end)^2)
landingSpeedMph = landingSpeed*2.23694

% Maximum Air-Relative Speed
Vrelative = sqrt((vx - wind).^2 + vy.^2);
maxSpeed = max(Vrelative)

% Landing Time Comparison
landingTime = t(end)
timeDifference = landingTime - tf


%% Part g)

% Recorded Altitudes
z0Video = Hvideo;
zDeployVideo = 2566.8;

% Initial Height from Video
H0Video = z0Video - groundASL

% Initial Height Estimated from Deployment
iDeploy = find(t >= tStart,1);

zDeployModel = Hvideo + y(iDeploy)
z0Estimate = zDeployVideo - y(iDeploy)
H0Estimate = z0Estimate - groundASL

% Comparison
heightError = H0Estimate - H0Video
percentError = 100*abs(heightError)/H0Video

% Height for Trajectory
height = max(0,H0Video + y);


%% Part i)

% Horizontal Distance
horizontalDistance = x(end)


%% Part j)

% Trajectory
figure
plot(x,height,'-b')

xlabel('Horizontal Distance (m)')
ylabel('Height Above Ground (m)')
title('Skydiver Trajectory')
grid on
