FILE(GLOB testprograms "${CMAKE_CURRENT_SOURCE_DIR}/*.py")
INSTALL(PROGRAMS ${testprograms}
  DESTINATION    test/rt/pyem
  COMPONENT      PythonFiles
)

install_develop_mode(${CMAKE_INSTALL_PREFIX}/test/rt/pyem)
