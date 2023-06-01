#include <string>
#include <vector>
#include <cmath>
#include <opencv2/core/types.hpp>

#include "../include/config.h"

float find_position(std::vector<std::vector<cv::Point2f>> &corners)
{
    if (corners.size() == 0)
        return 0;

    int center_x = (corners[0][0].x + corners[0][2].x) / 2;

    float pos = (2.0 * center_x) / constants::frame_width - 1.0;
    if (-constants::blind_spot <= pos && pos <= constants::blind_spot)
        return 0.0;
    else
        return pos;
}

double find_distance(std::vector<std::vector<cv::Point2f>> &corners)
{
    if (corners.size() == 0)
        return 0;

    float marker_size = hypot(corners[0][1].x - corners[0][0].x, corners[0][1].y - corners[0][0].y) +
                        hypot(corners[0][2].x - corners[0][1].x, corners[0][2].y - corners[0][1].y);

    return constants::distance_coefficient * 1000.0 * constants::marker_true_size / marker_size;
}

std::string get_direction(std::vector<std::vector<cv::Point2f>> &corners)
{
    
    return " ";
}
