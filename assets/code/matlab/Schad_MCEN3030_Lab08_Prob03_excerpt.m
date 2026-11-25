% Student analysis excerpt: Parts b–e.
% Textbook demonstration and DFT helper omitted. Requires Engine.txt and a DFT(t,f) helper.
%% Part b)

% Engine Data
A = load('Engine.txt');

tEngine = A(:,2);
fEngine = A(:,3);

% Plotting
figure
plot(tEngine,fEngine,'b')

xlabel('Time (s)')
ylabel('Engine Signal')
title('Engine Signal vs. Time')
grid on

% The engine signal is approximately periodic, with sharp peaks
% occurring roughly every 0.9 to 1.0 seconds. The peak amplitudes
% vary over time, and the signal is not a pure sine wave.


%% Part c)

% Selected Interval for DFT Analysis
NEngine = 500;

tDFT = tEngine(1:2*NEngine);
fDFT = fEngine(1:2*NEngine);

% Sampling Parameters
dtEngine = tDFT(2) - tDFT(1)
tauEngine = 2*NEngine*dtEngine

% The first 1000 data points contain approximately four cycles
% of the engine signal, with peaks spaced about 0.97 seconds apart.
% This interval was selected because the peak spacing is relatively
% consistent compared to the later portion of the data.


%% Part d)

% Discrete Fourier Transform
[kpEngine,AkEngine,BkEngine] = DFT(tDFT,fDFT);

% Amplitude and Frequency
for k = 1:length(kpEngine)
    frequencyEngine(k) = kpEngine(k) / tauEngine;
    amplitudeEngine(k) = sqrt(AkEngine(k)^2 + BkEngine(k)^2);
end

% Plotting
figure
stem(frequencyEngine(2:end),amplitudeEngine(2:end),'ob')

xlabel('Frequency (Hz)')
ylabel('Amplitude')
title('Engine Signal DFT Amplitude Spectrum')
grid on

% The zero-frequency component is excluded from the plot
% because the large average signal value would obscure
% the amplitudes of the oscillating components.


%% Part e)

[maxAmplitude,index] = max(amplitudeEngine(2:end));
maxFrequency = frequencyEngine(index+1);

maxAmplitude
maxFrequency

% The largest overall amplitude is 501.075 at 0 Hz, representing
% the average value of the engine signal.
% Excluding the DC component, the largest amplitude is 15.1655
% at approximately 4.1374 Hz.
% The fundamental frequency is approximately 1.0343 Hz.
% The strongest peak occurs at the fourth harmonic, indicating
% that the engine signal is not a pure sine wave.


