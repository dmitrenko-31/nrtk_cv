#include <iostream>
#include <opencv2/opencv.hpp>
#include <opencv2/aruco.hpp>

#include "../include/logic.h"
#include "../include/config.h"

int main(int, char **)
{

    // cv::VideoCapture cap("udp://@172.23.122.51:8554", cv::CAP_FFMPEG); //?overrun_nonfatal=1&fifo_size=500000
    cv::VideoCapture cap(0, cv::CAP_V4L2);

    cap.set(cv::CAP_PROP_BUFFERSIZE, 1);
    cap.set(cv::CAP_PROP_FOURCC, cv::VideoWriter::fourcc('M', 'P', '4', 'V'));

    if (!cap.isOpened())
    {
        std::cout << "Error opening video stream or file" << std::endl;
        return -1;
    }
    else
    {
        std::cout << "Successful opening video stream or file" << std::endl;
    }

    cv::namedWindow("Frame", cv::WINDOW_GUI_NORMAL | cv::WINDOW_NORMAL | cv::WINDOW_KEEPRATIO);
    cv::aruco::Dictionary dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_250);
    cv::aruco::ArucoDetector detector = cv::aruco::ArucoDetector(dictionary, cv::aruco::DetectorParameters(), cv::aruco::RefineParameters());
    cv::Mat frame;

    while (1)
    {
        // Capture frame-by-frame
        cap >> frame;

        // If the frame is empty, break immediately
        if (frame.empty())
            break;

        std::vector<int> ids;
        std::vector<std::vector<cv::Point2f>> corners;
        detector.detectMarkers(frame, corners, ids);


        if (ids.size() > 0)
        {
            for (int id : ids)
            {
                std::cout << id << " ";
            }
            std::cout << std::endl;
            cv::aruco::drawDetectedMarkers(frame, corners, ids);
            std::cout << find_distance(corners) << std::endl;
        }

        cv::imshow("Frame", frame);

        // Press  ESC on keyboard to exit
        if ((char)cv::waitKey(1) == 27)
            break;
    }

    // When everything done, release the video capture object
    cap.release();

    // Closes all the frames
    cv::destroyAllWindows();
    return 0;
}
