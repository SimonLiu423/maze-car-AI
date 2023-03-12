import pickle
import os

import sklearn.neighbors
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.tree import DecisionTreeRegressor
import math

path = "./log"
allFile = os.listdir(path)
data_set = []
for file in allFile:
    if file[0] == '1':
        # print(file)
        with open(os.path.join(path, file), "rb") as f:
            data_set.append(pickle.load(f))

# feature
car_x = []
car_y = []
dx = []
dy = []
f_sensor = []
lt_sensor = []
rt_sensor = []
angle = []
stuck_cnt = []

Y = []

for data in data_set:
    for i, sceneInfo in enumerate(data["scene_info"][:-1]):
        car_x.append(data["scene_info"][i+1]["x"])
        car_y.append(data["scene_info"][i+1]["y"])
        dx.append(data["scene_info"][i+1]["x"] - data["scene_info"][i]["x"])
        dy.append(data["scene_info"][i+1]["y"] - data["scene_info"][i]["y"])
        f_sensor.append(data["scene_info"][i+1]["F_sensor"])
        lt_sensor.append(data["scene_info"][i+1]["L_T_sensor"])
        rt_sensor.append(data["scene_info"][i+1]["R_T_sensor"])
        angle.append(data["scene_info"][i+1]["angle"])
        stuck_cnt.append(data["scene_info"][i+1]["stuck_cnt"])

        Y.append([data["command"][i+1]["left_PWM"], data["command"][i+1]["right_PWM"]])

Y = np.array(Y)
X = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
for i in range(len(car_x)):
    X = np.vstack((X, [car_x[i], car_y[i], dx[i], dy[i], f_sensor[i], lt_sensor[i], rt_sensor[i], angle[i], stuck_cnt[i]]))
X = X[1::]

# training
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

model = sklearn.neighbors.KNeighborsRegressor()
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
