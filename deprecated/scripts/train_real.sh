python cliport/train.py train.task=real-world-cleanup \
                        train.agent=cliport \
                        train.attn_stream_fusion_type=add \
                        train.trans_stream_fusion_type=conv \
                        train.lang_fusion_type=mult \
                        train.n_demos=10 \
                        train.n_steps=2010 \
                        train.exp_folder=exps \
                        dataset.cache=False 