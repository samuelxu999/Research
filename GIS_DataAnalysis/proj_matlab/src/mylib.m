%----------------------- user defined functions ------------------------

classdef mylib
    methods(Static)
        % Read data from excel
        % @datafile: excel data file name without extension
        % @dataRange: data range in table
        function [x,y]=read_data(datafile, dataRange)

            filename = strcat(datafile, '.xlsx');
            sheet = 1;
            xlRange = dataRange;

            % read data from excel file
            [subset] = xlsread(filename, sheet, xlRange);

            %remove Nan value.
            subset(isnan(subset))=[];

            %remove rows with Nan value.
            %subset(any(isnan(subset),2),:)=[];

            [row, col]=size(subset);

            % generate linear x vector
            x = linspace(1, row, row);
            % transform column to vector.
            y = subset.';
        end
        
        function dataSet=PrepareData(datafile, dataRange)
            filename = strcat(datafile, '.xlsx');
            sheet = 1;
            xlRange = dataRange;

            % read data from excel file
            [num, txt, raw] = xlsread(filename, sheet, xlRange);

            %remove rows with Nan value of cell.
            raw(any(cellfun(@(x) any(isnan(x)),raw), 2),:)=[];
            
            dataSet={};
            
            %calculate year median
            year_sum=1;
            value_sum=raw{1,1};
            preYear=raw{1,2};
            year_mdeian=0.0;
            ds_index = 0;
            for i=2:length(raw)
                if(preYear == raw{i,2})
                    year_sum = year_sum + 1;
                    value_sum = value_sum + raw{i,1};
                else
                    year_mdeian=value_sum/year_sum;
                    %disp([year_mdeian, value_sum, year_sum]);
                    ds_index=ds_index+1;
                    dataSet{ds_index,1}=year_mdeian;
                    dataSet{ds_index,2}=preYear;
                    
                    %initialize year_sum, value_sum and update preYear
                    year_sum = 1;
                    value_sum = raw{i,1};
                    preYear = raw{i,2};
                    %dataSet{length(dataSet)+1} = year_mdeian;
                end
            end
            % add last record
            ds_index=ds_index+1;
            dataSet{ds_index,1}=year_mdeian;
            dataSet{ds_index,2}=preYear;
            
            %dataSet=raw;
        end

        function plot_data(datafile, dataRange)
            % read data from exvel file
            [x, y]=mylib.read_data(datafile,dataRange);

            % plot data
            fig=plot(x,y,'.');
            ylim([-0.05 1.05]);

            %save fig to png
            figname = strcat(datafile, '.png');
            saveas(fig, figname);

        end
        
        function plot_fig(figdata, xdata, ydata)

            % plot data
            fig=plot(xdata, ydata, '*');
            ylim([-0.05 1.05]);

            %save fig to png
            figname = strcat(figdata, '.png');
            saveas(fig, figname);

        end

        function pf=myPolyfit(datafile, dataRange, n)

            [x, y]=mylib.read_data(datafile,dataRange);
            
            pf=polyfit(x, y, n);
            
            ft = polyval(pf,x);
            %[estimated_params]=sigm_fit(x,y);
            
            fig=plot(x,y,'.', x, ft, 'r--');
            ylim([-0.05 1.05]);
            legend('y','ft')
            
            %save fig to png
            %figname = strcat(datafile, '_pf.png');
            %saveas(fig, figname);

        end
        
        function pf=Polyfit(xdata, ydata, n)
            
            pf=polyfit(xdata, ydata, n);
            
            ft = polyval(pf,xdata);
            %[estimated_params]=sigm_fit(x,y);
            
            plot(xdata, ydata, 'o', xdata, ft, 'r--');
            ylim([-0.05 1.05]);
            legend('ydata','ft')
            
            %save fig to png
            %figname = strcat(datafile, '_pf.png');
            %saveas(fig, figname);

        end
        
        function pf=mySigmfit(datafile, dataRange)

            [x, y]=mylib.read_data(datafile,dataRange);
            
            pf=sigm_fit(x,y);

        end


        function [estimated_params]=sigmfit_test()
            xdata = linspace(-10.0,10.0);
            ydata=mylib.my_sigmoid(xdata, 1.0, 1.0) + 0.05*randn(size(xdata)); 
            ydata_n=1-(mylib.my_sigmoid(xdata, 1.0, 1.0) + 0.05*randn(size(xdata))); 
            % standard parameter estimation 
            %[estimated_params]=sigm_fit(x,y); 
            % Fit using polyfit
            [estimated_params, stat, Fit, x_vector, y_vector] = sigm_fit(xdata, ydata);

            % parameter estimation with forced 0.5 fixed min 
            %[estimated_params]=sigm_fit(x,y,[0.5 NaN NaN NaN]) 

            % parameter estimation without plotting 
            %[estimated_params]=sigm_fit(x,y,[],[],0)
            
            % plot figure
            fig = figure;
            plot( xdata, ydata, '*', x_vector, y_vector, '-' );
            ylim([-0.05 1.05]);
            title(strcat('Sigmoid fitting curve'));
        end

        function p=polyfit_test()
            x = linspace(-10.0,10.0);
            y=mylib.my_sigmoid(x, 1.0, 1.0) + 0.05*randn(size(x)); 

            plot(x,y,'.');

            p=polyfit(x,y,2);

        end

        %sigmoid function:
        %@x: 
        function s=my_sigmoid(x, a, b)
            s = b./ (1.0 + exp(-a*x));
        end
    end
end
