function(ADD_PYSTE_LIB libname)
	Python_add_library (lib${libname} MODULE lib${libname}.cpp)
	

	set_target_properties(lib${libname}
			PROPERTIES
			LINK_LIBRARIES "EM2;Boost::python27"
			)
	
	install(TARGETS lib${libname} DESTINATION ${Python_SITELIB})
endfunction()

ADD_PYSTE_LIB(pyAligner2)
ADD_PYSTE_LIB(pyAverager2)
ADD_PYSTE_LIB(pyCmp2)
ADD_PYSTE_LIB(pyProcessor2)
ADD_PYSTE_LIB(pyReconstructor2) 
ADD_PYSTE_LIB(pyProjector2)
ADD_PYSTE_LIB(pyEMObject2) 
ADD_PYSTE_LIB(pyEMData2)
target_sources(libpyEMData2 PRIVATE emdata_wrapitems.cpp)
ADD_PYSTE_LIB(pyGeometry2)
ADD_PYSTE_LIB(pyTransform2)
ADD_PYSTE_LIB(pyPointArray2)
ADD_PYSTE_LIB(pyUtils2)
ADD_PYSTE_LIB(pyBoxingTools2)
ADD_PYSTE_LIB(pyFundamentals2)
ADD_PYSTE_LIB(pyTypeConverter2)
target_sources(libpyTypeConverter2 PRIVATE typeconverter.cpp)
ADD_PYSTE_LIB(pyPolarData2)
ADD_PYSTE_LIB(pyAnalyzer2)
ADD_PYSTE_LIB(pyPDBReader2)

if(NOT WIN32)
	ADD_PYSTE_LIB(pyTomoSeg2)
endif()

if(ENABLE_OPENGL)
	ADD_PYSTE_LIB(pyGLUtils2)
	ADD_PYSTE_LIB(pyMarchingCubes2)
	
	target_sources(pyMarchingCubes2 PRIVATE
				   ${CMAKE_SOURCE_DIR}/libEM/marchingcubes.cpp
				   )
	target_sources(pyGLUtils2 PRIVATE
				   ${CMAKE_SOURCE_DIR}/libEM/emftgl.cpp
				   ${CMAKE_SOURCE_DIR}/libEM/glutil.cpp
				   ${CMAKE_SOURCE_DIR}/libEM/marchingcubes.cpp
				   )
	target_link_libraries(libpyGLUtils2       PRIVATE EMAN::OpenGL FTGL::FTGL)
	target_link_libraries(libpyMarchingCubes2 PRIVATE EMAN::OpenGL)
endif()

file(GLOB empythonlibs "${CMAKE_CURRENT_SOURCE_DIR}/*.py")
install(FILES ${empythonlibs}
		DESTINATION ${Python_SITELIB}
		COMPONENT PythonFiles
		)

add_subdirectory(qtgui)

target_link_libraries(libpyUtils2         PRIVATE Python::NumPy)
target_link_libraries(libpyTypeConverter2 PRIVATE Python::NumPy)
