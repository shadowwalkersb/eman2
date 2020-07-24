#ADD_EXECUTABLE(basic basic.cpp)
#TARGET_LINK_LIBRARIES(basic EM2)
#add_test(test_basic basic)

ADD_EXECUTABLE(imageio imageio.cpp)
TARGET_LINK_LIBRARIES(imageio EM2)
add_test(test_imageio imageio)

set(CTEST_BINARY_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

add_executable(test_eer test_eer.cpp)
target_link_libraries(test_eer EM2)
add_test(test-eer test_eer)
