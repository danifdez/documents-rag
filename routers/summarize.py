from fastapi import APIRouter
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re

router = APIRouter(
    prefix="/summarize",
    tags=["summarize"],
)

class SummarizeRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class SummarizeResponse(BaseModel):
    response: str

@router.post("/", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    model_name = "facebook/mbart-large-50-one-to-many-mmt"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)

    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    tokenizer.src_lang = request.source_language + "_XX"
    es_forced_bos_token_id = tokenizer.lang_code_to_id[request.target_language + "_XX"]

    plain_text = re.sub(r"<[^>]+>", "", request.text)

    inputs = tokenizer(
        plain_text,
        max_length=1024,
        truncation=True,
        return_tensors="pt"
    )

    summary_ids = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        num_beams=4,
        max_length=200,
        min_length=30,
        forced_bos_token_id=es_forced_bos_token_id,
        no_repeat_ngram_size=3
    )

    summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return SummarizeResponse(response=summary_text.strip())