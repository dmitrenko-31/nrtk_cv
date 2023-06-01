#include <string>

#ifndef logic_h
#define logic_h

float find_position(std::vector<std::vector<cv::Point2f>> &corners);
double find_distance(std::vector<std::vector<cv::Point2f>> &corners);
std::string get_direction();

#endif