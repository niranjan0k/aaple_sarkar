from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render
import requests
import json
from utility.common import simple_triple_des, simple_triple_des_decrypt, generate_checksum_value,\
string_to_byte_array, byte_array_to_string, convert_xml_to_dataset, set_app_status

# Constants
ClientCode = "BMCDEPT"
CheckSumKey = "BMccDL9r5R2Z"
EncryptKey = "@bm@cde@m@h@0nl!ne@11823"
EncryptIV = "BMC@02@1"
ApplicationID = "8355-CBRRC-23-01613"
PayStatus = "N"
Digital_status = "N"
serviceDays = "120"
amount = "500.00"
RequestFlag = "0"
App_status = "2"
Remark = "PayTest"
District_id = "519"
ApplicationDate = "NA"
MobileNo = "9999999999"
Name = "ApplicantName"
return_url = "http://localhost:51861/Home/PayComplete"
ServiceID = "7083"


def login_pg(request, str):
    print("hello")
    # Decrypt the querystring and obtain token sent by AapleSarkar application
    url_value = str
    request_decrypted = simple_triple_des_decrypt(str, EncryptKey, EncryptIV)
    param = request_decrypted.split('|')

    if param and len(param) > 0:
        usr_id, usr_timestamp, usr_session, client_checksum_value, str_service_cookie = param

        # Validation of Checksum sent by AapleSarkar application
        chk_value_raw_data = f"{usr_id}|{usr_timestamp}|{usr_session}|{CheckSumKey}|{str_service_cookie}"
        calculated_checksum_value = generate_checksum_value(chk_value_raw_data)

        if client_checksum_value == calculated_checksum_value:
            # Send the initial request string received from AapleSarkar application again to AapleSarkar application for validation and other processing
            response_xml = requests.get(f'http://your-aaple-sarkar-url/{str}/{ClientCode}').text
            response_decrypted = simple_triple_des_decrypt(response_xml, EncryptKey, EncryptIV)
            ds = convert_xml_to_dataset(response_decrypted)

            if url_value:
                return render(request, 'department_form.html', {
                    'username': ds.get('Username', ''),
                    'password': ds.get('Password', ''),
                    'email': ds.get('EmailID', ''),
                    'mobile_no': ds.get('MobileNo', ''),
                    'full_name': ds.get('FullName', ''),
                    'full_name_in_marathi': ds.get('FullName_mr', ''),
                    'gender': ds.get('Gender', ''),
                    'date_of_birth': ds.get('DOB', ''),
                    'uid_no': ds.get('UIDNO', ''),
                    'pan_no': ds.get('PANNo', ''),
                    'track_id': ds.get('TrackId', ''),
                    'user_id': ds.get('UserID', ''),
                })
    return HttpResponseRedirect('/error-page')

def department_form(request, input=None):
    _PayDate = "NA"
    _DigitalDate = "NA"
    _ServiceDate = "NA"

    Request1 = f"{request.session.get('TrackId', 'NA')}|{ClientCode}|{request.session.get('UserID', 'NA')}|{ServiceID}|{ApplicationID}|{PayStatus}|{_PayDate}|{Digital_status}|{_DigitalDate}|{serviceDays}|{_ServiceDate}|{amount}|{RequestFlag}|{App_status}|{Remark}|NA|NA|NA|NA|NA|{CheckSumKey}"

    checksum_value = generate_checksum_value(Request1)
    
    Request2 = f"{request.session.get('TrackId', 'NA')}|{ClientCode}|{request.session.get('UserID', 'NA')}|{ServiceID}|{ApplicationID}|{PayStatus}|{_PayDate}|{Digital_status}|{_DigitalDate}|{serviceDays}|{_ServiceDate}|{amount}|{RequestFlag}|{App_status}|{Remark}|NA|NA|NA|NA|NA|{checksum_value}"

    EncKey = simple_triple_des(Request2, EncryptKey, EncryptIV)

    Response = set_app_status(EncKey, ClientCode)

    Response = simple_triple_des_decrypt(Response, EncryptKey, EncryptIV)

    # Redirect to payment
    return HttpResponseRedirect("/payment")

def payment(request):
    # Assuming all variables like ClientCode, CheckSumKey, etc., are defined earlier
    Response = "|".join([str(request.session["TrackId"]), ClientCode, str(request.session["UserID"]), ServiceID, ApplicationID, PayStatus, PayDate, Digital_status, DigitalDate, serviceDays, ServiceDate, amount, RequestFlag, App_status, Remark, "NA", "NA", "NA", "NA", "NA", CheckSumKey])

    checksumvalue = generate_checksum_value(Response)

    finalstring = "|".join([ClientCode, checksumvalue, ServiceID, ApplicationID, District_id, ApplicationDate, str(request.session["TrackId"]), str(request.session["UserID"]), MobileNo, Name, return_url, "NA", "NA", "NA", "NA", "NA"])


    EncyKey = simple_triple_des(finalstring, EncryptKey, EncryptIV)

    objstr = {"webstr": EncyKey, "deptcode": ClientCode}

    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    serialized_data = json.dumps(objstr)

    response = requests.post("https://testcitizenservices.mahaitgov.in/en/OutPayment/ValidateRequest", data=serialized_data, headers=headers)

    message = response.text

    _Key = "rJq/H6RcZ9x9D8RTbtRKcDGjhWQb4EN+r3rFZ1pUNL8="  # replace it with key received in message above

    return redirect(f"https://testcitizenservices.mahaitgov.in?webstr={objstr["webstr"]}&DeptCode={objstr["deptcode"]}&Authentication{_Key}")
