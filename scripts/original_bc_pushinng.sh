#!/bin/bash

python main.py --simulator=pybullet --robot=panda --num_process=1 --render=f --env=close_loop_block_pushing --num_objects=1 --max_episode_steps=50 --planner_episode=20 --device=cuda:0 --batch_size=64 --seed=0 --max_train_step=10000 --random_orientation=t --model=equi --alg=bc_con --action_sequence=pxyzr --dpos=0.05 --drot_n=4 --heightmap_size=128 --equi_n=4 --n_hidden=64 --eval_freq=-1 --num_eval_processes=0 --buffer=aug --simulate_n=0 --buffer_aug_n=4 --seed=0

python main.py --simulator=pybullet --robot=panda --num_process=1 --render=f --env=close_loop_block_pushing --num_objects=1 --max_episode_steps=50 --planner_episode=20 --device=cuda:0 --batch_size=64 --seed=0 --max_train_step=10000 --random_orientation=t --model=equi --alg=bc_con --action_sequence=pxyzr --dpos=0.05 --drot_n=4 --heightmap_size=128 --equi_n=4 --n_hidden=64 --eval_freq=-1 --num_eval_processes=0 --buffer=aug --simulate_n=0 --buffer_aug_n=4 --seed=1

python main.py --simulator=pybullet --robot=panda --num_process=1 --render=f --env=close_loop_block_pushing --num_objects=1 --max_episode_steps=50 --planner_episode=20 --device=cuda:0 --batch_size=64 --seed=0 --max_train_step=10000 --random_orientation=t --model=equi --alg=bc_con --action_sequence=pxyzr --dpos=0.05 --drot_n=4 --heightmap_size=128 --equi_n=4 --n_hidden=64 --eval_freq=-1 --num_eval_processes=0 --buffer=aug --simulate_n=0 --buffer_aug_n=4 --seed=2

python main.py --simulator=pybullet --robot=panda --num_process=1 --render=f --env=close_loop_block_pushing --num_objects=1 --max_episode_steps=50 --planner_episode=20 --device=cuda:0 --batch_size=64 --seed=0 --max_train_step=10000 --random_orientation=t --model=equi --alg=bc_con --action_sequence=pxyzr --dpos=0.05 --drot_n=4 --heightmap_size=128 --equi_n=4 --n_hidden=64 --eval_freq=-1 --num_eval_processes=0 --buffer=aug --simulate_n=0 --buffer_aug_n=4 --seed=3