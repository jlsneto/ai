import json
import random

STATE = ['idle', 'foward', 'back', 'left', 'right']


class UnityEnv(object):
    n_request = 0
    data = None
    client_address = None
    request = None

    def __init__(self):
        self.distance = None
        self.reward = None
        self.done = True
        self.info = {}

    def step(self, action):
        # Send input to unity
        self.n_request += 1
        self.done = False
        # parse data
        self.distance = self.data['distance']
        self.reward = self.distance
        response_data = {
            "agentId": self.data['agentId'],
            "state": int(action)
        }

        if self.n_request % 30 == 0 or self.n_request == 1:
            pass
            # print(f"{self.client_address} request number {self.n_request}")
            # print(f"last_data = {data}")

        # self.request.write(

        self.request.write((bytes(json.dumps(response_data) + "\n", 'utf-8')))
        return self.distance, self.reward, self.done, self.info

    def sample(self):
        return random.choice(range(len(STATE)))

    def reset(self):
        return self.distance


# hp = Hp()
# policy = Policy(1, len(STATE))
# normalizer = Normalizer(1)
# train(env, policy, normalizer, hp)
env_unity = UnityEnv()
