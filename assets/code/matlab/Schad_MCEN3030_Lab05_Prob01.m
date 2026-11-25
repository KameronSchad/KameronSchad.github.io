%% Part a)

clc, clear, close all

format shortG

C = imread('Lettuce.jpg');

A = C(:,:,3); % Blue channel
image(A)

% Original Image
figure
mesh(A)
view(45,45)

% Singular Value Decomposition
B = double(A);
n = length(B);

[U,S,V] = svd(B);

nmat = [1 5 10 50 100 300];
m = length(nmat);

for i = 1:m
    clear Um Sm Vm

    p = nmat(i);

    Um = U(:,1:p);
    Sm = S(1:p,1:p);
    Vm = V(:,1:p);

    rec(:,:,i) = Um*Sm*Vm';

    np(i) = n*p+p;
end

q = n*n+n;

% Reconstructed Images
figure

for i = 1:m
    subplot(2,3,i)
    mesh(rec(:,:,i))
    view(0,-90)
    title(['Singular Values = ' num2str(nmat(i))])
end

% Matrix Storage Comparison
figure
semilogy(np,'-ob')
hold on
semilogy([1 m],[q q])
hold off

xlabel('Reconstruction')
ylabel('Number of Values')
title('Matrix Storage Comparison')
legend('Reconstructed Image','Original Image')
grid on