from your_module import user_risk_analysis  # replace 'your_module' with the file where the function is
from your_module import moderate_content    # make sure moderate_content is imported too

# Example test user ID
user_id = 1

# Call the function
score = user_risk_analysis(user_id)

print(f"Risk score for user {user_id}: {score}")
