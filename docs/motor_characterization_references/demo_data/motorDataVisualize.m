% motorDataVisualize.m
% 
% This script loads the provided motorData csv and plots it for control
% analysis. See section 2 for an example of by-hand characterization
% analysis; section 3 presents an automated method of doing the same, but
% it is incomplete and requires further troubleshooting.
%
% Author: Emily Goldberg
% Date: May 3, 2021
% For: MRD Lab plan B master's project


%% Section 1 - Data processing and plots

%Data specifications - change as appropriate
clear;
file = 'impulse1.csv';
lineFormat1 = 'k.';
lineFormat2 = 'g';
lineFormat3 = 'b-';
savePlots = false;
plotStart = 0; %[s]
inputTime = 2;
plotTime = 5; %[s] 
plotRange = [plotStart inputTime+plotTime];

%--------------------------------------------------------------------------
%Load and clean data
%--------------------------------------------------------------------------
data = load(file);

%If time is 0, data input hasn't started or is already finished
%If it's an NaN row, it's because there was a bad index read and the
%software rejected it
for row = size(data,1):-1:1
    if data(row,1) < 1 || isnan(data(row,1))
        data(row,:) = [];
    end            
end

if min(size(data)) < 1
    disp("Data file empty");
    return;
end

%Unit conversion
time = data(:,1) / 8000;                  %[s]
voltage = data(:,2);                      %[V]
pos = data(:,3) - data(1,3);              %[rev]
vel = data(:,4) * 60;                     %[rpm]
latency = diff(time) * 1000;              %[ms]

rangeVoltage = range(voltage);
rangePos = range(pos);
rangeVel = range(vel);

%--------------------------------------------------------------------------
%Plots
%--------------------------------------------------------------------------
%Input and response
f1 = figure(); f1.Position = [100 150 600 500];
sgtitle(file, 'Interpreter', 'none');

subplot(3,1,1); plot(time,voltage,lineFormat2); hold on; 
plot(time,voltage,lineFormat1); box off;
title('Command Voltage'); 
ylabel('Voltage [V]'); 
xlim(plotRange);
ylim([min(voltage)-0.1*rangeVoltage-0.001,min(voltage)+1.1*rangeVoltage+0.001]);
legend('Interpolation','Recorded sample','Location','southeast');

subplot(3,1,2); plot(time,pos,lineFormat2); hold on;
plot(time,pos,lineFormat1); box off;
title('Response Position'); 
ylabel('Position [rev]');
xlim(plotRange);
ylim([min(pos)-0.1*rangePos,min(pos)+1.1*rangePos]);

subplot(3,1,3); plot(time,vel,lineFormat2); hold on;
plot(time,vel,lineFormat1); box off;
title('Response Velocity'); 
ylabel('Velocity [rpm]'); xlabel('Time [s]');
xlim(plotRange);
ylim([min(vel)-0.1*rangeVel-0.001,min(vel)+1.1*rangeVel+0.001]);

set(gcf,'color','w');

%Latency
f2 = figure(); f2.Position = [750 200 500 350];
str = sprintf('Latency: median %0.1f ms, mean %0.1f ms', median(latency,'omitnan'), mean(latency,'omitnan'));
sgtitle(str)

subplot(2,1,1)
plot(latency,'k.'); box off;
xlim([0 length(latency)])
ylim([0 1.2*max(latency)])
ylabel('Latency [ms]'); xlabel('Observation [#]');

subplot(2,1,2)
histogram(diff(time)*1000, 25, 'FaceColor','k'); box off;
xlim([0 1.2*max(latency)])
ylim([0 length(time)])
xlabel('Latency [ms]'); ylabel('Frequency')

set(gcf,'color','w');

%--------------------------------------------------------------------------
%Save plots
%--------------------------------------------------------------------------
if savePlots
    saveas(f1,sprintf('%s.png',file(1:end-4)))
    saveas(f2,sprintf('%s_latency.png',file(1:end-4)))
end

%% Section 2 - Motor characterization by hand
%Assumes generic DC motor transfer function G(s) = b/(s*(s+1))

%Find steady-state velocity
settleTime = 2.02; %[s] - choose by visual inspection
SSV = mean(vel(time > settleTime)); %[rpm] - steady-state value

%Plot and identify settling time (when it passes and stays within 2% of
%steady-state value)
SSVvals = ones(length(time))*0.98*SSV;
f3 = figure(3); f3.Position = [100 150 600 500];
plot(time,vel,lineFormat1); hold on; 
plot(time, SSVvals, lineFormat3);
title('Observed Velocity'); 
ylabel('Velocity [rpm]'); xlabel('Time [s]');
xlim([1.95 2.1]);
set(gcf,'Color','w'); box off;
legend('Observed','0.98*SSV','Location','southeast')

%Estimate a and b
crossingTime = 2.012; %estimated using plot
Ts = crossingTime - inputTime; %[s] Settling time
a_est = 4 / Ts; %1/time constant
b_est = SSV * a_est; %gain (could also call it K)
s = tf('s');
G_est = b_est / (s*(s+a_est));

%Get simulated step response data
[y_est, t_est] = step(G_est*s); %Simulated velocity step response
Y_est = [0 y_est' y_est(end)];
T_est = [0 t_est'+inputTime time(end)];

%Plot simulated response on top of observed response
f4 = figure(4); f4.Position = [720 150 600 500];
plot(time,vel,lineFormat1); hold on; 
plot(T_est, Y_est, lineFormat3); 
title('Observed vs Predicted Velocity'); 
ylabel('Velocity [rpm]'); xlabel('Time [s]');
xlim([1.95 2.1]);
set(gcf,'Color','w'); box off;
legend('Observed','Simulated','Location','southeast')

%% Section 3 - Automated motor characterization
%INCOMPLETE; this has been written but not confirmed to work with actual
%data. Quick experimental calculations seem to be returning incorrect
%transfer functions; more troubleshooting required.

%Gather velocity, acceleration, and voltage
tDiff = mean(diff(time)); %average timestep in [s]
acc = [0; diff(vel)] / tDiff; %[rev/s^2]
X = [acc vel];
V = voltage;

%Get motor model using time-domain equation (1/b)x_dd+(b/a)x_d = V
C = pinv(X) * V;
b = 1/(C(1));
a = C(2)/b;
G = b/(s*(s+a));

%Simulate velocity step response
[ySim, tSim] = step(G*s);
Y = [0 ySim' ySim(end)];
T = [0 tSim'+inputTime time(end)];

%Plot simulated response on top of observed response
f5 = figure(5); f5.Position = [720 150 600 500];
plot(time,vel,lineFormat1); hold on; 
plot(T, Y, lineFormat2); 
title('Observed vs Predicted Velocity'); 
ylabel('Velocity [rev/s]'); xlabel('Time [s]');
xlim([1.95 2.1]);
set(gcf,'Color','w'); box off;
legend('Observed','Simulated','Location','southeast')

