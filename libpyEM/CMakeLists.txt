function(ADD_PYSTE_LIB libname)
	add_library(${libname} SHARED lib${libname}.cpp)
	
	if(WIN32)
		set(suffix .pyd)
	else()
		set(suffix .so)
	endif()

	set_target_properties(${libname}
			PROPERTIES
			PREFIX lib
			SUFFIX ${suffix}
			LINK_LIBRARIES "EM2;Boost::python3"
			)
	
	install(TARGETS ${libname} DESTINATION ${SP_DIR})
endfunction()

set(PYLIBS 
pyAligner2
pyAverager2
pyCmp2
pyProcessor2
pyReconstructor2 
pyProjector2
pyEMObject2 
pyEMData2
pyGeometry2
pyTransform2
pyPointArray2
pyUtils2
pyBoxingTools2
pyFundamentals2
pyTypeConverter2
pyPolarData2
pyAnalyzer2
pyPDBReader2
	)

foreach(lib ${PYLIBS})
	ADD_PYSTE_LIB(${lib})
	target_link_libraries(${lib} EM2 ${Boost_LIBRARIES} Python::Python)
endforeach()

target_sources(pyEMData2 PRIVATE emdata_wrapitems.cpp)
target_sources(pyTypeConverter2 PRIVATE typeconverter.cpp)

if(NOT WIN32)
	ADD_PYSTE_LIB(pyTomoSeg2)
	target_link_libraries(pyTomoSeg2 EM2 ${Boost_LIBRARIES} Python::Python)
endif()

option(ENABLE_OPENGL "enable EMAN2 OpenGL usage" ON)
if(ENABLE_OPENGL)
	include(${CMAKE_SOURCE_DIR}/cmake/OpenGL.cmake)

	option(ENABLE_STATIC_FTGL "If build EMAN with libftgl.a" OFF)
	mark_as_advanced(ENABLE_STATIC_FTGL)
	
	find_package(FTGL REQUIRED)
	
	add_subdirectory(fonts)

	ADD_PYSTE_LIB(pyGLUtils2)
		target_link_libraries(pyGLUtils2 EM2 ${Boost_LIBRARIES} Python::Python)
	ADD_PYSTE_LIB(pyMarchingCubes2)
		target_link_libraries(pyMarchingCubes2 EM2 ${Boost_LIBRARIES} Python::Python)
	
	target_sources(pyMarchingCubes2 PRIVATE
				   marchingcubes.cpp
				   )
	target_sources(pyGLUtils2 PRIVATE
				   emftgl.cpp
				   glutil.cpp
				   marchingcubes.cpp
				   )
	target_link_libraries(pyGLUtils2       OpenGL::OpenGL FTGL::FTGL)
	target_link_libraries(pyMarchingCubes2 OpenGL::OpenGL)
endif()

file(GLOB empythonlibs "${CMAKE_CURRENT_SOURCE_DIR}/*.py")
install(FILES ${empythonlibs}
		DESTINATION ${SP_DIR}
		COMPONENT PythonFiles
		)

add_subdirectory(qtgui)

target_link_libraries(pyUtils2         NumPy Boost::numpy3)
target_link_libraries(pyTypeConverter2 NumPy Boost::numpy3)
