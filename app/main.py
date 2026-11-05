# AI Personal Study Assistant

def main():
    print("===================================")
    print("     AI PERSONAL STUDY ASSISTANT")
    print("===================================")

    print("\nAvailable features:")
    print("1. Upload study materials")
    print("2. Ask questions")
    print("3. Generate summaries")
    print("4. Generate exam questions")

    choice = input("\nEnter your choice (1-4): ")

    if choice == "1":
        print("You selected: Upload study materials")

    elif choice == "2":
        print("You selected: Ask questions")

    elif choice == "3":
        print("You selected: Generate summaries")

    elif choice == "4":
        print("You selected: Generate exam questions")

    else:
        print("Invalid choice. Please select 1-4.")


if __name__ == "__main__":
    main()