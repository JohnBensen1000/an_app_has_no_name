import matplotlib.pyplot as plt

def get_count_list(file_name):
    with open(file_name, "r") as file:
        file_lines = file.readlines()

    y_list = []

    for line in file_lines[1:]:
        line_data = line.split(",")
        y         = 0
        for data_point in line_data[1:]:
            if "undefined" not in data_point:
                y += float(data_point)

        y_list.append(y)

    return y_list

instance_count_list = get_count_list("instance_count_4_3_22.csv") 
response_count_list = get_count_list("response_count_4_3_22.csv") 

num_instance = 0
for instance_count in instance_count_list:
    num_instance += instance_count

num_response = 0
for response_count in response_count_list:
    num_response += response_count

print(num_instance / num_response)

# FEBRUARY 20, 2022 - APRIL 3, 2022 --> 31.34




