import pickle
import pandas as pd
from sklearn.impute import SimpleImputer
from flask import Flask, request

app = Flask(__name__)


@app.route("/api/v1/prediction", methods=["POST"])
def get_prediction():
    if request.method == "POST":
        data = request.json
        response = LoanPrediction().main(data)
        return response


class LoanPrediction:
    """
    This class will import the CSV containing the loan parameters and do the prediction for the input parameters
    """

    def __init__(self):
        self.model_name = "loan_prediction.sav"
        self.model = None
        self.response = dict()

    def load_model(self):

        try:
            self.model = pickle.load(open(self.model_name, 'rb'))

        except Exception as e:
            response = {
                "status": "Failed",
                "status_message": f"Failed to load model with exception {e}"
            }
            return response

        return True

    def create_json(self, data):

        df_json = {
            "ApplicantIncome": int(data['ApplicantIncome']),
            "CoapplicantIncome": int(data['CoapplicantIncome']),
            "LoanAmount": int(data["LoanAmount"]),
            "Loan_Amount_Term": int(data["Loan_Amount_Term"]),
            "Credit_History": int(data["Credit_History"])
        }
        if data['Dependents'] == '1':
            df_json["Dependents_1"] = 1
            df_json["Dependents_2"] = 0
            df_json["Dependents_3 + "] = 0
        elif data['Dependents'] == '3+':
            df_json["Dependents_1"] = 0
            df_json["Dependents_2"] = 0
            df_json["Dependents_3 + "] = 1
        elif data['Dependents'] == "2":
            df_json["Dependents_1"] = 0
            df_json["Dependents_2"] = 1
            df_json["Dependents_3 + "] = 0
        elif data["Dependents"] == "0":
            df_json["Dependents_1"] = 0
            df_json["Dependents_2"] = 0
            df_json["Dependents_3 + "] = 0

        if data['Education'] == "Graduate":
            df_json['Education_NotGraduate'] = 0
        elif data['Education'] == "Not Graduate":
            df_json['Education_NotGraduate'] = 1

        if data["Married"] == "No":
            df_json['Married_Yes'] = 0
        elif data["Married"] == "Yes":
            df_json['Married_Yes'] = 1

        if data["Self_Employed"] == "Yes":
            df_json["Self_Employed_Yes"] = 1
        elif data["Self_Employed"] == "No":
            df_json["Self_Employed_Yes"] = 0

        if data["Gender"] == "Male":
            df_json["Gender_Male"] = 1
        elif data["Gender"] == "Female":
            df_json["Gender_Male"] = 0

        if data["Property_Area"] == "Rural":
            df_json["Property_Area_Semiurban"] = 0
            df_json["Property_Area_Urban"] = 0
        elif data["Property_Area"] == "Semiurban":
            df_json["Property_Area_Semiurban"] = 1
            df_json["Property_Area_Urban"] = 0
        elif data["Property_Area"] == "Urban":
            df_json["Property_Area_Semiurban"] = 0
            df_json["Property_Area_Urban"] = 1

        return df_json

    def get_test_data(self, data):

        df = pd.DataFrame.from_dict([data])
        test_data_encoded = pd.get_dummies(df, drop_first=True)
        imp = SimpleImputer(strategy='mean')
        imp_train = imp.fit(test_data_encoded)
        test_data_encoded = imp_train.transform(test_data_encoded)
        print(self.model)
        y_prediction = self.model.predict(test_data_encoded)
        print(y_prediction)
        if y_prediction[0] == 1:
            loan_status = "Loan is approved"
        elif y_prediction[0] == 0:
            loan_status = "Loan is not approved"

        response = {
            "status": "success",
            "status_message": loan_status
        }
        return response

    def validation(self, data):

        dict_keys = ('Gender', 'Married', 'Dependents', 'Education', 'Self_Employed', 'ApplicantIncome',
                     'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term', 'Credit_History', 'Property_Area')

        self.response["status"] = "Fail"
        if len(data.keys()) > len(dict_keys):
            self.response['status_message'] = "Mandatory keys missing in the request"
            return self.response

        # Check and Remove extra keys from data
        extra_keys = []
        for k in data.keys():
            if k not in dict_keys:
                extra_keys.append(k)
        [data.pop(key) for key in extra_keys]

        if 'Gender' in data:
            if data["Gender"] not in ["Male", "Female"]:
                self.response["status_message"] = "Improper Gender data"
                return self.response

        if 'Married' in data:
            if data["Married"] not in ["Yes", "No"]:
                self.response["status_message"] = "Improper Marriage data"
                return self.response

        if 'Dependents' in data:
            if data["Dependents"] not in ["1", "2", "3+"]:
                self.response["status_message"] = "Improper Dependents data"
                return self.response

        if 'Education' in data:
            if data["Education"] not in ["Graduate", "Not Graduate"]:
                self.response["status_message"] = "Improper Education Data"
                return self.response

        if 'Self_Employed' in data:
            if data["Self_Employed"] not in ["Yes", "No"]:
                self.response["status_message"] = "Improper Self_Employed data"
                return self.response

        if 'Property_Area' in data:
            if data["Property_Area"] not in ["Urban", "Rural", "Semiurban"]:
                self.response["status_message"] = "Improper Property_Area data"
                return self.response

        self.response["status"] = "Success"
        self.response["status_message"] = "Validation Successful"
        return self.response

    def main(self, kwargs):
        data = kwargs

        data_validation = self.validation(data)
        if data_validation.get("status_message") == "Fail":
            return data_validation

        get_model = self.load_model()

        json_data = self.create_json(data)

        if get_model:
            predictions = self.get_test_data(json_data)
            return predictions
        else:
            return get_model


if __name__ == '__main__':
    app.run(debug=True)
