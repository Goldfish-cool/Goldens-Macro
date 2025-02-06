import ctypes
import json
from customtkinter import *
from PIL import Image, ImageDraw
import requests
import os

config_path = os.path.join(os.path.dirname(__file__), "config.json")
config_data = None

def get_current_version():
    return read_config()["current_version"]

def read_config(key=""):
    with open(config_path) as config_file:
        config_data = config_file.read()
        config_data = json.loads(config_data)
        if len(config_data) == 0:
            ctypes.windll.user32.MessageBoxW(0, "CONFIG DATA NOT FOUND", "Error", 0)
            exit(1)
        if not key == "":
            return config_data[key]
        return config_data

def save_config(config_data_p):
    global config_data
    with open(config_path, 'w') as config_file:
        json.dump(config_data_p, config_file, indent=4)
    config_data = read_config()

def iterate_generate_list(json_object, var_list):
    for i in range(len(json_object)):
        if type(json_object[i]) == dict:
            var_list[i] = {}
            iterate_generate_dict(json_object[i], var_list[i])
        elif type(json_object[i]) == list:
            var_list[i] = []
            iterate_generate_list(json_object[i], var_list[i])
        else:
            var_list.append(StringVar(value=json_object[i]))

def iterate_generate_dict(json_object, var_list):
    for key in json_object:
        if type(json_object[key]) == dict:
            var_list[key] = {}
            iterate_generate_dict(json_object[key], var_list[key])
        elif type(json_object[key]) == list:
            var_list[key] = []
            iterate_generate_list(json_object[key], var_list[key])
        else:
            var_list[key] = StringVar(value=json_object[key])

def generate_tk_list():
    config_data = read_config()
    tk_var_list = {}
    iterate_generate_dict(config_data, tk_var_list)
    return tk_var_list

def iterate_save_dict(json_object, var_list):
    for key in json_object:
        if type(var_list[key]) == dict:
            iterate_save_dict(json_object[key], var_list[key])
        elif type(var_list[key]) == list:
            iterate_save_list(json_object[key], var_list[key])
        elif type(var_list[key]) == str:
            json_object[key] = var_list[key]
        else:
            json_object[key] = var_list[key].get()

def iterate_save_list(json_object, var_list):
    for i in range(len(var_list)):
        if type(var_list[i]) == dict:
            iterate_save_dict(json_object[i], var_list[i])
        elif type(var_list[i]) == list:
            iterate_save_list(json_object[i], var_list[i])
        else:
            json_object[i] = var_list[i].get()

def save_tk_list(tk_var_list):
    config_data = read_config()
    iterate_save_dict(config_data, tk_var_list)
    save_config(config_data)

config_data = read_config()
