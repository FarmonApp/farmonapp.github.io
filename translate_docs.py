import argparse
import asyncio
import os
import sys
from pathlib import Path

import aiofiles
from openai import AsyncAzureOpenAI

# Read API key from environment variable
api_key = os.environ.get("AZURE_OPENAI_API_KEY", "32a943563fed492397b60a760f12851d")
if not api_key:
    print("Error: The AZURE_OPENAI_API_KEY environment variable is not set.")
    sys.exit(1)

client = AsyncAzureOpenAI(
    api_key=api_key,
    azure_endpoint="https://farmon-gpt.openai.azure.com/",
    api_version="2024-05-01-preview"
)

async def translate_file(md_file, language_code, language_name, overwrite=False):
    # Skip files that are already in the target language
    if md_file.suffix == f".{language_code}.md":
        return f"Skipping {md_file} as it is already in the target language."
    
    # Construct the translated file name
    translated_file = md_file.with_name(md_file.name.replace('.en.md', f'.{language_code}.md'))
    
    # Skip if the translated file already exists and overwrite is False
    if translated_file.exists() and not overwrite:
        return f"Skipping {md_file} as {translated_file} already exists."
    
    # Read the original Markdown content
    async with aiofiles.open(md_file, 'r', encoding='utf-8') as f:
        content = await f.read()

    # Prepare messages for the Azure OpenAI ChatCompletion API
    messages = [
        {
            "role": "system",
            "content": f"You are a helpful assistant that translates English markdown text into {language_name}, preserving the markdown formatting."
        },
        {
            "role": "user",
            "content": content
        }
    ]

    # Call the Azure OpenAI API to perform the translation
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5
        )

        # Extract the translated content
        translated_content = response.choices[0].message.content.strip()

        # Write the translated content to the new file
        async with aiofiles.open(translated_file, mode='w', encoding='utf-8') as f:
            await f.write(translated_content)

        return f"Translated {md_file} to {translated_file}"

    except Exception as e:
        return f"An error occurred while translating {md_file}: {e}"

async def main(overwrite, languages, folder):
    # Define the path to the specified folder
    docs_path = Path(folder)

    if not docs_path.exists():
        print(f"Error: The specified folder '{folder}' does not exist.")
        sys.exit(1)

    # Iterate over all Markdown files in the specified folder and subdirectories
    files = list(docs_path.glob(pattern='**/*.en.md'))
    
    tasks = [
        translate_file(md_file, language_code=code, language_name=name, overwrite=overwrite)
        for code, name in languages
        for md_file in files
    ]
    
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Translate Markdown files using Azure OpenAI.')
    parser.add_argument('--language', action='append', required=True, help='Target language code and name in format code:name (e.g., "fr:French")')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing translated files')
    parser.add_argument('--folder', default='docs', help='Path to the folder containing markdown files (default: "docs")')

    args = parser.parse_args()

    # Parse languages
    languages = []
    for lang in args.language:
        if ':' in lang:
            code, name = lang.split(':', 1)
            languages.append((code.strip(), name.strip()))
        else:
            print(f"Invalid language format: {lang}")
            sys.exit(1)

    asyncio.run(main(overwrite=args.overwrite, languages=languages, folder=args.folder))