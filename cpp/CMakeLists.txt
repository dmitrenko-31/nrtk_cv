cmake_minimum_required(VERSION 3.0.0)
project(ArucoDetector VERSION 0.1.0)
find_package(OpenCV REQUIRED)
INCLUDE_DIRECTORIES( ${OpenCV_INCLUDE_DIRS} )

include(CTest)
enable_testing()

file(GLOB SOURCES
    ./include/*.h
    ./sources/*.cpp
)

add_executable(ArucoDetector ${SOURCES})
target_link_libraries(ArucoDetector ${OpenCV_LIBS} )

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})

include(CPack)
