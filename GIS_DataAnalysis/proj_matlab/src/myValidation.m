classdef myValidation
    % Evaluation goodness of fit: https://www.mathworks.com/help/curvefit/evaluating-goodness-of-fit.html
    % --- The sum of squares due to error (SSE) 
    % ---  R-square
    % --- Adjusted R-square
    % --- Root mean squared error (RMSE)
    methods(Static)
        function [Fit, RMSE_Fit] = valid_polyfit(datafile, n, isPlot, isSavefig)
            % Extract data from excel file
            %sheet = 1;
            dataRange = 'A2:C500';
            
            dataset = mylib.PrepareData(datafile, dataRange);

            %disp(dataset);

            % generate x and y data
            xdata = [];
            ydata = [];
            for i=1:length(dataset)
                ydata=[ydata; dataset{i, 1}];
                xdata=[xdata; dataset{i, 2}];
            end

            % Fit using polyfit
            order=n;
            [fit,stats,ctr] = polyfit(xdata,ydata,order);
            Fit = polyval(fit,xdata,[],ctr);

            % Calculate RMSE 
            %clc;
            %RMSE_Fit1 = sqrt(mean((yn-Fit1).^2)*length(xn)/gof1.dfe)
            RMSE_Fit = sqrt(mean((ydata-Fit).^2));

            % optimize rmse by removing outlier who is great than 2*RMSE
            xdata_opt = [];
            ydata_opt = [];
            for i=1:length(xdata)
                % remove outlier
                if(sqrt((ydata(i)-Fit(i)).^2) < (RMSE_Fit*1.5))
                    ydata_opt=[ydata_opt; ydata(i)];
                    xdata_opt=[xdata_opt; xdata(i)]; 
                end
            end

            if((length(xdata)-length(xdata_opt))<4)
                % Refit to calculate new estimated_params
                [fit_opt,stats,ctr] = polyfit(xdata_opt,ydata_opt,order);
                Fit_opt = polyval(fit_opt,xdata_opt,[],ctr);

                % recalculate rmse
                RMSE_Fit = sqrt(mean((ydata_opt-Fit_opt).^2));
            else
                RMSE_Fit = 1.0;
            end
            
            % Bad fitting condition, do not plot.
            if(RMSE_Fit < 1.0)           
                % plot figure
                fig = figure;
                if(isPlot==false)
                    set(fig, 'Visible', 'off');
                end
                plot( xdata, ydata, '*',xdata_opt, ydata_opt, 'o', xdata, Fit, '-' );
                ylim([-0.05 1.05]);
                title(strcat('Poly fitting curve: ', datafile));

                %save figure
                if(isSavefig==true)
                    %save figure named by datafile name
                    figname = strcat(datafile, '.png');
                    saveas(fig, figname);
                end 
            end
            
        end
        
       function [Fit, RMSE_Fit] = valid_gaussfit(datafile, isPlot, isSavefig)
            % Extract data from excel file
            %sheet = 1;
            dataRange = 'A2:C500';
            
            dataset = mylib.PrepareData(datafile, dataRange);

            %disp(dataset);

            % generate x and y data
            xdata = [];
            ydata = [];
            for i=1:length(dataset)
                ydata=[ydata; dataset{i, 1}];
                xdata=[xdata; dataset{i, 2}];
            end
            
            % Fit using gaussian function
            [sigma,mu, norm_y] = gaussfit( xdata, ydata );
            
            % Get Fit data;
            Fit = 1/(sqrt(2*pi)* sigma ) * exp( - (xdata-mu).^2 / (2*sigma^2));
            
            % Calculate RMSE 
            %RMSE_Fit = sqrt(mean((ydata-Fit).^2)*length(xdata)/(length(xdata)-2));
            RMSE_Fit = sqrt(mean((ydata-Fit).^2));
            
            % optimize rmse by removing outlier who is great than 2*RMSE
            xdata_opt = [];
            ydata_opt = [];
            for i=1:length(xdata)
                % remove outlier
                if(sqrt((ydata(i)-Fit(i)).^2) < (RMSE_Fit*2))
                    ydata_opt=[ydata_opt; ydata(i)];
                    xdata_opt=[xdata_opt; xdata(i)]; 
                end
            end

            if((length(xdata)-length(xdata_opt))<4)
                % Refit to calculate new estimated_params
                [sigma,mu, norm_y] = gaussfit( xdata_opt, ydata_opt );
                Fit_opt = 1/(sqrt(2*pi)* sigma ) * exp( - (xdata_opt-mu).^2 / (2*sigma^2));

                % recalculate rmse
                RMSE_Fit = sqrt(mean((ydata_opt-Fit_opt).^2));
            else
                RMSE_Fit = 1.0;
            end
  
            % Bad fitting condition, do not plot.
            if(RMSE_Fit < 1.0)
                % plot figure
                fig = figure;
                if(isPlot==false)
                    set(fig, 'Visible', 'off');
                end
                plot( xdata_opt, ydata_opt, '*', xdata_opt, norm_y, 'o', xdata_opt, Fit_opt, '-' );
                ylim([-0.05 1.05]);
                title(strcat('Gaussian fitting curve: ', datafile));

                %save figure
                if(isSavefig==true)
                    %save figure named by datafile name
                    figname = strcat(datafile, '.png');
                    saveas(fig, figname);
                end   
            end
            
       end
        
       function [Fit, RMSE_Fit, Polarity] = valid_sigmfit(datafile, isPlot, isSavefig)
            % Extract data from excel file
            %sheet = 1;
            dataRange = 'A2:C500';
            
            dataset = mylib.PrepareData(datafile, dataRange);

            %disp(dataset);

            % generate x and y data
            xdata = [];
            ydata = [];
            for i=1:length(dataset)
                ydata=[ydata; dataset{i, 1}];
                xdata=[xdata; dataset{i, 2}];
            end
            
            % Fit using polyfit
            [estimated_params, stat, Fit, x_vector, y_vector] = sigm_fit(xdata, ydata);
            
            % Output RMSE 
            Polarity = 0;
            if((abs(estimated_params(2)-estimated_params(1)))<0.1)
                RMSE_Fit = 1.0;
            else
                % get polarity of sigmoid 1 or -1
                if(estimated_params(2)-estimated_params(1)>0)
                    Polarity = 1;
                else
                    Polarity = -1;
                end
                
                % calculate rmse
                RMSE_Fit = sqrt(mean((ydata-Fit).^2));
                %disp(RMSE_Fit);
                
                % optimize rmse by removing outlier who is great than 3*RMSE
                xdata_opt = [];
                ydata_opt = [];
                for i=1:length(xdata)
                    % remove outlier
                    if(sqrt((ydata(i)-Fit(i)).^2) < (RMSE_Fit*1.5))
                        ydata_opt=[ydata_opt; ydata(i)];
                        xdata_opt=[xdata_opt; xdata(i)]; 
                    end
                end
                
                if((length(xdata)-length(xdata_opt))<4)
                    % Refit to calculate new estimated_params
                    [estimated_params, stat, Fit_opt, x_vector, y_vector] = sigm_fit(xdata_opt, ydata_opt);

                    % recalculate rmse
                    RMSE_Fit = sqrt(mean((ydata_opt-Fit_opt).^2));
                else
                    RMSE_Fit = 1.0;
                    Polarity = 0;
                end
            end
            
            % Bad fitting condition, do not plot.
            if(RMSE_Fit < 1.0)
                % plot figure
                fig = figure;
                if(isPlot==false)
                    set(fig, 'Visible', 'off');
                end
                plot( xdata_opt, ydata_opt, '*', xdata_opt, ydata_opt, 'o', x_vector, y_vector, '-' );
                ylim([-0.05 1.05]);
                title(strcat('Sigmoid fitting curve: ', datafile));

                %save figure
                if(isSavefig==true)
                    %save figure named by datafile name
                    figname = strcat(datafile, '.png');
                    saveas(fig, figname);
                end          
            end
       end
    
    end
end