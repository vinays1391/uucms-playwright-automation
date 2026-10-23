"""Common lifecycle statuses for Ph.D and R&D workflows."""

PENDING = "Pending"
APPROVED = "Approved"
REJECTED = "Rejected"
RETURNED = "Returned"
IN_PROGRESS = "In Progress"
COMPLETED = "Completed"

# Synopsis submission master table (R&D Phase 1)
DATE_NOT_SETUP = "Date not Setup"
YET_TO_UPLOAD = "Yet to Upload"
AWAITING_APPROVAL = "Awaiting Approval"
SENT_BACK = "Sent Back"
DEADLINE_PASSED = "Deadline Passed"

# Synopsis "Action Pending With" master table
PENDING_WITH_STUDENT = "Student"
PENDING_WITH_GUIDE = "Guide"
PENDING_WITH_CO_GUIDE = "Co-Guide"
PENDING_WITH_GUIDE_AND_CO_GUIDE = "Guide & Co-Guide"
PENDING_WITH_DEPARTMENT_CHAIRPERSON = "Department Chairperson"
PENDING_WITH_DOCTORAL_COMMITTEE_CHAIRPERSON = "Doctoral Committee Chairperson"
PENDING_WITH_NONE = "None"

# Progress report submission master table (R&D Phase 2)
# The Phase-2 CSV renders the not-yet-uploaded state as "Yet to upload".
PROGRESS_YET_TO_UPLOAD = "Yet to upload"

# Final Viva Voce / Colloquium / Symposium statuses (R&D Phase 2)
YET_TO_SEND = "Yet to Send"
SCHEDULED = "Scheduled"
YET_TO_UPLOAD_DETAILS = "Yet to Upload Details"
