#include "../include/VideoStream.h"
#include "../include/ObjectDetect.h"
#include "../include/FlowTracking.h"
#include "../include/Utilities.h"

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
	if (streamType == StreamType::CAMERA) {
		ret = setCapture();
	}
	else if(streamType == StreamType::VIDEO){
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
int VideoStream::StreamDetection(int streamType, char* video_src, int detectmode, int minArea, int minDist) {
	int ret = 0;

	//open stream
	if (streamType == StreamType::CAMERA) {
		ret = setCapture();
	}
	else if (streamType == StreamType::VIDEO) {
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
	Mat fgmask;
	vector<cv::Rect> found_filtered;
	ObjDetect myObjdetect = ObjDetect();
	ObjTracking myObjTrack = ObjTracking();

	int object_count = 0;
	int track_count = 0;
	while (capture.read(frame))
	{
		if (frame.empty())
		{
			printf(" --(!) No captured frame -- Break!");
			break;
		}

		int drawmode = 0;
		// Apply the detection to the frame
		switch (detectmode) {
		case DetectionMode::FACE:
			myObjdetect.detectFace(frame, found_filtered);
			break;
		case DetectionMode::EYES:
			myObjdetect.detectEye(frame, found_filtered);
			break;
		case DetectionMode::MOTION:
			myObjdetect.detectMotionMOG(frame, found_filtered, MotionMethod::MOG2, minArea);
			drawmode = DrawTpye::LABEL_TEXT | DrawTpye::POLYLINES | DrawTpye::RECTANGLE | DrawTpye::CENTER;
			myObjTrack.run(frame, found_filtered, minDist, drawmode, 2);
		default:
			break;
		}

		//draw bounding box for detected objects 
		drawmode = DrawTpye::RECTANGLE | DrawTpye::CENTER;
		Utilities::draw_detections(frame, found_filtered, Scalar(0, 255, 0),2, drawmode);

		//draw the detect object count on the frame
		object_count = found_filtered.size();
		putText(frame, ("Detect: " + to_string(object_count)), Point(10, 30), 
				FONT_HERSHEY_SIMPLEX, 0.6, Scalar(0, 0, 255), 2);

		track_count = myObjTrack.objtracks.size();
		putText(frame, ("Tracking: " + to_string(track_count)), Point(10, 60), 
				FONT_HERSHEY_SIMPLEX, 0.6, Scalar(255, 0, 0), 2);

		// Apply the detection to the frame
		imshow("Stream Detection", frame);

		//display frame
		char c = (char)waitKey(1);
		if (c == 27) { break; } // escape
	}

	return 0;
}