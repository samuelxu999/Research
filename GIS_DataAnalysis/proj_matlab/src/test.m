format long;
%x = linspace(-10.0,10.0);
%y = my_sigmoid(x, 1.0, 1.0)
%y1 = my_sigmoid(x, 2.0, 1.0)
%y2 = my_sigmoid(x, 3.0, 1.0)
%y3 = my_sigmoid(x, 0.5, 1.0)

%plot(x, y, x, y1, x, y2, x, y3) 
%ylim([-0.05 1.05])

tt=0;

%month_fit();

%year_fit();


%size(subset)
%disp(subset);

%p=mylib.polyfit_test();
%disp(p);

%estimated_params=mylib.sigmfit_test();
%disp(estimated_params);

ret = test_validation();
disp(ret);

% % data
% x=1:100;
% sigma=15; mu=40; A=3;
% y=A*exp(-(x-mu).^2/(2*sigma^2))+rand(size(x))*0.3;
% plot(x,y,'.');
% 
% % fitting
% [sigmaNew,muNew,Anew]=gaussian_fit(x,y);
% y=Anew*exp(-(x-muNew).^2/(2*sigmaNew^2));
% hold on; plot(x,y,'.r');

% x = -10:1:10;
% s = 2;
% m = 3;
% y = 1/(sqrt(2*pi)* s ) * exp( - (x-m).^2 / (2*s^2)) + 0.02*randn( 1, 21 );
% [sigma,mu] = gaussfit( x, y )
% xp = -10:0.1:10;
% yp = 1/(sqrt(2*pi)* sigma ) * exp( - (xp-mu).^2 / (2*sigma^2));
% plot( x, y, 'o', xp, yp, '-' );

function RET = test_validation()
    close all;
    datafile_list = cell(1, 8);
    datafile_list{1} = 'dataset/reconstruction1';
    datafile_list{2} = 'dataset/reconstruction2';
    datafile_list{3} = 'dataset/cropland_urban1';
    datafile_list{4} = 'dataset/demo1';
    datafile_list{5} = 'dataset/flood_urban1';
    datafile_list{6} = 'dataset/forest_urban1';
    datafile_list{7} = 'dataset/grass_urban1';
    datafile_list{8} = 'dataset/nochangeCrop';
    
    RMSE_list = {};
%==================== Group test ==========================
    for i=1:length(datafile_list)
        %disp(datafile_list{i});    
        RMSE_list{i,1} = datafile_list{i};
        
        % -------------- fit and validate test ----------------        
        tmp_rmst = {};
        [ Fit , RMSE_Fit ] = myValidation.valid_polyfit(datafile_list{i}, 1, false, false);
        tmp_rmst{1, 1} = 'polyfit';
        tmp_rmst{1, 2} =  RMSE_Fit;
        
        [ Fit , RMSE_Fit ] = myValidation.valid_gaussfit( datafile_list{i}, false, false);
        tmp_rmst{2, 1} = 'gaussfit';
        tmp_rmst{2, 2} =  RMSE_Fit;
        
        [ Fit , RMSE_Fit ] = myValidation.valid_sigmfit( datafile_list{i}, false, false);
        tmp_rmst{3, 1} = 'sigmfit';
        tmp_rmst{3, 2} =  RMSE_Fit;
        
        sorted_rmst = sortrows(tmp_rmst, 2);
        
        RMSE_list{i,2} = sorted_rmst{1,1};
        RMSE_list{i,3} = sorted_rmst{1,2};
        
        % ------------- plot and save optimized fitting curve ---------
        if(strcmp(sorted_rmst{1,1}, 'polyfit'))
            myValidation.valid_polyfit(datafile_list{i}, 1, false, true);
        elseif(strcmp(sorted_rmst{1,1},'gaussfit'))
            myValidation.valid_gaussfit( datafile_list{i}, false, true);
        else
            myValidation.valid_sigmfit( datafile_list{i}, false, true);
        end

    end

% ==================== Single test ==========================
%         test_fileid = 1;
%         RMSE_list{1,1} = datafile_list{test_fileid};
%         
%         tmp_rmst = {};
%         [ Fit , RMSE_Fit ] = myValidation.valid_polyfit(datafile_list{test_fileid}, 1, false, false);
%         tmp_rmst{1, 1} = 'polyfit';
%         tmp_rmst{1, 2} =  RMSE_Fit;
%         
%         [ Fit , RMSE_Fit ] = myValidation.valid_gaussfit( datafile_list{test_fileid}, false, false);
%         tmp_rmst{2, 1} = 'gaussfit';
%         tmp_rmst{2, 2} =  RMSE_Fit;
%         
%         [ Fit , RMSE_Fit ] = myValidation.valid_sigmfit( datafile_list{test_fileid}, false, false);
%         tmp_rmst{3, 1} = 'sigmfit';
%         tmp_rmst{3, 2} =  RMSE_Fit;
%         
%         sorted_rmst = sortrows(tmp_rmst, 2)
%         RMSE_list{1,2} = sorted_rmst{1,1};
%         RMSE_list{1,3} = sorted_rmst{1,2};
%         
%         % plot optimized fitting curve
%         if(strcmp(RMSE_list{1, 2}, 'polyfit'))
%             myValidation.valid_polyfit(datafile_list{test_fileid}, 1, true, false);
%         elseif(strcmp(RMSE_list{1, 2},'gaussfit'))
%             myValidation.valid_gaussfit( datafile_list{test_fileid}, true, false);
%         else
%             myValidation.valid_sigmfit( datafile_list{test_fileid}, true, false);
%         end
    
    RET = RMSE_list;
    
    %close all;
end

function year_fit()
    datafile1 = 'dataset/reconstruction1';
    datafile2 = 'dataset/reconstruction2';
    datafile3 = 'dataset/cropland_urban1';
    datafile4 = 'dataset/demo1';
    datafile5 = 'dataset/flood_urban1';
    datafile6 = 'dataset/forest_urban1';
    datafile7 = 'dataset/grass_urban1';
    datafile8 = 'dataset/nochangeCrop';
    
    %sheet = 1;
    dataRange = 'A2:C500';
    
    dataset = mylib.PrepareData(datafile5, dataRange);
    
    %disp(dataset);
    
    % generate x and y data
    xdata = [];
    ydata = [];
    for i=1:length(dataset)
        ydata=[ydata; dataset{i, 1}];
        xdata=[xdata; dataset{i, 2}];
    end
    
    % plot data
    %mylib.plot_fig(datafile8, xdata, ydata)

    %fig=plot(xdata, ydata,'o');
    %ylim([-0.05 1.05]);
    
    %fit data
    
    %mylib.Polyfit(xdata, ydata, 5);
    pf=sigm_fit(xdata, ydata);
    disp(pf);
    

end

function month_fit()

    datafile1 = 'dataset/reconstruction1';
    datafile2 = 'dataset/reconstruction2';
    datafile3 = 'dataset/cropland_urban1';
    datafile4 = 'dataset/demo1';
    datafile5 = 'dataset/flood_urban1';
    datafile6 = 'dataset/forest_urban1';
    datafile7 = 'dataset/grass_urban1';
    datafile8 = 'dataset/nochangeCrop';

    %sheet = 1;
    dataRange = 'A1:A500';

    % polt data on figure
    %mylib.plot_data(datafile7, dataRange);

    % fit data on function
    f = mylib.myPolyfit(datafile1, dataRange, 4);
    %f = mylib.myPolyfit(datafile2, dataRange, 4);
    %f = mylib.myPolyfit(datafile3, dataRange, 4);
    %f = mylib.myPolyfit(datafile4, dataRange, 3);
    %f = mylib.mySigmfit(datafile5, dataRange);
    %f = mylib.myPolyfit(datafile6, dataRange, 4);
    %f = mylib.myPolyfit(datafile7, dataRange, 1);
    %f = mylib.myPolyfit(datafile8, dataRange, 1);

    disp(f);

end




