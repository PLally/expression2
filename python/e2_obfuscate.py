import re
import logging
import argparse

logging.basicConfig(level=logging.INFO)


def replace_index(start, end, string='', repl=''):
    return f'{string[:start]}{repl}{string[end:]}'


class Expression2:
    """represents expression2 code

    args:
    filename (str): filename to read e2 code from
    text (str):  e2 code, text is only used if filename is not specified
    """
    def __init__(self, filename=None, text=None):
        if filename is not None:
            try:
                with open(filename, "r") as file:
                    self.text = file.read()
            except FileNotFoundError as e:
                logging.warning('file does not exists')
                if text is not None:
                    self.text = text
                else:
                    raise e

        elif text is not None:
            self.text = text

        self.name = None
        self.variables = []

    def save(self, filename):
        """save text to a file"""
        with open(filename, 'w') as file:
            file.write(self.text)

    def obfuscate(self):
        """obfuscate e2 text

        This function compresses the e2 text to as few lines as possible and
        replaces variable names with a series of ls and 1s"""
        self.text = re.sub(r'#\[[^]]*\]#', ' ', self.text)  # remove multi line comments

        lines = self.text.split('\n')
        new_text = ''

        logging.debug('obfuscating e2')
        variables = {}
        quotes = []
        for line in lines:

            if len(quotes) % 2 == 0:
                line = line.lstrip()

            if line == '':
                if len(quotes) % 2 == 0:
                    continue
                else:
                    print(i)
                    new_text += "\n"
                    continue

            if line.startswith('#ifdef') or line.startswith('#endif') or line.startswith('#else') or line.startswith('#include'):
                new_text += '\n' + line + '\n'
                continue

            line = re.sub(r'#.*', ' ', line)

            if not (line.startswith('@model ') or line.startswith('@name ')):
                # the following while loop is responsible for obfuscating variable names
                # it iterates over a list of quotes and potential variable names
                # it determines if the potential variable name is within quotes
                # if it is not, the variable is added to a dict and replaced
                q_iter = re.finditer('"', line)
                v_iter = re.finditer(r'(?:(?<=[^a-zA-Z0-9_])|(?<=^))[A-Z][a-zA-Z0-9_]*', line)
                q = next(q_iter, None)
                v = next(v_iter, None)
                offset = 0

                while q is not None or v is not None:

                    if v is not None and v.group() == 'This':
                        # do not obfuscate "This" as it has special meaning.
                        v = next(v_iter, None)
                    elif q is not None and (v is None or q.end() < v.end()):
                        # if the quote has a smaller index than the variable add them to the quotes list
                        quotes.append(q)
                        q = next(q_iter, None)
                    elif v is not None and (q is None or v.end() < q.end()):

                        if len(quotes) % 2 == 0:  # if the potential variable is not within quotes
                            if v.group(0) not in variables:
                                logging.debug(f'variable found: {v.group(0)}')
                                variables[v.group(0)] = f'I{len(variables):b}'.replace('0', 'l')

                            line = replace_index(v.start()+offset, v.end()+offset, line, variables[v.group(0)])

                            offset += len(variables[v.group(0)])-len(v.group(0))
                        v = next(v_iter, None)

            if line[:1] == '@' or len(quotes) % 2 != 0:
                new_text += line + '\n'
            else:
                new_text += line + ' '
        self.text = new_text

        return self.text


def main(file, out):
    if out is None:
        out_file = file.replace('.txt', '') + '_obfuscated.txt'
    else:
        out_file = out
    e2 = Expression2(filename=file)
    e2.obfuscate()
    e2.save(filename=out_file)
    print(f'Saved as {out_file}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Obfuscate e2s by removing new lines and '
                                                 'replacing variable making them harder to read')
    parser.add_argument('file', nargs='?', default=None, type=str, metavar='e2_file',
                        help='e2 file to obfuscate')
    parser.add_argument('out', nargs='?', default=None, type=str, metavar='output_file',
                        help='file to write obfuscated code to')

    args = parser.parse_args()
    if args is not None and args.file is not None:
        main(args.file, args.out)
    else:
        print('a filepath was not specified')
        file_input = input('e2 file:')
        main(file_input, None)


