/*
========================
Object Detect.
========================
Created on July 18, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide ObjDetect for user to detect object related feature in frame of video stream.
*/

#include "opencv2/objdetect.hpp"
#include "opencv2/videoio.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"
#include "opencv2/imgcodecs.hpp"
#include "opencv2/video.hpp"
#include "opencv2/bgsegm.hpp"

#include <iostream>
#include <stdio.h>

using namespace std;
using namespace cv;

//define MotionMethod 
enum MotionMethod {
	Diff = 0,
	MOG = 1,
	MOG2 = 2
};


class ObjDetect {
	private:
		char mStrOpencvData[256];
		CascadeClassifier face_cascade;
		CascadeClassifier eyes_cascade;
		
	public:
		ObjDetect();
		Ptr<BackgroundSubtractor> mBgSubMOG;	//MOG2 Background subtractor
		Ptr<BackgroundSubtractor> mBgSubMOG2;	//MOG2 Background subtractor

		int setface_cascade(char* cascadepath);
		int seteye_cascade(char* cascadepath);
		int detectFace(Mat frame, std::vector<cv::Rect> &faces);
		int detectEye(Mat frame, std::vector<cv::Rect> &eyes);
		int detectMotionMOG(Mat frame, vector<cv::Rect> &found_filtered, int mode, int minArea);
};
