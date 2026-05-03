import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()  # reads .env into os.environ

client = Anthropic()  # reads ANTHROPIC_API_KEY from env

def run_analysis(file_name):
    print(f"🚀 Starting analysis for: {file_name}")

    # 1. Upload the file
    with open(file_name, "rb") as f:
        file_obj = client.beta.files.upload(
            file=(file_name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            betas=["files-api-2025-04-14"],
        )
    print(f"✅ File uploaded. ID: {file_obj.id}")

    system_instruction = """You are an automated Financial Analyst.
1. Use the code_execution tool to read the provided Excel file with pandas.
2. Identify columns related to Revenue, Income, Loss, or Expense.
3. Calculate the total aggregate for Revenue and Loss.
4. Return a JSON object: {"total_revenue": X, "total_loss": Y, "net": Z}."""

    response = client.beta.messages.create(
        model="claude-opus-4-5",  # see note below
        betas=["files-api-2025-04-14", "code-execution-2025-08-25"],
        max_tokens=4096,
        system=system_instruction,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please process the attached spreadsheet."},
                    {"type": "container_upload", "file_id": file_obj.id},
                ],
            }
        ],
        tools=[{
            "type": "code_execution_20250825",
            "name": "code_execution",
        }],
    )

    print("\n--- Claude's Final Report ---")
    for block in response.content:
        if block.type == "text":
            print(block.text)

if __name__ == "__main__":
    target_file = "data.xlsx"
    if os.path.exists(target_file):
        run_analysis(target_file)
    else:
        print(f"❌ {target_file} not found")