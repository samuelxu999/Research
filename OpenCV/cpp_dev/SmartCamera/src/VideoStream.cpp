#include "../include/VideoStream.h"
#include "../include/ObjectDetect.h"

VideoStream::VideoStream() {

}

int VideoStream::setCapture(){
	capture.open(0);
	if (!capture.isOpened()) { 
		printf("--(!)Error opening video capture\n"); 
		return -1; 
	}
}

int VideoStream::setCapture(char* video_src) {
	capture.open(video_src);
	if (!capture.isOpened()) {
		printf("--(!)Error opening video capture\n");
		return -1;
	}
}

int VideoStream::StreamPreviewer(int streamType, char* video_src) {
	int ret = 0;

	//open stream
	if (streamType == StreamType::Camera) { 
		ret = setCapture();
	}
	else if(streamType == StreamType::Video){
		ret = setCapture(video_src);
	}
	else{
		printf("Not supported stream mode, please use StreamType.Camera or StreamType.Video");
		ret = -1;
	}
	//check open stream status
	if (!ret) {	return -1; }

	//read frame by frame to preview stream
	Mat frame;
	while (capture.read(frame))
	{
		if (frame.empty())
		{
			printf(" --(!) No captured frame -- Break!");
			break;
		}

		//display frame
		imshow("Stream Previewer", frame);

		char c = (char)waitKey(10);
		if (c == 27) { break; } // escape
	}

	return 0;
}
int VideoStream::StreamDetection(int streamType, char* video_src, int detectmode) {
	int ret = 0;

	//open stream
	if (streamType == StreamType::Camera) {
		ret = setCapture();
	}
	else if (streamType == StreamType::Video) {
		ret = setCapture(video_src);
	}
	else {
		printf("Not supported stream mode, please use StreamType.Camera or StreamType.Video");
		ret = -1;
	}
	//check open stream status
	if (!ret) { return -1; }

	//read frame by frame to preview stream
	Mat frame;
	std::vector<Rect> faces;
	ObjDetect myObjdetect = ObjDetect();

	while (capture.read(frame))
	{
		if (frame.empty())
		{
			printf(" --(!) No captured frame -- Break!");
			break;
		}


		// Apply the detection to the frame
		switch (detectmode) {
		case DetectionMode::Face:
			myObjdetect.detectFace(frame, faces);
			break;
		case DetectionMode::Eyes:
			myObjdetect.detectEye(frame, faces);
			break;
		default:
			break;
		}

		// Apply the detection to the frame
		imshow("Stream Detection", frame);

		//display frame
		char c = (char)waitKey(10);
		if (c == 27) { break; } // escape
	}

	return 0;
}