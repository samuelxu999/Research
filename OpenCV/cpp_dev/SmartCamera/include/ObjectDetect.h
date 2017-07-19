#include "opencv2/objdetect.hpp"
#include "opencv2/videoio.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"

#include <iostream>
#include <stdio.h>

using namespace std;
using namespace cv;

class ObjDetect {
	private:
		char mStrOpencvData[256];
		CascadeClassifier face_cascade;
		CascadeClassifier eyes_cascade;

	public:
		ObjDetect();

		int setface_cascade(char* cascadepath);
		int seteye_cascade(char* cascadepath);
		int detectFace(Mat frame, std::vector<Rect> faces);
		int detectEye(Mat frame, std::vector<Rect> eyes);
};
