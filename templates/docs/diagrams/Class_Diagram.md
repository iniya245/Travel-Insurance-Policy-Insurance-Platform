# Class Diagram

User
------------------------
+ user_id
+ name
+ email
+ phone
+ password
------------------------
+ register()
+ login()

Policy
------------------------
+ policy_id
+ destination
+ travel_date
------------------------
+ applyPolicy()
+ viewPolicy()

Claim
------------------------
+ claim_id
+ policy_id
+ claim_reason
------------------------
+ submitClaim()

Admin
------------------------
+ admin_id
+ username
+ password
------------------------
+ login()
+ viewUsers()
+ viewPolicies()
+ viewClaims()