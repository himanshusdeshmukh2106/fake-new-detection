from flask import Flask, request, render_template, jsonify
from factcheck.utils.llmclient import CLIENTS
from factcheck.utils.multimodal import modal_normalization
import argparse
import json
import os
import tempfile

from factcheck.utils.utils import load_yaml
from factcheck import FactCheck

app = Flask(__name__, static_folder="assets")


# Define the custom filter
def zip_lists(a, b):
    return zip(a, b)


# Register the filter with the Jinja2 environment
app.jinja_env.filters["zip"] = zip_lists


# Occurrences count filter
def count_occurrences(input_dict, target_string, key):
    input_list = [item[key] for item in input_dict]
    return input_list.count(target_string)


app.jinja_env.filters["count_occurrences"] = count_occurrences


# Occurrences count filter
def filter_evidences(input_dict, target_string, key):
    return [item for item in input_dict if target_string == item[key]]


app.jinja_env.filters["filter_evidences"] = filter_evidences


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get global config and factcheck instance
        api_config = app.config.get('API_CONFIG', {})
        factcheck_instance = app.config.get('FACTCHECK_INSTANCE')
        
        if not factcheck_instance:
            return render_template("main_layout.html", error="Fact-check service not available")
        
        response = None
        
        # Check if it's file upload first
        if 'file' in request.files and request.files['file'].filename != '':
            # Handle file upload (image or video)
            file = request.files['file']
            
            # Save file temporarily
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)
            
            # Determine modal type from file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                modal_type = 'image'
            elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']:
                modal_type = 'video'
            else:
                # Clean up and return error
                os.remove(file_path)
                os.rmdir(temp_dir)
                return render_template("main_layout.html", error="Unsupported file type. Please upload an image or video.")
            
            try:
                # Process the file using multimodal processing
                text_content = modal_normalization(
                    modal=modal_type, 
                    input=file_path, 
                    gemini_api_key=api_config.get('GEMINI_API_KEY'),
                    api_config=api_config
                )
                
                # Clean up temporary file
                os.remove(file_path)
                os.rmdir(temp_dir)
                
                # Process with fact-checking
                response = factcheck_instance.check_text(text_content)
                
            except Exception as e:
                # Clean up on error
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
                return render_template("main_layout.html", error=f"Error processing file: {str(e)}")
                
        else:
            # Handle text input
            text_response = request.form.get("response", "").strip()
            if text_response == "":
                return render_template("main_layout.html", error="Please enter text to fact-check or upload a file.")
            
            # Process with fact-checking
            response = factcheck_instance.check_text(text_response)

        # If we have a response, save it and return results
        if response:
            # Save the response json file
            os.makedirs("assets", exist_ok=True)
            with open("assets/response.json", "w") as f:
                json.dump(response, f)

            return render_template("main_layout.html", responses=response, shown_claim=0)
        else:
            return render_template("main_layout.html", error="No response generated. Please try again.")

    return render_template("main_layout.html")


@app.route("/shownClaim/<content_id>")
def get_content(content_id):
    # load the response json file
    import json

    with open("assets/response.json") as f:
        response = json.load(f)

    return render_template("main_layout.html", responses=response, shown_claim=(int(content_id) - 1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="gemini-1.5-pro")
    parser.add_argument("--client", type=str, default=None, choices=CLIENTS.keys())
    parser.add_argument("--prompt", type=str, default="chatgpt_prompt")
    parser.add_argument("--retriever", type=str, default="serper")
    parser.add_argument("--modal", type=str, default="text")
    parser.add_argument("--input", type=str, default="demo_data/text.txt")
    parser.add_argument("--api_config", type=str, default="api_config.yaml")
    args = parser.parse_args()

    # Load API config from yaml file
    try:
        api_config = load_yaml(args.api_config)
    except Exception as e:
        print(f"Error loading api config: {e}")
        api_config = {}

    # Make api_config globally available
    app.config['API_CONFIG'] = api_config

    factcheck_instance = FactCheck(
        default_model=args.model,
        api_config=api_config,
        prompt=args.prompt,
        retriever=args.retriever,
    )

    # Make factcheck_instance globally available
    app.config['FACTCHECK_INSTANCE'] = factcheck_instance

    app.run(host="0.0.0.0", port=2024, debug=True)
