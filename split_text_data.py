# ===============================
# 1️⃣ Install Required Libraries (run once)
# ===============================
# !pip install transformers datasets torch scikit-learn pandas

# ===============================
# 2️⃣ Imports
# ===============================
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from torch.nn import CrossEntropyLoss
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, f1_score, precision_score, recall_score
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

# ===============================
# 3️⃣ Load Train & Test Data
# ===============================
train_df = pd.read_csv("train_diet.csv")
test_df = pd.read_csv("test_diet.csv")

text_column = 'combined_text'
label_column = 'rule_based_diet'

# ===============================
# 4️⃣ Label Encoding
# ===============================
label_encoder = LabelEncoder()
train_df['label_enc'] = label_encoder.fit_transform(train_df[label_column])
test_df['label_enc'] = label_encoder.transform(test_df[label_column])
num_labels = len(label_encoder.classes_)

print("Classes found:", list(label_encoder.classes_))

# ===============================
# 5️⃣ Tokenizer
# ===============================
tokenizer = AutoTokenizer.from_pretrained("emilyalsentzer/Bio_ClinicalBERT")

class DietDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        encoding = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=self.max_len,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

train_dataset = DietDataset(train_df[text_column].tolist(), train_df['label_enc'].tolist(), tokenizer)
test_dataset = DietDataset(test_df[text_column].tolist(), test_df['label_enc'].tolist(), tokenizer)

# ===============================
# 6️⃣ Compute Class Weights
# ===============================
classes = np.unique(train_df['label_enc'])
class_weights = compute_class_weight(class_weight='balanced', classes=classes, y=train_df['label_enc'])
class_weights = torch.tensor(class_weights, dtype=torch.float)

# ===============================
# 7️⃣ Load Model
# ===============================
model = AutoModelForSequenceClassification.from_pretrained(
    "emilyalsentzer/Bio_ClinicalBERT",
    num_labels=num_labels
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# ===============================
# 8️⃣ Define Metrics
# ===============================
def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    precision = precision_score(labels, preds, average='macro', zero_division=0)
    recall = recall_score(labels, preds, average='macro', zero_division=0)
    f1 = f1_score(labels, preds, average='macro', zero_division=0)
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# ===============================
# 9️⃣ Training Arguments
# ===============================
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=4,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=3e-5,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir='./logs',
    logging_steps=50,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True
)

# ===============================
# 10️⃣ Trainer
# ===============================
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics
)

# ===============================
# 11️⃣ Train Model
# ===============================
trainer.train()

# ===============================
# 12️⃣ Evaluate Model
# ===============================
model.eval()
all_preds = []
all_labels = []

for batch in DataLoader(test_dataset, batch_size=32):
    input_ids = batch['input_ids'].to(device)
    attention_mask = batch['attention_mask'].to(device)
    labels = batch['labels'].to(device)
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
    preds = torch.argmax(outputs.logits, dim=1)
    all_preds.extend(preds.cpu().numpy())
    all_labels.extend(labels.cpu().numpy())

# ===============================
# 13️⃣ Overall Metrics in %
# ===============================
accuracy = accuracy_score(all_labels, all_preds) * 100
precision = precision_score(all_labels, all_preds, average='macro', zero_division=0) * 100
recall = recall_score(all_labels, all_preds, average='macro', zero_division=0) * 100
f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0) * 100

print("\n===== Overall Metrics (%) =====")
print(f"Accuracy:  {accuracy:.2f}%")
print(f"Precision: {precision:.2f}%")
print(f"Recall:    {recall:.2f}%")
print(f"F1 Score:  {f1:.2f}%")

# ===============================
# 14️⃣ Per-Class Metrics in %
# ===============================
report_dict = classification_report(
    all_labels,
    all_preds,
    target_names=label_encoder.classes_,
    output_dict=True,
    zero_division=0
)

report_df = pd.DataFrame(report_dict).transpose()

# Convert precision, recall, f1-score to %
for col in ['precision', 'recall', 'f1-score']:
    report_df[col] = report_df[col] * 100

report_df = report_df.round(2)

print("\n===== Per-Class Metrics (%) =====")
print(report_df[['precision', 'recall', 'f1-score', 'support']])



