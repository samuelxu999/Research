#include "../include/ObjectDetect.h"
#include <cstring>

ObjDetect::ObjDetect(){
	strcpy(mStrOpencvData, "D:/ProgramFiles/opencv_3.2_dev/sources/opencv/data/");
}

int ObjDetect::setface_cascade(char* cascadepath) {
	char strPath[256];
	strcpy(strPath, mStrOpencvData);
	strcat(strPath, cascadepath);
	return face_cascade.load(strPath);
}

int ObjDetect::seteye_cascade(char* cascadepath) {
	char strPath[256];
	strcpy(strPath, mStrOpencvData);
	strcat(strPath, cascadepath);
	return eyes_cascade.load(strPath);
}

int ObjDetect::detectFace(Mat frame, std::vector<Rect> faces) {
	//load cascade
	if (!setface_cascade("haarcascades/haarcascade_frontalface_alt.xml")) {
		printf("Error loading face cascade\n");
		return -1;
	}

	//std::vector<Rect> faces;
	Mat frame_gray;
	cvtColor(frame, frame_gray, COLOR_BGR2GRAY);
	equalizeHist(frame_gray, frame_gray);

	//-- Detect faces
	face_cascade.detectMultiScale(frame_gray, faces, 1.3, 5, 0 | CASCADE_SCALE_IMAGE, Size(30, 30));

	//draw face
	for (size_t i = 0; i < faces.size(); i++) {
		//Point center(faces[i].x + faces[i].width / 2, faces[i].y + faces[i].height / 2);
		//ellipse(frame, center, Size(faces[i].width / 2, faces[i].height / 2), 0, 0, 360, Scalar(0, 255, 0), 2, 8, 0);
		rectangle(frame, faces[i], Scalar(0, 255, 0), 2, 8, 0);
	}
	return 0;
}

int  ObjDetect::detectEye(Mat frame, std::vector<Rect> eyes) {
	//load cascade
	if (!setface_cascade("haarcascades/haarcascade_frontalface_alt.xml")) {
		printf("Error loading face cascade\n");
		return -1;
	}
	if (!seteye_cascade("/haarcascades/haarcascade_eye.xml")) {
		printf("Error loading eye cscade\n");
		return -1;
	}

	std::vector<Rect> faces;
	Mat frame_gray;
	cvtColor(frame, frame_gray, COLOR_BGR2GRAY);
	equalizeHist(frame_gray, frame_gray);

	//-- Detect faces
	face_cascade.detectMultiScale(frame_gray, faces, 1.3, 5, 0 | CASCADE_SCALE_IMAGE, Size(30, 30));

	//-- In each face, detect eyes
	for (size_t i = 0; i < faces.size(); i++) {
		//mark face
		Point center(faces[i].x + faces[i].width / 2, faces[i].y + faces[i].height / 2);
		ellipse(frame, center, Size(faces[i].width / 2, faces[i].height / 2), 0, 0, 360, Scalar(0, 255, 0), 2, 8, 0);

		Mat faceROI = frame_gray(faces[i]);
		std::vector<Rect> eyes;

		//-- In each face, detect eyes
		eyes_cascade.detectMultiScale(faceROI, eyes, 1.1, 2, 0 | CASCADE_SCALE_IMAGE, Size(30, 30));

		//draw eyes
		for (size_t j = 0; j < eyes.size(); j++)
		{
			Point eye_center(faces[i].x + eyes[j].x + eyes[j].width / 2, faces[i].y + eyes[j].y + eyes[j].height / 2);
			int radius = cvRound((eyes[j].width + eyes[j].height)*0.25);
			circle(frame, eye_center, radius, Scalar(255, 0, 0), 2, 8, 0);
		}
	}
	return 0;
}