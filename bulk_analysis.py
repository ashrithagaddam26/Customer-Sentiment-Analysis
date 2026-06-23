import boto3
import json
import csv
import time
import yaml
import re

with open("config.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

SYSTEM_PROMPT = config["prompt"]["system_prompt"]

ACCESS_KEY = config["aws"]["access_key"]
SECRET_KEY = config["aws"]["secret_key"]
REGION = config["aws"]["region"]
MODEL_ID = config["aws"]["model_id"]


def clean_text(text):
    text = str(text)
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"\b\d+\b", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =====================================================
# NOVA ANALYSIS FUNCTION
# =====================================================
def get_nova_analysis(description):
    try:
        client = boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=ACCESS_KEY.strip(),
            aws_secret_access_key=SECRET_KEY.strip(),
            region_name=REGION,
        )

        model_id = MODEL_ID

        prompt = f"""
{SYSTEM_PROMPT}

Ticket Description:
{description}
"""

        native_request = {
            "schemaVersion": "messages-v1",
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"maxTokens": 100, "temperature": 0, "topP": 0.1},
        }

        # =====================================================
        # INVOKE MODEL
        # =====================================================
        response = client.invoke_model(
            modelId=model_id, body=json.dumps(native_request)
        )

        response_body = json.loads(response.get("body").read())
        raw_text = response_body["output"]["message"]["content"][0]["text"].strip()

        # =====================================================
        # REMOVE MARKDOWN JSON IF PRESENT
        # =====================================================
        if "```" in raw_text:
            raw_text = raw_text.split("```")[1]
            raw_text = raw_text.replace("json", "").strip()

        # =====================================================
        # PARSE JSON
        # =====================================================
        result = json.loads(raw_text)

        return {
            "predicted_subject": result.get("predicted_subject", "Unknown"),
            "sentiment": result.get("sentiment", "NEUTRAL"),
            "explanation_of_sentiment": result.get(
                "reason", "No explanation generated"
            ),
        }

    except Exception as e:
        print("\nERROR:", str(e))
        return {
            "predicted_subject": "Error",
            "sentiment": "ERROR",
            "explanation_of_sentiment": "Processing issue",
        }


# =====================================================
# MAIN PROGRAM
# =====================================================
if __name__ == "__main__":
    # Use the clean file generated from Step 1
    input_csv = "Final_Perfect_Data.csv"
    output_csv = "Week3_Final_Exclusive_Results.csv"

    try:
        with open(input_csv, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            headers = reader.fieldnames

            print("\nCSV HEADERS FOUND:")
            print(headers)

            # Target text column
            description_col = (
                "Cleaned_Description"
                if "Cleaned_Description" in headers
                else "Ticket Description"
            )

            # =====================================================
            # NEW OUTPUT HEADERS (Including Predicted Subject)
            # =====================================================
            fieldnames = [
                "Customer_ID",
                "Ticket Description",
                "Subject",
                "Sentiment",
            ]

            # =====================================================
            # OUTPUT FILE GENERATION
            # =====================================================
            with open(output_csv, mode="w", newline="", encoding="utf-8") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                count = 0
                print("\n===================================")
                print("STRICT ANALYSIS LOOP STARTED")
                print("===================================\n")

                for row in reader:
                    # Process first 4500 rows
                    if count >= 10:
                        break

                    description = row.get(description_col, "")

                    description = clean_text(description)
                    row["Cleaned_Description"] = description

                    if description and str(description).strip():
                        count += 1
                        print(f"\n[{count}] Processing Ticket Content...")

                        # Call model using only description context
                        analysis = get_nova_analysis(description)

                        print(f"PREDICTED SUBJECT: {analysis['predicted_subject']}")
                        print(f"SENTIMENT:         {analysis['sentiment']}")

                        # Save results to the output row
                        # Save results to the output row
                        output_row = {
                            "Customer_ID": row.get("\ufeffCustomer_ID", ""),
                            "Ticket Description": description,
                            "Subject": analysis["predicted_subject"],
                            "Sentiment": analysis["sentiment"],
                        }

                        writer.writerow(output_row)
                        time.sleep(0.3)

        print("\n===================================")
        print("SUCCESS!")
        print(f"Fresh accurate results saved in: {output_csv}")
        print("===================================\n")

    except Exception as e:
        print("\n===================================")
        print("FINAL ERROR:", str(e))
        print("===================================\n")
