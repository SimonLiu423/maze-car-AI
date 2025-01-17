import pickle
import os

import sklearn.neighbors
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.tree import DecisionTreeRegressor
import math
from enum import IntEnum


class Action(IntEnum):
    STRAIGHT = 0
    LEFT = 1
    RIGHT = 2


path = "./log"
allFile = os.listdir(path)
allFile.sort()

data_set = []
prev_map = ''
cnt = 0
for file in allFile:
    frame_used = int(file.split('frame')[0].split('_')[1])
    # if frame_used > 3500:
    #     continue
    if prev_map == file[0]:
        if cnt >= 4:
            continue
        cnt += 1
    else:
        prev_map = file[0]
        cnt = 0
    print(file, cnt)
    with open(os.path.join(path, file), "rb") as f:
        data_set.append(pickle.load(f))
    break

# feature
f_sensor = []
l_sensor = []
r_sensor = []
lt_sensor = []
rt_sensor = []
# angle = []
# target_angle = []
# stuck_cnt = []
# direction = []
# angle_diff = []

Y = []

for data in data_set:
    for i, sceneInfo in enumerate(data["scene_info"]):
        f_sensor.append(data["scene_info"][i]["F_sensor"])
        l_sensor.append(data["scene_info"][i]["L_sensor"])
        r_sensor.append(data["scene_info"][i]["R_sensor"])
        lt_sensor.append(data["scene_info"][i]["L_T_sensor"])
        rt_sensor.append(data["scene_info"][i]["R_T_sensor"])
        # angle.append(data["scene_info"][i]["angle"])
        # target_angle.append(data["scene_info"][i]["target_angle"])
        # stuck_cnt.append(data["scene_info"][i]["stuck_cnt"])
        # direction.append(data["scene_info"][i]["direction"])
        # angle_diff.append(data["scene_info"][i]["angle_diff"])

        Y.append([data["action"][i]["left_PWM"], data["action"][i]["right_PWM"]])

Y = np.array(Y)
X = np.array([0, 0, 0, 0, 0])
for i in range(len(f_sensor)):
    # X = np.vstack((X, [f_sensor[i], l_sensor[i], r_sensor[i], angle[i], target_angle[i], stuck_cnt[i], direction[i],
    #                    angle_diff[i]]))
    X = np.vstack((X, [f_sensor[i], l_sensor[i], r_sensor[i], lt_sensor[i], rt_sensor[i]]))
X = X[1::]
print(X.shape, Y.shape)
print(X, Y)

# training
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

model = sklearn.tree.DecisionTreeRegressor()
model.fit(x_train, y_train)

# evaluation
y_predict = model.predict(x_test)
mse = mean_squared_error(y_test, y_predict)
print(mse)
rmse = math.sqrt(mse)
print("RMSE=%.2f" % rmse)

# save model
if not os.path.exists(os.path.dirname(__file__) + "/save"):
    os.makedirs(os.path.dirname(__file__) + "/save")
with open(os.path.join(os.path.dirname(__file__), 'save', "model.pickle"), 'wb') as f:
    pickle.dump(model, f)
