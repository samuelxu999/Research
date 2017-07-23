/*
========================
Flow Tracking.
========================
Created on July 20, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide moving object tracking by processing frame of video stream.
*/

#ifndef FLOWTRACKING_H
#define FLOWTRACKING_H

#include "opencv2/core.hpp"
#include "opencv2/videoio.hpp"
#include "../include/Utilities.h"

using namespace std;
using namespace cv;

//ObjTracking construction function
class LabeledObject {
	public:
		int idx;
		cv::Rect rect;
		vector<Point> tracks;
		int isActive;		
		int activeTimeout;
		Scalar color;

		LabeledObject() {
			idx = 0;
			isActive = 0;
			//wait 5 frame to check timeout, then set isActive = 0 to inactive moving object
			activeTimeout = 5;
			//generate random color
			//RNG rng;
			//color = Scalar(rng.uniform(0, 255), rng.uniform(0, 255), rng.uniform(0, 255));
			color = Scalar(rand() % 255, rand() % 255, rand() % 255);
		};
};


//Object tracking class which is responsible for label and tracking object.
class ObjTracking {
	public:
		int track_seeds;
		vector<LabeledObject> objtracks;
		int track_len;
		int frame_idx;
		int detect_interval;
		int timeout;
		ObjTracking();

		//add LabeledObject() instance to tracking list
		LabeledObject addObjTrack(cv::Rect rect);

		//update LabeledObject() instance by appending new point to tracking list
		void updateObjTrack(LabeledObject &lb_object, cv::Rect rect);

		//delete inactive LabeledObject() instance from tracking list
		void deleteObjTrack();

		//run tracking algorithm
		void run(Mat frame, vector<cv::Rect> found_object, 
					int minDist, 
					int drawMode = DrawTpye::DEFAULT, 
					int thickness = 1);
};

#endif

