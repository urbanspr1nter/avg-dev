import jsonlines
import json
from unsloth import FastLanguageModel
from trl import SFTTrainer, SFTConfig
import torch
from datasets import Dataset
from prompt import get_system_prompt

def subgoals_to_text(example):
    subgoals = json.loads(example["instruction_subgoals"])

    text = ''
    for subgoal in subgoals:
        text += f"- {subgoal}\n"

    
    example["instruction_subgoals"] = text;

    return example

base_model = "unsloth/gemma-3-270m-it"

model, tokenizer = FastLanguageModel.from_pretrained(
    base_model,
    dtype=torch.bfloat16,
    max_seq_length=8192,
    load_in_4bit=False,
    load_in_8bit=False,
    full_finetuning=False,
    device_map="auto"
)

model = FastLanguageModel.get_peft_model(
    model,
    r=32,
    lora_alpha=32,
    use_gradient_checkpointing="unsloth",
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj"
    ]
)
model = FastLanguageModel.for_training(model)


# dataset
with jsonlines.open("dataset/plans-v1.jsonl") as j:
    dataset = list(j)

dataset = Dataset.from_list(dataset)
dataset = dataset.map(subgoals_to_text)

def convert_to_chatml(example):
    conversations = [
        {
            "role": "system",
            "content": get_system_prompt()
        },
        {
            "role": "user",
            "content": example["goal"]
        },
        {
            "role": "assistant",
            "content": example["instruction_subgoals"]
        }
    ]

    return { "conversations": conversations }

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
    #max_steps=5,
    num_train_epochs=10,
    learning_rate=1e-4,
    logging_steps=1,
    optim="adamw_8bit",
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    seed=42,
    output_dir="outputs/checkpoints",
    report_to="none"
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=training_args
)

trainer_stats = trainer.train()

# save safetensors for vLLM serving
model.save_pretrained_merged(
    "outputs/gemma-3-270m-ft",
    tokenizer,
    safe_serialization=True
)

# save to gguf for LM Studio
model.save_pretrained_gguf(
    "outputs/gemma-3-270b-ft-GGUF", tokenizer,
    quantization_method = "f16"
)
