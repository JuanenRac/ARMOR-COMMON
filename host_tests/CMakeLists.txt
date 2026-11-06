cmake_minimum_required(VERSION 3.16)
project(armor_common_host_tests CXX)
enable_testing()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT MSVC)
  add_compile_options(-Wall -Wextra -Werror -Wshadow)
endif()

# The readers and writers of the messages (generated/armor_wire.hpp) against the verdicts of the Python validator.
add_executable(test_wire_oracle test_wire_oracle.cpp)
target_include_directories(test_wire_oracle PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../generated ${CMAKE_CURRENT_SOURCE_DIR}/../firmware_base/core)
add_test(NAME wire_oracle COMMAND test_wire_oracle ${CMAKE_CURRENT_SOURCE_DIR}/../conformance/wire_cases.tsv ${CMAKE_CURRENT_BINARY_DIR}/wire_rewrites.tsv)
