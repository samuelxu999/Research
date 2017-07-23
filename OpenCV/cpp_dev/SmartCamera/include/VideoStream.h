/*
========================
Video Stream.
========================
Created on July 18, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide video stream related function.
*/

#ifndef VIDEOSTREAM_H
#define VIDEOSTREAM_H

#include "opencv2/objdetect.hpp"
#include "opencv2/videoio.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"

#include <iostream>
#include <stdio.h>

using namespace std;
using namespace cv;

//Define for stream type: camera or video files
enum StreamType { 
	CAMERA = 0,
	VIDEO = 1
};

//Define detect mode
enum RecordMode {
	NO_RECORD = 0,
	VIDEO_RECORD = 1,
	PICTURE_SNAP = 2
};

// Define detect mode
enum DetectionMode {
	NO_DETECTION = 0,
	FACE = 1,
	EYES = 2,
	BODY = 3,
	MOTION = 4
};

class VideoStream {
	private:

	public:
		VideoCapture capture;
		VideoStream();
		int setCapture(char* video_src);
		int setCapture();

		int StreamPreviewer(int streamType, char* video_src);

		int StreamDetection(int streamType, char* video_src, int detectmode, int minArea=100, int minDist=50);
};

#endif