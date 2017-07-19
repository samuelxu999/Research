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
	Camera = 0,
	Video = 1
};

//Define detect mode
enum RecordMode {
	NoRecord = 0,
	VideoRecord = 1,
	PictureSnap = 2
};

// Define detect mode
enum DetectionMode {
	NoDetection = 0,
	Face = 1,
	Eyes = 2,
	Body = 3,
	Motion = 4
};

class VideoStream {
	private:

	public:
		VideoCapture capture;
		VideoStream();
		int setCapture(char* video_src);
		int setCapture();

		int StreamPreviewer(int streamType, char* video_src);

		int StreamDetection(int streamType, char* video_src, int detectmode);
};