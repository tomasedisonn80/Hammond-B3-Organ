cmake_minimum_required(VERSION 3.21)
project(HammondB3Organ VERSION 0.1.0 LANGUAGES CXX)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
    message(FATAL_ERROR "Use an out-of-source build, for example: cmake -S . -B build")
endif()

option(HAMMOND_ENABLE_SANITIZERS "Enable AddressSanitizer and UndefinedBehaviorSanitizer" OFF)
option(HAMMOND_BUILD_VST3 "Build the optional pinned-SDK native VST3 instrument" OFF)
set(HAMMOND_VST3_SDK_ROOT "" CACHE PATH "Separately acquired, locked VST3 SDK checkout")
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
include(CTest)

if(HAMMOND_ENABLE_SANITIZERS)
    if(MSVC OR NOT CMAKE_CXX_COMPILER_ID MATCHES "^(GNU|Clang|AppleClang)$")
        message(FATAL_ERROR
            "HAMMOND_ENABLE_SANITIZERS requires GCC or Clang with both ASan and UBSan; "
            "MSVC/clang-cl and other compiler drivers are unsupported.")
    endif()
    include(CheckCXXSourceCompiles)
    function(hammond_check_sanitizers)
        set(CMAKE_REQUIRED_FLAGS "${CMAKE_REQUIRED_FLAGS} -fsanitize=address,undefined -fno-omit-frame-pointer")
        list(APPEND CMAKE_REQUIRED_LINK_OPTIONS "-fsanitize=address,undefined")
        check_cxx_source_compiles("int main() { return 0; }" HAMMOND_SANITIZERS_AVAILABLE)
    endfunction()
    hammond_check_sanitizers()
    if(NOT HAMMOND_SANITIZERS_AVAILABLE)
        message(FATAL_ERROR "The selected compiler cannot compile/link ASan and UBSan together.")
    endif()
endif()

function(hammond_configure_target target)
    target_compile_features(${target} PUBLIC cxx_std_20)
    if(MSVC)
        target_compile_options(${target} PRIVATE /W4 /WX /permissive- /Zc:__cplusplus)
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "^(GNU|Clang|AppleClang)$")
        target_compile_options(${target} PRIVATE
            -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror)
    else()
        message(WARNING "No strict warning configuration is defined for ${CMAKE_CXX_COMPILER_ID}.")
    endif()
    if(HAMMOND_ENABLE_SANITIZERS)
        target_compile_options(${target} PRIVATE
            -fsanitize=address,undefined -fno-omit-frame-pointer)
        # A static core's consumers also need the sanitizer runtime at link time.
        target_link_options(${target} PUBLIC -fsanitize=address,undefined)
    endif()
endfunction()

file(GLOB HAMMOND_CORE_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp")
if(NOT HAMMOND_CORE_SOURCES)
    message(FATAL_ERROR "No core C++ sources were found in src/.")
endif()
add_library(hammond_core STATIC ${HAMMOND_CORE_SOURCES})
target_include_directories(hammond_core PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include")
hammond_configure_target(hammond_core)

# Documentary routing is compiled separately from the unchanged organ profile.
# Both independent CSV readings and the comparison manifest are build inputs.
set(HAMMOND_PEDAL_COMPILER "${CMAKE_CURRENT_SOURCE_DIR}/tools/compile_pedal_routing.py")
set(HAMMOND_PEDAL_MAP "${CMAKE_CURRENT_SOURCE_DIR}/data/pedal-map.json")
set(HAMMOND_PEDAL_REFERENCE "${CMAKE_CURRENT_SOURCE_DIR}/data/references/factory-table-iii.json")
set(HAMMOND_PEDAL_REVIEW_A "${CMAKE_CURRENT_SOURCE_DIR}/data/references/review-a-pedal.csv")
set(HAMMOND_PEDAL_REVIEW_B "${CMAKE_CURRENT_SOURCE_DIR}/data/references/review-b-pedal.csv")
set(HAMMOND_GENERATED_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(HAMMOND_PEDAL_HEADER "${HAMMOND_GENERATED_INCLUDE_DIR}/hammond/generated/PedalRoutingData.h")
add_custom_command(
    OUTPUT "${HAMMOND_PEDAL_HEADER}"
    COMMAND "${Python3_EXECUTABLE}" "${HAMMOND_PEDAL_COMPILER}"
        --input "${HAMMOND_PEDAL_MAP}" --reference "${HAMMOND_PEDAL_REFERENCE}"
        --review-a "${HAMMOND_PEDAL_REVIEW_A}" --review-b "${HAMMOND_PEDAL_REVIEW_B}"
        --output "${HAMMOND_PEDAL_HEADER}"
    DEPENDS "${HAMMOND_PEDAL_COMPILER}"
        "${CMAKE_CURRENT_SOURCE_DIR}/tools/validate_pedal_map.py"
        "${CMAKE_CURRENT_SOURCE_DIR}/tools/validate_factory_reference.py"
        "${HAMMOND_PEDAL_MAP}" "${HAMMOND_PEDAL_REFERENCE}"
        "${HAMMOND_PEDAL_REVIEW_A}" "${HAMMOND_PEDAL_REVIEW_B}"
    COMMENT "Checking both factory pedal readings and compiling native routing"
    VERBATIM)
add_custom_target(hammond_pedal_routing DEPENDS "${HAMMOND_PEDAL_HEADER}")
add_dependencies(hammond_core hammond_pedal_routing)
target_include_directories(hammond_core PRIVATE "${HAMMOND_GENERATED_INCLUDE_DIR}")

set(HAMMOND_AUTHORING_PROFILE "${CMAKE_CURRENT_SOURCE_DIR}/data/profiles/nominal-unmeasured-v1.json")
set(HAMMOND_PROFILE_COMPILER "${CMAKE_CURRENT_SOURCE_DIR}/tools/compile_profile.py")
set(HAMMOND_COMPILED_PROFILE "${CMAKE_CURRENT_BINARY_DIR}/nominal.b3p")
add_custom_command(
    OUTPUT "${HAMMOND_COMPILED_PROFILE}"
    COMMAND "${Python3_EXECUTABLE}" "${HAMMOND_PROFILE_COMPILER}"
        --input "${HAMMOND_AUTHORING_PROFILE}" --output "${HAMMOND_COMPILED_PROFILE}"
    DEPENDS "${HAMMOND_PROFILE_COMPILER}" "${HAMMOND_AUTHORING_PROFILE}"
    COMMENT "Validating and compiling the nominal unmeasured profile"
    VERBATIM)
add_custom_target(hammond_profile ALL DEPENDS "${HAMMOND_COMPILED_PROFILE}")

file(GLOB HAMMOND_RENDER_SOURCE CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tools/render.cpp")
if(HAMMOND_RENDER_SOURCE)
    add_executable(hammond_render ${HAMMOND_RENDER_SOURCE})
    if(MINGW)
        target_link_options(hammond_render PRIVATE -municode)
    endif()
    target_link_libraries(hammond_render PRIVATE hammond_core)
    hammond_configure_target(hammond_render)
    add_dependencies(hammond_render hammond_profile)
endif()

add_executable(hammond_benchmark tools/benchmark.cpp)
target_link_libraries(hammond_benchmark PRIVATE hammond_core)
hammond_configure_target(hammond_benchmark)
target_compile_definitions(hammond_benchmark PRIVATE
    HAMMOND_BENCHMARK_PROFILE="${HAMMOND_COMPILED_PROFILE}"
    HAMMOND_BENCHMARK_CONFIGURATION="$<CONFIG>"
    HAMMOND_BENCHMARK_COMPILER_ID="${CMAKE_CXX_COMPILER_ID}"
    HAMMOND_BENCHMARK_COMPILER_VERSION="${CMAKE_CXX_COMPILER_VERSION}"
    HAMMOND_BENCHMARK_TARGET_SYSTEM="${CMAKE_SYSTEM_NAME}"
    HAMMOND_BENCHMARK_TARGET_PROCESSOR="${CMAKE_SYSTEM_PROCESSOR}"
    HAMMOND_BENCHMARK_SANITIZERS=$<BOOL:${HAMMOND_ENABLE_SANITIZERS}>)
add_dependencies(hammond_benchmark hammond_profile)

add_executable(hammond_model_info tools/model_info.cpp)
target_link_libraries(hammond_model_info PRIVATE hammond_core)
hammond_configure_target(hammond_model_info)

add_executable(hammond_parameter_info tools/parameter_info.cpp)
target_link_libraries(hammond_parameter_info PRIVATE hammond_core)
hammond_configure_target(hammond_parameter_info)

add_executable(hammond_console_trace tools/console_trace.cpp)
target_link_libraries(hammond_console_trace PRIVATE hammond_core)
hammond_configure_target(hammond_console_trace)
add_dependencies(hammond_console_trace hammond_profile)

add_executable(hammond_pedal_trace tools/pedal_trace.cpp)
target_link_libraries(hammond_pedal_trace PRIVATE hammond_core)
hammond_configure_target(hammond_pedal_trace)
add_dependencies(hammond_pedal_trace hammond_profile)

if(HAMMOND_BUILD_VST3)
    if(CMAKE_VERSION VERSION_LESS 3.25)
        message(FATAL_ERROR "The pinned optional VST3 SDK requires CMake 3.25 or newer.")
    endif()
    include(cmake/VerifyVst3Sdk.cmake)
    hammond_verify_vst3_sdk("${HAMMOND_VST3_SDK_ROOT}")
    set_target_properties(hammond_core PROPERTIES POSITION_INDEPENDENT_CODE ON)
    add_subdirectory(plugins/vst3)
endif()

if(BUILD_TESTING)
    find_package(Threads REQUIRED)
    set(HAMMOND_TEST_TARGETS ${HAMMOND_VST3_TEST_TARGETS})
    file(GLOB HAMMOND_CPP_TESTS CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_*.cpp")
    foreach(test_source IN LISTS HAMMOND_CPP_TESTS)
        get_filename_component(test_name "${test_source}" NAME_WE)
        add_executable(${test_name} "${test_source}")
        target_link_libraries(${test_name} PRIVATE hammond_core)
        if(test_name STREQUAL "test_state_exchange")
            target_link_libraries(${test_name} PRIVATE Threads::Threads)
        endif()
        target_include_directories(${test_name} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/tests")
        target_compile_definitions(${test_name} PRIVATE
            HAMMOND_TEST_PROFILE="${HAMMOND_COMPILED_PROFILE}"
            HAMMOND_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
        hammond_configure_target(${test_name})
        add_dependencies(${test_name} hammond_profile)
        add_test(NAME ${test_name} COMMAND ${test_name})
        list(APPEND HAMMOND_TEST_TARGETS ${test_name})
    endforeach()

    file(GLOB HAMMOND_PYTHON_TESTS CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_*.py")
    foreach(test_source IN LISTS HAMMOND_PYTHON_TESTS)
        get_filename_component(test_name "${test_source}" NAME_WE)
        add_test(NAME "python_${test_name}" COMMAND "${Python3_EXECUTABLE}" "${test_source}")
        set_tests_properties("python_${test_name}" PROPERTIES
            WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
            ENVIRONMENT "PYTHONDONTWRITEBYTECODE=1;HAMMOND_TEST_PROFILE=${HAMMOND_COMPILED_PROFILE};HAMMOND_SOURCE_DIR=${CMAKE_CURRENT_SOURCE_DIR}")
    endforeach()

    if(TEST python_test_vst3_build_tools)
        set_property(TEST python_test_vst3_build_tools APPEND PROPERTY ENVIRONMENT
            "HAMMOND_TEST_CMAKE=${CMAKE_COMMAND}")
    endif()

    if(TARGET hammond_render)
        foreach(test_source IN LISTS HAMMOND_PYTHON_TESTS)
            get_filename_component(test_name "${test_source}" NAME_WE)
            set_property(TEST "python_${test_name}" APPEND PROPERTY ENVIRONMENT
                "HAMMOND_RENDER_EXECUTABLE=$<TARGET_FILE:hammond_render>")
        endforeach()
        list(APPEND HAMMOND_TEST_TARGETS hammond_render)
    endif()

    if(TEST python_test_model_info)
        set_property(TEST python_test_model_info APPEND PROPERTY ENVIRONMENT
            "HAMMOND_MODEL_INFO_EXECUTABLE=$<TARGET_FILE:hammond_model_info>")
        list(APPEND HAMMOND_TEST_TARGETS hammond_model_info)
    endif()

    if(TEST python_test_parameter_bridge)
        set_property(TEST python_test_parameter_bridge APPEND PROPERTY ENVIRONMENT
            "HAMMOND_PARAMETER_INFO_EXECUTABLE=$<TARGET_FILE:hammond_parameter_info>")
        list(APPEND HAMMOND_TEST_TARGETS hammond_parameter_info)
    endif()

    if(TEST python_test_console_benchmark)
        set_property(TEST python_test_console_benchmark APPEND PROPERTY ENVIRONMENT
            "HAMMOND_BENCHMARK_EXECUTABLE=$<TARGET_FILE:hammond_benchmark>")
        list(APPEND HAMMOND_TEST_TARGETS hammond_benchmark)
    endif()

    foreach(test_source IN LISTS HAMMOND_PYTHON_TESTS)
        get_filename_component(test_name "${test_source}" NAME_WE)
        set_property(TEST "python_${test_name}" APPEND PROPERTY ENVIRONMENT
            "HAMMOND_CONSOLE_TRACE_EXECUTABLE=$<TARGET_FILE:hammond_console_trace>")
    endforeach()
    list(APPEND HAMMOND_TEST_TARGETS hammond_console_trace)

    foreach(test_source IN LISTS HAMMOND_PYTHON_TESTS)
        get_filename_component(test_name "${test_source}" NAME_WE)
        set_property(TEST "python_${test_name}" APPEND PROPERTY ENVIRONMENT
            "HAMMOND_PEDAL_TRACE_EXECUTABLE=$<TARGET_FILE:hammond_pedal_trace>")
    endforeach()
    list(APPEND HAMMOND_TEST_TARGETS hammond_pedal_trace)

    # Unlike invoking CTest directly, this target first builds its required inputs.
    add_custom_target(check
        COMMAND "${CMAKE_CTEST_COMMAND}" --output-on-failure --no-tests=error -C "$<CONFIG>"
        WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
        DEPENDS hammond_profile ${HAMMOND_TEST_TARGETS}
        USES_TERMINAL)
endif()

# The scoped local install contains the offline tools and their existing data.
# Relative GNUInstallDirs destinations preserve --prefix and later relocation.
include(GNUInstallDirs)
if(TARGET hammond_render)
    foreach(install_dir CMAKE_INSTALL_BINDIR CMAKE_INSTALL_DATADIR)
        if(IS_ABSOLUTE "${${install_dir}}" OR
           "${${install_dir}}" MATCHES "(^|[/\\\\])\\.\\.($|[/\\\\])" OR
           "${${install_dir}}" STREQUAL "")
            message(FATAL_ERROR
                "OfflineTools requires a nonempty relative ${install_dir} without parent traversal.")
        endif()
    endforeach()
    install(CODE "
        if(NOT EXISTS \"$<TARGET_FILE:hammond_render>\" OR
           NOT EXISTS \"$<TARGET_FILE:hammond_model_info>\" OR
           NOT EXISTS \"$<TARGET_FILE:hammond_parameter_info>\" OR
           NOT EXISTS \"$<TARGET_FILE:hammond_console_trace>\" OR
           NOT EXISTS \"${HAMMOND_COMPILED_PROFILE}\" OR
           NOT EXISTS \"${CMAKE_CURRENT_SOURCE_DIR}/tools/plot_console_trace.py\")
            message(FATAL_ERROR
                \"OfflineTools requires built hammond_render, hammond_model_info, hammond_parameter_info, hammond_console_trace, nominal.b3p and the source plot script; build all four executable targets for the selected configuration before installing.\")
        endif()
        " COMPONENT OfflineTools)
    install(TARGETS hammond_render hammond_model_info hammond_parameter_info hammond_console_trace
        RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}" COMPONENT OfflineTools)
    install(PROGRAMS tools/plot_console_trace.py
        DESTINATION "${CMAKE_INSTALL_BINDIR}" COMPONENT OfflineTools)
    install(FILES "${HAMMOND_COMPILED_PROFILE}"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/hammond-b3-organ"
        COMPONENT OfflineTools)
    install(FILES
        examples/fixtures/catalog-v1.json
        examples/fixtures/a4-fundamental-v1.events
        examples/fixtures/two-manual-changes-v1.events
        examples/fixtures/low-fold-coherent-v1.events
        examples/fixtures/held-bank-cancel-v1.events
        examples/fixtures/high-fold-coherent-v1.events
        DESTINATION "${CMAKE_INSTALL_DATADIR}/hammond-b3-organ/fixtures"
        COMPONENT OfflineTools)
    install(FILES
        examples/fixtures/console/console-catalog-v1.json
        examples/fixtures/console/console-travel-v1.events
        examples/fixtures/console/console-percussion-legato-v1.events
        examples/fixtures/console/console-routing-mask-v1.events
        DESTINATION "${CMAKE_INSTALL_DATADIR}/hammond-b3-organ/fixtures/console"
        COMPONENT OfflineTools)
    if(BUILD_TESTING AND TEST python_test_install)
        set_property(TEST python_test_install APPEND PROPERTY ENVIRONMENT
            "HAMMOND_TEST_CMAKE=${CMAKE_COMMAND}"
            "HAMMOND_TEST_BUILD_DIR=${CMAKE_CURRENT_BINARY_DIR}"
            "HAMMOND_TEST_CONFIG=$<CONFIG>"
            "HAMMOND_MODEL_INFO_EXECUTABLE=$<TARGET_FILE:hammond_model_info>"
            "HAMMOND_PARAMETER_INFO_EXECUTABLE=$<TARGET_FILE:hammond_parameter_info>"
            "HAMMOND_INSTALL_BINDIR=${CMAKE_INSTALL_BINDIR}"
            "HAMMOND_INSTALL_DATADIR=${CMAKE_INSTALL_DATADIR}")
        set_tests_properties(python_test_install PROPERTIES TIMEOUT 120)
    endif()
endif()
