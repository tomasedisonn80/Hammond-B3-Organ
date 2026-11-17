# Host-independent adapters are tested by the ordinary build. SDL2 is entered
# only when the user explicitly enables the native application.
find_package(Threads REQUIRED)
add_library(hammond_standalone_support STATIC
    Session.cpp UiModel.cpp InspectionModel.cpp StateFiles.cpp RegistrationLibrary.cpp
    MidiInput.cpp MidiDevice.cpp MidiReplay.cpp)
target_link_libraries(hammond_standalone_support PUBLIC hammond_core Threads::Threads)
target_include_directories(hammond_standalone_support PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
target_compile_definitions(hammond_standalone_support PRIVATE
    HAMMOND_HAS_RTMIDI=$<BOOL:${HAMMOND_ENABLE_MIDI}>)
if(HAMMOND_ENABLE_MIDI)
    include("${PROJECT_SOURCE_DIR}/cmake/VerifyRtMidi.cmake")
    hammond_add_rtmidi(hammond_rtmidi "${HAMMOND_RTMIDI_ROOT}")
    target_link_libraries(hammond_standalone_support PRIVATE hammond_rtmidi)
    if(HAMMOND_ENABLE_SANITIZERS)
        target_compile_options(hammond_rtmidi PRIVATE
            -fsanitize=address,undefined -fno-omit-frame-pointer)
        target_link_options(hammond_rtmidi PUBLIC -fsanitize=address,undefined)
    endif()
endif()
hammond_configure_target(hammond_standalone_support)

set(HAMMOND_STANDALONE_TEST_TARGETS)
if(BUILD_TESTING)
    file(GLOB HAMMOND_STANDALONE_CPP_TESTS CONFIGURE_DEPENDS
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_*.cpp")
    foreach(test_source IN LISTS HAMMOND_STANDALONE_CPP_TESTS)
        get_filename_component(test_name "${test_source}" NAME_WE)
        add_executable(${test_name} "${test_source}")
        target_link_libraries(${test_name} PRIVATE hammond_standalone_support Threads::Threads)
        target_include_directories(${test_name} PRIVATE "${PROJECT_SOURCE_DIR}/tests")
        target_compile_definitions(${test_name} PRIVATE
            HAMMOND_TEST_PROFILE="${HAMMOND_COMPILED_PROFILE}"
            HAMMOND_SOURCE_DIR="${PROJECT_SOURCE_DIR}")
        hammond_configure_target(${test_name})
        add_dependencies(${test_name} hammond_profile)
        add_test(NAME ${test_name} COMMAND ${test_name})
        if(test_name STREQUAL "test_standalone_midi_concurrency")
            set_tests_properties(${test_name} PROPERTIES TIMEOUT 45 LABELS "standalone;concurrency")
        endif()
        if(test_name STREQUAL "test_standalone_registration_library")
            set_tests_properties(${test_name} PROPERTIES TIMEOUT 30 LABELS "standalone;library;filesystem")
        endif()
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS ${test_name})
    endforeach()
    # Compile the unchanged transport adapter against a deterministic test-only
    # RtMidi API. This target needs neither RtMidi nor a native MIDI SDK, and
    # does not link the separately configured production backend object.
    if((CMAKE_SYSTEM_NAME STREQUAL "Linux" AND NOT ANDROID) OR
       CMAKE_SYSTEM_NAME STREQUAL "Windows" OR CMAKE_SYSTEM_NAME STREQUAL "Darwin")
        add_executable(test_standalone_midi_backend
            backend_tests/test_standalone_midi_backend.cpp MidiDevice.cpp MidiInput.cpp)
        target_include_directories(test_standalone_midi_backend BEFORE PRIVATE
            "${CMAKE_CURRENT_SOURCE_DIR}/backend_tests/fake"
            "${CMAKE_CURRENT_SOURCE_DIR}" "${PROJECT_SOURCE_DIR}/tests")
        target_compile_definitions(test_standalone_midi_backend PRIVATE HAMMOND_HAS_RTMIDI=1)
        target_link_libraries(test_standalone_midi_backend PRIVATE hammond_core Threads::Threads)
        hammond_configure_target(test_standalone_midi_backend)
        add_test(NAME test_standalone_midi_backend
            COMMAND test_standalone_midi_backend --ordinary)
        add_test(NAME test_standalone_midi_backend_quarantine
            COMMAND test_standalone_midi_backend --quarantine)
        set_tests_properties(test_standalone_midi_backend PROPERTIES
            TIMEOUT 30 LABELS "standalone;backend")
        # Only these injected failed-close cases intentionally retain a callback
        # context until process exit. Ordinary destruction keeps the normal leak
        # policy, while memory/undefined-behavior instrumentation remains active here.
        set_tests_properties(test_standalone_midi_backend_quarantine PROPERTIES
            TIMEOUT 30 LABELS "standalone;backend;intentional-quarantine"
            ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0:halt_on_error=1")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_midi_backend)
    endif()
endif()

include("${PROJECT_SOURCE_DIR}/cmake/StandaloneBenchmark.cmake")

if(HAMMOND_BUILD_STANDALONE)
    include("${PROJECT_SOURCE_DIR}/cmake/VerifySdl2.cmake")
    hammond_verify_sdl2("${HAMMOND_SDL2_ROOT}")
    # SDL includes GNUInstallDirs before our final install rules. Preserve the
    # distinction between its automatic empty-cache sentinel and a caller's
    # explicitly empty DATADIR by materializing a not-yet-specified default now.
    # The shared install module continues to track DATAROOTDIR on reconfigure.
    if(NOT DEFINED CMAKE_INSTALL_DATADIR)
        include(GNUInstallDirs)
        set(CMAKE_INSTALL_DATADIR "${CMAKE_INSTALL_DATADIR}" CACHE PATH
            "Read-only architecture-independent data (DATAROOTDIR)" FORCE)
        set(_HAMMOND_LAST_AUTOMATIC_DATADIR "${CMAKE_INSTALL_DATADIR}" CACHE INTERNAL
            "Last materialized automatic data directory" FORCE)
    endif()
    enable_language(C)
    set(SDL_SHARED OFF CACHE BOOL "Standalone uses the pinned static SDL2 library" FORCE)
    set(SDL_STATIC ON CACHE BOOL "Standalone uses the pinned static SDL2 library" FORCE)
    set(SDL_TEST OFF CACHE BOOL "Do not build SDL2 test support" FORCE)
    set(SDL_TESTS OFF CACHE BOOL "Do not build SDL2 example tests" FORCE)
    set(SDL2_DISABLE_INSTALL ON CACHE BOOL "Project owns its standalone install payload" FORCE)
    set(SDL2_DISABLE_SDL2MAIN ON CACHE BOOL "The application provides its portable entry point" FORCE)
    add_subdirectory("${HAMMOND_SDL2_ROOT}" "${CMAKE_BINARY_DIR}/_sdl2" EXCLUDE_FROM_ALL)

    add_library(hammond_standalone_replay STATIC ScriptedInput.cpp)
    target_link_libraries(hammond_standalone_replay PUBLIC SDL2::SDL2-static)
    target_include_directories(hammond_standalone_replay PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
    target_compile_definitions(hammond_standalone_replay PRIVATE SDL_MAIN_HANDLED)
    hammond_configure_target(hammond_standalone_replay)

    add_library(hammond_standalone_audio STATIC AudioDevice.cpp)
    target_link_libraries(hammond_standalone_audio PUBLIC hammond_standalone_support SDL2::SDL2-static)
    target_compile_definitions(hammond_standalone_audio PRIVATE SDL_MAIN_HANDLED)
    hammond_configure_target(hammond_standalone_audio)

    set(HAMMOND_STANDALONE_PROFILE "${CMAKE_CURRENT_BINARY_DIR}/generated/EmbeddedProfile.h")
    add_custom_command(
        OUTPUT "${HAMMOND_STANDALONE_PROFILE}"
        COMMAND "${Python3_EXECUTABLE}" "${PROJECT_SOURCE_DIR}/tools/embed_profile.py"
            --input "${HAMMOND_COMPILED_PROFILE}" --output "${HAMMOND_STANDALONE_PROFILE}"
        DEPENDS "${PROJECT_SOURCE_DIR}/tools/embed_profile.py" "${HAMMOND_COMPILED_PROFILE}"
        COMMENT "Embedding the unchanged nominal profile in the standalone instrument"
        VERBATIM)
    set(HAMMOND_REFERENCE_ART "${CMAKE_CURRENT_BINARY_DIR}/generated/ReferenceArtData.h")
    add_custom_command(
        OUTPUT "${HAMMOND_REFERENCE_ART}"
        COMMAND "${Python3_EXECUTABLE}" "${PROJECT_SOURCE_DIR}/tools/compile_reference_art.py"
            --input "${PROJECT_SOURCE_DIR}/assets/standalone/reference/manifest.json"
            --source "${PROJECT_SOURCE_DIR}/docs/design/atlas-cover-reference.jpg"
            --output "${HAMMOND_REFERENCE_ART}"
        DEPENDS "${PROJECT_SOURCE_DIR}/tools/compile_reference_art.py"
            "${PROJECT_SOURCE_DIR}/assets/standalone/reference/manifest.json"
            "${PROJECT_SOURCE_DIR}/assets/standalone/reference/cabinet.rgb.gz"
            "${PROJECT_SOURCE_DIR}/assets/standalone/reference/left-wood-cheek.rgb.gz"
            "${PROJECT_SOURCE_DIR}/assets/standalone/reference/right-wood-cheek.rgb.gz"
            "${PROJECT_SOURCE_DIR}/docs/design/atlas-cover-reference.jpg"
        COMMENT "Verifying and embedding exact decorative reference pixels"
        VERBATIM)
    set(HAMMOND_REFERENCE_APRON "${CMAKE_CURRENT_BINARY_DIR}/generated/ReferenceApronData.h")
    add_custom_command(
        OUTPUT "${HAMMOND_REFERENCE_APRON}"
        COMMAND "${Python3_EXECUTABLE}" "${PROJECT_SOURCE_DIR}/tools/compile_reference_apron.py"
            --input "${PROJECT_SOURCE_DIR}/assets/standalone/reference-apron-v1/manifest.json"
            --source "${PROJECT_SOURCE_DIR}/docs/design/atlas-cover-reference.jpg"
            --output "${HAMMOND_REFERENCE_APRON}"
        DEPENDS "${PROJECT_SOURCE_DIR}/tools/compile_reference_apron.py"
            "${PROJECT_SOURCE_DIR}/assets/standalone/reference-apron-v1/manifest.json"
            "${PROJECT_SOURCE_DIR}/assets/standalone/reference-apron-v1/apron.rgba.gz"
            "${PROJECT_SOURCE_DIR}/docs/design/atlas-cover-reference.jpg"
        COMMENT "Verifying and embedding the exact masked reference apron"
        VERBATIM)
    add_library(hammond_standalone_drawing STATIC Drawing.cpp
        "${HAMMOND_REFERENCE_ART}" "${HAMMOND_REFERENCE_APRON}")
    target_link_libraries(hammond_standalone_drawing PUBLIC SDL2::SDL2-static)
    target_include_directories(hammond_standalone_drawing
        PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}" "${PROJECT_SOURCE_DIR}/include"
        PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/generated")
    target_compile_definitions(hammond_standalone_drawing PRIVATE SDL_MAIN_HANDLED)
    hammond_configure_target(hammond_standalone_drawing)
    add_executable(hammond_standalone
        main.cpp InstrumentView.cpp "${HAMMOND_STANDALONE_PROFILE}")
    target_link_libraries(hammond_standalone PRIVATE
        hammond_standalone_audio hammond_standalone_replay hammond_standalone_drawing)
    target_include_directories(hammond_standalone PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/generated")
    target_compile_definitions(hammond_standalone PRIVATE SDL_MAIN_HANDLED)
    hammond_configure_target(hammond_standalone)
    add_dependencies(hammond_standalone hammond_profile)
    # Manual software-paint measurement; deliberately not a timing CTest gate.
    add_executable(hammond_standalone_paint_benchmark
        "${PROJECT_SOURCE_DIR}/tools/standalone_paint_benchmark.cpp" InstrumentView.cpp)
    target_link_libraries(hammond_standalone_paint_benchmark PRIVATE
        hammond_standalone_drawing hammond_standalone_support)
    target_compile_definitions(hammond_standalone_paint_benchmark PRIVATE SDL_MAIN_HANDLED)
    hammond_configure_target(hammond_standalone_paint_benchmark)
    if(BUILD_TESTING)
        # The identical fixture is first retained against the genuine pre-edit
        # painter; the independent paired checker owns all change allowances.
        add_executable(test_standalone_reference_apron_raster
            native_tests/test_standalone_reference_apron_raster.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_reference_apron_raster PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_reference_apron_raster PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_reference_apron_raster)
        add_test(NAME test_standalone_reference_apron_raster
            COMMAND test_standalone_reference_apron_raster)
        set_tests_properties(test_standalone_reference_apron_raster PROPERTIES
            TIMEOUT 60 LABELS "standalone;native;reference-apron")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_reference_apron_raster)
        add_executable(test_standalone_reference_apron_art
            native_tests/test_standalone_reference_apron_art.cpp "${HAMMOND_REFERENCE_APRON}")
        target_link_libraries(test_standalone_reference_apron_art PRIVATE hammond_standalone_drawing)
        target_include_directories(test_standalone_reference_apron_art PRIVATE
            "${CMAKE_CURRENT_BINARY_DIR}/generated")
        target_compile_definitions(test_standalone_reference_apron_art PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_reference_apron_art)
        add_test(NAME test_standalone_reference_apron_art COMMAND test_standalone_reference_apron_art)
        set_tests_properties(test_standalone_reference_apron_art PROPERTIES
            TIMEOUT 30 LABELS "standalone;native;reference-apron")

        # Test-only failure injection compiles the same production Drawing and
        # pairs the same frozen fixture with genuine optional-texture failure.
        add_library(hammond_standalone_drawing_apron_unavailable STATIC Drawing.cpp
            "${HAMMOND_REFERENCE_ART}" "${HAMMOND_REFERENCE_APRON}")
        target_link_libraries(hammond_standalone_drawing_apron_unavailable PUBLIC SDL2::SDL2-static)
        target_include_directories(hammond_standalone_drawing_apron_unavailable
            PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}" "${PROJECT_SOURCE_DIR}/include"
            PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/generated")
        target_compile_definitions(hammond_standalone_drawing_apron_unavailable PRIVATE
            SDL_MAIN_HANDLED SDL_CreateTexture=hammond_test_create_texture)
        hammond_configure_target(hammond_standalone_drawing_apron_unavailable)
        add_executable(test_standalone_reference_apron_unavailable
            native_tests/test_standalone_reference_apron_raster.cpp
            native_tests/reference_apron_unavailable_texture.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_reference_apron_unavailable PRIVATE
            hammond_standalone_drawing_apron_unavailable hammond_standalone_support)
        target_compile_definitions(test_standalone_reference_apron_unavailable PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_reference_apron_unavailable)
        add_test(NAME test_standalone_reference_apron_unavailable
            COMMAND test_standalone_reference_apron_unavailable)
        set_tests_properties(test_standalone_reference_apron_unavailable PROPERTIES
            TIMEOUT 60 LABELS "standalone;native;reference-apron;fallback")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS
            test_standalone_reference_apron_art test_standalone_reference_apron_unavailable)
        add_executable(test_standalone_drawing native_tests/test_standalone_drawing.cpp)
        target_link_libraries(test_standalone_drawing PRIVATE hammond_standalone_drawing)
        target_compile_definitions(test_standalone_drawing PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_drawing)
        add_test(NAME test_standalone_drawing COMMAND test_standalone_drawing)
        set_tests_properties(test_standalone_drawing PROPERTIES
            TIMEOUT 15 LABELS "standalone;native")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_drawing)
        add_executable(test_standalone_quad_drawing native_tests/test_standalone_quad_drawing.cpp)
        target_link_libraries(test_standalone_quad_drawing PRIVATE hammond_standalone_drawing)
        target_compile_definitions(test_standalone_quad_drawing PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_quad_drawing)
        add_test(NAME test_standalone_quad_drawing COMMAND test_standalone_quad_drawing)
        set_tests_properties(test_standalone_quad_drawing PROPERTIES
            TIMEOUT 30 LABELS "standalone;native;geometry")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_quad_drawing)
        add_executable(test_standalone_workspace_raster
            native_tests/test_standalone_workspace_raster.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_workspace_raster PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_workspace_raster PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_workspace_raster)
        add_test(NAME test_standalone_workspace_raster COMMAND test_standalone_workspace_raster)
        set_tests_properties(test_standalone_workspace_raster PROPERTIES
            TIMEOUT 60 LABELS "standalone;native;workspace;geometry")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_workspace_raster)
        add_executable(test_standalone_inspection_raster
            native_tests/test_standalone_inspection_raster.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_inspection_raster PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_inspection_raster PRIVATE
            SDL_MAIN_HANDLED
            HAMMOND_TEST_PROFILE="${HAMMOND_COMPILED_PROFILE}"
            HAMMOND_TEST_SOURCE_ROOT="${PROJECT_SOURCE_DIR}")
        hammond_configure_target(test_standalone_inspection_raster)
        add_dependencies(test_standalone_inspection_raster hammond_profile)
        add_test(NAME test_standalone_inspection_raster COMMAND test_standalone_inspection_raster)
        set_tests_properties(test_standalone_inspection_raster PROPERTIES
            TIMEOUT 60 LABELS "standalone;native;inspection")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_inspection_raster)
        add_executable(test_standalone_material_acceptance
            native_tests/test_standalone_material_acceptance.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_material_acceptance PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_material_acceptance PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_material_acceptance)
        add_test(NAME test_standalone_material_acceptance COMMAND test_standalone_material_acceptance)
        set_tests_properties(test_standalone_material_acceptance PROPERTIES
            TIMEOUT 60 LABELS "standalone;native;material;geometry")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_material_acceptance)
        add_executable(test_standalone_waveform_material
            native_tests/test_standalone_waveform_material.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_waveform_material PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_waveform_material PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_waveform_material)
        add_test(NAME test_standalone_waveform_material COMMAND test_standalone_waveform_material)
        set_tests_properties(test_standalone_waveform_material PROPERTIES
            TIMEOUT 60 LABELS "standalone;native;material;geometry")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_waveform_material)
        add_executable(test_standalone_product_visual
            native_tests/test_standalone_product_visual.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_product_visual PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_product_visual PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_product_visual)
        add_test(NAME test_standalone_product_visual COMMAND test_standalone_product_visual)
        set_tests_properties(test_standalone_product_visual PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;material;geometry")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_product_visual PROPERTIES TIMEOUT 240)
        endif()
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_product_visual)
        add_executable(test_standalone_percussion_raster
            native_tests/test_standalone_percussion_raster.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_percussion_raster PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_percussion_raster PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_percussion_raster)
        add_test(NAME test_standalone_percussion_raster COMMAND test_standalone_percussion_raster)
        set_tests_properties(test_standalone_percussion_raster PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;percussion;geometry")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_percussion_raster PROPERTIES TIMEOUT 240)
        endif()
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_percussion_raster)
        add_executable(test_standalone_upper_rack_material_raster
            native_tests/test_standalone_upper_rack_material_raster.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_upper_rack_material_raster PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_upper_rack_material_raster PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_upper_rack_material_raster)
        add_test(NAME test_standalone_upper_rack_material_raster
            COMMAND test_standalone_upper_rack_material_raster)
        set_tests_properties(test_standalone_upper_rack_material_raster PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;material;geometry")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_upper_rack_material_raster PROPERTIES TIMEOUT 240)
        endif()
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_upper_rack_material_raster)
        add_executable(test_standalone_lower_rack_material_raster
            native_tests/test_standalone_lower_rack_material_raster.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_lower_rack_material_raster PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_lower_rack_material_raster PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_lower_rack_material_raster)
        add_test(NAME test_standalone_lower_rack_material_raster
            COMMAND test_standalone_lower_rack_material_raster)
        set_tests_properties(test_standalone_lower_rack_material_raster PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;material;geometry")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_lower_rack_material_raster PROPERTIES TIMEOUT 240)
        endif()
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_lower_rack_material_raster)
        add_executable(test_standalone_footage_typography_raster
            native_tests/test_standalone_footage_typography_raster.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_footage_typography_raster PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_footage_typography_raster PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_footage_typography_raster)
        add_test(NAME test_standalone_footage_typography_raster
            COMMAND test_standalone_footage_typography_raster)
        set_tests_properties(test_standalone_footage_typography_raster PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;typography;geometry")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_footage_typography_raster PROPERTIES TIMEOUT 240)
        endif()
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_footage_typography_raster)
        add_test(NAME test_standalone_title_density
            COMMAND "${Python3_EXECUTABLE}" -B
                "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_title_density.py"
                --executable "$<TARGET_FILE:test_standalone_footage_typography_raster>")
        set_tests_properties(test_standalone_title_density PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;typography")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_title_density PROPERTIES TIMEOUT 240)
        endif()
        add_executable(test_standalone_typography_clips
            native_tests/test_standalone_typography_clips.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_typography_clips PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_typography_clips PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_typography_clips)
        add_test(NAME test_standalone_typography_clips
            COMMAND test_standalone_typography_clips)
        set_tests_properties(test_standalone_typography_clips PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;typography;geometry")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_typography_clips PROPERTIES TIMEOUT 240)
        endif()
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_typography_clips)
        # The fixture includes the real painter to inspect the private material
        # helper without adding a production test API or a before-image switch.
        add_executable(test_standalone_header_material
            native_tests/test_standalone_header_material.cpp)
        target_link_libraries(test_standalone_header_material PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_header_material PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_header_material)
        add_test(NAME test_standalone_header_material
            COMMAND test_standalone_header_material)
        set_tests_properties(test_standalone_header_material PROPERTIES
            TIMEOUT 180 LABELS "standalone;native;material;geometry")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_header_material PROPERTIES TIMEOUT 480)
        endif()
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_header_material)
        set(HAMMOND_HEADER_STATISTICS_CHILD_TIMEOUT 20)
        if(HAMMOND_ENABLE_SANITIZERS)
            set(HAMMOND_HEADER_STATISTICS_CHILD_TIMEOUT 60)
        endif()
        add_test(NAME test_standalone_header_statistics
            COMMAND "${Python3_EXECUTABLE}" -B
                "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_header_statistics.py"
                --executable "$<TARGET_FILE:test_standalone_header_material>"
                --timeout-seconds "${HAMMOND_HEADER_STATISTICS_CHILD_TIMEOUT}")
        set_tests_properties(test_standalone_header_statistics PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;material")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_header_statistics PROPERTIES TIMEOUT 240)
        endif()
        # Like the full header fixture, this regression includes the painter
        # exactly once and exposes no production test hook.
        add_executable(test_standalone_header_grain_bounds
            native_tests/test_standalone_header_grain_bounds.cpp)
        target_link_libraries(test_standalone_header_grain_bounds PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_header_grain_bounds PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_header_grain_bounds)
        add_test(NAME test_standalone_header_grain_bounds
            COMMAND test_standalone_header_grain_bounds)
        set_tests_properties(test_standalone_header_grain_bounds PROPERTIES
            TIMEOUT 30 LABELS "standalone;native;material;geometry")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_header_grain_bounds PROPERTIES TIMEOUT 90)
        endif()
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_header_grain_bounds)
        add_executable(test_standalone_manual_key_material_raster
            native_tests/test_standalone_manual_key_material_raster.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_manual_key_material_raster PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_manual_key_material_raster PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_manual_key_material_raster)
        add_test(NAME test_standalone_manual_key_material_raster
            COMMAND test_standalone_manual_key_material_raster)
        set_tests_properties(test_standalone_manual_key_material_raster PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;material;geometry")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_manual_key_material_raster PROPERTIES TIMEOUT 240)
        endif()
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_manual_key_material_raster)
        add_executable(test_standalone_keyboard_rim_raster
            native_tests/test_standalone_keyboard_rim_raster.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_keyboard_rim_raster PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_keyboard_rim_raster PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_keyboard_rim_raster)
        add_test(NAME test_standalone_keyboard_rim_raster
            COMMAND test_standalone_keyboard_rim_raster)
        set_tests_properties(test_standalone_keyboard_rim_raster PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;rim;geometry")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_keyboard_rim_raster PROPERTIES TIMEOUT 240)
        endif()
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_keyboard_rim_raster)
        add_executable(test_standalone_scaled_view
            native_tests/test_standalone_scaled_view.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_scaled_view PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_scaled_view PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_scaled_view)
        add_test(NAME test_standalone_scaled_view COMMAND test_standalone_scaled_view)
        set_tests_properties(test_standalone_scaled_view PROPERTIES
            TIMEOUT 60 LABELS "standalone;native;workspace")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_scaled_view)
        add_executable(test_standalone_preset_raster
            native_tests/test_standalone_preset_raster.cpp InstrumentView.cpp)
        target_link_libraries(test_standalone_preset_raster PRIVATE
            hammond_standalone_drawing hammond_standalone_support)
        target_compile_definitions(test_standalone_preset_raster PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_preset_raster)
        add_test(NAME test_standalone_preset_raster COMMAND test_standalone_preset_raster)
        set_tests_properties(test_standalone_preset_raster PROPERTIES
            TIMEOUT 30 LABELS "standalone;native")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS test_standalone_preset_raster)
        if(HAMMOND_ENABLE_SANITIZERS)
            # Full SDL C and project C++ instrumentation measured 75/173/129 s
            # for these unchanged assertions (interface continuation A41).
            # Preserve ordinary Release deadlines; memory checking has separate
            # bounded budgets and is not a rendering-performance qualification.
            set_tests_properties(test_standalone_workspace_raster PROPERTIES TIMEOUT 180)
            set_tests_properties(test_standalone_scaled_view PROPERTIES TIMEOUT 360)
            set_tests_properties(test_standalone_preset_raster PROPERTIES TIMEOUT 300)
        endif()
        add_executable(test_standalone_audio_device native_tests/test_standalone_audio_device.cpp)
        target_link_libraries(test_standalone_audio_device PRIVATE hammond_standalone_audio)
        target_include_directories(test_standalone_audio_device PRIVATE "${PROJECT_SOURCE_DIR}/tests")
        target_compile_definitions(test_standalone_audio_device PRIVATE
            SDL_MAIN_HANDLED
            HAMMOND_TEST_PROFILE="${HAMMOND_COMPILED_PROFILE}"
            HAMMOND_SOURCE_DIR="${PROJECT_SOURCE_DIR}")
        hammond_configure_target(test_standalone_audio_device)
        add_dependencies(test_standalone_audio_device hammond_profile)
        add_test(NAME test_standalone_audio_device COMMAND test_standalone_audio_device)
        set_tests_properties(test_standalone_audio_device PROPERTIES
            ENVIRONMENT "SDL_AUDIODRIVER=dummy" TIMEOUT 15)
        add_executable(test_standalone_device_removal native_tests/test_standalone_device_removal.cpp)
        target_link_libraries(test_standalone_device_removal PRIVATE hammond_standalone_audio)
        target_include_directories(test_standalone_device_removal PRIVATE "${PROJECT_SOURCE_DIR}/tests")
        target_compile_definitions(test_standalone_device_removal PRIVATE
            SDL_MAIN_HANDLED
            HAMMOND_TEST_PROFILE="${HAMMOND_COMPILED_PROFILE}"
            HAMMOND_SOURCE_DIR="${PROJECT_SOURCE_DIR}")
        hammond_configure_target(test_standalone_device_removal)
        add_dependencies(test_standalone_device_removal hammond_profile)
        add_test(NAME test_standalone_device_removal COMMAND test_standalone_device_removal)
        set_tests_properties(test_standalone_device_removal PROPERTIES
            ENVIRONMENT "SDL_AUDIODRIVER=dummy" TIMEOUT 15 LABELS "standalone;native")
        # Only this test recompilation replaces SDL_OpenAudioDevice with a
        # recording trampoline. The production application links the ordinary
        # AudioDevice object; the probe still delegates to real SDL callbacks.
        add_library(hammond_standalone_allocation_object OBJECT AudioDevice.cpp)
        target_link_libraries(hammond_standalone_allocation_object PRIVATE
            hammond_standalone_support SDL2::SDL2-static)
        target_compile_definitions(hammond_standalone_allocation_object PRIVATE
            SDL_MAIN_HANDLED SDL_OpenAudioDevice=hammond_probe_open_audio_device)
        hammond_configure_target(hammond_standalone_allocation_object)
        add_executable(test_standalone_callback_allocation
            native_tests/test_standalone_callback_allocation.cpp
            $<TARGET_OBJECTS:hammond_standalone_allocation_object>)
        target_link_libraries(test_standalone_callback_allocation PRIVATE
            hammond_standalone_support SDL2::SDL2-static)
        target_include_directories(test_standalone_callback_allocation PRIVATE "${PROJECT_SOURCE_DIR}/tests")
        target_compile_definitions(test_standalone_callback_allocation PRIVATE
            SDL_MAIN_HANDLED
            HAMMOND_TEST_PROFILE="${HAMMOND_COMPILED_PROFILE}"
            HAMMOND_SOURCE_DIR="${PROJECT_SOURCE_DIR}")
        hammond_configure_target(test_standalone_callback_allocation)
        add_dependencies(test_standalone_callback_allocation hammond_profile)
        add_test(NAME test_standalone_callback_allocation COMMAND test_standalone_callback_allocation)
        set_tests_properties(test_standalone_callback_allocation PROPERTIES
            ENVIRONMENT "SDL_AUDIODRIVER=dummy" TIMEOUT 15)
        add_test(NAME test_standalone_app
            COMMAND "${CMAKE_COMMAND}" -E env
                "HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>"
                "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_app.py")
        set_tests_properties(test_standalone_app PROPERTIES TIMEOUT 60 LABELS "standalone;native")
        add_test(NAME test_standalone_midi_cli
            COMMAND "${CMAKE_COMMAND}" -E env
                "HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>"
                "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_midi_cli.py")
        set_tests_properties(test_standalone_midi_cli PROPERTIES TIMEOUT 90 LABELS "standalone;native;midi")
        add_test(NAME test_standalone_expression_diagnostics
            COMMAND "${CMAKE_COMMAND}" -E env
                "HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>"
                "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_expression_diagnostics.py")
        set_tests_properties(test_standalone_expression_diagnostics PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;midi")
        # Test-only dependency substitution around the unchanged native app and
        # transport; the shipped executable retains its configured backend.
        if((CMAKE_SYSTEM_NAME STREQUAL "Linux" AND NOT ANDROID) OR
           CMAKE_SYSTEM_NAME STREQUAL "Windows" OR CMAKE_SYSTEM_NAME STREQUAL "Darwin")
            add_executable(hammond_standalone_calibration_probe
                native_tests/calibration_lifecycle_driver.cpp MidiDevice.cpp
                InstrumentView.cpp "${HAMMOND_STANDALONE_PROFILE}")
            target_include_directories(hammond_standalone_calibration_probe BEFORE PRIVATE
                "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/fake_calibration"
                "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}/generated")
            target_compile_definitions(hammond_standalone_calibration_probe PRIVATE
                SDL_MAIN_HANDLED HAMMOND_HAS_RTMIDI=1)
            target_link_libraries(hammond_standalone_calibration_probe PRIVATE
                hammond_standalone_audio hammond_standalone_replay hammond_standalone_drawing)
            hammond_configure_target(hammond_standalone_calibration_probe)
            if(MINGW)
                target_link_options(hammond_standalone_calibration_probe PRIVATE -municode)
            endif()
            add_dependencies(hammond_standalone_calibration_probe hammond_profile)
            add_test(NAME test_standalone_native_calibration
                COMMAND "${CMAKE_COMMAND}" -E env
                    "HAMMOND_STANDALONE_CALIBRATION_PROBE=$<TARGET_FILE:hammond_standalone_calibration_probe>"
                    "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_native_calibration.py")
            set_tests_properties(test_standalone_native_calibration PROPERTIES
                TIMEOUT 90 LABELS "standalone;native;midi")
            if(HAMMOND_ENABLE_SANITIZERS)
                # Ten instrumented subprocesses retain their individual 15 s
                # limits; leave bounded room for the complete lifecycle suite.
                set_tests_properties(test_standalone_native_calibration PROPERTIES TIMEOUT 180)
            endif()
            list(APPEND HAMMOND_STANDALONE_TEST_TARGETS hammond_standalone_calibration_probe)
        endif()
        add_test(NAME test_standalone_native_midi_replay
            COMMAND "${CMAKE_COMMAND}" -E env
                "HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>"
                "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_midi_replay.py")
        set_tests_properties(test_standalone_native_midi_replay PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;midi")
        add_test(NAME test_standalone_workflows
            COMMAND "${CMAKE_COMMAND}" -E env
                "HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>"
                "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_workflows.py")
        set_tests_properties(test_standalone_workflows PROPERTIES TIMEOUT 90 LABELS "standalone;native")
        add_test(NAME test_standalone_workspace_replay
            COMMAND "${CMAKE_COMMAND}" -E env
                "HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>"
                "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_workspace_replay.py")
        set_tests_properties(test_standalone_workspace_replay PROPERTIES
            TIMEOUT 90 LABELS "standalone;native;workspace")
        set(HAMMOND_REPLAY_PAINT_CHILD_TIMEOUT 12)
        if(HAMMOND_ENABLE_SANITIZERS)
            set(HAMMOND_REPLAY_PAINT_CHILD_TIMEOUT 30)
        endif()
        add_test(NAME test_standalone_replay_paint_boundary
            COMMAND "${Python3_EXECUTABLE}" -B
                "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_replay_paint_boundary.py"
                --executable "$<TARGET_FILE:hammond_standalone>"
                --timeout-seconds "${HAMMOND_REPLAY_PAINT_CHILD_TIMEOUT}")
        set_tests_properties(test_standalone_replay_paint_boundary PROPERTIES
            TIMEOUT 60 LABELS "standalone;native;workspace")
        if(HAMMOND_ENABLE_SANITIZERS)
            set_tests_properties(test_standalone_replay_paint_boundary PROPERTIES TIMEOUT 90)
        endif()
        add_test(NAME test_standalone_replay_boundaries
            COMMAND "${CMAKE_COMMAND}" -E env
                "HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>"
                "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_replay_boundaries.py")
        set_tests_properties(test_standalone_replay_boundaries PROPERTIES TIMEOUT 60 LABELS "standalone;native")
        add_test(NAME test_standalone_chapel
            COMMAND "${CMAKE_COMMAND}" -E env
                "HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>"
                "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_chapel.py")
        set_tests_properties(test_standalone_chapel PROPERTIES TIMEOUT 90 LABELS "standalone;native")
        add_test(NAME test_standalone_starter_load
            COMMAND "${CMAKE_COMMAND}" -E env
                "HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>"
                "HAMMOND_REGISTRATION_EXECUTABLE=$<TARGET_FILE:hammond_registration>"
                "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_starter_load.py")
        set_tests_properties(test_standalone_starter_load PROPERTIES
            TIMEOUT 60 LABELS "standalone;native;registration")
        add_executable(test_standalone_input_replay native_tests/test_standalone_input_replay.cpp)
        target_link_libraries(test_standalone_input_replay PRIVATE hammond_standalone_replay)
        target_compile_definitions(test_standalone_input_replay PRIVATE SDL_MAIN_HANDLED)
        hammond_configure_target(test_standalone_input_replay)
        add_test(NAME test_standalone_input_replay COMMAND test_standalone_input_replay)
        set_tests_properties(test_standalone_input_replay PROPERTIES
            ENVIRONMENT "SDL_VIDEODRIVER=dummy" TIMEOUT 15)
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS
            test_standalone_audio_device test_standalone_device_removal test_standalone_callback_allocation
            test_standalone_input_replay hammond_standalone)
        add_custom_target(hammond_standalone_test_inputs
            DEPENDS hammond_profile hammond_registration ${HAMMOND_STANDALONE_TEST_TARGETS})
    endif()

    if(MINGW)
        target_link_options(hammond_standalone PRIVATE -municode)
    endif()
endif()

set(HAMMOND_STANDALONE_TEST_TARGETS ${HAMMOND_STANDALONE_TEST_TARGETS} PARENT_SCOPE)
