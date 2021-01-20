add_library(SPARX SHARED "")
set_property(TARGET SPARX PROPERTY CXX_STANDARD 14)
target_include_directories(SPARX PRIVATE
		${CMAKE_SOURCE_DIR}/libEM
		${Boost_INCLUDE_DIR}
		)

target_sources(SPARX PRIVATE
			   		${CMAKE_CURRENT_LIST_DIR}/emdata_sparx.cpp
			   		${CMAKE_CURRENT_LIST_DIR}/fundamentals.cpp
			   		${CMAKE_CURRENT_LIST_DIR}/fourierfilter.cpp
			   		${CMAKE_CURRENT_LIST_DIR}/rsconvolution.cpp
			   		${CMAKE_CURRENT_LIST_DIR}/native_fft.cpp
			   		${CMAKE_CURRENT_LIST_DIR}/util_sparx.cpp
			   		${CMAKE_CURRENT_LIST_DIR}/lapackblas.cpp
			   		${CMAKE_CURRENT_LIST_DIR}/pca.cpp
			   		${CMAKE_CURRENT_LIST_DIR}/varimax.cpp
			   		${CMAKE_CURRENT_LIST_DIR}/lbfgsb.cpp
			   		${CMAKE_CURRENT_LIST_DIR}/steepest.cpp
			   )
