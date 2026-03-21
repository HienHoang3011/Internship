import torch
from transformers import AutoModel, AutoTokenizer
from app.services.embedding.base import BaseEmbeddingService 

class VidenseEmbedding(BaseEmbeddingService):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('namdp-ptit/ViDense')
        self.model = AutoModel.from_pretrained('namdp-ptit/ViDense')

    def avg_pooling(self, attention_mask, outputs):
        last_hidden = outputs.last_hidden_state
        return (last_hidden * attention_mask.unsqueeze(-1)).sum(1) / attention_mask.sum(-1).unsqueeze(-1)

    def get_name(self):
        return 'vidense'    
    def embed(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            outputs = self.avg_pooling(inputs['attention_mask'], outputs)
        return outputs
    def embed_batch(self, sentences):
        inputs = self.tokenizer(sentences, return_tensors='pt', padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            outputs = self.avg_pooling(inputs['attention_mask'], outputs)
        return outputs

