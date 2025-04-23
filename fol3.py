import os
import shutil
import json
from pdfminer.high_level import extract_text
import google.generativeai as genai
import pandas as pd
import PyPDF2
import re
from PIL import Image
import io
import fitz  


SOURCE_FOLDER = "XYZ"  
DESTINATION_FOLDER = "XYZ_modified" # THIS FOLDER WILL BE CREATED


GEMINI_API_KEY = "AIzaSyATy_wlsCcYpF-_uBoMeDuizWSS2E1OTjY" 

def reorganize_folders(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        print(f"Created destination folder: {destination_folder}")
    
    total_files = 0
    submission_pdfs = []
    
    for folder_name in os.listdir(source_folder):
        folder_path = os.path.join(source_folder, folder_name)
        

        if not os.path.isdir(folder_path) or not folder_name.isdigit():
            continue
        
        padded_folder_number = folder_name.zfill(3)
        
        submission_folder = os.path.join(folder_path, "Submission")
        if os.path.exists(submission_folder) and os.path.isdir(submission_folder):

            files_processed, sub_pdfs = process_files(
                submission_folder, 
                destination_folder, 
                padded_folder_number, 
                "a"
            )
            submission_pdfs.extend(sub_pdfs)
            total_files += files_processed
            print(f"Processed {files_processed} files from folder {folder_name}/Submission")
        else:
            print(f"Warning: Submission folder not found in {folder_name}")
        

        supplementary_folder = os.path.join(folder_path, "Supplementary")
        if os.path.exists(supplementary_folder) and os.path.isdir(supplementary_folder):

            files_processed, _ = process_files(
                supplementary_folder, 
                destination_folder, 
                padded_folder_number, 
                "b"
            )
            total_files += files_processed
            print(f"Processed {files_processed} files from folder {folder_name}/Supplementary")
    
    print(f"\nTotal files processed: {total_files}")
    print(f"Found {len(submission_pdfs)} PDF files from Submission folders to analyze")
    
    return submission_pdfs

def process_files(source_folder, destination_folder, padded_folder_number, folder_type):
    files_processed = 0
    pdf_files = []
    
    for filename in os.listdir(source_folder):
        source_file = os.path.join(source_folder, filename)
        
        if not os.path.isfile(source_file):
            continue
        
        new_filename = f"{padded_folder_number}{folder_type}_{filename}"
        destination_file = os.path.join(destination_folder, new_filename)
        
        shutil.copy2(source_file, destination_file)
        files_processed += 1
        
        if folder_type == 'a' and filename.lower().endswith('.pdf'):
            pdf_files.append(destination_file)
    
    return files_processed, pdf_files

def extract_text_from_pdf(pdf_path):

    try:
        return extract_text(pdf_path)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {str(e)}")
        return ""

def get_pdf_metadata(pdf_path):
    metadata = {
        "Page_Count": 0,
        "Column_Format": "Unknown"
    }
    
    try:
       
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            metadata["Page_Count"] = len(pdf_reader.pages)
        
        doc = fitz.open(pdf_path)
        if doc.page_count > 0:
           
            pages_to_check = min(3, doc.page_count)
            column_votes = []
            
            for page_num in range(pages_to_check):
                page = doc[page_num]
               
                blocks = page.get_text("dict")["blocks"]
                
                if len(blocks) < 5:
                    continue
                
                x_positions = []
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            if "spans" in line:
                                for span in line["spans"]:
                                    x_positions.append(span["bbox"][0])  
                
                if x_positions:
                   
                    x_positions.sort()
                    
                    page_width = page.rect.width
                    left_half = [x for x in x_positions if x < page_width/2]
                    right_half = [x for x in x_positions if x >= page_width/2]
                    
                    if len(left_half) > 10 and len(right_half) > 10:
                        column_votes.append("Double")
                    else:
                        column_votes.append("Single")
            
            if column_votes:
                double_count = column_votes.count("Double")
                if double_count > len(column_votes) / 2:
                    metadata["Column_Format"] = "Double Column"
                else:
                    metadata["Column_Format"] = "Single Column"
                    
        doc.close()
    except Exception as e:
        print(f"Error extracting additional metadata from {pdf_path}: {str(e)}")
    
    return metadata

def send_to_gemini(pdf_text, filename):
   
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        prompt = f"""
        Extract the following details from the research paper and return the output as a JSON object:
        {{
            "Title": "<Title of the paper>",
            "Authors": ["<List of authors>"],
            "No of Authors": "<Number of authors>",
            "Keywords": ["<List of keywords>"],
            "Affiliations": ["<List of affiliations>"]
        }}
        
        Text:
        {pdf_text[:10000]}  # Limit text to avoid token limits
        """

        response = model.generate_content(prompt)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned_text)
        
        
        result["Filename"] = filename
        result["id"] = filename[:3] 
        
        return result
    except Exception as e:
        print(f"Error processing with Gemini AI for {filename}: {str(e)}")
        
        return {
            "Filename": filename,
            "Title": "Error - Processing failed",
            "Authors": [],
            "Keywords": [],
            "DOI": "",
            "Journal/ Conference name": "",
            "Journal/ Conference website": "",
            "Affiliations": []
        }

def process_submission_pdfs(pdf_files):

    results = []
    
    total = len(pdf_files)
    for i, pdf_path in enumerate(pdf_files):
        filename = os.path.basename(pdf_path)
        print(f"Processing PDF {i+1}/{total}: {filename}")
        
        
        pdf_text = extract_text_from_pdf(pdf_path)
        if not pdf_text:
            print(f"  Warning: Could not extract text from {filename}")
            continue
            
        
        print(f"  Sending to Gemini AI...")
        metadata = send_to_gemini(pdf_text, filename)
        
        print(f"  Extracting additional PDF metadata...")
        additional_metadata = get_pdf_metadata(pdf_path)
        metadata.update(additional_metadata)
        
        for key in metadata:
            if isinstance(metadata[key], list):
                metadata[key] = "; ".join(metadata[key])
                
        results.append(metadata)
        print(f"  Successfully processed: {filename}")
    
    return results

def save_to_excel(results, destination_folder):
    
    if not results:
        print("No results to save to Excel.")
        return
    
    
    df = pd.DataFrame(results)
    
    # Reorder columns to put Filename at the beginning
    preferred_order = ['Filename', 'id','Title', 'Authors','No of Authors', 'Keywords', 
                       'Affiliations', 'Page_Count', 'Column_Format']
    
    
    all_cols = list(df.columns)
    
    
    reordered_cols = [col for col in preferred_order if col in all_cols]
    
    
    remaining_cols = [col for col in all_cols if col not in preferred_order]
    reordered_cols.extend(remaining_cols)
    
    df = df[reordered_cols]
    
    excel_path = os.path.join(destination_folder, "Research_Papers_Metadata.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Saved metadata for {len(results)} papers to: {excel_path}")

def main():
  
    print("Step 1: Reorganizing files...")
    submission_pdfs = reorganize_folders(SOURCE_FOLDER, DESTINATION_FOLDER)
    
   
    print("\nStep 2: Processing submission PDFs with Gemini AI...")
    results = process_submission_pdfs(submission_pdfs)
    
   
    print("\nStep 3: Saving results to Excel...")
    save_to_excel(results, DESTINATION_FOLDER)
    
    print("\nComplete! All files have been reorganized and research papers analyzed.")

if __name__ == "__main__":
    main()