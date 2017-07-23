#include "../include/FlowTracking.h"

//ObjTracking construction function
ObjTracking::ObjTracking() {
	track_seeds = 0;
	track_len = 10;
	frame_idx = 0;
	detect_interval = 5;
	timeout = 5;
}

//new LabeledObject instance and add to tracking list.
LabeledObject ObjTracking::addObjTrack(cv::Rect rect) {
	//new LabeledObject instance
	LabeledObject lb_object = LabeledObject();

	//generate id for lb_object
	track_seeds++;
	lb_object.idx = track_seeds;

	//set current rectangle data
	lb_object.rect = rect;

	//set head of track data as center of rectangle
	lb_object.tracks.push_back(Utilities::rectCenter(rect));
	
	//set activate state
	lb_object.isActive = 1;

	//return new tracking object instance
	return lb_object;
}

//update status of LabeledObject instance that are in tracking list
void ObjTracking::updateObjTrack(LabeledObject &lb_object, cv::Rect rect){
	//set current rectangle data
	lb_object.rect = rect;

	//append center of rectangle to lb_object.tracks list
	lb_object.tracks.push_back(Utilities::rectCenter(rect)); 

	//refresh activeTimeout with default value in timeout
	lb_object.activeTimeout = timeout;
}

//delete LabeledObject instance that are not active to compress tracking list
void ObjTracking::deleteObjTrack() {
	for(size_t i = 0; i< objtracks.size(); i++) {
		if(objtracks[i].isActive==0){
			//detect inactive object
			objtracks.erase(objtracks.begin() + i);
		}
	}
}


//draw tracking infomration on frame, such as label and path.
void draw_tracking(cv::Mat frame, LabeledObject obj, int mode , int thickness) {
	if (mode == DrawDefault || mode == DrawLabelText) {
		//display object label
		Point p = obj.tracks[obj.tracks.size() - 1];
		putText(frame, to_string(obj.idx), Point(p.x-4, p.y-4), 
				FONT_HERSHEY_SIMPLEX, 0.5, obj.color, 1);
	}
	if (mode == DrawDefault || mode == DrawPolyLines) {
		//draw moving path
		vector<Point> pts;
		for (size_t i = 0; i < obj.tracks.size(); i++) {
			pts.push_back(obj.tracks[i]);
		}
		polylines(frame, pts,false, obj.color, 2);
	}

}

//apply object tracking algorithm by processing found_object on frame.
void ObjTracking::run(Mat frame, vector<cv::Rect> found_object, int minDist, int drawMode, int thickness) {
	//saved tracked objects in _found_object
	vector<cv::Rect> old_tracks;

	//if tracks is not empty, update tracks
	//for each (LabeledObject lb_object in objtracks) {
	for (size_t i = 0; i < objtracks.size(); i++) {
		if (objtracks[i].isActive == 0) {
			continue;
		}

		//calculate minimum distance between previous rect and object
		int minDistance = minDist;
		cv::Rect minRect = cv::Rect(0, 0, 0, 0);
		
		//for each object to check tracking information
		//for each (cv::Rect rect in found_object) {
		for (size_t j = 0; j < found_object.size(); j++) {
			cv::Rect rect = found_object[j];
			//get center of rect
			Point cen_rect = Utilities::rectCenter(rect);
			Point cen_obj = objtracks[i].tracks[objtracks[i].tracks.size() - 1];

			//if center of rect within tracked object, then update track data of tracked object
			int pointDist = Utilities::pointDistance(cen_rect, cen_obj);
			
			if (pointDist < minDist) {
				//add old_tracks list
				old_tracks.push_back(rect);
				//get minDistance and minRect
				if (pointDist < minDistance) {
					minDistance = pointDist;
					minRect = rect;
				}
			}
		}
		//add rect with minimum distance to tracks
		if (Utilities::rectArea(minRect) != 0) {
			updateObjTrack(objtracks[i], minRect);
		}
	}
	
	//for each object to add new track object to self.tracks
	//for each (cv::Rect rect in found_object) {
	for (size_t i = 0; i < found_object.size(); i++) {
		cv::Rect rect = found_object[i];
		//if rect not in old_tracks
		if (std::find(old_tracks.begin(), old_tracks.end(), rect) == old_tracks.end()) {
			//add lb_object to self.tracks
			objtracks.push_back(addObjTrack(rect));
		}
	}
	
	//for each object to update active state and timeout
	//for each (LabeledObject obj in objtracks) {
	for (size_t i = 0; i < objtracks.size(); i++) {
		//skip inactive ones
		if (objtracks[i].isActive == 0) {
			continue;
		}

		//update activeTimeout and check isActive state
		if (objtracks[i].activeTimeout == 0) {
			objtracks[i].isActive = 0;
		}
		else {
			//calculate activeTimeout
			objtracks[i].activeTimeout--;
		}

		//For those overlap objects, merge to one object by changing isActive state
		//for each (LabeledObject obj_t in objtracks) {
		for (size_t j = 0; j < objtracks.size(); j++) {
			if (objtracks[i].idx < objtracks[j].idx && objtracks[i].tracks[objtracks[i].tracks.size() - 1] == objtracks[j].tracks[objtracks[j].tracks.size() - 1]) {
				objtracks[j].isActive = 0;
			}
		}

		//draw the tracking information on the frame
		if (objtracks[i].tracks.size() > 0) {
			draw_tracking(frame, objtracks[i], drawMode, thickness);
		}
	}

	//delete inactive object from tracking list
	deleteObjTrack();
}