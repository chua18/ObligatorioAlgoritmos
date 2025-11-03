def get_message_type(message):
    content = ""
    message_type = message["type"]

    if message_type == "text":
        content = message["text"]["body"]

    elif message_type == "interactive":
        interactive_object = message["interactive"]
        interactive_type = interactive_object["type"]

        if interactive_type == "button_reply":
            content = interactive_object["button_reply"]["title"]
        elif interactive_type == "list_reply":
            content = interactive_object["list_reply"]["title"]
        else:
            print("sin mensaje")
    else:
        print("sin mensaje")

    return message_type, content