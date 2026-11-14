include_guard(GLOBAL)

# The runtime selector consumes only this immutable table. The documentary
# catalog stays available separately, with its original identity and limitations.
set(HAMMOND_FIXED_REGISTRATION_COMPILER "${PROJECT_SOURCE_DIR}/tools/compile_fixed_registrations.py")
set(HAMMOND_FIXED_REGISTRATION_AUTHORING "${PROJECT_SOURCE_DIR}/data/registrations/atlas-chapel-nominal-v1.json")
set(HAMMOND_FIXED_REGISTRATION_REVIEW_A "${PROJECT_SOURCE_DIR}/data/registrations/review-a-chapel.csv")
set(HAMMOND_FIXED_REGISTRATION_REVIEW_B "${PROJECT_SOURCE_DIR}/data/registrations/review-b-chapel.csv")
set(HAMMOND_FIXED_REGISTRATION_HEADER "${HAMMOND_GENERATED_INCLUDE_DIR}/hammond/generated/FixedRegistrationData.h")

add_custom_command(
    OUTPUT "${HAMMOND_FIXED_REGISTRATION_HEADER}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${HAMMOND_GENERATED_INCLUDE_DIR}/hammond/generated"
    COMMAND "${Python3_EXECUTABLE}" "${HAMMOND_FIXED_REGISTRATION_COMPILER}"
        --input "${HAMMOND_FIXED_REGISTRATION_AUTHORING}"
        --review-a "${HAMMOND_FIXED_REGISTRATION_REVIEW_A}"
        --review-b "${HAMMOND_FIXED_REGISTRATION_REVIEW_B}"
        --output "${HAMMOND_FIXED_REGISTRATION_HEADER}"
    DEPENDS "${HAMMOND_FIXED_REGISTRATION_COMPILER}"
        "${PROJECT_SOURCE_DIR}/tools/compile_chapel_presets.py"
        "${PROJECT_SOURCE_DIR}/data/chapel-presets.schema.json"
        "${HAMMOND_FIXED_REGISTRATION_AUTHORING}"
        "${HAMMOND_FIXED_REGISTRATION_REVIEW_A}" "${HAMMOND_FIXED_REGISTRATION_REVIEW_B}"
    COMMENT "Admitting both chapel readings and compiling the frozen fixed registrations"
    VERBATIM)
add_custom_target(hammond_fixed_registration_data DEPENDS "${HAMMOND_FIXED_REGISTRATION_HEADER}")
add_dependencies(hammond_core hammond_fixed_registration_data)
