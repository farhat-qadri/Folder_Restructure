# Research Paper Metadata Extractor

This Python script reorganizes research paper PDFs from a specified folder structure and extracts metadata using the Gemini AI API. The script is designed to work with folders containing research submissions and supplementary materials.

## Features

- Reorganizes PDF files from a folder structure with numbered subfolders
- Extracts metadata from research papers using Google's Gemini AI
- Analyzes PDF structure to determine page count and column format
- Consolidates all metadata into a single Excel spreadsheet

## Prerequisites

### Installation

All required packages are listed in the `requirements.txt` file. Install them with:

```
pip install -r requirements.txt
```

### Google Gemini API Key

You'll need a Google Gemini API key to use this script. You can obtain one by:

1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Sign up or log in
3. Go to API Keys and create a new key
4. Copy the API key for use in the script

## Configuration

Before running the script, you need to modify these variables at the top of the file:

```python
SOURCE_FOLDER = "XYZ"  # Change this to your source folder path
DESTINATION_FOLDER = "XYZ_modified"  # This folder will be created
GEMINI_API_KEY = "AIzaSyATy_wlsCcYpF-_uBoMeDuizWSS2E1OTjY"  # Replace with your API key
```

## Folder Structure

The script expects a specific folder structure:

```
SOURCE_FOLDER/
├── 1/
│   ├── Submission/
│   │   └── paper.pdf
│   └── Supplementary/
│       └── additional.pdf
├── 2/
│   ├── Submission/
│   │   └── paper.pdf
│   └── Supplementary/
...
```

The script will reorganize files into:

```
DESTINATION_FOLDER/
├── 001a_paper.pdf            # From folder 1/Submission
├── 001b_additional.pdf       # From folder 1/Supplementary
├── 002a_paper.pdf            # From folder 2/Submission
...
├── Research_Papers_Metadata.xlsx  # Generated metadata file
```

## Step-by-Step Usage

1. **Install Required Dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Set Up Configuration**
   - Open `fol3.py` in a text editor
   - Set `SOURCE_FOLDER` to the path of your input folder
   - Set `DESTINATION_FOLDER` to your desired output folder
   - Replace `GEMINI_API_KEY` with your Google Gemini API key

3. **Run the Script**
   ```
   python fol3.py
   ```

4. **Monitor Progress**
   - The script will print status updates as it processes each folder and file
   - It will indicate when it's extracting text, sending to Gemini AI, and extracting PDF metadata

5. **Review the Results**
   - After completion, check the `DESTINATION_FOLDER` for:
     - Reorganized PDF files with new naming convention
     - `Research_Papers_Metadata.xlsx` file containing all extracted information

## Extracted Metadata

The script will extract and save the following metadata to Excel:
- Filename
- ID (first 3 characters of filename)
- Title
- Authors
- Number of Authors
- Keywords
- Affiliations
- Page Count
- Column Format (Single or Double Column)

## Troubleshooting

- **PDF Text Extraction Failed**: Some PDFs may have security restrictions or be image-based. Consider using OCR software first.
- **API Rate Limits**: If processing many PDFs, you might hit Google API rate limits. Consider adding delays.
- **Memory Issues**: For very large PDFs, you might need to increase your system's available memory.

## Limitations

- The script only processes the first 10,000 characters of each PDF to stay within API limits
- Image-based PDFs may not yield good text extraction
- API accuracy depends on the quality of the extracted text

## Notes

- The script appends letter 'a' to filenames from Submission folders and 'b' to files from Supplementary folders
- Folder numbers are padded to 3 digits (e.g., folder "7" becomes "007" in filenames)
