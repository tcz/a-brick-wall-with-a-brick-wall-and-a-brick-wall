
import openai
import requests
from huggingface_hub.inference_api import InferenceApi
import re, os

aws_access_code = os.environ['AWS_ACCESS_CODE']
aws_secret = os.environ['AWS_SECRET']
aws_region = os.environ['AWS_REGION']
s3_bucket = os.environ['S3_BUCKET']
huggingface_api_key = os.environ['HUGGINGFACE_API_KEY']
import boto3

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3',
                      region_name=aws_region,
                      aws_access_key_id=aws_access_code,
                      aws_secret_access_key=aws_secret,
                      )
    s3.upload_file(local_file, bucket, s3_file)

    response = s3.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket,
                                                        'Key': s3_file},
                                                ExpiresIn=3600)

    return response

def generate_file_name_from_text(counter, text):
    file_name = re.sub(r'\W+', ' ', text).strip().replace(' ', '_')
    return str(counter).zfill(5) + file_name

def generate_counter_and_prompt_from_filename(file_name):
    counter = int(file_name[:5])
    prompt = file_name[5:-4]
    prompt = prompt.replace("_", " ")

    return counter, prompt

def seed(count):
    return " " * (count + 500)

results_dir = 'results'

if not os.path.exists(results_dir):
    os.makedirs(results_dir)

files = os.listdir(results_dir)
files = [f for f in files if os.path.isfile(os.path.join(results_dir, f))]
files.sort()
last_file = files[-1] if files else None

if last_file is None:
    prompt = 'a clock tower with a clock on each of its side'
    counter = 1
else:
    counter, prompt = generate_counter_and_prompt_from_filename(last_file)
    counter = counter + 1

while True:
    try:
        inference = InferenceApi(repo_id="stabilityai/stable-diffusion-2-1", token="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")
        result = inference(inputs=prompt + ' ' + seed(counter))
        print(result)

        filename = os.path.join(results_dir, generate_file_name_from_text(counter, prompt) + '.png')
        result.save(filename)
        url = upload_to_aws(filename, s3_bucket, os.path.basename(filename))

        print(url)

        inference = InferenceApi(repo_id="ydshieh/vit-gpt2-coco-en", token=huggingface_api_key)
        result = inference(inputs=url)

        print(result)

        prompt = result[0]['generated_text']
        counter = counter + 1

    except Exception as e:
        continue

