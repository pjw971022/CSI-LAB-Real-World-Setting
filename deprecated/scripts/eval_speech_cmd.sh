export MASTER_ADDR="115.145.175.206"
export MASTER_PORT="23111"
export WORLD_SIZE="4"
export RANK="0"
export LOCAL_RANK="0"
export OPENAI_API_KEY=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
export TRANSFORMERS_CACHE=/home/mnt/models/.cache/huggingface/hub
export RAVENS_ROOT=/home/pjw971022/Sembot/ravens/
python3 evaluation/llm_eval_real.py task=real-world-multi-modal \
                                mode=test \
                                category_mode=0 \
                                record.save_video=False \
                                task_level=1 \
                                llm_type=gemini \
                                plan_mode=open_loop
