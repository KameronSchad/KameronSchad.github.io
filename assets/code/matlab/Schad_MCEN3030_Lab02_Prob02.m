%% Part a)

clc, clear, close all

%   Use the Bisection Method to find the rate. This can be done by first 
%   multiplying MPay by the denominator and subtracting the Loan*Rate term, 
%   so the function is set equal to zero. The Bisection Method can then be 
%   used with an upper and lower bound that contain the root. The bounds 
%   are repeatedly reduced until the desired tolerance is reached.

%% Part b)

clc, clear, close all

a_1 = 0.001; %initial lower bound
b_1 = 1;     %initial upper bound
c_1 = (a_1 + b_1)/2;
tol_1 = 1;

maxTol_1 = 1e-6; %Error

function funcValue_1 = func_1(rate_1)
    %Defining Terms
    Loan_1 = 450000;  %Dollars
    Period_1 = 360;   %Months
    MPay_1 = 3000;    %Dollars

    funcValue_1 = MPay_1 * 12 * (1 - (1 / (1 + (rate_1 / 12)) ^ Period_1)) - Loan_1 * rate_1; %Function
end

i_1 = 0;
while tol_1 > maxTol_1
    i_1 = i_1 + 1;

    tol_1 = (b_1 - a_1) / 2;
    c_1 = (a_1 + b_1) / 2;

    resv_1(i_1,:) = [i_1 a_1 b_1 c_1 tol_1];
    
    if func_1(a_1) * func_1(c_1) < 0
        b_1 = c_1;
    else
        a_1 = c_1;
    end
end

rate_1 = c_1
resv_1

%% Part c)

a_2 = 0.001; %initial lower bound
b_2 = 1;     %initial upper bound
c_2 = (a_2 + b_2)/2;
tol_2 = 1;

maxTol_2 = 1e-6; %Error

function funcValue_2 = func_2(rate_2)
%Defining Terms
Loan_2 = 450000;  %Dollars
Period_2 = 240;   %Months
MPay_2 = 3300;    %Dollars

funcValue_2 = MPay_2 * 12 * (1 - (1 / (1 + (rate_2 / 12)) ^ Period_2)) - Loan_2 * rate_2; %Function
end

i_2 = 0;
while tol_2 > maxTol_2
    i_2 = i_2 + 1;

    tol_2 = (b_2 - a_2) / 2;
    c_2 = (a_2 + b_2) / 2;

    resv_2(i_2,:) = [i_2 a_2 b_2 c_2 tol_2];

    if func_2(a_2) * func_2(c_2) < 0
        b_2 = c_2;
    else
        a_2 = c_2;
    end
end

rate_2 = c_2
resv_2

%% Part d)

plot(resv_1(:,1), resv_1(:,4))
hold on
plot(resv_2(:,1), resv_2(:,4))
hold off

xlabel('Number of Iterations')
ylabel('Annual Interest Rate')
legend('30 Years, $3000/month','20 Years, $3300/month')
grid on

%% Part e)

%   The 30 year loan with a monthly payment of $3000 resulted in an annual 
%   interest rate of approximately 7.02%, while the 20 year loan with a 
%   monthly payment of $3300 resulted in a lower annual interest rate of 
%   approximately 6.29%. Based on the annual interest rates, the 20 year 
%   loan should be chosen because it has the lower interest rate.