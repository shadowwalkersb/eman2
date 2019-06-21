set(Boost_USE_MULTITHREADED ON)
set(Boost_NO_BOOST_CMAKE ON)
find_package(Boost COMPONENTS python numpy REQUIRED)

message("Boost_LIBRARIES:   ${Boost_LIBRARIES}")
message("Boost_INCLUDE_DIR: ${Boost_INCLUDE_DIR}")

#this definition is for boost.python > 1.35.0 
set_target_properties(Boost::python
					  PROPERTIES
					  INTERFACE_COMPILE_DEFINITIONS BOOST_PYTHON_NO_PY_SIGNATURES
					  INTERFACE_INCLUDE_DIRECTORIES ${PYTHON_INCLUDE_DIRS}
					  INTERFACE_INCLUDE_DIRECTORIES $<$<AND:$<CXX_COMPILER_ID:GNU>,$<BOOL:$ENV{CONDA_BUILD}>>:$ENV{BUILD_PREFIX}/x86_64-conda_cos6-linux-gnu/include/c++/7.3.0/>
					  )
if(WIN32)
	ADD_DEFINITIONS(-DBOOST_DISABLE_ASSERTS)
endif()

IF(CMAKE_SYSTEM MATCHES "IRIX.*")
    INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIR}/boost/compatibility/cpp_c_headers)
ENDIF()
