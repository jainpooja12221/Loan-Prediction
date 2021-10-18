# Loan_approval
Request URL: http://127.0.0.1:5000/api/v1/prediction
Request Method: POST

Request payload: 
{
    "Gender": "Male",
    "Married": "No",
    "Dependents": "1",
    "Education": "Graduate",
    "Self_Employed": "Yes",
    "ApplicantIncome": 9963,
    "CoapplicantIncome": 0,
    "LoanAmount": 180,
    "Loan_Amount_Term": 360,
    "Credit_History":1,
    "Property_Area": "Rural"
}

Sample response: 
{
    "status": "success",
    "status_message": "Loan is approved"
}
