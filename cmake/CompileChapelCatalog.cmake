include_guard(GLOBAL)

set(HAMMOND_CHAPEL_COMPILER "${PROJECT_SOURCE_DIR}/tools/compile_chapel_presets.py")
set(HAMMOND_CHAPEL_AUTHORING "${PROJECT_SOURCE_DIR}/data/registrations/atlas-chapel-nominal-v1.json")
set(HAMMOND_CHAPEL_REVIEW_A "${PROJECT_SOURCE_DIR}/data/registrations/review-a-chapel.csv")
set(HAMMOND_CHAPEL_REVIEW_B "${PROJECT_SOURCE_DIR}/data/registrations/review-b-chapel.csv")
set(HAMMOND_CHAPEL_CATALOG "${PROJECT_BINARY_DIR}/chapel-catalog.json")

add_custom_command(
    OUTPUT "${HAMMOND_CHAPEL_CATALOG}"
    COMMAND "${Python3_EXECUTABLE}" "${HAMMOND_CHAPEL_COMPILER}"
        --input "${HAMMOND_CHAPEL_AUTHORING}"
        --review-a "${HAMMOND_CHAPEL_REVIEW_A}"
        --review-b "${HAMMOND_CHAPEL_REVIEW_B}"
        --output "${HAMMOND_CHAPEL_CATALOG}"
    DEPENDS "${HAMMOND_CHAPEL_COMPILER}" "${HAMMOND_CHAPEL_AUTHORING}"
        "${HAMMOND_CHAPEL_REVIEW_A}" "${HAMMOND_CHAPEL_REVIEW_B}"
        "${PROJECT_SOURCE_DIR}/data/chapel-presets.schema.json"
    COMMENT "Admitting both documentary chapel preset readings"
    VERBATIM)
add_custom_target(hammond_chapel_catalog ALL DEPENDS "${HAMMOND_CHAPEL_CATALOG}")
