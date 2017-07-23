/*
========================
Utility.
========================
Created on July 19, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide utility class for user to call function.
*/
#ifndef UTILITIES_H
#define UTILITIES_H

#include "opencv2/objdetect.hpp"
#include "opencv2/videoio.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"

#include <iostream>
#include <stdio.h>
#include <math.h>

#define ScaleWeight_W	0.15
#define ScaleWeight_H	0.2

using namespace std;
using namespace cv;

//Define draw type
enum DrawTpye
{
	DEFAULT = 0,
	RECTANGLE = 1,
	CENTER = 2,
	LABEL_TEXT = 3,
	POLYLINES = 4
}; 


class Utilities {
	public:
		Utilities();

		//return whether contour r inside q
		bool static rectInside(cv::Rect r, cv::Rect q);

		//get filtered contours based on _minArea
		vector<cv::Rect> static cont_filter(vector< vector<Point> > cnts, int minArea);

		//get filtered rectangle to remove inside ones
		vector<cv::Rect> static rect_filter(vector<cv::Rect> rects);

		//#return center of rectangle
		Point static rectCenter(cv::Rect rect);

		//return whether _point inside _rect
		bool static pointInside(Point point, cv::Rect rect);

		//return distance of p1 and p2
		int static pointDistance(Point p1, Point p2);

		//return distance of center of rectangle r and q
		int static centerRectDistance(cv::Rect r, cv::Rect q);

		//calculate area of rectangle rect
		int static rectArea(cv::Rect rect);

		//calculate internal radius of rectangle rect
		int static rectRadius(cv::Rect rect);

		//draw rectangles for found object
		void static draw_detections(cv::Mat img, 
									vector<cv::Rect> rects, 
									Scalar rectColor = (0, 0, 255), 
									int thickness = 1, 
									int mode = DrawTpye::DEFAULT);

};

#endif

