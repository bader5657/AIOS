from core.app.material_receipts.results import ReviewFailureCode
from core.app.material_receipts.review_use_cases import ReviewFacade
from core.material_receipts.errors import MaterialReceiptError, MaterialReceiptFailureCode


def test_source_active_failure_maps_to_bounded_public_duplicate():
    error = ReviewFacade._candidate_error(
        MaterialReceiptError(MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS)
    )
    assert error.code is ReviewFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS
    assert error.candidate_code is MaterialReceiptFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS
    assert error.args == (ReviewFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS.value,)


def test_unrelated_integrity_failure_remains_integrity_error():
    error = ReviewFacade._candidate_error(
        MaterialReceiptError(MaterialReceiptFailureCode.DATA_INTEGRITY_ERROR)
    )
    assert error.code is ReviewFailureCode.CANDIDATE_OPERATION_FAILED
    assert error.candidate_code is MaterialReceiptFailureCode.DATA_INTEGRITY_ERROR
