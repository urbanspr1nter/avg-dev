from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig
import torch

base_model = "unsloth/gemma-3-270m-it"

model = AutoModelForCausalLM.from_pretrained(
    base_model,
    dtype=torch.float16,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(base_model)

lora_config = LoraConfig(
    r=32,
    lora_alpha=32,
    lora_dropout=0,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj"
    ],
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)

# dataset
dataset = load_dataset("mlabonne/FineTome-100K", split="train[:100]")

def convert_to_chatml(example):
    messages = example["conversations"]

    conversations = []
    for message in messages:
        if message["from"] == "human":
            conversations.append(
                {
                    "role": "user",
                    "content": message["value"]
                }
            )
        elif message["from"] == "gpt":
            conversations.append(
                {
                    "role": "assistant",
                    "content": message["value"]
                }
            )

    return {
        "conversations": conversations
    }

dataset = dataset.map(convert_to_chatml)

def formatting_prompts_func(examples):
   convos = examples["conversations"]
   texts = [tokenizer.apply_chat_template(convo, tokenize = False, add_generation_prompt = False).removeprefix('<bos>') for convo in convos]
   return { "text" : texts, }


dataset = dataset.map(formatting_prompts_func, batched=True)

training_args = SFTConfig(
    dataset_text_field="text",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    warmup_ratio=0.03,
    max_steps=5,
    #num_train_epochs=1,
    learning_rate=2e-5,
    logging_steps=1,
    optim="adamw_8bit",
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    seed=42,
    output_dir="outputs",
    report_to="none"
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=training_args
)

trainer_stats = trainer.train()