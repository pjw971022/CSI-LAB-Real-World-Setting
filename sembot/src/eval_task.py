import hydra
from omegaconf import DictConfig, OmegaConf
import openai
from arguments import get_config
from interfaces import setup_LMP
from visualizers import ValueMapVisualizer
from envs.rlbench_env import VoxPoserRLBench
from utils import set_lmp_objects,load_prompt
import numpy as np
from rlbench import tasks
import os
os.environ['OPENAI_API_KEY'] =  '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' 
import wandb
import numpy as np
import sys 
sys.path.append('/home/jinwoo/workspace/Sembot/physical_reasoning')
from physical_reasoning.interactive_agent import InteractiveAgent
MAX_TRY = 20
CUSTOM_TASKS = [
    ########################   high success rate (with obs)   #########################
    # tasks.PutRubbishInBin,
    # tasks.LampOff,
    # tasks.PutKnifeOnChoppingBoard,
    # tasks.TakeOffWeighingScales,
    tasks.PushButton,

    ########################   middle success rate   #########################
    # tasks.SlideBlockToTarget, # 타겟의 반대 방향은 좌우앞뒤 중 어디인지 알아야함. 
    # tasks.OpenWineBottle, 더 깊게 잡지 않아서 실패하는 테스크
    #  tasks.TakeLidOffSaucepan, 더 깊게 잡지 않아서 실패하는 테스크
    ########################   low success rate   #########################
    ####### oracle plan은 되는 테스크
    #  tasks.PutGroceriesInCupboard,

    ####### oracle plan을 만들기도 어려운 테스크
    #  tasks.ChangeClock,

    ########################   New tasks   ###########################

    ########## Tasks likely to appear in the video DB. ###############
    #  tasks.PressSwitch,
    #  tasks.PutBooksOnBookshelf,
    #  tasks.CloseLaptopLid,

    ####################### Detection Error ##########################
    #  tasks.MeatOffGrill, # grill lid / target position
    #  tasks.TakeUmbrellaOutOfUmbrellaStand, # umbrella haddle 
    #  tasks.OpenMicrowave, # microwave handle 
    #  tasks.OpenWashingMachine, # washing machine handle 
    #  tasks.GetIceFromFridge, # ice dispenser 
    #  tasks.PutBottleInFridge, # fridge handle 
    #  tasks.InsertUsbInComputer, # usb port 
    ########################   Dynamic object   ######################
    #  tasks.MoveHanger, 
    ######################### 방향 맞추기 너무 어려움 #####################
    #  tasks.PlugChargerInPowerSupply,
]

@hydra.main(config_path=f'./configs', config_name="rlbench_config")
def main(cfgs: DictConfig):
    config = cfgs
    plain_dict = OmegaConf.to_container(config, resolve=True, enum_to_str=True)

    # uncomment this if you'd like to change the language model (e.g., for faster speed or lower cost)
    for lmp_name, cfg in config['lmp_config']['lmps'].items():
        cfg['model'] = 'llama3-70b' #'gemini-1.0-pro-latest' # #'gpt-4-1106-preview' #'gemini-1.0-pro-latest'

    # initialize env and voxposer ui
    use_server = config['use_server']
    use_sembot = config['use_sembot']
    use_oracle_plan = config['use_oracle_plan']
    use_oracle_instruction = config['use_oracle_instruction']
    save_pcd = config['save_pcd']

    visualizer = ValueMapVisualizer(config['visualizer'])
    env = VoxPoserRLBench(visualizer=visualizer,
                           save_pcd=save_pcd,
                              use_server=use_server,
                              server_ip=config['server_ip'],)
    lmps, lmp_env = setup_LMP(env, config, debug=False)
    voxposer_ui = lmps['plan_ui']
    composer_ui = lmps['composer_ui']

    interactive_agent = InteractiveAgent(composer_ui, config['interactive_agent'])
    
    task_list = CUSTOM_TASKS
    
    for task in task_list:
        env.load_task(task)
        task_name = env.task.get_name()
        wandb.init(project="voxposer-naive",
                   entity="pjw971022",
                   name=task_name, 
                   reinit=True)
        wandb.config.update(plain_dict)
        i = 0
        cnt = 0
        while i < cfgs['episode_length'] and cnt < MAX_TRY:
            # try:
            desc_, obs = env.reset()
            if len(desc_)==2:
                descriptions, target_obj = desc_
            else:
                descriptions = desc_
            set_lmp_objects(lmps, env.get_object_names())  # set the object names to be used by voxposer
            instruction = np.random.choice(descriptions) #f"move the {target_obj} to the cupboard." 
            env.instruction = instruction            
            wandb.log({"instruction": instruction})
            
            if use_oracle_plan:
                oracle_plan_code = load_prompt(f"{config['env_name']}/oracle_plan/{task_name}.txt")
                if '{target_obj}' in oracle_plan_code:
                    oracle_plan_code = oracle_plan_code.replace('{target_obj}', target_obj)
                voxposer_ui(instruction, plan_code=oracle_plan_code) # 
            elif use_sembot:
                if use_oracle_instruction:
                    oracle_instruction = load_prompt(f"{config['env_name']}/oracle_instruction/{task_name}.txt")
                    obs_dict = {'instruction': oracle_instruction, 'possible_obj': env.get_object_names()}
                    interactive_agent(obs_dict) #
                else:
                    oracle_plan_code = None
                    obs_dict = {'instruction': instruction, 'possible_obj': env.get_object_names()}
                    instruction += f'. {interactive_agent.obs_captioning()}'
                    interactive_agent(obs_dict)
            else:
                if use_oracle_instruction:
                    oracle_instruction = load_prompt(f"{config['env_name']}/oracle_instruction/{task_name}.txt")
                    voxposer_ui(oracle_instruction) #
                else:      
                    voxposer_ui(instruction)
            i +=1

    wandb.finish()

if __name__ =='__main__':
    main()