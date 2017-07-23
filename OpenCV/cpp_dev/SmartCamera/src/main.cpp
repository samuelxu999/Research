#include "../include/main.h"

/* This demo will tutor you how to load a picture to test your OpenCV development environment*/
int loadImg(char* strPath) {
	Mat image;
	image = imread(strPath, CV_LOAD_IMAGE_COLOR);   // Read the file

	if (!image.data)                              // Check for invalid input
	{
		cout << "Could not open or find the image file: " << strPath << std::endl;
		return -1;
	}

	namedWindow("Display window", WINDOW_AUTOSIZE);// Create a window for display.
	imshow("Display window", image);                   // Show our image inside it.

	waitKey(0);  // Wait for a keystroke in the window
	return 0;
}

int testObjDetect(char* imgpath){
	//load image
	Mat frame;
	frame = imread(imgpath, CV_LOAD_IMAGE_COLOR);   // Read the file

	if (!frame.data)                              // Check for invalid input
	{
		cout << "Could not open or find the image file: " << imgpath << std::endl;
		return -1;
	}

	//detect face
	std::vector<cv::Rect> faces;
	std::vector<cv::Rect> eyes;
	ObjDetect myObjdetect = ObjDetect();
	//myObjdetect.detectFace(frame, faces);
	myObjdetect.detectEye(frame, eyes);

	//-- Show result
	namedWindow("Display window", WINDOW_AUTOSIZE);// Create a window for display.
	imshow("Display window", frame);                   // Show our image inside it.

	waitKey(0);  // Wait for a keystroke in the window
}

int testVideoStream(char* srcpath) {

	VideoStream myVideo = VideoStream();	

	//return myVideo.StreamPreviewer(StreamType::Camera, srcpath);

	//return myVideo.StreamDetection(StreamType::Camera, srcpath, DetectionMode::Face);
	return myVideo.StreamDetection(Video, srcpath, Motion,100);
}

	 

int main(int argc, char** argv)
{
	if (argc != 2)
	{
		cout << " Usage: " << argv[0] << " [image path]" << endl;
		return -1;
	}

	int ret = 0;

	//ret = loadImg(argv[1]);

	//ret = testObjDetect(argv[1]);

	ret = testVideoStream(argv[1]);

	return ret;
}
