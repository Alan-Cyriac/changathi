from colorama import init
init()
from colorama import Fore, Back, Style
print(Fore.RED + 'some red text')
print(Fore.GREEN + 'and with a green background')
print(Style.DIM + 'and in dim text')
print(Style.RESET_ALL)
print('back to normal now')

print('\033[31m' + 'some red text')
print('\033[39m')