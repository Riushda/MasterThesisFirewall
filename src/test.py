from client.json_parser import JsonParser


def main():
    parser = JsonParser(None, "./input.json")
    print(parser.parse_json())
    print(parser)


if __name__ == "__main__":
    main()
