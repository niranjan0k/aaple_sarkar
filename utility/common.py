from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from zeep import Client
import hashlib
import xml.etree.ElementTree as ET
from io import StringIO
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def simple_triple_des(data, str_key, str_iv):
    key = bytes(str_key, 'utf-8')
    iv = bytes(str_iv, 'utf-8')
    data_bytes = bytes(data, 'utf-8')
    tdes = DES3.new(key, DES3.MODE_CBC, iv)
    enc = tdes.encrypt(pad(data_bytes, DES3.block_size))
    return enc.hex()

def simple_triple_des_decrypt(data, str_key, str_iv):
    key = bytes(str_key, 'utf-8')
    iv = bytes(str_iv, 'utf-8')
    data_bytes = string_to_byte_array(data)
    tdes = DES3.new(key, DES3.MODE_CBC, iv)
    dec = unpad(tdes.decrypt(data_bytes), DES3.block_size)
    return dec.decode('utf-8')

def string_to_byte_array(hex_string):
    number_chars = len(hex_string)
    bytes_array = bytearray(number_chars // 2)
    for i in range(0, number_chars, 2):
        bytes_array[i // 2] = int(hex_string[i:i+2], 16)
    return bytes_array

def generate_checksum_value(req_str):
    ascii_encoding = 'ascii'
    checksum_value = hashlib.md5(req_str.encode(ascii_encoding)).hexdigest()
    return checksum_value



def byte_array_to_string(byte_array):
    hex_string = ''.join('{:02X}'.format(byte) for byte in byte_array)
    return hex_string

def convert_xml_to_dataset(xml_data):
    try:
        xml_ds = ET.parse(StringIO(xml_data))
        return xml_ds
    except Exception as e:
        print(f"Error while parsing XML: {e}")
        return None



def set_app_status(ency_key, dept_code):
    client = Client('http://tempuri.org/your-service-url?wsdl')
    result = client.service.SetAppStatus(ency_key, dept_code)
    return result

def get_parameter_new(ency_key, dept_code):
    client = Client('http://tempuri.org/your-service-url?wsdl')
    result = client.service.GetParameterNew(ency_key, dept_code)
    return result