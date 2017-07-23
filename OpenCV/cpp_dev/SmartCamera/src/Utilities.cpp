#include "../include/Utilities.h"

using namespace std;
using namespace cv;

Utilities::Utilities() {
	
}

bool Utilities::rectInside(cv::Rect r, cv::Rect q) {
	return r.x > q.x && r.y > q.y && 
			r.x + r.width < q.x + q.width && 
			r.y + r.height < q.y + q.height;
}

double pow2(float x) {
	return x*x;
}

vector<cv::Rect> Utilities::cont_filter(vector< vector<Point> > cnts, int minArea) {
	vector<cv::Rect> found_filtered;

	for (size_t i = 0; i < cnts.size(); i++) {
		if(cv::contourArea(cnts[i])< minArea){
			continue;
		}
		found_filtered.push_back(boundingRect(cnts[i]));
	}
	//return found_filtered;
	return Utilities::rect_filter(found_filtered);
}

vector<cv::Rect> Utilities::rect_filter(vector<cv::Rect> rects){
	vector<cv::Rect> found_filtered;
	for (size_t i = 0; i < rects.size(); i++) {
		for (size_t j = 0; j < rects.size(); j++)
		if ( i!=j  && Utilities::rectInside(rects[i], rects[j])) {
			continue;
		}
		found_filtered.push_back(rects[i]);		
	}
	return found_filtered;
}

Point Utilities::rectCenter(cv::Rect rect) {
	//get center of rect
	int cen_rx = int(rect.x + rect.width/2);
	int cen_ry = int(rect.y + rect.height/2);

	return Point(cen_rx, cen_ry);
}

bool  Utilities::pointInside(Point point, cv::Rect rect) {
	return point.x > rect.x &&
			point.x < rect.x + rect.width &&
			point.y > rect.y &&
			point.y < rect.y + rect.height;
}

int Utilities::pointDistance(Point p1, Point p2) {
	double diff = 0.0;
	diff = pow2(p1.x - p2.x) + pow2(p1.y - p2.y);
	return int(sqrt(diff));
}

int Utilities::centerRectDistance(cv::Rect r, cv::Rect q){
	Point p1 = Utilities::rectCenter(r);
	Point p2 = Utilities::rectCenter(q);
	return Utilities::pointDistance(p1,p2);
}

int Utilities::rectArea(cv::Rect rect) {
	float area = int(rect.width * rect.height);
	return int(area);
}

int Utilities::rectRadius(cv::Rect rect) {
	float radius = sqrt(pow2(rect.width / 2) + pow2(rect.height / 2));
	return int(radius);
}

void Utilities::draw_detections(cv::Mat frame, vector<cv::Rect> rects, Scalar color, int thickness, int mode) {
	int pad_w = 0; 
	int pad_h = 0;  

	for (size_t i = 0; i < rects.size(); i++) {
		if (mode == DrawTpye::DEFAULT || mode == DrawTpye::RECTANGLE) {
			pad_w = int(ScaleWeight_W*rects[i].width / 2);
			pad_h = int(ScaleWeight_H*rects[i].height / 2);
			rectangle(frame,
				Point(rects[i].tl().x - pad_w, rects[i].tl().y - pad_h),
				Point(rects[i].br().x + pad_w, rects[i].br().y + pad_h),
				color, thickness, 8, 0);
		}
		if (mode == DrawTpye::DEFAULT || mode == DrawTpye::CENTER) {
			circle(frame, Utilities::rectCenter(rects[i]), 3, Scalar(0, 0, 255), -1, 8, 0);
		}
	}
}
