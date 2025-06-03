import os
import argparse
import sys
from pypdf import PdfWriter, PdfReader
from pypdf.errors import PdfReadError
import re

def natural_sort_key(s):
    """Sort helper that handles numbers naturally (e.g., file2 before file10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def merge_pdfs(input_paths, output_path, sort_files=False):
    """
    Merges multiple PDF files specified in input_paths into a single
    PDF file saved at output_path.

    Args:
        input_paths (list): A list of strings, where each string is the
                            path to an input PDF file.
        output_path (str): The path where the merged PDF file will be saved.
        sort_files (bool): If True, sort the input files alphabetically by path
                           before merging. Defaults to False.
    """
    merger = PdfWriter()
    pdf_files_processed = []
    total_pages_added = 0

    #if sort_files:
     #   input_paths.sort()

    if sort_files:
        input_paths.sort(key=natural_sort_key)

    print("Starting PDF merge process...")
    print(f"Output file will be: {output_path}")

    for path in input_paths:
        if not os.path.exists(path):
            print(f"Warning: File not found, skipping: {path}")
            continue

        if not path.lower().endswith('.pdf'):
            print(f"Warning: File is not a PDF, skipping: {path}")
            continue

        try:
            print(f"Processing: {os.path.basename(path)} ... ", end="")
            with open(path, 'rb') as infile:
                reader = PdfReader(infile)
                if reader.is_encrypted:
                     # Attempt to decrypt with an empty password, might fail for protected files
                    try:
                        reader.decrypt('')
                        print("(decrypted with empty password) ", end="")
                    except Exception as decrypt_error:
                        print(f"\nError: File is encrypted and could not be decrypted: {path}. Skipping. Error: {decrypt_error}")
                        continue # Skip this file

                num_pages = len(reader.pages)
                if num_pages == 0:
                    print(f"\nWarning: File seems empty or corrupted (0 pages): {path}. Skipping.")
                    continue

                # Add the entire PDF (more efficient than page by page for pypdf)
                merger.append(fileobj=infile)
                pdf_files_processed.append(os.path.basename(path))
                total_pages_added += num_pages
                print(f"Added {num_pages} pages.")

        except PdfReadError as e:
            print(f"\nError: Could not read PDF (possibly corrupted): {path}. Skipping. Details: {e}")
        except Exception as e:
            print(f"\nAn unexpected error occurred processing {path}: {e}. Skipping.")

    if not pdf_files_processed:
        print("\nError: No valid PDF files were found or processed. No output file created.")
        merger.close() # Close the writer even if nothing was added
        return False

    try:
        print(f"\nWriting merged PDF ({total_pages_added} total pages) to: {output_path} ...")
        with open(output_path, 'wb') as outfile:
            merger.write(outfile)
        print("Merge successful!")
        print("\nFiles merged (in order):")
        for i, name in enumerate(pdf_files_processed):
            print(f"  {i+1}. {name}")
        return True
    except Exception as e:
        print(f"\nError writing output file {output_path}: {e}")
        return False
    finally:
        merger.close() # Ensure the writer is closed even if errors occur during write


def find_pdfs_in_directory(directory_path):
    """Finds all PDF files in the specified directory."""
    pdf_files = []
    if not os.path.isdir(directory_path):
        print(f"Error: Input directory not found: {directory_path}")
        sys.exit(1) # Exit if the directory doesn't exist

    print(f"Scanning directory: {directory_path}")
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(".pdf"):
            full_path = os.path.join(directory_path, filename)
            pdf_files.append(full_path)
    return pdf_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge multiple PDF files into a single document.",
        formatter_class=argparse.RawTextHelpFormatter # Better help message formatting
        )

    parser.add_argument(
        'input',
        nargs='*',  # 0 or more arguments
        help="Paths to the input PDF files to merge. \n"
             "Example: python merge_pdfs.py file1.pdf file2.pdf file3.pdf"
        )

    parser.add_argument(
        '-d', '--directory',
        help="Path to a directory containing PDF files to merge. \n"
             "If provided, all PDFs in this directory will be merged. \n"
             "This overrides any individual files listed in 'input'. \n"
             "Example: python merge_pdfs.py -d /path/to/pdfs"
        )

    parser.add_argument(
        '-o', '--output',
        default='merged_output.pdf',
        help="Path for the output merged PDF file. \n"
             "Default: merged_output.pdf"
        )

    parser.add_argument(
        '-s', '--sort',
        action='store_true', # Makes it a flag, no argument needed
        help="Sort the input PDF files alphabetically by path before merging. \n"
             "Useful mainly when using the --directory option."
        )

    args = parser.parse_args()

    input_files = []

    if args.directory:
        # Use directory input
        input_files = find_pdfs_in_directory(args.directory)
        if not input_files:
            print(f"Error: No PDF files found in directory: {args.directory}")
            sys.exit(1) # Exit if no PDFs found in the specified dir
    elif args.input:
        # Use individual file input
        input_files = args.input
    else:
        # No input specified
        parser.print_help()
        print("\nError: You must provide input PDF files or specify an input directory using -d/--directory.")
        sys.exit(1) # Exit if no input method is chosen

    # Perform the merge
    success = merge_pdfs(input_files, args.output, args.sort)

    if not success:
        sys.exit(1) # Exit with an error code if merge failed