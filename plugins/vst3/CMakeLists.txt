# This directory is entered only after the external SDK passes the project lock.
set(SDK_ROOT "${HAMMOND_VST3_SDK_ROOT}")
set(vst3sdk_SOURCE_DIR "${SDK_ROOT}")
set(public_sdk_SOURCE_DIR "${SDK_ROOT}/public.sdk")
set(pluginterfaces_SOURCE_DIR "${SDK_ROOT}/pluginterfaces")
list(APPEND CMAKE_MODULE_PATH "${SDK_ROOT}/cmake/modules")

# This is deliberately a headless SDK subset. No user's plugin directory is
# modified, including when the caller has previously cached SDK sample options.
set(SMTG_ENABLE_VSTGUI_SUPPORT OFF CACHE BOOL "No custom editor in this instrument" FORCE)
set(SMTG_ENABLE_VST3_PLUGIN_EXAMPLES OFF CACHE BOOL "Exclude SDK plugin samples" FORCE)
set(SMTG_ENABLE_VST3_HOSTING_EXAMPLES OFF CACHE BOOL "Exclude SDK host applications" FORCE)
set(SMTG_ENABLE_WAYLAND_SUPPORT OFF CACHE BOOL "Exclude SDK GUI support" FORCE)
set(SMTG_ENABLE_IOS_TARGETS OFF CACHE BOOL "Desktop native qualification only" FORCE)
set(SMTG_CREATE_PLUGIN_LINK OFF CACHE BOOL "Never link into a system plugin directory" FORCE)
set(SMTG_RUN_VST_VALIDATOR ON CACHE BOOL "Build and run SDK validator qualification" FORCE)
set(SMTG_CREATE_MODULE_INFO ON CACHE BOOL "Generate actual native module metadata" FORCE)
set(SMTG_CREATE_BUNDLE_FOR_WINDOWS ON CACHE BOOL "Produce an explicit VST3 bundle" FORCE)
set(SMTG_ADD_VST3_UTILITIES ON CACHE BOOL "Build required SDK module-info tooling" FORCE)
set(SMTG_AAX_SDK_PATH "" CACHE PATH "No AAX wrapper in this instrument" FORCE)

# Import SDK helpers in this directory scope as well as its own subdirectory.
# SDK compile flags remain local to SDK targets; project source warnings retain
# hammond_configure_target's strict policy.
include(SMTG_VST3_SDK)
add_subdirectory("${SDK_ROOT}" "${CMAKE_BINARY_DIR}/_vst3sdk" EXCLUDE_FROM_ALL)
smtg_enable_vst3_sdk()

# SDK setup adds directory-wide floating-point shortcuts on MSVC and Xcode.
# Our admission checks and exact control/state conversion require finite-value
# semantics and access to the caller's rounding environment. SDK targets were
# already created in their own directory and retain their upstream policy.
get_directory_property(_hammond_native_compile_options COMPILE_OPTIONS)
list(REMOVE_ITEM _hammond_native_compile_options
    "/fp:fast" "-ffast-math" "-ffp-contract=fast")
set_property(DIRECTORY PROPERTY COMPILE_OPTIONS "${_hammond_native_compile_options}")

function(hammond_configure_native_target target)
    hammond_configure_target(${target})
    if(MSVC)
        target_compile_options(${target} PRIVATE /fp:strict)
    endif()
endfunction()

set(HAMMOND_EMBEDDED_PROFILE "${CMAKE_CURRENT_BINARY_DIR}/generated/EmbeddedProfile.h")
add_custom_command(
    OUTPUT "${HAMMOND_EMBEDDED_PROFILE}"
    COMMAND "${Python3_EXECUTABLE}" "${PROJECT_SOURCE_DIR}/tools/embed_profile.py"
        --input "${HAMMOND_COMPILED_PROFILE}" --output "${HAMMOND_EMBEDDED_PROFILE}"
    DEPENDS "${HAMMOND_COMPILED_PROFILE}" "${PROJECT_SOURCE_DIR}/tools/embed_profile.py"
    COMMENT "Embedding the exact compiled nominal profile for stopped initialization"
    VERBATIM)
add_custom_target(hammond_embedded_profile DEPENDS "${HAMMOND_EMBEDDED_PROFILE}")
add_dependencies(hammond_embedded_profile hammond_profile)

# Keep SDK validation as an explicit mandatory CTest gate. A validator failure
# must not prevent an independent ABI harness from inspecting the linked module.
# The SDK validator itself retains its own build-time selftest.
set(SMTG_RUN_VST_VALIDATOR OFF)
smtg_add_vst3plugin(HammondB3
    Processor.cpp Processor.h
    Controller.cpp Controller.h
    Factory.cpp PluginIds.h
    StateStream.cpp StateStream.h
    "${HAMMOND_EMBEDDED_PROFILE}")
set(SMTG_RUN_VST_VALIDATOR ON)
add_dependencies(HammondB3 hammond_embedded_profile)
target_link_libraries(HammondB3 PRIVATE hammond_core sdk)
target_include_directories(HammondB3 PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/generated")
target_include_directories(HammondB3 SYSTEM PRIVATE "${SDK_ROOT}")
hammond_configure_native_target(HammondB3)

if(SMTG_MAC)
    smtg_target_set_bundle(HammondB3
        BUNDLE_IDENTIFIER "org.hammond-b3-organ.nominal-vst3"
        COMPANY_NAME "Hammond-B3-Organ contributors")
    # The SDK helper's non-Xcode branch does not populate these CMake fields.
    set_target_properties(HammondB3 PROPERTIES
        MACOSX_BUNDLE_GUI_IDENTIFIER "org.hammond-b3-organ.nominal-vst3"
        MACOSX_BUNDLE_BUNDLE_VERSION "${PROJECT_VERSION}"
        MACOSX_BUNDLE_SHORT_VERSION_STRING "${PROJECT_VERSION}")
endif()

# These generated local bundles contain linked SDK code, so retain the selected
# primary notice and the repository's component-specific provenance/terms.
configure_file("${SDK_ROOT}/LICENSE.txt"
    "${CMAKE_CURRENT_BINARY_DIR}/generated/VST3_SDK_LICENSE.txt" COPYONLY)
smtg_target_add_plugin_resources(HammondB3 RESOURCES
    "${CMAKE_CURRENT_BINARY_DIR}/generated/VST3_SDK_LICENSE.txt"
    "${PROJECT_SOURCE_DIR}/THIRD_PARTY_NOTICES.md")

get_target_property(HAMMOND_VST3_BUNDLE_PATH HammondB3 SMTG_PLUGIN_PACKAGE_PATH)
file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/hammond-vst3-path-$<CONFIG>.txt"
    CONTENT "${HAMMOND_VST3_BUNDLE_PATH}\n")

if(BUILD_TESTING)
    add_test(NAME hammond_vst3_validator
        COMMAND $<TARGET_FILE:validator> "${HAMMOND_VST3_BUNDLE_PATH}")
    set_tests_properties(hammond_vst3_validator PROPERTIES TIMEOUT 180)
    set(HAMMOND_VST3_TEST_TARGETS HammondB3 validator)
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_native_controller.cpp")
        add_executable(test_native_controller
            tests/test_native_controller.cpp Controller.cpp StateStream.cpp)
        target_link_libraries(test_native_controller PRIVATE hammond_core sdk)
        if(SMTG_MAC)
            find_library(HAMMOND_COREFOUNDATION_FRAMEWORK CoreFoundation REQUIRED)
            target_link_libraries(test_native_controller PRIVATE "${HAMMOND_COREFOUNDATION_FRAMEWORK}")
        endif()
        target_include_directories(test_native_controller PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
        target_include_directories(test_native_controller SYSTEM PRIVATE "${SDK_ROOT}")
        hammond_configure_native_target(test_native_controller)
        add_test(NAME test_native_controller COMMAND test_native_controller)
        list(APPEND HAMMOND_VST3_TEST_TARGETS test_native_controller)
    endif()

    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/NativeHarness.cpp")
        # Compile unmodified SDK loader sources under SDK policies, independently
        # of the strict warnings on our harness and test sources.
        if(SMTG_MAC)
            set(hammond_module_loader "${SDK_ROOT}/public.sdk/source/vst/hosting/module_mac.mm")
            set_source_files_properties("${hammond_module_loader}"
                PROPERTIES COMPILE_OPTIONS "-fobjc-arc")
        elseif(SMTG_WIN)
            set(hammond_module_loader "${SDK_ROOT}/public.sdk/source/vst/hosting/module_win32.cpp")
        elseif(SMTG_LINUX)
            set(hammond_module_loader "${SDK_ROOT}/public.sdk/source/vst/hosting/module_linux.cpp")
        else()
            message(FATAL_ERROR "The native harness supports Linux, macOS and Windows desktop targets.")
        endif()
        add_library(hammond_vst3_test_loader STATIC "${hammond_module_loader}")
        target_compile_features(hammond_vst3_test_loader PRIVATE cxx_std_17)
        target_link_libraries(hammond_vst3_test_loader PUBLIC sdk_hosting ${CMAKE_DL_LIBS})
        if(SMTG_MAC)
            find_library(HAMMOND_COCOA_FRAMEWORK Cocoa REQUIRED)
            target_link_libraries(hammond_vst3_test_loader PUBLIC "${HAMMOND_COCOA_FRAMEWORK}")
        endif()
        add_library(hammond_vst3_test_host STATIC tests/NativeHarness.cpp)
        target_link_libraries(hammond_vst3_test_host PUBLIC hammond_core hammond_vst3_test_loader)
        target_include_directories(hammond_vst3_test_host PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/tests")
        target_include_directories(hammond_vst3_test_host SYSTEM PUBLIC "${SDK_ROOT}")
        hammond_configure_native_target(hammond_vst3_test_host)

        foreach(native_test test_native_abi test_native_behavior)
            if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/${native_test}.cpp")
                add_executable(${native_test} "tests/${native_test}.cpp")
                target_link_libraries(${native_test} PRIVATE hammond_vst3_test_host)
                hammond_configure_native_target(${native_test})
                add_dependencies(${native_test} HammondB3 hammond_profile)
                add_test(NAME ${native_test}
                    COMMAND ${native_test} "${HAMMOND_VST3_BUNDLE_PATH}" "${HAMMOND_COMPILED_PROFILE}")
                set_tests_properties(${native_test} PROPERTIES TIMEOUT 180)
                list(APPEND HAMMOND_VST3_TEST_TARGETS ${native_test})
            endif()
        endforeach()
    endif()
    set(HAMMOND_VST3_TEST_TARGETS "${HAMMOND_VST3_TEST_TARGETS}" PARENT_SCOPE)
endif()

# CI needs a build-only aggregate so one verbose CTest invocation can retain
# complete success/failure logs and JUnit output without running tests twice.
# New registered native tests enter this dependency list automatically.
add_custom_target(hammond_vst3_test_inputs
    DEPENDS HammondB3 validator ${HAMMOND_VST3_TEST_TARGETS})

add_custom_target(check_vst3
    COMMAND "${CMAKE_CTEST_COMMAND}" --output-on-failure --no-tests=error
        -C "$<CONFIG>" -R "^(hammond_vst3_validator|test_native_)"
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
    DEPENDS hammond_vst3_test_inputs
    USES_TERMINAL)
