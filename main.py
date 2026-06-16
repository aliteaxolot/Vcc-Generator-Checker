import re
import os
import random
from datetime import datetime
import colorama
from colorama import Fore, Style, Back

# VCC Validator Functions
def validate_vcc(card_info):
    """
    Validates virtual credit card information in the format: number|date|year|cvc
    Returns a dictionary with validation results
    """
    parts = card_info.strip().split('|')
    
    # Check if format is correct
    if len(parts) != 4:
        return {
            "card": card_info,
            "valid": False,
            "error": "Invalid format. Expected: number|month|year|cvc"
        }
    
    card_number, month, year, cvc = parts
    
    # Validate card number (using Luhn algorithm)
    if not is_valid_card_number(card_number):
        return {
            "card": card_info,
            "valid": False,
            "error": "Invalid card number"
        }
    
    # Validate expiration date
    try:
        month = int(month)
        year = int(year)
        
        if not (1 <= month <= 12):
            return {
                "card": card_info,
                "valid": False,
                "error": "Invalid month (must be 1-12)"
            }
        
        # Add 2000 if year is only 2 digits
        if year < 100:
            year += 2000
            
        # Check if card is expired
        current_date = datetime.now()
        if year < current_date.year or (year == current_date.year and month < current_date.month):
            return {
                "card": card_info,
                "valid": False,
                "error": "Card expired"
            }
    except ValueError:
        return {
            "card": card_info,
            "valid": False,
            "error": "Invalid date format"
        }
    
    # Validate CVC
    if not re.match(r'^\d{3,4}$', cvc):
        return {
            "card": card_info,
            "valid": False,
            "error": "Invalid CVC (must be 3 or 4 digits)"
        }
    
    # Determine card type based on number
    card_type = get_card_type(card_number)
    
    return {
        "card": card_info,
        "valid": True,
        "card_type": card_type,
        "error": None
    }

def is_valid_card_number(card_number):
    """
    Validates a credit card number using the Luhn algorithm
    """
    # Remove any spaces or dashes
    card_number = card_number.replace(' ', '').replace('-', '')
    
    # Check if card number contains only digits
    if not card_number.isdigit():
        return False
    
    # Check length based on card type
    if not 13 <= len(card_number) <= 19:
        return False
    
    # Luhn algorithm
    digits = [int(d) for d in card_number]
    checksum = 0
    odd_even = len(digits) % 2
    
    for i, digit in enumerate(digits):
        if (i + odd_even) % 2 == 0:
            doubled = digit * 2
            checksum += doubled if doubled < 10 else doubled - 9
        else:
            checksum += digit
    
    return checksum % 10 == 0

def get_card_type(card_number):
    """
    Determines credit card type based on the card number pattern
    """
    # Remove spaces and dashes
    card_number = card_number.replace(' ', '').replace('-', '')
    
    # Visa
    if re.match(r'^4[0-9]{12}(?:[0-9]{3})?$', card_number):
        return "Visa"
    
    # Mastercard
    elif re.match(r'^5[1-5][0-9]{14}$', card_number):
        return "Mastercard"
    
    # American Express
    elif re.match(r'^3[47][0-9]{13}$', card_number):
        return "American Express"
    
    # Discover
    elif re.match(r'^6(?:011|5[0-9]{2})[0-9]{12}$', card_number):
        return "Discover"
    
    # Other
    else:
        return "Unknown"

def read_vccs_from_file(filename="vcc.txt"):
    """
    Reads VCCs from a file, one per line
    """
    vccs = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    vccs.append(line)
        return vccs
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def save_results_to_file(results, filename="vcc_results.txt"):
    """
    Saves validation results to a file
    """
    try:
        # Create separate files for valid and invalid VCCs
        valid_file = filename.replace('.txt', '_valid.txt')
        invalid_file = filename.replace('.txt', '_invalid.txt')
        
        # Write all results to main file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("VCC Validation Results\n")
            file.write("-" * 60 + "\n")
            
            valid_count = 0
            invalid_count = 0
            
            for result in results:
                if result["valid"]:
                    valid_count += 1
                    file.write(f"VALID: {result['card']} - {result['card_type']}\n")
                else:
                    invalid_count += 1
                    file.write(f"INVALID: {result['card']} - Error: {result['error']}\n")
            
            file.write("-" * 60 + "\n")
            file.write(f"Summary: {valid_count} valid and {invalid_count} invalid VCCs (Total: {len(results)})\n")
        
        # Write valid VCCs to separate file
        with open(valid_file, 'w', encoding='utf-8') as file:
            file.write("Valid VCCs\n")
            file.write("-" * 60 + "\n")
            
            for result in results:
                if result["valid"]:
                    file.write(f"{result['card']}\n")
            
            file.write("-" * 60 + "\n")
            file.write(f"Total: {valid_count} valid VCCs\n")
        
        # Write invalid VCCs to separate file
        with open(invalid_file, 'w', encoding='utf-8') as file:
            file.write("Invalid VCCs\n")
            file.write("-" * 60 + "\n")
            
            for result in results:
                if not result["valid"]:
                    file.write(f"{result['card']} - Error: {result['error']}\n")
            
            file.write("-" * 60 + "\n")
            file.write(f"Total: {invalid_count} invalid VCCs\n")
        
        return {
            "main": filename,
            "valid": valid_file,
            "invalid": invalid_file
        }
    except Exception as e:
        print(f"Error saving results: {e}")
        return None

# Credit Card Generator Functions
def generate_card():
    """
    Generate one credit card in the format: number|month|year|cvc
    """
    prefix = "415464440104"
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(25, 30))
    cvv = str(random.randint(100, 999))
    return f"{prefix}{suffix}|{month}|20{year}|{cvv}"

def show_card(card):
    """
    Display card with full address details
    """
    print(f"\nGenerated Card: {card}")
    print("CARDHOLDER NAME : TROLEX_001")
    print("COUNTRY : UNITED KINGDOM")
    print("ADDRESS : UK ")
    print("ADDRESS 2 : UK ")
    print("CITY : UK ")
    print("STATS : UK")
    print("POSTAL CODE : LU3 1NZ")

# Common UI Functions
def print_header():
    """Print the Confession Cafe VCC Checker header in blue bold text"""
    header = f"""
    {Fore.BLUE}{Style.BRIGHT}	    			╔═════════════════════════════════════════════════════╗
    				║						      ║
    				║		      CONFESSION TOOL  	    	      ║
    				║						      ║
    				║═════════════════════════════════════════════════════║
    				║						      ║
    				║		      VCC GEN & CHECKER	  	      ║
    				║						      ║
    				╚═════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(header)

# VCC Checker Functions
def check_single_card():
    """
    Function to check a single card entered by user
    """
    print("\nSingle Card Validation")
    print("Format: number|month|year|cvc")
    print("Example: 4111111111111111|05|2029|123\n")
    
    card_info = input("Enter card details: ")
    result = validate_vcc(card_info)
    
    print("\nValidation Result:")
    print("-" * 60)
    
    if result["valid"]:
        print(f"{Fore.GREEN}VALID:{Style.RESET_ALL} {result['card']}")
    else:
        print(f"{Fore.RED}INVALID:{Style.RESET_ALL} {result['card']} - Error: {result['error']}")
    
    print("-" * 60)
    input("\nPress Enter to continue...")

def check_multiple_cards():
    """
    Function to check multiple cards from a file
    """
    # Define the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__)) or "."
    vcc_file = os.path.join(script_dir, "vcc.txt")
    results_file = os.path.join(script_dir, "vcc_results.txt")
    
    # Check if vcc.txt exists
    if not os.path.exists(vcc_file):
        print(f"\nError: vcc.txt file not found in {script_dir}")
        print("Creating a template file for you...")
        
        # Create an empty vcc.txt file for convenience
        try:
            with open(vcc_file, "w", encoding='utf-8') as f:
                f.write("# Add your VCCs below (one per line)\n")
                f.write("# Format: number|month|year|cvc\n")
                f.write("# Example: 4111111111111111|05|2029|123\n")
            
            print(f"\nAn empty vcc.txt file has been created at: {vcc_file}")
            print("Please add your VCCs to this file and run the program again.")
            input("\nPress Enter to continue...")
            return
        except Exception as e:
            print(f"Error creating template file: {e}")
            input("\nPress Enter to continue...")
            return
    
    # Read VCCs from file
    vccs = read_vccs_from_file(vcc_file)
    
    if not vccs or len(vccs) == 0:
        print(f"\nNo VCCs found in {vcc_file} or the file is empty.")
        print("Please add VCCs in the format: number|month|year|cvc")
        input("\nPress Enter to continue...")
        return
    
    print(f"\nFound {len(vccs)} VCCs in vcc.txt")
    print("Validating...")
    
    # Validate all VCCs
    results = []
    for vcc in vccs:
        results.append(validate_vcc(vcc))
    
    # Count valid and invalid
    valid_count = sum(1 for r in results if r["valid"])
    invalid_count = len(results) - valid_count
    
    # Display results in console
    print("\nValidation Results:")
    print("-" * 60)
    
    if valid_count > 0:
        print(f"{Fore.GREEN}VALID VCCs ({valid_count}):{Style.RESET_ALL}")
        for result in results:
            if result["valid"]:
                print(f"- {result['card']}")
    
    if invalid_count > 0:
        print(f"\n{Fore.RED}INVALID VCCs ({invalid_count}):{Style.RESET_ALL}")
        for result in results:
            if not result["valid"]:
                print(f"- {result['card']} - Error: {result['error']}")
    
    print("-" * 60)
    print(f"Summary: {valid_count} valid and {invalid_count} invalid VCCs (Total: {len(results)})")
    
    # Save results to files
    output_files = save_results_to_file(results, results_file)
    if output_files:
        print(f"\nResults saved to:")
        print(f"- All results: {output_files['main']}")
        print(f"- Valid VCCs: {output_files['valid']}")
        print(f"- Invalid VCCs: {output_files['invalid']}")
        
        # Double check that files exist
        for file_type, file_path in output_files.items():
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            if file_size == 0:
                print(f"Warning: {file_type} file appears to be empty")
    else:
        print("\nError: Failed to save results to file.")
    
    input("\nPress Enter to continue...")

# CC Generator Functions
def generate_single_card():
    """Function to generate a single card"""
    card = generate_card()
    show_card(card)
    input("\nPress Enter to continue...")

def generate_multiple_cards():
    """Function to generate multiple cards"""
    try:
        target = int(input("Enter number of cards to generate: "))
        cards = [generate_card() for _ in range(target)]
        print(f"\nTarget: {target} cards generated.")
        for c in cards:
            show_card(c)
        while True:
            print("\n1. Save")
            print("2. No Save")
            print("3. Regenerate")
            opt = input("Choose an option (1/2/3): ").strip()
            if opt == "1":
                with open("vcc.txt", "w") as f:
                    for c in cards:
                        f.write(c + "\n")
                print("Saved to cc_dump.txt")
                break
            elif opt == "2":
                print("Not saved.")
                break
            elif opt == "3":
                return generate_multiple_cards()
            else:
                print("Invalid option.")
    except ValueError:
        print("Please enter a valid number.")
    
    input("\nPress Enter to continue...")

def main():
    # Initialize colorama
    colorama.init()
    
    while True:
        # Clear screen (cross-platform)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Display the new header
        print_header()
        
        # Display main menu
        print(f"\n{Fore.CYAN}Select an option:{Style.RESET_ALL}")
        print("1. VCC Checker")
        print("2. VCC Generator")
        print("3. Exit")
        
        choice = input("\nChoice (1-3): ")
        
        if choice == '1':
            # VCC Checker submenu
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print_header()
                print(f"\n{Fore.CYAN}VCC Checker Options:{Style.RESET_ALL}")
                print("1. Check Single Card")
                print("2. Check Multiple Cards (from vcc.txt)")
                print("3. Back to Main Menu")
                
                checker_choice = input("\nChoice (1-3): ")
                
                if checker_choice == '1':
                    check_single_card()
                elif checker_choice == '2':
                    check_multiple_cards()
                elif checker_choice == '3':
                    break
                else:
                    print(f"\n{Fore.RED}Invalid choice. Please select 1, 2, or 3.{Style.RESET_ALL}")
                    input("\nPress Enter to continue...")
                    
        elif choice == '2':
            # VCC Generator submenu
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print_header()
                print(f"\n{Fore.CYAN}VCC Generator Options:{Style.RESET_ALL}")
                print("1. Generate 1 credit card")
                print("2. Generate multiple credit cards")
                print("3. Back to Main Menu")
                
                generator_choice = input("\nChoice (1-3): ")
                
                if generator_choice == '1':
                    generate_single_card()
                elif generator_choice == '2':
                    generate_multiple_cards()
                elif generator_choice == '3':
                    break
                else:
                    print(f"\n{Fore.RED}Invalid choice. Please select 1, 2, or 3.{Style.RESET_ALL}")
                    input("\nPress Enter to continue...")
                    
        elif choice == '3':
            print("\nThank you for using Confession Tool VCC!")
            break
        else:
            print(f"\n{Fore.RED}Invalid choice. Please select 1, 2, or 3.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
