# Peepalytics
ML_DS_TakeHome Assignment


# Peepalytics: Transaction Data Extraction and Analysis

## Overview

Peepalytics is a data extraction and analysis tool that processes financial transaction data from scanned PDF statements. The project leverages Optical Character Recognition (OCR) to extract transaction information, cleanses and processes the data, and then presents it in a web-based dashboard for analysis and insights.

### Core Components:
- **OCR Extraction**: Uses PaddleOCR to extract text and tables from scanned PDF files.
- **Data Parsing**: Data is parsed, cleaned, and stored for further analysis.
- **Data Redaction**: Sensitive information in the extracted data is redacted to ensure privacy.
- **Web Dashboard**: A user-friendly interface built with Streamlit to interact with and visualize the transaction data.


## Workflow

### 1. **Data Extraction**:
The core extraction process begins with the use of PaddleOCR, an OCR engine that processes the scanned PDF files and extracts structured data. This data extraction pipeline is housed in the `extractor` folder and can be executed via the command line interface (CLI).

To run the extraction, use the following command:
```bash``

python -m extractor --pdf sample_dataset.pdf --output .\data


### What Happens During Extraction:
The ocr.py script extracts text from the provided PDF using PaddleOCR.

The parse.py script processes the raw extracted text to identify and structure the data into fields (like money_in, money_out, date, description, etc.).

The redact.py script redacts any sensitive data, such as account numbers or personal information, ensuring privacy.

### 2. Data Adjustment:
Because of accuracy issues with the OCR extraction, particularly regarding the placement of money-related values, I manually corrected some misplaced data in the extracted table.

Manual Adjustments: Specifically, some values for money-in were incorrectly placed in the money-out column. To address this, I used the Pandas .iloc function in the dashboard.py script to manually move the values from the money-out column to money-in for the affected rows. This ensures that the transaction data reflects the correct amounts and categories.



### 3. Web Dashboard:
Once the data has been cleaned and processed, the next step is to visualize and analyze it. The dashboard.py file creates a Streamlit-based web dashboard where the transaction data can be filtered, visualized, and explored.

Key Features of the Dashboard:
Filters: Users can filter transactions by date, description, and amount range.

KPIs: Key performance indicators (KPIs) such as total inflow, total outflow, and transaction count are displayed at the top of the dashboard.

Charts: Visualizations like daily spend and running balance are plotted to help users understand their transaction trends.

Interactive Table: The transaction data is presented in an interactive table, couldnt achieve the functionality of users clicking any row to view a redacted image of the statement with the transaction details highlighted.


## Folder Structure

        Peepalytics/
        ├── dashboard_helpers/
        │   ├── dashboard.py               # Streamlit Dashboard for displaying transaction data and visualizations
        │   └── page_2_redacted/           # Folder containing the redacted images for each page of the PDF
        ├── data/
        │   ├── ocr/
        │   │   └── page_2_paddleocr_.json # OCR extracted data for page 2
        │   ├── processed/
        │   │   └── page_1.jpg             # Processed image of page 1
        │   │   └── page_2.jpg             # Processed image of page 2
        │   ├── redacted/
        │   │   └── page_2_redacted.jpg    # Redacted image of page 2
        │   ├── account_number_statement_period/
        │   └── transactions.csv           # Final CSV with transaction data
        ├── extractor/
        │   ├── __main__.py                    # Main extraction script to process the PDF
        │   ├── ocr.py                     # OCR extraction logic
        │   ├── parse.py                   # Data parsing logic
        │   └── redact.py                  # Logic to redact sensitive data
        ├── metrics/
        │   └── evaluate.py                # Evaluation metrics script for assessing extraction accuracy
        ├── scripts/
        │   ├── peepalytics_tasks.txt      # Task list for the project
        │   └── README.md                  # Project documentation
        └── venv/
        |    └── # Virtual environment for package management
        |── sample_dataset.pdf
        |── requirements.txt


## Installation & Setup
        Clone the repository:
        Clone this repository to your local machine:
        
        bash
        git clone https://github.com/yourusername/peepalytics.git
        cd peepalytics
        Set up the virtual environment:
        It's recommended to use a virtual environment to manage dependencies:
        
        bash
        python -m venv venv
        source venv/bin/activate  # On Windows, use: venv\Scripts\activate
        Install required dependencies:
        Install all necessary Python packages using pip:
        
        bash
        pip install -r requirements.txt
        Run the extraction pipeline:
        After setting up the environment, use the following command to extract data from a PDF file:
        
        bash
        python -m extractor --pdf sample_dataset.pdf --output .\data
        Run the web dashboard:
        To start the Streamlit dashboard:
        
        bash
        streamlit run dashboard_helpers/dashboard.py
        This will start the Streamlit web app in your browser.

## Conclusion
Peepalytics offers a comprehensive workflow for extracting, processing, redacting, and analyzing transaction data from scanned PDF statements. By leveraging OCR technology and manual adjustments, the tool ensures accurate and insightful transaction analysis. The web dashboard provides an intuitive interface for users to interact with their financial data.


Thanks

Developer name: Promise ibediogwu Ekele

Phone number: +2347063083925

email_address: promiseibediogwu1@gmail.com

github repo:

















