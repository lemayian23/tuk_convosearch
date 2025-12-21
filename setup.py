#!/usr/bin/env python3
"""
Setup script for TUK-ConvoSearch
"""
import os
import sys
import shutil
from pathlib import Path

def setup_project():
    """Setup the TUK-ConvoSearch project"""
    print("🚀 Setting up TUK-ConvoSearch MVP...")
    
    # Create necessary directories
    directories = [
        "data/raw",
        "data/processed", 
        "data/vector_db",
        "app/web/templates",
        "tests"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Create sample documents
    create_sample_documents()
    
    # Create .env file if it doesn't exist
    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write("# TUK-ConvoSearch Configuration\n")
            f.write("# Uncomment and set your API keys\n")
            f.write("# OPENAI_API_KEY=your_key_here\n")
            f.write("# For local LLM with Ollama:\n")
            f.write("LLM_PROVIDER=ollama\n")
            f.write("LLM_MODEL=llama2\n")
            f.write("OLLAMA_BASE_URL=http://localhost:11434\n")
            f.write("\n# Conversation History\n")
            f.write("ENABLE_HISTORY=true\n")
            f.write("HISTORY_RETENTION_DAYS=30\n")
        print(f"✓ Created {env_file} file")
    
    # Instructions
    print("\n" + "="*50)
    print("SETUP COMPLETE! 🎉")
    print("="*50)
    print("\n🌟 NEW FEATURE: Conversation History added!")
    print("   - Chat history is now saved")
    print("   - View your conversation history")
    print("   - Start new conversations")
    print("\nNext steps:")
    print("1. Add TUK documents (PDF/DOCX/TXT) to data/raw/")
    print("2. Install Ollama (if using local LLM):")
    print("   Visit: https://ollama.ai/")
    print("3. Pull the LLM model:")
    print("   $ ollama pull llama2")
    print("4. Run the application:")
    print("   $ python -m app.web.main")
    print("5. Open browser: http://localhost:8000")
    print("6. Click 'Upload Docs' button to index documents")
    print("\nFor OpenAI GPT, set OPENAI_API_KEY in .env")
    print("="*50)

def create_sample_documents():
    """Create sample TUK documents for testing"""
    sample_dir = "data/raw"
    
    # Sample admission policy
    admission_policy = """# Technical University of Kenya - Admission Policy 2024

## Undergraduate Admissions
1. Minimum Entry Requirements:
   - KCSE Mean Grade: C+ (Plus)
   - Subject Requirements: Specific cluster subjects as per program

2. Application Period:
   - Regular Intake: January - March
   - September Intake: June - August

3. Required Documents:
   - KCSE Certificate
   - National ID
   - Passport Photo
   - Application Fee Receipt

4. Application Fee: KSh 2,000 (Non-refundable)

## Postgraduate Admissions
1. Minimum Requirements:
   - Bachelor's Degree: Second Class Upper Division
   - Relevant field of study

2. Application Deadlines:
   - May Intake: March 31st
   - January Intake: November 30th

Contact: admissions@tukenya.ac.ke | 020-1234567"""

    # Sample exam regulations
    exam_regulations = """# TUK Examination Regulations

## Examination Periods
Main Examinations:
- May/June Semester: First week of June
- November/December Semester: First week of December

Supplementary Examinations:
- August (for May/June failures)
- January (for November/December failures)

## Grading System
- 70-100%: A (Excellent)
- 60-69%: B (Good)
- 50-59%: C (Average)
- 40-49%: D (Pass)
- Below 40%: F (Fail)

## Important Rules
1. Student ID mandatory for all exams
2. No electronic devices allowed
3. 75% attendance required to sit exams
4. Special exams require medical documentation

Penalty for cheating: Immediate suspension."""

    # Sample fee structure
    fee_structure = """# TUK Fee Structure 2024/2025

## Undergraduate Programs (Per Semester)
1. Engineering Programs: KSh 75,000
2. Computer Science: KSh 70,000
3. Business & Economics: KSh 65,000
4. Built Environment: KSh 68,000

## Payment Schedule
- 60% on registration
- 40% by mid-semester
- Late payment penalty: 5% per month

## Payment Methods
1. Bank Transfer:
   - Bank: Kenya Commercial Bank
   - Account: 1234567890
   - Branch: Tom Mboya Street

2. MPESA:
   - Paybill: 123456
   - Account: Student Registration Number

Financial Aid Office: Room 201, Administration Block"""

    # Write sample files
    with open(f"{sample_dir}/admission_policy.txt", "w") as f:
        f.write(admission_policy)
    
    with open(f"{sample_dir}/exam_regulations.txt", "w") as f:
        f.write(exam_regulations)
    
    with open(f"{sample_dir}/fee_structure.txt", "w") as f:
        f.write(fee_structure)
    
    print("✓ Created 3 sample TUK documents")

if __name__ == "__main__":
    setup_project()2222227  1e1/1`  ;./q`>

