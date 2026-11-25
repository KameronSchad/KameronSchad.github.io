%% Part c)

clc, clear, close all

format shortG;

% Stress Matrix (MPa)
A = [-4.725    0.5628  -3.106;
     0.5628   -3.838    1.915;
    -3.106     1.915   -5.762];

maxerr = 1e-6;
error = 1;

guess = [1;
         1;
         1];

% Power Method (Largest Absolute Eigenvalue)
[lamres,uv3] = powerm(A,guess,error,maxerr);

lambda3 = lamres;

% Inverse Power Method (Smallest Absolute Eigenvalue)
B = inv(A);

[lamres,uv1] = powerm(B,guess,error,maxerr);

lambda1 = 1 / lamres;

% Shifted Inverse Power Method (Middle Eigenvalue)
shift = -3.5;
C = inv(A - shift * eye(3));

[lamres,uv2] = powerm(C,guess,error,maxerr);

lambda2 = shift + 1 / lamres;

% Eigenvalues and Eigenvectors
eigenvalues = [lambda1;
               lambda2;
               lambda3]

eigenvectors = [uv1 uv2 uv3]

function [lambdag,ug] = powerm(A,ug,errtype,maxerr)
    error = 1;
    lambdag = 0;

    while error > maxerr
        p = A * ug;
        lambda = norm(p);
        unew = p / lambda;
    
        % Sign Modification
        if unew' * ug < -0.5
            lambda = -lambda;
            unew = -unew;
        end
    
        errorlam = abs((lambda - lambdag) / lambda);
        erroruve = norm(unew - ug) / norm(unew);
    
        if errtype == 1
            error = erroruve;
        end
    
        if errtype == 2
            error = errorlam;
        end
    
        ug = unew;
        lambdag = lambda;
    end
end

%% Part d)

% Von Mises Stress
vonMises = sqrt(((lambda1 - lambda2)^2 + (lambda2 - lambda3)^2 + (lambda3 - lambda1)^2) / 2)

%% Part e)

% Safety Factor
Yield = 620.422;    % MPa
safetyFactor = Yield / vonMises

%% Part f)

figure

plot3([0 uv1(1)],[0 uv1(2)],[0 uv1(3)],'r','LineWidth',2)
hold on
plot3([0 uv2(1)],[0 uv2(2)],[0 uv2(3)],'g','LineWidth',2)
plot3([0 uv3(1)],[0 uv3(2)],[0 uv3(3)],'b','LineWidth',2)
hold off

grid on
axis equal
xlabel('X')
ylabel('Y')
zlabel('Z')
title('Eigenvectors of Stress Matrix')
legend('Eigenvector 1','Eigenvector 2','Eigenvector 3')
view(45,30)

%% Part g)

% Eigenvector Dot Products
dot12 = uv1' * uv2;
dot13 = uv1' * uv3;
dot23 = uv2' * uv3;

% Orthogonality Matrix
Q = [uv1 uv2 uv3];

format short

QTQ = Q' * Q

format shortG

%% Part h)

% Diagonal Eigenvalue Matrix
D = diag(eigenvalues);

% Reconstructed Stress Matrix
Acheck = Q * D * Q'

%% Part i)

[V,D] = eig(A);
V
D

%% Part j)

% The eigenvalues calculated using the power methods were compared with 
% the principal stresses obtained from SolidWorks Simulation. The 
% calculated eigenvalues were -1.6971 MPa, -3.5838 MPa, and -9.0441 MPa,
% while SolidWorks reported -1.697 MPa, -3.584 MPa, and -9.044 MPa, 
% respectively. The results showed agreement, with minor differences
% attributed to rounding.

%% Part k)

% The von Mises stress calculated using the eigenvalues was 6.6087 MPa, 
% while SolidWorks Simulation reported 6.609 MPa. The results showed 
% agreement, with the small difference attributed to rounding. This 
% confirms the accuracy of the calculated von Mises stress.