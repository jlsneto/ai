import threading

import numpy as np
import os
import shutil

from core.envs import env_unity, STATE
from server.socket_ import tcp_server

frame_num = 0


# Configuração dos hiperparâmetros
class Hp():
    def __init__(self):
        self.nb_steps = 1000
        self.n_steps = 100
        self.episode_time = 120
        self.learning_rate = 0.02
        self.nb_directions = 16
        self.nb_best_directions = 16
        assert self.nb_best_directions <= self.nb_directions
        self.noise = 0.03
        self.seed = 1
        self.env_name = 'HalfCheetahBulletEnv-v0'


# Normalização dos estados
class Normalizer():
    def __init__(self, nb_inputs):
        self.frames_ = 0
        self.n = np.zeros(nb_inputs)
        self.mean = np.zeros(nb_inputs)
        self.mean_diff = np.zeros(nb_inputs)
        self.var = np.zeros(nb_inputs)

    def observe(self, x):
        self.n += 1.
        last_mean = self.mean.copy()
        # input(f'({x} - {self.mean}) / {self.n}')
        self.mean += (x - self.mean) / self.n
        self.mean_diff += (x - last_mean) * (x - self.mean)
        self.var = (self.mean_diff / self.n).clip(min=1e-2)  # 0.001

    def normalize(self, inputs):
        obs_mean = self.mean
        obs_std = np.sqrt(self.var)
        return (inputs - obs_mean) / obs_std


# Construção da inteligência artificial

class Policy():
    def __init__(self, input_size, output_size):
        self.theta = np.zeros((output_size, input_size))

    def evaluate(self, input, delta=None, direction=None):
        if direction is None:
            return self.theta.dot(input)
        elif direction == 'positive':
            return (self.theta + hp.noise * delta).dot(input)
        else:
            return (self.theta - hp.noise * delta).dot(input)

    def sample_deltas(self):
        return [np.random.randn(*self.theta.shape) for _ in range(hp.nb_directions)]

    # rollout [recompensa positiva, recompensa negativa, pertubução (delta)]
    # sigma_r -> desvio padrão da recompensa
    def update(self, rollouts, sigma_r):
        step = np.zeros(self.theta.shape)
        for r_pos, r_neg, d in rollouts:
            step += (r_pos - r_neg) * d
        self.theta += hp.learning_rate / (hp.nb_best_directions * sigma_r) * step

    # Explora a política em uma direção específica e dentro de um episódio


def explore(env, normalizer, policy, direction=None, delta=None):
    distance, reward, done, info = env.step(env.sample())
    num_plays = 0.
    sum_rewards = 0
    last_distance = distance
    while not done and num_plays < hp.n_steps:
        normalizer.observe(distance)
        distance = normalizer.normalize(distance)
        action = policy.evaluate(distance, delta, direction)
        distance, reward, done, info = env.step(action.argmax())
        if last_distance == distance:
            reward = -10
        reward = max(min(reward, 1), -1)
        sum_rewards += reward
        num_plays += 1
        normalizer.frames_ += 1
    return sum_rewards


# Treinamento da inteligência artificial
def train(env, policy, normalizer, hp):
    for step in range(hp.nb_steps):
        # Inicialização das perturbações (deltas) e as recompensas positivas e negativas
        deltas = policy.sample_deltas()
        positive_rewards = [0] * hp.nb_directions
        negative_rewards = [0] * hp.nb_directions

        # Obtendo as recompensas das direções positivas
        for k in range(hp.nb_directions):
            positive_rewards[k] = explore(env, normalizer, policy, direction='positive', delta=deltas[k])

        # Obtendo as recompensas das direções negativas
        for k in range(hp.nb_directions):
            negative_rewards[k] = explore(env, normalizer, policy, direction='negative', delta=deltas[k])

        # Obtendo todas as recompensas positivas e negativas para computar o desvio padrão dessas recompensas
        all_rewards = np.array(positive_rewards + negative_rewards)
        sigma_r = all_rewards.std()

        # Ordenação dos rollouts e seleção das melhores direções
        scores = {k: max(r_pos, r_neg) for k, (r_pos, r_neg) in enumerate(zip(positive_rewards, negative_rewards))}
        order = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:hp.nb_best_directions]
        rollouts = [(positive_rewards[k], negative_rewards[k], deltas[k]) for k in order]

        # Atualização da política
        policy.update(rollouts, sigma_r)

        # Impressão da recompensa final depois da atualização
        reward_evaluation = explore(env, normalizer, policy)
        hp.n_steps += 1
        print('Step: ', step, ' Reward: ', reward_evaluation)
    return True


th = threading.Thread(target=tcp_server, args=("192.168.1.71", 9999))
th.daemon = 1
th.start()

while True:
    print("Aguardando dados")
    if env_unity.data is not None:
        hp = Hp()
        np.random.seed(hp.seed)
        policy = Policy(1, len(STATE))
        normalizer = Normalizer(1)
        print("NORMALIZE")
        done = train(env_unity, policy, normalizer, hp)
        print("ACABOU TREINO")
        if done:
            break
th.join()
