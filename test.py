from slugify import slugify

def main():
    name = '[萌萌喵梦子]鹿岛(78P)'
    name_output = slugify(name, separator=" ")
    print(name_output)

if __name__ == '__main__':
    main()
    