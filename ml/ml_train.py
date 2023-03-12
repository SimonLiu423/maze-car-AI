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
data_set = []
for file in allFile[:5]:
    if file[0] == '1':
        # print(file)
        with open(os.path.join(path, file), "rb") as f:
            data_set.append(pickle.load(f))

# feature
f_sensor = []
l_sensor = []
r_sensor = []
angle = []
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
        angle.append(data["scene_info"][i]["angle"])
        # target_angle.append(data["scene_info"][i]["target_angle"])
        # stuck_cnt.append(data["scene_info"][i]["stuck_cnt"])
        # direction.append(data["scene_info"][i]["direction"])
        # angle_diff.append(data["scene_info"][i]["angle_diff"])

        Y.append(data["action"][i])

Y = np.array(Y)
X = np.array([0, 0, 0, 0])
for i in range(len(f_sensor)):
    # X = np.vstack((X, [f_sensor[i], l_sensor[i], r_sensor[i], angle[i], target_angle[i], stuck_cnt[i], direction[i],
    #                    angle_diff[i]]))
    X = np.vstack((X, [f_sensor[i], l_sensor[i], r_sensor[i], angle[i]]))
X = X[1::]

# training
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

model = sklearn.neighbors.KNeighborsClassifier(n_neighbors=5)
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
