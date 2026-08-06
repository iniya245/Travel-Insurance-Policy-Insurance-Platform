# ER Diagram

USER
-------------------------
User_ID (PK)
Name
Email
Phone
Password
        |
        | 1 : M
        |
        V
POLICY
-------------------------
Policy_ID (PK)
User_ID (FK)
Destination
Travel_Date
Policy_Type
        |
        | 1 : M
        |
        V
CLAIM
-------------------------
Claim_ID (PK)
Policy_ID (FK)
Claim_Reason
Claim_Status

ADMIN
-------------------------
Admin_ID (PK)
Username
Password